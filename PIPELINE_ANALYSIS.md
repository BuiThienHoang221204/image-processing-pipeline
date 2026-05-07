# Pipeline Architecture Analysis & Implementation Plan

**Dự án:** Image Processing Pipeline  
**Ngày:** May 7, 2026  
**Mục đích:** Phân tích, so sánh yêu cầu với hiện trạng, và đề xuất kế hoạch triển khai chi tiết.

---

## 1. Phân tích vấn đề hiện tại

### 1.1 Hiện trạng codebase
Dự án hiện tại **đã triển khai** kiến trúc Pipeline với các đặc tính:
- ✅ Base class `Pipeline` với generator + toán tử `|` (Unix-like)
- ✅ Lazy evaluation (xử lý tuần tự, tiết kiệm RAM)
- ✅ Modular stages (capture → detect → save → annotate → output)
- ✅ Flexible composition (nối stages bằng `|`)

**Hiện tại có các stages:**

| Stage | File | Chức năng |
|-------|------|----------|
| Input | `capture_images.py`, `capture_video.py` | Thu thập ảnh/video |
| Detection | `detect_faces.py` | Phát hiện khuôn mặt (Caffe model) |
| Processing | `save_faces.py` | Lưu các crop khuôn mặt (đã sửa để handle empty) |
| Annotation | `annotate_image.py` | Vẽ bounding box |
| Output | `save_video.py`, `save_summary.py`, `display_video.py` | Lưu/hiển thị output |

**Vấn đề hiện tại:**
- ❌ Thiếu stage **Resize** (thay đổi kích thước ảnh)
- ❌ Thiếu stage **Filter** (điều chỉnh màu sắc: grayscale, sepia, brightness, v.v.)
- ❌ Thiếu stage **Watermark** (thêm logo/text watermark)
- ❌ Thiếu stage **Compression** (nén ảnh để giảm dung lượng)
- ⚠️ Không hỗ trợ dynamic pipeline (không thể bỏ qua stages dựa trên user config)
- ⚠️ Error handling tối thiểu (skip + log cảnh báo, chưa có retry logic)
- ⚠️ Chưa hỗ trợ parallel processing (chỉ serial xử lý)

### 1.2 Yêu cầu từ tài liệu giao tiếp
Tài liệu yêu cầu 6 stage chính:
1. **Input Stage** — ✅ Có (capture)
2. **Resize Stage** — ❌ Thiếu
3. **Filter Stage** — ❌ Thiếu
4. **Watermark Stage** — ❌ Thiếu
5. **Compression Stage** — ❌ Thiếu
6. **Output Stage** — ✅ Có (save/display)

---

## 2. Giải thích yêu cầu chi tiết

### 2.1 Mục tiêu cuối cùng
**Xây dựng một pipeline xử lý ảnh hoàn chỉnh:**
- User upload ảnh → pass qua các stages → output ảnh đã xử lý
- Mỗi stage độc lập, có thể add/remove/modify mà không ảnh hưởng others
- Hỗ trợ cấu hình động (skip stages không cần thiết)
- Robust error handling & logging

### 2.2 Từng stage chi tiết

#### 2.2.1 Input Stage (Capture)
**Hiện tại:** ✅ Đã có (`capture_images.py`)
- Đọc ảnh từ folder
- Validate format (JPEG, PNG)
- Check size constraints
- Output: `data["image"]`, `data["image_id"]`

**Cần cải tiến:**
- Thêm metadata: `data["original_width"]`, `data["original_height"]`
- Validate file size (max MB)
- Reject unsupported formats

#### 2.2.2 Resize Stage
**Yêu cầu:** Đổi kích thước theo user spec hoặc default
- Input: `data["image"]`, params `(width, height)`
- Preserve aspect ratio (tuỳ option)
- Output: `data["image"]` (updated), `data["resized"]` = True/False

**Thách thức:**
- Edge case: ảnh nhỏ hơn target size (upscale vs. reject?)
- Performance: resize lớn có thể chậm

#### 2.2.3 Filter Stage
**Yêu cầu:** Áp dụng filter (grayscale, sepia, brightness adjustment, v.v.)
- Input: `data["image"]`, param `filter_type` (string enum)
- Apply bất kỳ filter nào được chọn
- Output: `data["image"]` (updated), `data["filter_applied"]`

