# Hướng dẫn gán nhãn YOLO Dataset (YOLO Labeling Guideline)

Tài liệu này quy định các nguyên tắc gán nhãn cho `part_a` và `part_b` nhằm đảm bảo tính nhất quán và chất lượng dữ liệu huấn luyện.


## 1. Quy định vẽ Bounding Box (Bbox) ôm sát vật thể
- **Yêu cầu:** Viền của bounding box phải **khít tuyệt đối** vào các pixel ngoài cùng của vật thể (`part_a`, `part_b`).
- **Chi tiết:**
  - Không để thừa khoảng trống (background) quá 1-2 pixel xung quanh vật thể.
  - Không vẽ thiếu hoặc cắt lẹm vào phần thân của vật thể.
  - Đảm bảo bbox bao bọc chính xác giới hạn thực tế của từng bộ phận.

## 2. Xử lý vật thể bị che khuất (Occlusion)
Khi `part_a` hoặc `part_b` bị robot hoặc các vật thể khác che khuất một phần:
- **Trường hợp che khuất nhẹ (< 50%):** Vẫn phải vẽ bounding box **ước lượng cho toàn bộ vật thể** (bao gồm cả phần bị che khuất phía sau). Việc này giúp mô hình học được hình dạng đầy đủ của vật thể.
- **Trường hợp che khuất nặng (> 50% hoặc không đoán được hình dạng):** Chỉ vẽ bounding box bao quanh **phần nhìn thấy được** (hoặc bỏ qua hoàn toàn nếu không thể nhận diện được đó là vật thể gì).

## 3. Xử lý frame bị mờ/nhòe (Motion Blur)
Đối với các frame bị mờ do chuyển động (motion blur) sinh ra từ Isaac Sim:
- **Giữ lại:** Nếu frame bị mờ nhưng mắt thường vẫn có thể nhận diện và phân định rõ ràng ranh giới (biên) của `part_a` và `part_b` -> Tiến hành gán nhãn bình thường.
- **Loại bỏ:** Nếu frame bị nhòe quá nặng, không thể xác định rõ biên giới hoặc điểm bắt đầu/kết thúc của `part_a`/`part_b` -> **Loại bỏ frame đó** (không gán nhãn).
