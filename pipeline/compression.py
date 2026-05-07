import cv2
from pipeline.pipeline import Pipeline

class Compression(Pipeline):
    """Compress image to reduce file size."""
    
    def __init__(self, quality=85, output_format="jpg"):
        """
        Args:
            quality (int): Compression quality (0-100). Higher is better quality, larger file.
            output_format (str): "jpg" or "png".
        """
        super().__init__()
        self.quality = max(0, min(100, quality))
        self.output_format = output_format.lower()
    
    def map(self, data):
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip compression")
            return data
        
        try:
            # Encode image to memory buffer
            if self.output_format == "jpg":
                params = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                ext = ".jpg"
            elif self.output_format == "png":
                # PNG compression is 0-9
                comp_level = int((100 - self.quality) / 11)
                params = [int(cv2.IMWRITE_PNG_COMPRESSION), comp_level]
                ext = ".png"
            else:
                params = []
                ext = f".{self.output_format}"
            
            success, buffer = cv2.imencode(ext, image, params)
            if not success:
                raise RuntimeError("Failed to encode image")
            
            compressed_bytes = buffer.tobytes()
            original_size = image.nbytes
            compressed_size = len(compressed_bytes)
            
            # Update data with compressed result
            data["image_bytes"] = compressed_bytes
            data["compressed"] = True
            data["compression_info"] = {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "ratio": compressed_size / original_size if original_size > 0 else 1.0,
                "format": self.output_format
            }
            
            print(f"[INFO] {image_id}: compressed {original_size} -> {compressed_size} bytes")
        except Exception as e:
            print(f"[ERROR] {image_id}: compression failed: {e}")
            data["error"] = str(e)
            
        return data
