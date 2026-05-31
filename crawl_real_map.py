import requests
import pandas as pd
import os
import math
import time

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_fallback_data():
    print("\n⚠️ KÍCH HOẠT PHƯƠNG ÁN B: Sử dụng bộ dữ liệu Local (Offline)...")
    nodes_data = [['KL Sentral', 3.1344, 101.6865], ['KLCC', 3.1590, 101.7135], ['Bukit Bintang', 3.1462, 101.7113],
                  ['Pasar Seni', 3.1427, 101.6955], ['Masjid Jamek', 3.1497, 101.6963], ['Ampang Park', 3.1598, 101.7180],
                  ['Merdeka', 3.1423, 101.7018], ['Chinatown', 3.1439, 101.6975], ['Muzium Negara', 3.1375, 101.6874]]
    edges_data = [['KL Sentral', 'Pasar Seni'], ['Pasar Seni', 'Masjid Jamek'], ['Masjid Jamek', 'KLCC'],
                  ['KLCC', 'Ampang Park'], ['Muzium Negara', 'Pasar Seni'], ['Pasar Seni', 'Merdeka'],
                  ['Merdeka', 'Bukit Bintang'], ['Chinatown', 'Pasar Seni'], ['KLCC', 'Bukit Bintang']]
    
    if not os.path.exists('data'): os.makedirs('data')
    pd.DataFrame([{'name': n[0], 'lat': n[1], 'lon': n[2], 'blocked': False} for n in nodes_data]).to_csv('data/nodes.csv', index=False)
    pd.DataFrame([{'node1': e[0], 'node2': e[1], 'blocked': False} for e in edges_data]).to_csv('data/edges.csv', index=False)
    print("✅ Đã chuẩn bị xong Dữ liệu Local. Hãy chạy 'streamlit run main.py'!")

def crawl_kuala_lumpur_roads():
    print("🌍 Bắt đầu thu thập dữ liệu không gian trạng thái Kuala Lumpur...")
    
    overpass_query = """
    [out:json][timeout:25];
    way["highway"~"primary|trunk"](3.13, 101.68, 3.16, 101.72);
    (._;>;);
    out body;
    """
    
    # 3 Server dự phòng chống block
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]
    
    headers = {'User-Agent': 'HUST_AI_Project_Student/2.0 (IT3160)'}
    data = None

    # Tự động nhảy Server nếu bị lỗi
    for url in endpoints:
        print(f"📡 Đang kết nối Server: {url.split('//')[1].split('/')[0]}...")
        try:
            response = requests.get(url, params={'data': overpass_query}, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Kết nối thành công! Đang tải bản đồ...")
                break # Thành công thì thoát vòng lặp
        except Exception:
            print("⏳ Server bận, đang chuyển hướng...")
            time.sleep(1)

    # Nếu cả 3 server đều lỗi -> Dùng dữ liệu offline
    if not data or 'elements' not in data:
        print("❌ Toàn bộ server vệ tinh đang quá tải.")
        generate_fallback_data()
        return

    # Quá trình khâu đồ thị
    raw_nodes = {el['id']: (el['lat'], el['lon']) for el in data['elements'] if el['type'] == 'node'}
    final_nodes = {}
    edges_set = set()
    
    for el in data['elements']:
        if el['type'] == 'way' and len(el['nodes']) >= 2:
            n1_id, n2_id = el['nodes'][0], el['nodes'][-1]
            if n1_id in raw_nodes and n2_id in raw_nodes:
                name1, name2 = f"Node_{n1_id}", f"Node_{n2_id}"
                final_nodes[name1] = raw_nodes[n1_id]
                final_nodes[name2] = raw_nodes[n2_id]
                edges_set.add(tuple(sorted([name1, name2])))

    print("🔗 Đang phân tích và khâu đồ thị (Graph Stitching)...")
    node_names = list(final_nodes.keys())
    for n1 in node_names:
        coord1 = final_nodes[n1]
        distances = sorted([(haversine(coord1, final_nodes[n2]), n2) for n2 in node_names if n1 != n2])
        for i in range(min(2, len(distances))):
            edges_set.add(tuple(sorted([n1, distances[i][1]])))

    if not os.path.exists('data'): os.makedirs('data')
    pd.DataFrame([{'name': k, 'lat': v[0], 'lon': v[1], 'blocked': False} for k, v in final_nodes.items()]).to_csv('data/nodes.csv', index=False)
    pd.DataFrame([{'node1': e[0], 'node2': e[1], 'blocked': False} for e in edges_set]).to_csv('data/edges.csv', index=False)
    
    print(f"🎉 Hoàn tất! Đã thu thập {len(final_nodes)} nút và khâu thành {len(edges_set)} đoạn đường.")

if __name__ == "__main__":
    crawl_kuala_lumpur_roads()