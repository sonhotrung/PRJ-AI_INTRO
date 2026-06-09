import heapq
import math
from collections import deque

def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

class SearchNode:
    __slots__ = ['state', 'parent', 'g', 'h', 'f']
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g, self.h = g, h
        self.f = g + h
    def __lt__(self, other): return self.f < other.f

# LƯU Ý: Đã thêm tham số blocked_nodes
def search_algorithm(start_node, goal_node, nodes_data, edges_data, blocked_nodes, strategy='A*'):
    fringe = [] 
    if strategy == 'BFS':
        fringe = deque([SearchNode(start_node, None, 0, 0)])
    elif strategy == 'DFS':
        fringe = [SearchNode(start_node, None, 0, 0)]
    else:
        h_start = haversine_distance(nodes_data[start_node], nodes_data[goal_node]) if strategy == 'A*' else 0
        heapq.heappush(fringe, SearchNode(start_node, None, 0, h_start))

    closed = set()
    explored_count = 0

    while fringe:
        if strategy == 'BFS': 
            current_node = fringe.popleft()
        elif strategy == 'DFS': 
            current_node = fringe.pop()
        else: 
            current_node = heapq.heappop(fringe)
        
        if current_node.state == goal_node:
            path, cost = [], current_node.g
            while current_node:
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1], cost, explored_count

        if current_node.state not in closed:
            closed.add(current_node.state)
            explored_count += 1
            
            for neighbor, is_blocked in edges_data.get(current_node.state, []):
                # RÀNG BUỘC: Né cạnh bị chặn, nút đã duyệt, và NÚT BỊ ADMIN CHẶN
                if is_blocked or neighbor in closed or neighbor in blocked_nodes: 
                    continue
                
                dist = haversine_distance(nodes_data[current_node.state], nodes_data[neighbor])
                g_n = current_node.g + (1 if strategy == 'BFS' else dist)
                h_n = haversine_distance(nodes_data[neighbor], nodes_data[goal_node]) if strategy == 'A*' else 0
                
                new_node = SearchNode(neighbor, current_node, g_n, h_n)
        
                if strategy == 'BFS': fringe.append(new_node)
                elif strategy == 'DFS': fringe.append(new_node)
                else: heapq.heappush(fringe, new_node)
                
    return None, 0, explored_count