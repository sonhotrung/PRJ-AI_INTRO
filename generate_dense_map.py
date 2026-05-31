import pandas as pd
import math
import os

nodes_data = [
    ['KLCC', 3.1577, 101.7119], ['Pavilion', 3.1488, 101.7135], ['Bukit Bintang', 3.1462, 101.7113],
    ['KL Tower', 3.1528, 101.7038], ['Masjid Jamek', 3.1497, 101.6963], ['Merdeka Square', 3.1480, 101.6935],
    ['Chinatown', 3.1439, 101.6975], ['Petaling Street', 3.1445, 101.6978], ['National Museum', 3.1375, 101.6874],
    ['KL Sentral', 3.1344, 101.6865], ['Brickfields', 3.1305, 101.6850], ['Mid Valley', 3.1185, 101.6766],
    ['The Gardens', 3.1190, 101.6750], ['Bangsar South', 3.1116, 101.6644], ['Istana Negara', 3.1342, 101.6616],
    ['Perdana Botanical', 3.1428, 101.6830], ['Bangsar', 3.1293, 101.6743], ['Damansara Heights', 3.1466, 101.6619],
    ['Bukit Damansara', 3.1485, 101.6560], ['Minden', 3.1550, 101.6500], ['Mont Kiara', 3.1666, 101.6528],
    ['Solaris', 3.1720, 101.6590], ['Publika', 3.1712, 101.6660], ['Sunway Putra', 3.1650, 101.6938],
    ['Titiwangsa Lake', 3.1768, 101.7042], ['Pudu', 3.1362, 101.7130], ['Royal Selangor Golf', 3.1450, 101.7230],
    ['Ampang Park', 3.1598, 101.7180], ['The Intermark', 3.1615, 101.7195], ['Batu Caves', 3.2379, 101.6813]
]

edges_set = set()
for i in range(len(nodes_data)):
    distances = []
    for j in range(len(nodes_data)):
        if i != j:
            dist = math.hypot(nodes_data[i][1] - nodes_data[j][1], nodes_data[i][2] - nodes_data[j][2])
            distances.append((dist, j))
    distances.sort()
    for k in range(3): 
        edge = tuple(sorted([i, distances[k][1]]))
        edges_set.add(edge)

final_nodes = {n[0]: (n[1], n[2]) for n in nodes_data}
final_edges = []

for idx, (i, j) in enumerate(edges_set):
    n1, lat1, lon1 = nodes_data[i]
    n2, lat2, lon2 = nodes_data[j]
    
    mid1_lat, mid1_lon = lat1 + (lat2 - lat1)*0.33, lon1 + (lon2 - lon1)*0.33
    mid2_lat, mid2_lon = lat1 + (lat2 - lat1)*0.66, lon1 + (lon2 - lon1)*0.66
    
    mid1_name, mid2_name = f"WP_{n1}-{n2}_1", f"WP_{n1}-{n2}_2"
    final_nodes[mid1_name] = (mid1_lat, mid1_lon)
    final_nodes[mid2_name] = (mid2_lat, mid2_lon)
    
    final_edges.extend([
        {'node1': n1, 'node2': mid1_name, 'blocked': False},
        {'node1': mid1_name, 'node2': mid2_name, 'blocked': False},
        {'node1': mid2_name, 'node2': n2, 'blocked': False}
    ])

if not os.path.exists('data'): os.makedirs('data')

pd.DataFrame([{'name': k, 'lat': v[0], 'lon': v[1], 'blocked': False} for k, v in final_nodes.items()]).to_csv('data/nodes.csv', index=False)
e_df = pd.DataFrame(final_edges)
e_df.index.name = 'ID'
e_df.to_csv('data/edges.csv')
print(f"✅ Đã tạo {len(final_nodes)} trạm và {len(e_df)} đoạn đường.")