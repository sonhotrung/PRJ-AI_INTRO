import pandas as pd
import math
import os

# 1. CHUẨN BỊ ĐÚNG 30 ĐIỂM (NODES) THỰC TẾ TẠI KL
nodes_data = [
    ['KL Sentral', 3.1344, 101.6865], ['KLCC', 3.1590, 101.7135], ['Bukit Bintang', 3.1462, 101.7113],
    ['Pasar Seni', 3.1427, 101.6955], ['Masjid Jamek', 3.1497, 101.6963], ['Ampang Park', 3.1598, 101.7180],
    ['Merdeka', 3.1423, 101.7018], ['Chinatown', 3.1439, 101.6975], ['Muzium Negara', 3.1375, 101.6874],
    ['Pudu', 3.1362, 101.7130], ['KL Tower', 3.1528, 101.7038], ['Titiwangsa', 3.1768, 101.7042],
    ['Sunway Putra', 3.1650, 101.6938], ['Brickfields', 3.1305, 101.6850], ['Bangsar', 3.1293, 101.6743],
    ['Mid Valley', 3.1185, 101.6766], ['Damansara', 3.1466, 101.6619], ['Mont Kiara', 3.1666, 101.6528],
    ['Batu Caves', 3.2379, 101.6813], ['The Intermark', 3.1615, 101.7195], ['Pavilion', 3.1488, 101.7135],
    ['Perdana Botanical', 3.1428, 101.6830], ['Istana Negara', 3.1342, 101.6616], ['Bangsar South', 3.1116, 101.6644],
    ['Minden', 3.1550, 101.6500], ['Solaris', 3.1720, 101.6590], ['Publika', 3.1712, 101.6660],
    ['Titiwangsa Lake', 3.1768, 101.7042], ['Royal Selangor Golf', 3.1450, 101.7230], ['Bukit Damansara', 3.1485, 101.6560]
]

def haversine(coord1, coord2):
    """Tính khoảng cách địa lý giữa 2 điểm (km)"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_exact_map():
    print("⚙️ Đang thiết kế Đồ thị: Đúng 30 Nút và 100 Đường...")
    
    edges_set = set()

    # BƯỚC 1: Đảm bảo tính liên thông (Mỗi điểm phải nối với ít nhất 2 điểm gần nhất)
    for i in range(len(nodes_data)):
        distances = []
        for j in range(len(nodes_data)):
            if i != j:
                dist = haversine((nodes_data[i][1], nodes_data[i][2]), (nodes_data[j][1], nodes_data[j][2]))
                distances.append((dist, nodes_data[j][0]))
        
        distances.sort()
        # Lấy 2 điểm gần nhất
        for k in range(2):
            edge = tuple(sorted([nodes_data[i][0], distances[k][1]]))
            edges_set.add(edge)

    # Tính toán toàn bộ các cạnh khả thi còn lại
    all_possible_edges = []
    for i in range(len(nodes_data)):
        for j in range(i + 1, len(nodes_data)):
            dist = haversine((nodes_data[i][1], nodes_data[i][2]), (nodes_data[j][1], nodes_data[j][2]))
            edge = tuple(sorted([nodes_data[i][0], nodes_data[j][0]]))
            if edge not in edges_set:
                all_possible_edges.append((dist, edge))
                
    # Sắp xếp các cạnh còn lại theo khoảng cách tăng dần (Ưu tiên nối các điểm gần nhau trước)
    all_possible_edges.sort(key=lambda x: x[0])

    # BƯỚC 2: Bơm thêm đường cho đến khi đạt CHÍNH XÁC 100 đường
    target_edges = 100
    for dist, edge in all_possible_edges:
        if len(edges_set) >= target_edges:
            break
        edges_set.add(edge)

    # LƯU FILE
    if not os.path.exists('data'): 
        os.makedirs('data')
        
    # Lưu Nodes
    pd.DataFrame([{'name': n[0], 'lat': n[1], 'lon': n[2], 'blocked': False} for n in nodes_data]).to_csv('data/nodes.csv', index=False)
    
    # Lưu Edges
    edges_list = [{'node1': e[0], 'node2': e[1], 'blocked': False} for e in edges_set]
    edges_df = pd.DataFrame(edges_list)
    edges_df.index.name = 'ID'
    edges_df.to_csv('data/edges.csv')
    
    print(f"✅ Hoàn tất! Đã tạo file với chính xác {len(nodes_data)} Điểm và {len(edges_df)} Đường đi.")
    print("👉 Bây giờ bạn có thể chạy: streamlit run main.py")

if __name__ == "__main__":
    generate_exact_map()