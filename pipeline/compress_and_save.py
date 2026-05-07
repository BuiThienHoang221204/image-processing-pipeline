import os
import cv2
from pipeline.pipeline import Pipeline

class CompressAndSave(Pipeline):
    def __init__(self, output_dir: str = "output", quality: int = 60):
        self.output_dir = output_dir
        self.quality = int(quality)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def map(self, data: dict) -> dict:
        image = data.get("image")
        image_id = data.get("image_id", "unknown.jpg")
        file_name = os.path.basename(image_id)
        
        if image is not None:
            out_path = os.path.join(self.output_dir, file_name)
            # Thông số nén cho định dạng JPEG (từ 0 đến 100, số càng nhỏ càng nén mạnh/chất lượng thấp)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            cv2.imwrite(out_path, image, encode_param)
            data["output_path"] = out_path
            
        return data