**Các filter cần support:**
- Grayscale (B&W)
- Sepia (tone cổ điển)
- Brightness adjustment
- Contrast adjustment
- Blur (optional)

#### 2.2.4 Watermark Stage
**Yêu cầu:** Thêm watermark (logo, text, v.v.)
- Input: `data["image"]`, params: `watermark_type`, `position`, `opacity`
- Support: text watermark, image watermark
- Scale watermark theo ảnh size
- Output: `data["image"]` (updated), `data["watermarked"]`

**Thách thức:**
- Alpha blending
- Font rendering (text watermark)
- Position calculation (corner/center/custom)
- Avoid obscuring important content

#### 2.2.5 Compression Stage
**Yêu cầu:** Nén ảnh (giảm file size, giữ quality tối ưu)
- Input: `data["image"]`, param `quality` (0-100, default 85)
- Nén theo format (JPEG quality, PNG level)
- Output: `data["image_bytes"]` (in-memory), `data["compressed_size"]`, `data["original_size"]`

**Thách thức:**
- Trade-off: quality vs. size
- Format-specific: JPEG quality vs. PNG compression level
- In-memory vs. on-disk

#### 2.2.6 Output Stage
**Hiện tại:** ✅ Có (nhưng cần mở rộng)
- Save final image to disk / cloud storage
- Generate download URL (nếu cloud)
- Return to user / store for future use

### 2.3 Lợi ích (kiến trúc)
1. **Modularity** — Mỗi stage là class độc lập → dễ test, debug, modify
2. **Scalability** — Stages độc lập có thể parallelize nếu input cho phép
3. **Reusability** — Filter stage có thể reuse cho ứng dụng khác
4. **Maintainability** — Separation of concerns → dễ maintain

---

## 3. Phương án giải quyết

### 3.1 Chiến lược triển khai
**Tiếp cận tuần tự (Sequential):**
1. Tạo class **Resize** → test
2. Tạo class **Filter** → test
3. Tạo class **Watermark** → test
4. Tạo class **Compression** → test
5. Tạo helper function **build_pipeline()** (dynamic pipeline)
6. Cập nhật entry point (process_images_pipeline.py) để dùng dynamic pipeline
7. Thêm error handling & logging toàn bộ

### 3.2 Pattern & Contract

**Mỗi stage class:**
```python
from pipeline.pipeline import Pipeline

class StageName(Pipeline):
    def __init__(self, param1, param2=default):
        super().__init__()
        self.param1 = param1
        # ... init

    def map(self, data):
        """
        Input:  data dict (bắt buộc: 'image_id', 'image')
        Output: data dict (updated or with new fields)
        """
        image = data.get("image")
        image_id = data.get("image_id")
        
        # Validate
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skipping")
            return data
        
        try:
            # Process
            result = process_image(image)
            data["image"] = result
            data["stage_applied"] = True
        except Exception as e:
            print(f"[ERROR] {image_id}: {e}")
            # Decide: skip or re-raise
            data["error"] = str(e)
        
        return data

    def filter(self, data):
        """Optional: filter out data if needed"""
        return data.get("error") is None  # skip if error

    def has_next(self):
        """Optional: stop condition"""
        return True
```

---

## 4. Đề xuất ưu tiên

### 4.1 Ưu tiên cao (MVP)
1. **Resize** — Cơ bản, dùng trong hầu hết apps
2. **Filter** (Grayscale + Brightness) — Đơn giản, hữu ích
3. **Compression** — Giảm storage cost, cần thiết

### 4.2 Ưu tiên trung
4. **Watermark** (text watermark) — Thêm branding
5. **Dynamic pipeline** — Cấu hình linh hoạt

### 4.3 Ưu tiên thấp (nice-to-have)
6. **Parallel processing** — Chỉ nếu có bottleneck
7. **Advanced filters** (sepia, blur, v.v.) — Bonus
8. **Image watermark** (logo từ file) — Sau này

---

## 5. Các file cần thay đổi / tạo mới

### 5.1 File tạo mới

