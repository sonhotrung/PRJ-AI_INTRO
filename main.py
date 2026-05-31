import streamlit as st
import pandas as pd
import folium
import os
from streamlit_folium import st_folium
from folium import plugins

from engine import search_algorithm
from api import get_real_road_curve

st.set_page_config(page_title="KL Smart Map", layout="wide")

# --- 1. KHỞI TẠO BỘ NHỚ RAM ---
if 'map_data_loaded' not in st.session_state:
    n_df = pd.read_csv('data/nodes.csv')
    e_df = pd.read_csv('data/edges.csv')
    if 'ID' not in e_df.columns: e_df = e_df.reset_index().rename(columns={'index': 'ID'})
    if 'blocked' not in e_df.columns: e_df['blocked'] = False
    if 'blocked' not in n_df.columns: n_df['blocked'] = False
    
    st.session_state.nodes_df = n_df
    st.session_state.edges_df = e_df
    st.session_state.map_data_loaded = True

if 'start_node' not in st.session_state: st.session_state.start_node = None
if 'end_node' not in st.session_state: st.session_state.end_node = None
if 'result_path' not in st.session_state: st.session_state.result_path = None
if 'last_processed_click' not in st.session_state: st.session_state.last_processed_click = None

nodes_df = st.session_state.nodes_df
edges_df = st.session_state.edges_df
nodes = {r['name']: (r['lat'], r['lon']) for _, r in nodes_df.iterrows()}

# --- 2. XỬ LÝ SỰ KIỆN CLICK (STATE MACHINE) TRƯỚC KHI VẼ ---
map_state = st.session_state.get("ai_maps")
click_message = None

if map_state and map_state.get("last_active_drawing"):
    props = map_state["last_active_drawing"]["properties"]
    click_id = props.get("name")
    
    if click_id and click_id != st.session_state.last_processed_click:
        st.session_state.last_processed_click = click_id
        is_admin = (st.session_state.get("role_select") == "⚙️ Điều độ viên (Admin)")
        
        if is_admin:
            # QUYỀN ADMIN: TẮT/MỞ ĐƯỜNG VÀ ĐIỂM
            if props.get("type") == "edge":
                e_id = props["edge_id"]
                current_state = st.session_state.edges_df.loc[st.session_state.edges_df['ID'] == e_id, 'blocked'].values[0]
                st.session_state.edges_df.loc[st.session_state.edges_df['ID'] == e_id, 'blocked'] = not current_state
            elif props.get("type") == "node":
                node_name = props["name"]
                current_state = st.session_state.nodes_df.loc[st.session_state.nodes_df['name'] == node_name, 'blocked'].values[0]
                st.session_state.nodes_df.loc[st.session_state.nodes_df['name'] == node_name, 'blocked'] = not current_state
        else:
            # QUYỀN USER: MÁY TRẠNG THÁI (STATE MACHINE)
            if props.get("type") == "node":
                node_name = props["name"]
                
                # Kiểm tra điểm có đang bị Admin phong tỏa không
                if st.session_state.nodes_df.loc[st.session_state.nodes_df['name'] == node_name, 'blocked'].values[0]:
                    click_message = ("error", "Điểm này đang bị phong tỏa ⛔, không thể chọn!")
                else:
                    if st.session_state.start_node is None:
                        st.session_state.start_node = node_name
                    elif st.session_state.end_node is None:
                        if node_name == st.session_state.start_node:
                            click_message = ("warning", "Bạn đã chọn điểm này làm xuất phát rồi!")
                        else:
                            st.session_state.end_node = node_name
                            click_message = ("info", "Đang tính toán lộ trình AI...")
                    else:
                        # Reset nếu click lần 3
                        st.session_state.start_node = node_name
                        st.session_state.end_node = None
                        st.session_state.result_path = None
            else:
                click_message = ("warning", "Vui lòng click vào Giao lộ (chấm), không click vào dây đường!")

# --- 3. CẬP NHẬT ĐỒ THỊ & CHẠY AI ---
blocked_nodes_set = set(st.session_state.nodes_df[st.session_state.nodes_df['blocked'] == True]['name'])
graph_edges = {}
for _, r in st.session_state.edges_df.iterrows():
    u, v, b = r['node1'], r['node2'], r['blocked']
    if u not in graph_edges: graph_edges[u] = []
    graph_edges[u].append((v, b))
    if v not in graph_edges: graph_edges[v] = []
    graph_edges[v].append((u, b))

if st.session_state.start_node and st.session_state.end_node and st.session_state.result_path is None:
    algo = st.session_state.get("algo_select", "A*")
    path, cost, exp = search_algorithm(
        st.session_state.start_node, st.session_state.end_node, 
        nodes, graph_edges, blocked_nodes_set, algo
    )
    if path:
        st.session_state.result_path = path
        click_message = ("success", f"Đã tìm thấy đường! Duyệt {exp} nút. Chi phí: {cost:.2f} km")
    else:
        st.session_state.result_path = [] # Mảng rỗng báo hiệu không có đường
        click_message = ("error", "Đường đã bị phong tỏa hoàn toàn, không có cách nào tới đích!")

if click_message:
    msg_type, msg_text = click_message
    if msg_type == "warning": st.toast(msg_text, icon="⚠️")
    elif msg_type == "error": st.toast(msg_text, icon="🚫")
    elif msg_type == "success": st.toast(msg_text, icon="✅")
    elif msg_type == "info": st.toast(msg_text, icon="ℹ️")

