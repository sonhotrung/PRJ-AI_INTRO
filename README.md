🚀 Hướng dẫn Cài đặt & Chạy dự án
1. Yêu cầu hệ thống
Đảm bảo máy tính của bạn đã cài đặt Python 3.8 trở lên.

2. Cài đặt thư viện
Mở Terminal/Command Prompt tại thư mục dự án và chạy lệnh sau để cài đặt các thư viện cần thiết:

Bash
pip install streamlit pandas folium streamlit-folium requests

3. Khởi tạo Dữ liệu Đồ thị
Trước khi chạy ứng dụng lần đầu tiên, bạn cần tạo lưới dữ liệu 100 đường bằng cách chạy lệnh:

Bash
python generate_exact_map.py
(Hệ thống sẽ báo thành công và tự động tạo file trong thư mục data/)

4. Khởi chạy Ứng dụng
Chạy lệnh sau để mở giao diện Web:

Bash
streamlit run main.py

🎮 Hướng dẫn Sử dụng
1. Vai trò Hành khách (Tìm đường)

Ở thanh điều hướng (Sidebar), chọn vai trò Hành khách (User).

Click vào một chấm đen bất kỳ trên bản đồ để làm Điểm xuất phát (Hóa Xanh lá).

Click vào một chấm đen thứ hai để làm Điểm đến (Hóa Vàng).

Hệ thống AI sẽ tự động tính toán, né các điểm bị kẹt và vẽ dải đường di chuyển màu xanh dương.

Lưu ý: Click vào điểm thứ 3 sẽ tự động bắt đầu lại chu trình mới.

2. Vai trò Điều độ viên (Mô phỏng kẹt xe)

Ở thanh điều hướng, chọn vai trò Điều độ viên (Admin).

Click vào bất kỳ Tuyến đường (Cạnh) hoặc Giao lộ (Nút) nào để chuyển trạng thái thành Bị Phong Tỏa (Màu Đỏ).

AI sẽ tự động nhận diện các "vùng cấm" này và tìm đường vòng khi người dùng yêu cầu lộ trình.

Bấm "LƯU VĨNH VIỄN" nếu muốn ghi đè cấu hình kẹt xe này vào file gốc.