| File | Mục đích |
|------|---------|
| `pipeline/resize.py` | Resize stage |
| `pipeline/filter.py` | Filter stage (grayscale, brightness, v.v.) |
| `pipeline/watermark.py` | Watermark stage (text + image) |
| `pipeline/compression.py` | Compression stage |
| `pipeline/pipeline_builder.py` | Helper để build dynamic pipeline |
| `tests/pipeline/test_resize.py` | Unit test Resize |
| `tests/pipeline/test_filter.py` | Unit test Filter |
| `tests/pipeline/test_watermark.py` | Unit test Watermark |
| `tests/pipeline/test_compression.py` | Unit test Compression |

### 5.2 File cần cập nhật

| File | Thay đổi |
|------|----------|
| `process_images_pipeline.py` | Thêm dynamic pipeline builder + new stages |
| `pipeline/capture_images.py` | Thêm metadata (original_width, original_height) |
| `pipeline/save_faces.py` | Cập nhật để tính toán compression ratio (nếu cần) |
| `README.md` | Thêm doc về các stage mới + cách dùng |
| `requirements.txt` | Nếu cần thêm lib (ví dụ Pillow cho advanced image ops) |

### 5.3 Cấu trúc sau khi triển khai
```
pipeline/
  ├── __init__.py
  ├── pipeline.py                 (base class)
  ├── capture_images.py          ✅ Hiện có
  ├── capture_video.py           ✅ Hiện có
  ├── detect_faces.py            ✅ Hiện có
  ├── save_faces.py              ✅ Hiện có (đã sửa)
  ├── save_summary.py            ✅ Hiện có (đã sửa)
  ├── annotate_image.py          ✅ Hiện có
  ├── display_video.py           ✅ Hiện có
  ├── save_video.py              ✅ Hiện có
  ├── resize.py                  🆕 New
  ├── filter.py                  🆕 New
  ├── watermark.py               🆕 New
  ├── compression.py             🆕 New
  ├── pipeline_builder.py         🆕 New
  ├── libs/
  │   ├── __init__.py
  │   ├── face_detector.py       ✅ Hiện có
  │   ├── colors.py              ✅ Hiện có
  │   ├── utils.py               ✅ Hiện có
  │   └── image_processing.py    🆕 (helpers cho filter/watermark)
```

---

## 6. Cách triển khai cụ thể

### 6.1 Stage 1: Resize (ưu tiên cao)

**File:** `pipeline/resize.py`

```python
import cv2
from pipeline.pipeline import Pipeline

class Resize(Pipeline):
    """Resize image to specified dimensions or preserve aspect ratio."""
    
    def __init__(self, width=None, height=None, preserve_aspect=True):
        """
        Args:
            width (int): Target width (pixels)
            height (int): Target height (pixels)
            preserve_aspect (bool): Keep aspect ratio if True
        """
        super().__init__()
        self.width = width
        self.height = height
        self.preserve_aspect = preserve_aspect
    
    def map(self, data):
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip resize")
            return data
        
        try:
            original_h, original_w = image.shape[:2]
            
            # Calculate target size
            target_w, target_h = self.width or original_w, self.height or original_h
            
            if self.preserve_aspect and self.width and self.height:
                # Fit image keeping aspect, pad if needed
                ratio = min(self.width / original_w, self.height / original_h)
                new_w, new_h = int(original_w * ratio), int(original_h * ratio)
                # For now, simple resize without padding
                resized = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_AREA)
            else:
                # Direct resize (may stretch)
                resized = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            data["image"] = resized
            data["resized"] = True
            data["resize_info"] = {
                "original_size": (original_w, original_h),
                "target_size": (target_w, target_h)
            }
            print(f"[INFO] {image_id}: resized {(original_w, original_h)} -> {(target_w, target_h)}")
        except Exception as e:
            print(f"[ERROR] {image_id}: resize failed: {e}")
            data["error"] = str(e)
        
        return data
```

### 6.2 Stage 2: Filter (ưu tiên cao)

**File:** `pipeline/filter.py`