# --- 4. GIAO DIỆN SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ KL Smart Navigator")
    role = st.selectbox("Vai trò", ["👤 Hành khách (User)", "⚙️ Điều độ viên (Admin)"], key="role_select")
    st.divider()
    
    if role == "⚙️ Điều độ viên (Admin)":
        st.error("🛠️ **CHẾ ĐỘ ADMIN:** Click vào điểm hoặc đường để Chặn/Mở khóa.")
        if st.button("💾 LƯU VĨNH VIỄN", type="primary", use_container_width=True):
            st.session_state.edges_df.to_csv('data/edges.csv', index=False)
            st.session_state.nodes_df.to_csv('data/nodes.csv', index=False)
            st.success("Đã cập nhật hệ thống thành công!")
        if st.button("🔄 Mở khóa toàn bộ", use_container_width=True):
            st.session_state.edges_df['blocked'] = False
            st.session_state.nodes_df['blocked'] = False
            st.session_state.last_processed_click = None 
            st.rerun()
    else:
        st.info("💡 **HƯỚNG DẪN:**\n- Click Nút lần 1: Chọn Điểm Đi\n- Click Nút lần 2: Chọn Điểm Đến (AI tự chạy)\n- Click Nút lần 3: Làm lại từ đầu")
        st.write("🟢 **Điểm đi:**", st.session_state.start_node if st.session_state.start_node else "*(Chưa chọn)*")
        st.write("🟡 **Điểm đến:**", st.session_state.end_node if st.session_state.end_node else "*(Chưa chọn)*")
        algo = st.selectbox("Thuật toán AI", ["A*", "UCS", "BFS"], key="algo_select")
        
        if st.button("🔄 Làm mới / Xóa Lộ Trình", use_container_width=True):
            st.session_state.start_node = None
            st.session_state.end_node = None
            st.session_state.result_path = None
            st.session_state.last_processed_click = None 
            st.rerun()

# --- 5. VẼ BẢN ĐỒ VỚI BẢNG MÀU CHUẨN XÁC ---
m = folium.Map(location=[3.145, 101.695], zoom_start=14, tiles="cartodbpositron")
edge_features, node_features = [], []

for _, r in st.session_state.edges_df.iterrows():
    u, v = r['node1'], r['node2']
    if u not in nodes or v not in nodes: continue
    
    is_b = r['blocked']
    curved_coords = get_real_road_curve(nodes[u], nodes[v], u, v)
    
    # Ép kiểu và LÀM NHẸ 50% SỐ ĐIỂM BẰNG SLICE [::2]
    geom_coords = [[float(coord[1]), float(coord[0])] for coord in curved_coords[::2]]

    edge_features.append({
        "type": "Feature",
        "properties": {
            "type": "edge", "edge_id": int(r['ID']), "name": f"{u} ↔ {v}",
            "status": "Đường bị chặn ⛔" if is_b else "Thông xe 🟢",
            "color": "#FF004D" if is_b else "#999999", 
            "weight": 5, "dash": "5, 5" if is_b else "1"
        },
        "geometry": {"type": "LineString", "coordinates": geom_coords}
    })

for name, coords in nodes.items():
    is_blocked = name in blocked_nodes_set
    # MẶC ĐỊNH MÀU ĐEN
    color, rad, status_text = "#000000", 7, "Giao lộ"
    
    if is_blocked: 
        color, rad, status_text = "#FF0000", 9, "ĐIỂM PHONG TỎA ⛔"
    elif name == st.session_state.start_node: 
        color, rad = "#00FF00", 11 # ĐIỂM ĐI: XANH LÁ
    elif name == st.session_state.end_node: 
        color, rad = "#FFD700", 11 # ĐIỂM ĐẾN: VÀNG

    node_features.append({
        "type": "Feature",
        "properties": {
            "type": "node", "name": name, 
            "status": status_text, "color": color, 
            "weight": 2, "radius": rad
        },
        "geometry": {"type": "Point", "coordinates": [float(coords[1]), float(coords[0])]}
    })

folium.GeoJson(
    {"type": "FeatureCollection", "features": edge_features},
    style_function=lambda x: {"color": x["properties"]["color"], "weight": x["properties"]["weight"], "dashArray": x["properties"]["dash"]},
    tooltip=folium.GeoJsonTooltip(fields=["name", "status"], aliases=["Tuyến:", "Trạng thái:"], labels=True)
).add_to(m)

folium.GeoJson(
    {"type": "FeatureCollection", "features": node_features},
    marker=folium.CircleMarker(fill=True, fillOpacity=1),
    style_function=lambda x: {"color": "#FFFFFF", "fillColor": x["properties"]["color"], "weight": 1, "radius": x["properties"]["radius"]},
    tooltip=folium.GeoJsonTooltip(fields=["name", "status"], aliases=["Điểm:", "Trạng thái:"], labels=True)
).add_to(m)

# ANIMATION LỘ TRÌNH (ÁP DỤNG LÀM NHẸ [::2])
if st.session_state.result_path and len(st.session_state.result_path) >= 2:
    path = st.session_state.result_path
    full_coords = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        curved = get_real_road_curve(nodes[u], nodes[v], u, v)
        if i == 0: full_coords.extend(curved[::2])
        else: full_coords.extend(curved[1::2])
    
    if len(full_coords) >= 2:
        plugins.AntPath(locations=full_coords, color="#0068c9", pulse_color="#FFFFFF", weight=7, opacity=0.9, delay=800).add_to(m)

# VŨ KHÍ BÍ MẬT CHỐNG TRẮNG MÀN HÌNH
st_folium(
    m, 
    use_container_width=True, 
    height=650, 
    key="ai_maps",
    returned_objects=["last_active_drawing"]
)