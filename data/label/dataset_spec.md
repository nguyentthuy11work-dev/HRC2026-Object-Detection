# Đặc tả Dữ liệu YOLO Dataset (Dataset Specification)

Tài liệu này cung cấp thông tin chi tiết về số lượng dữ liệu và phân bổ các tập Train/Val/Test của bộ dữ liệu `yolo_dataset_v1`.

---

## 1. Tổng số lượng dữ liệu
- **Tổng số lượng frame (ảnh):** 583 ảnh.
- **Tổng số lượng nhãn (bounding boxes):** 1,908 boxes.

## 2. Phân bổ các tập dữ liệu (Train / Val / Test)
Bộ dữ liệu được chia theo tỷ lệ xấp xỉ **80% Train / 10% Val / 10% Test**:

| Tập dữ liệu (Split) | Số lượng Frame | Tỷ lệ (%) |
| :--- | :--- | :--- |
| **Train** | 466 | ~80.0% |
| **Val** | 58 | ~10.0% |
| **Test** | 59 | ~10.0% |
| **Tổng cộng** | **583** | **100%** |

## 3. Thống kê chi tiết nhãn từng Class
Chi tiết số lượng bounding box của từng class (`part_a` và `part_b`) trên mỗi tập dữ liệu:

### Tổng quan toàn bộ Dataset
- **Class `part_a`:** 962 boxes
- **Class `part_b`:** 946 boxes
- **Tổng số box:** 1,908 boxes

### Chi tiết theo từng tập (Split)

#### Tập Huấn luyện (Train)
- **Tổng số frame:** 466
- **Class `part_a`:** 774 boxes
- **Class `part_b`:** 757 boxes

#### Tập Kiểm thử (Val)
- **Tổng số frame:** 58
- **Class `part_a`:** 94 boxes
- **Class `part_b`:** 92 boxes

#### Tập Thử nghiệm (Test)
- **Tổng số frame:** 59
- **Class `part_a`:** 94 boxes
- **Class `part_b`:** 97 boxes