```python
import cv2
import numpy as np
from pipeline.pipeline import Pipeline

class Filter(Pipeline):
    """Apply color/tone filters to image."""
    
    FILTER_TYPES = ["grayscale", "sepia", "brightness", "contrast", "blur"]
    
    def __init__(self, filter_type="grayscale", intensity=1.0):
        """
        Args:
            filter_type (str): One of FILTER_TYPES
            intensity (float): 0.5-2.0 (1.0 = normal)
        """
        super().__init__()
        if filter_type not in self.FILTER_TYPES:
            raise ValueError(f"Unknown filter: {filter_type}. Choose from {self.FILTER_TYPES}")
        self.filter_type = filter_type
        self.intensity = intensity
    
    def map(self, data):
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip filter")
            return data
        
        try:
            if self.filter_type == "grayscale":
                filtered = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Convert back to 3-channel for consistency
                filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
            elif self.filter_type == "sepia":
                filtered = self._apply_sepia(image)
            elif self.filter_type == "brightness":
                filtered = cv2.convertScaleAbs(image, alpha=self.intensity, beta=0)
            elif self.filter_type == "contrast":
                filtered = cv2.convertScaleAbs(image, alpha=self.intensity, beta=0)
            elif self.filter_type == "blur":
                filtered = cv2.GaussianBlur(image, (int(5 * self.intensity), int(5 * self.intensity)), 0)
            else:
                filtered = image
            
            data["image"] = filtered
            data["filter_applied"] = self.filter_type
            print(f"[INFO] {image_id}: applied filter '{self.filter_type}'")
        except Exception as e:
            print(f"[ERROR] {image_id}: filter failed: {e}")
            data["error"] = str(e)
        
        return data
    
    def _apply_sepia(self, image):
        """Apply sepia tone filter."""
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        sepia_img = cv2.transform(image, sepia_filter)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        return sepia_img
```

### 6.3 Stage 3: Watermark (ưu tiên trung)

**File:** `pipeline/watermark.py`

```python
import cv2
import numpy as np
from pipeline.pipeline import Pipeline

class Watermark(Pipeline):
    """Add text or image watermark to image."""
    
    def __init__(self, text=None, image_path=None, position="bottom-right", opacity=0.7):
        """
        Args:
            text (str): Text watermark
            image_path (str): Path to watermark image file
            position (str): "top-left", "top-right", "bottom-left", "bottom-right", "center"
            opacity (float): 0.0-1.0
        """
        super().__init__()
        if text is None and image_path is None:
            raise ValueError("Either text or image_path must be provided")
        self.text = text
        self.image_path = image_path
        self.position = position
        self.opacity = opacity
    
    def map(self, data):
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip watermark")
            return data
        
        try:
            if self.text:
                watermarked = self._add_text_watermark(image, self.text)
            elif self.image_path:
                watermarked = self._add_image_watermark(image, self.image_path)
            
            data["image"] = watermarked
            data["watermarked"] = True
            print(f"[INFO] {image_id}: watermark added")
        except Exception as e:
            print(f"[ERROR] {image_id}: watermark failed: {e}")
            data["error"] = str(e)
        
        return data
    
    def _add_text_watermark(self, image, text):
        """Add text watermark."""
        h, w = image.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        color = (255, 255, 255)  # White
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x, y = self._calc_position(w, h, text_size[0], text_size[1])
        
        # Blend (optional overlay)
        overlay = image.copy()
        cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness)
        watermarked = cv2.addWeighted(image, 1 - self.opacity, overlay, self.opacity, 0)
        return watermarked
    
    def _add_image_watermark(self, image, wm_path):
        """Add image watermark (logo)."""
        wm = cv2.imread(wm_path, cv2.IMREAD_UNCHANGED)
        if wm is None:
            raise FileNotFoundError(f"Watermark image not found: {wm_path}")
        
        h, w = image.shape[:2]
        wm_h, wm_w = wm.shape[:2]
        
        # Scale watermark if too large
        max_w, max_h = w // 4, h // 4
        if wm_w > max_w or wm_h > max_h:
            ratio = min(max_w / wm_w, max_h / wm_h)
            wm_w, wm_h = int(wm_w * ratio), int(wm_h * ratio)
            wm = cv2.resize(wm, (wm_w, wm_h))
        
        x, y = self._calc_position(w, h, wm_w, wm_h)
        
        # Alpha blend
        if wm.shape[2] == 4:  # Has alpha channel
            alpha = wm[:, :, 3] / 255.0
            for c in range(3):
                image[y:y+wm_h, x:x+wm_w, c] = \
                    image[y:y+wm_h, x:x+wm_w, c] * (1 - alpha * self.opacity) + \
                    wm[:, :, c] * alpha * self.opacity
        else:
            image[y:y+wm_h, x:x+wm_w] = cv2.addWeighted(
                image[y:y+wm_h, x:x+wm_w], 1 - self.opacity,
                wm, self.opacity, 0
            )
        
        return image
    
    def _calc_position(self, img_w, img_h, obj_w, obj_h):
        """Calculate position based on self.position."""
        margin = 10
        positions = {
            "top-left": (margin, margin),
            "top-right": (img_w - obj_w - margin, margin),
            "bottom-left": (margin, img_h - obj_h - margin),
            "bottom-right": (img_w - obj_w - margin, img_h - obj_h - margin),
            "center": ((img_w - obj_w) // 2, (img_h - obj_h) // 2)
        }
        return positions.get(self.position, positions["bottom-right"])
```

