import argparse
import glob
import os
import sys

# Import các giai đoạn (stages) của ứng dụng nhóm
from pipeline.capture_images import CaptureImages
from pipeline.resize import Resize
from pipeline.filter import ImageFilter
from pipeline.watermark import Watermark
from pipeline.compress_and_save import CompressAndSave

def main():
    parser = argparse.ArgumentParser(description="Image Processing Pipeline - FIT IUH")
    parser.add_argument("-i", "--input", type=str, required=True, help="Đường dẫn thư mục chứa ảnh đầu vào")
    parser.add_argument("-o", "--output", type=str, default="output", help="Đường dẫn lưu ảnh đầu ra")
    parser.add_argument("--width", type=int, default=800, help="Chiều rộng ảnh sau khi Resize")
    parser.add_argument("--height", type=int, default=600, help="Chiều cao ảnh sau khi Resize")
    parser.add_argument("--filter", type=str, choices=["gray", "sepia", "none"], default="sepia", help="Bộ lọc được áp dụng")
    parser.add_argument("--watermark", type=str, default="FIT IUH - Group X", help="Dấu bản quyền (Text)")
    parser.add_argument("--quality", type=int, default=60, help="Chất lượng ảnh sau khi nén (0-100)")
    
    args = parser.parse_args()

    # Thu thập file
    search_pattern = os.path.join(args.input, "**", "*.jpg")
    files = glob.glob(search_pattern, recursive=True)
    if not files:
        print(f"Không tìm thấy ảnh tại: {args.input}")
        sys.exit(1)

    print("Cấu hình Pipeline Động:")
    print(f" -> Input: {len(files)} ảnh từ thư mục {args.input}")
    print(f" -> Resize: {args.width}x{args.height}")
    if args.filter != "none":
        print(f" -> Lọc màu: {args.filter}")
    if args.watermark:
        print(f" -> Đóng bản quyền: '{args.watermark}'")
    print(f" -> Nén ảnh và Lưu: {args.output} (Chất lượng Nén: {args.quality}%)")
    print("-" * 40)

    # 1. Giai đoạn đầu vào (nhận đường dẫn thư mục)
    pipeline_flow = CaptureImages(args.input)
    
    # 2. Giai đoạn thay đổi kích thước
    pipeline_flow = pipeline_flow | Resize(width=args.width, height=args.height)
    
    # 3. Giai đoạn Lọc
    if args.filter != "none":
        pipeline_flow = pipeline_flow | ImageFilter(filter_type=args.filter)
        
    # 4. Giai đoạn đóng dấu bản quyền
    if args.watermark:
        pipeline_flow = pipeline_flow | Watermark(text=args.watermark)
        
    # 5 & 6. Giai đoạn Nén và Xuất
    pipeline_flow = pipeline_flow | CompressAndSave(output_dir=args.output, quality=args.quality)

    # Chạy pipeline ngầm định theo cơ chế Generator
    count = 0
    for result in pipeline_flow:
        out_path = result.get("output_path", "Unknown")
        print(f"Thành công: Đã xử lý và lưu tại {out_path}")
        count += 1
        
    print("-" * 40)
    print(f"Pipeline hoàn thành! Tổng số file xử lý: {count}")

if __name__ == "__main__":
    main()