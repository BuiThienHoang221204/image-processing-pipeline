# Kế Hoạch Triển Khai Kiến Trúc Pipeline Xử Lý Ảnh (Assignment FIT IUH)

## 1. Phân tích vấn đề hiện tại
- **Về mặt kiến trúc (Đạt 100%):** Source code hiện tại đã triển khai rất xuất sắc mẫu kiến trúc (Architectural Pattern) **Pipeline** bằng cách sử dụng Generator (`yield`) và nạp chồng toán tử `|` (trong file `pipeline/pipeline.py`). Dòng dữ liệu được luân chuyển mượt mà qua từng giai đoạn độc lập.
- **Về mặt nghiệp vụ (Chỉ đạt 30%):** Bài tập yêu cầu một luồng biến đổi ảnh cụ thể: **Input -> Resize -> Filter -> Watermark -> Nén -> Output**. Tuy nhiên, source hiện tại lại đang xử lý kịch bản: **Input -> Nhận diện khuôn mặt (Detect Faces) -> Cắt khuôn mặt (Crop) -> Output**. 
- **Vấn đề cốt lõi:** Chúng ta đang có phần "khung xương" (Architecture) hoàn hảo nhưng phần "thịt" (Business Logic/Stages) chưa khớp với yêu cầu đề bài.

## 2. Giải thích đúng yêu cầu
Theo đề bài, để đạt full điểm môn học, ứng dụng cần thỏa mãn luồng dữ liệu chuẩn sau:
1. **Giai đoạn đầu vào (Input):** Nhận ảnh, kiểm tra hợp lệ.
2. **Giai đoạn thay đổi kích thước (Resize):** Scale ảnh theo kích thước người dùng nhập (VD: 800x600).
3. **Giai đoạn lọc (Filter):** Áp dụng một hoặc nhiều bộ lọc màu (Grayscale, Sepia,...).
4. **Giai đoạn đóng dấu bản quyền (Watermark):** Chèn Text hoặc Logo lên góc ảnh để đánh dấu bản quyền.
5. **Giai đoạn nén (Compress):** Giảm dung lượng tệp (chất lượng JPEG, PNG) nhưng không làm mờ quá mức.
6. **Giai đoạn đầu ra (Output):** Lưu hình ảnh đã xử lý thành tệp vật lý.

*Các giai đoạn trên phải là các class độc lập, nhận dữ liệu ảnh từ giai đoạn trước, biến đổi và truyền (yield) sang giai đoạn sau.*

## 3. Phương án giải quyết
- **Giữ nguyên nền tảng kiến trúc (Base Architecture):** Giữ lại file `pipeline/pipeline.py` (Base class) và triết lý sử dụng `toán tử |`. Điều này vừa giúp tiết kiệm thời gian, vừa là minh chứng cực tốt cho tính "Tái sử dụng" và "Mở rộng" của môn Kiến trúc.
- **Tạo các Stage (Giai đoạn) mới:** Kế thừa class `Pipeline` để tạo ra 4 giai đoạn xử lý mới là `Resize`, `Filter`, `Watermark`, và `Compress`.
- **Ráp nối (Integration):** Trong file chạy chính (`process_images_pipeline.py`), cung cấp các tham số (argparse) để người dùng có thể cấu hình pipeline động (Ví dụ: Chỉ Resize và Filter, bỏ qua Watermark).

## 4. Đề xuất ưu tiên
1. **Ưu tiên 1 (Cốt lõi):** Lập trình ngay 4 class tượng trưng cho 4 giai đoạn mới (`Resize`, `Filter`, `Watermark`, `Compress`). Đây là phần ăn điểm để nộp bài.
2. **Ưu tiên 2 (Tích hợp):** Tạo một file thực thi mới (ví dụ: `assignment_pipeline.py`) hoặc thay đổi file `process_images_pipeline.py` để móc nối các module mới này bằng toán tử `|`.
3. **Ưu tiên 3 (Testing & Refine):** Chạy thử nghiệm trên các ảnh trong thư mục `assets/images/`, kiểm tra kết quả đầu ra có đúng hiệu ứng hay không và hoàn thiện báo cáo.

## 5. Các file cần thay đổi và tạo mới
- Mở thư mục `pipeline/` và **tạo mới 4 file**:
  - `resize.py`: Chứa class `Resize` (Dùng `cv2.resize`).
  - `filter.py`: Chứa class `ImageFilter` (Dùng `cv2.cvtColor` dể dùng thang độ xám (Grayscale)/Sepia).
  - `watermark.py`: Chứa class `Watermark` (Dùng `cv2.putText` để ghi Text bản quyền).
  - `compress.py`: Chứa class `Compress` (Dùng thông số nén của `cv2.imencode` hoặc setup output quality).
- **Cập nhật:**
  - `pipeline/__init__.py`: Import các class mới này để dễ dàng gọi.
  - `process_images_pipeline.py`: Viết lại hàm `main()` để cấu hình parser CLI nhận tham số như `--width`, `--height`, `--filter`, `--watermark_text` và kết nối pipeline chuẩn theo bài tập.

## 6. Cách triển khai cụ thể

Dưới đây là pseudo-code / phương hướng cho từng block cụ thể:

**Bước 1: Viết giai đoạn Resize (`pipeline/resize.py`)**
- Kế thừa `Pipeline`.
- Trong hàm `map(self, data)`, trích xuất ma trận ảnh (`image`).
- Dùng `cv2.resize(image, (width, height))`.
- Trả về (yield) ảnh đã resize.

**Bước 2: Viết giai đoạn Filter (`pipeline/filter.py`)**
- Nhận biến `filter_type` (VD: 'gray', 'sepia').
- Nếu type là 'gray', dùng `cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`. Trả dữ liệu ảnh đi tiếp.

**Bước 3: Viết giai đoạn Watermark (`pipeline/watermark.py`)**
- Dùng `cv2.putText` trên ảnh nhận được. Chèn text vào tọa độ góc dưới bên phải.

**Bước 4: Viết giai đoạn Nén & Lưu (Kết hợp `compress.py` & `save_image.py`)**
- OpenCV cung cấp tham số nén khi lưu ảnh `cv2.imwrite("output.jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 60])`. 
- Cấu hình file `save_image.py` hoặc tạo class `CompressAndSave` để đáp ứng cả yêu cầu 5 (Nén) và 6 (Đầu ra).

**Bước 5: Chuỗi thao tác Main (Tạo Quy Trình Động)**
```python
# Cấu trúc Pipeline theo bài tập
pipeline = (
    CaptureImages(file_paths) | 
    Resize(width=800, height=600) |
    ImageFilter(type="gray") |
    Watermark(text="FIT IUH - Group X") |
    CompressAndSave(output_dir="output/", quality=60)
)

# Chạy dòng chảy dữ liệu
for result in pipeline:
    print(f"Hoàn thành xử lý thao tác cho: {result['file_name']}")
```

---
*Báo cáo này được thiết kế để bạn có thể sao chép trực tiếp vào file Word/PowerPoint báo cáo đồ án của nhóm.*