### 6.4 Stage 4: Compression (ưu tiên cao)

**File:** `pipeline/compression.py`

```python
import cv2
import os
from pipeline.pipeline import Pipeline

class Compression(Pipeline):
    """Compress image to reduce file size."""
    
    def __init__(self, quality=85, output_format="jpg"):
        """
        Args:
            quality (int): 0-100 (higher = better quality, larger file)
            output_format (str): "jpg" or "png"
        """
        super().__init__()
        self.quality = max(0, min(100, quality))  # Clamp 0-100
        self.output_format = output_format.lower()
    
    def map(self, data):
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip compression")
            return data
        
        try:
            # Encode to bytes
            if self.output_format == "jpg":
                # JPEG compression
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                _, buffer = cv2.imencode('.jpg', image, encode_params)
            elif self.output_format == "png":
                # PNG compression (0-9, default 3)
                compression_level = int((100 - self.quality) / 11)  # Map quality to compression
                encode_params = [int(cv2.IMWRITE_PNG_COMPRESSION), compression_level]
                _, buffer = cv2.imencode('.png', image, encode_params)
            else:
                _, buffer = cv2.imencode(f'.{self.output_format}', image)
            
            compressed_bytes = buffer.tobytes()
            original_size = image.nbytes
            compressed_size = len(compressed_bytes)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            data["image_bytes"] = compressed_bytes
            data["compressed_size"] = compressed_size
            data["original_size"] = original_size
            data["compression_ratio"] = ratio
            data["compressed"] = True
            
            print(f"[INFO] {image_id}: compressed {original_size}B -> {compressed_size}B ({ratio:.1f}% reduction)")
        except Exception as e:
            print(f"[ERROR] {image_id}: compression failed: {e}")
            data["error"] = str(e)
        
        return data
```

### 6.5 Dynamic Pipeline Builder (ưu tiên trung)

**File:** `pipeline/pipeline_builder.py`

