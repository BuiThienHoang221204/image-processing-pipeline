# Image Processing Pipeline (Assignment FIT IUH)

Dự án xây dựng hệ thống xử lý hình ảnh dựa trên kiến trúc **Pipeline Architecture Style**, triển khai qua cơ chế `Generator` và nạp chồng toán tử `|` trong Python.

---

## 📁 Cấu trúc dự án

```text
image-processing-pipeline/
│
├── assignment_pipeline.py       # Bộ điều phối chính (Main / Orchestrator)
│
└── pipeline/                    # Chứa toàn bộ các khối xử lý (Pipeline Stages)
    ├── __init__.py
    ├── pipeline.py              # Khung Pipeline cơ sở
    ├── capture_images.py        # Stage 1: Input / Capture
    ├── resize.py                # Stage 2: Resize
    ├── filter.py                # Stage 3: Color Filter
    ├── watermark.py             # Stage 4: Watermark
    ├── compression.py           # Stage 5: Compression
    └── save_image.py            # Stage 6: Output / Save
```

---

## 📋 Chức năng chính
Theo yêu cầu đồ án, pipeline bao gồm các giai đoạn xử lý riêng biệt:
- **Ngõ vào (Input / Capture)**: Đọc hàng loạt tệp ảnh từ thư mục.
- **Biến đổi kích thước (Resize)**: Thay đổi kích thước Width x Height.
- **Màu sắc (Filter)**: Lọc màu (Grayscale, Sepia).
- **Đóng dấu (Watermark)**: Đóng dấu bản quyền chữ lên ảnh.
- **Nén & Đầu ra (Compress & Save)**: Giảm tỷ lệ nén dung lượng (JPEG) và lưu xuất file kết quả.

## � Hướng dẫn cài đặt
Sử dụng môi trường ảo (`venv`) trên Python 3.10+:

```bash
# 1. Tạo môi trường ảo
python -m venv venv

# 2. Kích hoạt môi trường
# Trên Git Bash / Mac / Linux:
source venv/Scripts/activate

# Trên Windows CMD:
# venv\Scripts\activate.bat

# 3. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

## 🎯 Cách chạy ứng dụng
Sử dụng file thực thi chính `assignment_pipeline.py`. Bạn có thể thay đổi các tham số (argparse) tự do thông qua command line.

**Lệnh chạy ví dụ (Windows CMD/Bash):**
```bash
python assignment_pipeline.py -i "assets/images" -o "output" --width 1024 --height 768 --filter "sepia" --watermark "FIT IUH - Group Pro" --quality 50
```

### Các Tham số (Arguments):
- `-i`, `--input`: (Bắt buộc) Thư mục chứa ảnh đầu vào.
- `-o`, `--output`: Thư mục lưu ảnh đầu ra (Mặc định: `output`).
- `--width`, `--height`: Giải phân giải khi thay đổi kích thước (Mặc định: `800x600`).
- `--filter`: Loại bộ lọc màu áp dụng: `sepia`, `gray`, `none` (Mặc định: `sepia`).
- `--watermark`: Thông điệp bản quyền (Mặc định: `FIT IUH - Group X`).
- `--quality`: Tỷ lệ chất lượng nén ảnh, 0-100 (Mặc định: `60`%).

---

*Hệ thống được phát triển với định hướng linh hoạt, nếu cần đổi Stage các quy trình (Pipeline), bạn có thể chỉnh sửa nối toán tử `|` trực tiếp tại hàm main của file `assignment_pipeline.py`.*
