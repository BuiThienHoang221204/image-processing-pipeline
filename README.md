# Image Processing Pipeline — Hướng Dẫn Dự Án# Image processing pipeline



**Modular image processing pipeline using OpenCV and Python generators**Modular image processing pipeline using OpenCV and Python generators.  



Dự án này cung cấp một hệ thống xử lý hình ảnh và video dạng module, linh hoạt, được xây dựng trên ngôn ngữ Python và thư viện OpenCV. Hệ thống sử dụng cơ chế **Python generators** để tạo ra các luồng dữ liệu (pipeline) hiệu quả về bộ nhớ.## Setup environment



---This project is using [Conda](https://conda.io) for project environment management.



## 📋 Dự án này làm gì?Setup the project environment:



Dự án cung cấp một khung (framework) để xây dựng các quy trình xử lý hình ảnh và video bằng cách kết nối các bước xử lý riêng lẻ lại với nhau (giống như cách hoạt động của lệnh `|` trong Unix).    $ conda env create -f environment.yml

    $ conda activate pipeline

**Các tính năng chính đã được triển khai:**    

- **Thu thập dữ liệu (Capture):** Đọc hình ảnh từ thư mục hoặc video từ file/camera.or update the environment if you `git pull` the repo:

- **Phát hiện khuôn mặt (Face Detection):** Sử dụng mô hình Deep Learning (Caffe) để nhận diện khuôn mặt trong khung hình.

- **Xử lý & Cắt (Processing & Cropping):** Tự động cắt và lưu lại vùng chứa khuôn mặt.    $ conda env update -f environment.yml

- **Chú thích (Annotation):** Vẽ các khung (bounding box) và ghi chú lên hình ảnh/video.

- **Báo cáo (Summary):** Xuất dữ liệu tóm tắt kết quả xử lý ra file JSON (số lượng ảnh, số khuôn mặt phát hiện được, v.v.).## Getting started



## 🎯 Tác dụng và ứng dụngFor detailed description read the Medium stories in order:

* [Modular image processing pipeline using OpenCV and Python generators](https://medium.com/deepvisionguru/modular-image-processing-pipeline-using-opencv-and-python-generators-9edca3ccb696)

### Tác dụng:* [Video processing pipeline with OpenCV](https://medium.com/deepvisionguru/video-processing-pipeline-with-opencv-ac10187d75b)

- **Tính Module hóa:** Giúp tách biệt logic của từng bước xử lý (đọc, lọc, nhận diện, lưu). Bạn có thể dễ dàng thêm hoặc bớt một bước xử lý mà không làm ảnh hưởng đến toàn bộ hệ thống.

- **Tiết kiệm tài nguyên:** Sử dụng generator giúp xử lý từng khung hình một (lazy evaluation), cực kỳ hữu ích khi làm việc với video dài hoặc tập dữ liệu hình ảnh khổng lồ mà không gây tràn bộ nhớ RAM.Don't forget to clap a bit if you like it. If you like it very much, you can clap a few times :)  

Thank you!

### Ứng dụng:

- **Hệ thống giám sát:** Tự động phát hiện và trích xuất khuôn mặt từ camera an ninh.## Tests

- **Tiền xử lý dữ liệu AI:** Chuẩn bị tập dữ liệu (dataset) khuôn mặt để huấn luyện các mô hình nhận diện khuôn mặt.

- **Xử lý video hàng loạt:** Áp dụng các bộ lọc hoặc thuật toán phân tích lên một lượng lớn video một cách tự động.`pytest` is used as a test framework. All tests are stored in `tests` folder. Run the tests:



## 🛠 Công nghệ sử dụng```bash

$ pytest

- **Ngôn ngữ:** Python (phiên bản 3.6+)```

- **Thư viện chính:**

    - **OpenCV (opencv-contrib-python):** Thư viện cốt lõi cho xử lý ảnh và video.## Resources and Credits

    - **NumPy:** Xử lý các ma trận điểm ảnh (pixel arrays).

    - **Caffe:** Chạy mô hình Deep Learning để phát hiện khuôn mặt.* For Unix like pipeline idea credits goes to this [Gist](https://gist.github.com/alexmacedo/1552724)

    - **tqdm:** Hiển thị thanh tiến trình khi xử lý.* Source of the example images and videos is [pixbay](https://pixabay.com)

    - **Pytest:** Dùng để chạy unit test đảm bảo tính ổn định.* Some ideas and code snippets are borrowed from [pyimagesearch](https://www.pyimagesearch.com/)

* Color constants from [Python Color Constants Module](https://www.webucator.com/blog/2015/03/python-color-constants-module/)

---

## License

## 🚀 Cách chạy Source Code

[MIT License](LICENSE)
### Bước 1: Cài đặt môi trường

Bạn có thể chọn một trong ba cách dưới đây:

#### Sử dụng venv với Python 3.10+

Nếu bạn sử dụng Python 3.10 hoặc 3.11:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường (chọn lệnh phù hợp với shell của bạn)

# Git Bash / MINGW64:
source venv/Scripts/activate

# PowerShell:
.\venv\Scripts\Activate.ps1

# Command Prompt (cmd.exe):
venv\Scripts\activate.bat

# Nâng cấp build tools
python -m pip install --upgrade pip setuptools wheel

# Cài đặt dependencies
pip install -r requirements.txt

# Kiểm tra cài đặt
python -c "import cv2; print('cv2 version:', cv2.__version__)"
```

### Bước 2: Chạy xử lý hình ảnh

Để quét các hình ảnh trong một thư mục và phát hiện khuôn mặt:

```bash
python process_images_pipeline.py -i assets/images -o output
```

*Kết quả sẽ được lưu trong thư mục `output`.*

### Bước 3: Chạy xử lý video

Để chạy phát hiện khuôn mặt trực tiếp trên video (sử dụng video có sẵn):

```bash
python process_video_pipeline.py -i assets/videos/faces.mp4
```

### Bước 4: Chạy kiểm thử (Tests)

Để đảm bảo mọi thứ hoạt động đúng:

```bash
pytest
```

---

## 📚 Tham khảo thêm

Để hiểu rõ hơn về pipeline architecture và cách nó hoạt động, bạn có thể đọc các bài viết Medium:
* [Modular image processing pipeline using OpenCV and Python generators](https://medium.com/deepvisionguru/modular-image-processing-pipeline-using-opencv-and-python-generators-9edca3ccb696)
* [Video processing pipeline with OpenCV](https://medium.com/deepvisionguru/video-processing-pipeline-with-opencv-ac10187d75b)

## 🙏 Credits & Resources

* For Unix like pipeline idea credits goes to this [Gist](https://gist.github.com/alexmacedo/1552724)
* Source of the example images and videos is [pixbay](https://pixabay.com)
* Some ideas and code snippets are borrowed from [pyimagesearch](https://www.pyimagesearch.com/)
* Color constants from [Python Color Constants Module](https://www.webucator.com/blog/2015/03/python-color-constants-module/)

## 📜 License

[MIT License](LICENSE)
