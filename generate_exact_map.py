import pandas as pd
import math
import os

# 1. CHUẨN BỊ ĐÚNG 50 ĐIỂM (NODES) THỰC TẾ TẠI KL
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
    ['Titiwangsa Lake', 3.1768, 101.7042], ['Royal Selangor Golf', 3.1450, 101.7230], ['Bukit Damansara', 3.1485, 101.6560],
    ['Saloma Link', 3.1615, 101.7082], ['Central Market', 3.1454, 101.6953], ['National Mosque', 3.1418, 101.6918],
    ['Aquaria KLCC', 3.1539, 101.7130], ['Dataran Merdeka', 3.1486, 101.6936], ['KL Bird Park', 3.1428, 101.6881],
    ['Thean Hou Temple', 3.1219, 101.6874], ['Berjaya Times Square', 3.1424, 101.7095], ['Kepong Park', 3.2205, 101.6441],
    ['Cheras Leisure Mall', 3.0851, 101.7410], ['EkoCheras', 3.0906, 101.7370], ['Desa ParkCity', 3.1873, 101.6316],
    ['One Utama', 3.1481, 101.6158], ['The Curve', 3.1578, 101.6115], ['IKEA Damansara', 3.1565, 101.6111],
    ['Taman Connaught', 3.0827, 101.7346], ['Bukit Jalil Stadium', 3.0556, 101.6917], ['Taman Desa', 3.1040, 101.6811],
    ['MyTown', 3.1345, 101.7247], ['TRX', 3.1419, 101.7196]
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
    print(f"Diem danh {len(nodes_data)} diem...")
    
    edges_set = set()

    # Thuật toán Nearest Neighbor để tạo ra chuỗi đường đơn giản
    # Đảm bảo mỗi điểm chỉ kết nối với 1 hoặc 2 điểm khác (bậc 1 hoặc 2)
    unvisited = list(range(len(nodes_data)))
    
    current = unvisited.pop(0) # Bắt đầu từ điểm 0
    
    while unvisited:
        # Tìm điểm gần nhất trong số các điểm chưa thăm
        nearest = min(unvisited, key=lambda j: haversine((nodes_data[current][1], nodes_data[current][2]), 
                                                         (nodes_data[j][1], nodes_data[j][2])))
        
        # Tạo kết nối
        edge = tuple(sorted([nodes_data[current][0], nodes_data[nearest][0]]))
        edges_set.add(edge)
        
        # Di chuyển sang điểm đó
        current = nearest
        unvisited.remove(nearest)
        
    # Tạo thêm 3 đường nối chéo ngẫu nhiên giữa các khu vực để tránh đồ thị là một đường thẳng duy nhất (giúp AI có ngã rẽ)
    import random
    random.seed(42)
    for _ in range(3):
        i, j = random.sample(range(len(nodes_data)), 2)
        edge = tuple(sorted([nodes_data[i][0], nodes_data[j][0]]))
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
    
    print(f"Hoan tat! Da tao file voi chinh xac {len(nodes_data)} Diem va {len(edges_df)} Duong di.")
    print("Bay gio ban co the chay: streamlit run main.py")

if __name__ == "__main__":
    generate_exact_map()