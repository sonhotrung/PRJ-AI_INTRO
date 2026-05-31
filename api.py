import requests
import json
import os
import time

CACHE_FILE = 'data/route_cache.json'

def load_cache():
    """Tải bộ nhớ đệm, tự động phục hồi nếu file bị hỏng"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    """Lưu trữ xuống ổ cứng"""
    if not os.path.exists('data'):
        os.makedirs('data')
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_real_road_curve(start_coord, end_coord, u_name, v_name):
    """Gọi OSRM API kèm cơ chế chống nghẽn (Rate Limit) và định danh Header"""
    cache = load_cache()
    route_key = f"{u_name}-{v_name}"
    route_key_rev = f"{v_name}-{u_name}"
    
    # Nếu đã có trong Cache (dù là đường cong hay đường thẳng dự phòng) -> Lấy ra dùng luôn
    if route_key in cache: 
        return cache[route_key]
    if route_key_rev in cache: 
        return list(reversed(cache[route_key_rev]))

    lat1, lon1 = start_coord
    lat2, lon2 = end_coord
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    
    # 1. BỔ SUNG HEADER: Bắt buộc phải có để OSRM không chặn
    headers = {
        'User-Agent': 'HUST_AI_Project_IT3160_Student/1.0'
    }
    
    fallback_path = [start_coord, end_coord]

    try:
        # 2. PACING: Ngủ 0.1 giây giữa mỗi nhịp gọi để tránh bị server đánh dấu là Spam
        time.sleep(0.1)
        
        # Giảm timeout xuống 3s để nếu mạng nghẽn thì thoát ra nhanh chóng, không làm đơ App
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok":
                coordinates = data["routes"][0]["geometry"]["coordinates"]
                real_path = [[lat, lon] for lon, lat in coordinates]
                
                cache[route_key] = real_path
                save_cache(cache)
                return real_path
        else:
            print(f"⚠️ OSRM Server bận (Mã lỗi: {response.status_code}) tại tuyến {u_name}-{v_name}")
            
    except Exception as e:
        print(f"⏳ Quá thời gian chờ API tại tuyến {u_name}-{v_name} (Chuyển sang đường dự phòng)")
        
    # 3. CACHING LỖI: Nếu API sập, lưu luôn đường thẳng dự phòng vào Cache.
    # Nhờ vậy, lần tải lại (rerun) tiếp theo sẽ KHÔNG mất công đợi 3s cho đoạn đường này nữa.
    cache[route_key] = fallback_path
    save_cache(cache)
    return fallback_path