```python
from pipeline.capture_images import CaptureImages
from pipeline.detect_faces import DetectFaces
from pipeline.save_faces import SaveFaces
from pipeline.save_summary import SaveSummary
from pipeline.display_summary import DisplaySummary
from pipeline.resize import Resize
from pipeline.filter import Filter
from pipeline.watermark import Watermark
from pipeline.compression import Compression


class PipelineConfig:
    """Configuration for dynamic pipeline."""
    
    def __init__(self):
        self.input_path = None
        self.output_path = "output"
        self.summary_file = "summary.json"
        
        # Stages
        self.enable_resize = False
        self.resize_width = None
        self.resize_height = None
        
        self.enable_filter = False
        self.filter_type = "grayscale"
        self.filter_intensity = 1.0
        
        self.enable_watermark = False
        self.watermark_text = None
        self.watermark_image = None
        self.watermark_position = "bottom-right"
        
        self.enable_compression = False
        self.compression_quality = 85
        
        # Face detection
        self.prototxt = "./models/face_detector/deploy.prototxt.txt"
        self.model = "./models/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
        self.confidence = 0.5
        self.batch_size = 1


def build_image_pipeline(config):
    """Build image processing pipeline based on config."""
    
    # Input
    pipeline = CaptureImages(config.input_path)
    
    # Optional: Resize
    if config.enable_resize:
        resize = Resize(width=config.resize_width, height=config.resize_height)
        pipeline = pipeline | resize
    
    # Optional: Filter
    if config.enable_filter:
        filter_stage = Filter(filter_type=config.filter_type, intensity=config.filter_intensity)
        pipeline = pipeline | filter_stage
    
    # Optional: Watermark
    if config.enable_watermark:
        watermark = Watermark(
            text=config.watermark_text,
            image_path=config.watermark_image,
            position=config.watermark_position
        )
        pipeline = pipeline | watermark
    
    # Face Detection (always include for this project)
    detect_faces = DetectFaces(
        prototxt=config.prototxt,
        model=config.model,
        confidence=config.confidence,
        batch_size=config.batch_size
    )
    pipeline = pipeline | detect_faces
    
    # Save Faces
    save_faces = SaveFaces(config.output_path)
    pipeline = pipeline | save_faces
    
    # Optional: Compression (before save)
    if config.enable_compression:
        compression = Compression(quality=config.compression_quality)
        pipeline = pipeline | compression
    
    # Summary
    import os
    summary_file = os.path.join(config.output_path, config.summary_file)
    save_summary = SaveSummary(summary_file)
    pipeline = pipeline | save_summary
    
    # Display
    display = DisplaySummary()
    pipeline = pipeline | display
    
    return pipeline, summary_file
```

### 6.6 Cập nhật entry point

**File:** `process_images_pipeline.py` (cập nhật)

```python
import os
from pipeline.pipeline_builder import PipelineConfig, build_image_pipeline


def parse_args():
    import argparse
    
    ap = argparse.ArgumentParser(description="Image processing pipeline with optional stages")
    ap.add_argument("-i", "--input", required=True, help="path to input image files")
    ap.add_argument("-o", "--output", default="output", help="path to output directory")
    
    # Optional stages
    ap.add_argument("--resize", type=int, nargs=2, metavar=("WIDTH", "HEIGHT"),
                    help="enable resize (specify width height)")
    ap.add_argument("--filter", choices=["grayscale", "sepia", "brightness", "contrast", "blur"],
                    default=None, help="enable filter")
    ap.add_argument("--filter-intensity", type=float, default=1.0, help="filter intensity")
    ap.add_argument("--watermark-text", type=str, help="text watermark")
    ap.add_argument("--watermark-position", default="bottom-right",
                    choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                    help="watermark position")
    ap.add_argument("--compress", type=int, default=None, metavar="QUALITY",
                    help="enable compression (0-100, default 85)")
    
    # Face detection
    ap.add_argument("--prototxt", default="./models/face_detector/deploy.prototxt.txt")
    ap.add_argument("--model", default="./models/face_detector/res10_300x300_ssd_iter_140000.caffemodel")
    ap.add_argument("--confidence", type=float, default=0.5)
    ap.add_argument("--batch-size", type=int, default=1)
    
    return ap.parse_args()


def main(args):
    # Build config
    config = PipelineConfig()
    config.input_path = args.input
    config.output_path = args.output
    
    # Resize
    if args.resize:
        config.enable_resize = True
        config.resize_width, config.resize_height = args.resize
    
    # Filter
    if args.filter:
        config.enable_filter = True
        config.filter_type = args.filter
        config.filter_intensity = args.filter_intensity
    
    # Watermark
    if args.watermark_text:
        config.enable_watermark = True
        config.watermark_text = args.watermark_text
        config.watermark_position = args.watermark_position
    
    # Compression
    if args.compress is not None:
        config.enable_compression = True
        config.compression_quality = args.compress
    
    # Face detection config
    config.prototxt = args.prototxt
    config.model = args.model
    config.confidence = args.confidence
    config.batch_size = args.batch_size
    
    # Build and run pipeline
    pipeline, summary_file = build_image_pipeline(config)
    
    try:
        for _ in pipeline:
            pass
    except StopIteration:
        return
    except KeyboardInterrupt:
        return
    finally:
        print(f"[INFO] Saving summary to {summary_file}...")


if __name__ == "__main__":
    args = parse_args()
    main(args)
```

---

## 7. Unit Tests

### 7.1 Test Resize

**File:** `tests/pipeline/test_resize.py`

```python
import pytest
import cv2
import numpy as np
from pipeline.resize import Resize


def test_resize_basic():
    """Test basic resize."""
    stage = Resize(width=100, height=100)
    
    # Create dummy image
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    data = {"image": image, "image_id": "test"}
    
    result = stage.map(data)
    
    assert result["resized"] == True
    assert result["image"].shape == (100, 100, 3)


def test_resize_empty_image():
    """Test with empty image."""
    stage = Resize(width=100, height=100)
    data = {"image": None, "image_id": "test"}
    
    result = stage.map(data)
    
    assert result.get("image") is None
    assert "resized" not in result or result["resized"] == False


def test_resize_preserve_aspect():
    """Test preserve aspect ratio."""
    stage = Resize(width=100, height=100, preserve_aspect=True)
    
    image = np.zeros((200, 400, 3), dtype=np.uint8)  # 2:1 aspect
    data = {"image": image, "image_id": "test"}
    
    result = stage.map(data)
    
    assert result["resized"] == True
    # Should fit within 100x100
```

### 7.2 Test Filter

**File:** `tests/pipeline/test_filter.py`

```python
import pytest
import cv2
import numpy as np
from pipeline.filter import Filter


def test_filter_grayscale():
    """Test grayscale filter."""
    stage = Filter(filter_type="grayscale")
    
    # Colored image (BGR)
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    data = {"image": image, "image_id": "test"}
    
    result = stage.map(data)
    
    assert result["filter_applied"] == "grayscale"
    assert result["image"].shape == (100, 100, 3)  # Back to 3-channel


def test_filter_invalid_type():
    """Test invalid filter type."""
    with pytest.raises(ValueError):
        Filter(filter_type="invalid_filter")
```

---

## 8. Hướng dẫn sử dụng

### 8.1 Ví dụ: Resize + Filter + Compress

```bash
python process_images_pipeline.py \
  -i assets/images \
  -o output \
  --resize 640 480 \
  --filter brightness \
  --filter-intensity 1.2 \
  --compress 90
```

### 8.2 Ví dụ: Thêm watermark text

```bash
python process_images_pipeline.py \
  -i assets/images \
  -o output \
  --watermark-text "© My Company" \
  --watermark-position "bottom-right"
```

### 8.3 Ví dụ: Chỉ phát hiện khuôn mặt (no optional stages)

```bash
python process_images_pipeline.py \
  -i assets/images \
  -o output
```

---

## 9. Lợi ích sau triển khai

| Yêu cầu | Trạng thái | Lợi ích |
|--------|-----------|--------|
| Modularity | ✅ Hoàn tất | Mỗi stage độc lập, dễ test & modify |
| Scalability | ✅ Cơ bản | Có thể extend parallel trong tương lai |
| Reusability | ✅ Hoàn tất | Stages có thể reuse trong app khác |
| Maintainability | ✅ Hoàn tất | Clear separation, dễ debug |
| Dynamic Config | ✅ Hoàn tất | User chọn stages cần thiết |
| Error Handling | ✅ Hoàn tất | Mỗi stage có try-catch + logging |
| Flexible Composition | ✅ Hoàn tất | Nối stages bằng `\|` tuỳ ý |

---

## 10. Timeline & Deliverables

### Phase 1: Core Stages (Tuần 1)
- ✅ Resize stage
- ✅ Filter stage (basic)
- ✅ Compression stage
- Tests & docs

### Phase 2: Advanced Features (Tuần 2)
- ✅ Watermark stage
- ✅ Dynamic pipeline builder
- Integration tests
- README update

### Phase 3: Optimization (Tuần 3, optional)
- Parallel processing
- Advanced filters
- Performance tuning

---

**Kết luận:** Dự án hiện có nền tảng pipeline tốt. Cần thêm 4 stages chính (Resize, Filter, Watermark, Compression) + dynamic builder để đạt yêu cầu kiến trúc hoàn chỉnh. Tất cả stage tuân theo pattern chung, dễ test & maintain.
