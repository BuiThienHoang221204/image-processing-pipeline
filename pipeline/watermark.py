import cv2
from pipeline.pipeline import Pipeline

class Watermark(Pipeline):
    """Add text or image watermark to image."""
    
    def __init__(self, text: str = "FIT IUH", image_path=None, position="bottom-right", opacity=0.7):
        """
        Args:
            text (str): Text watermark to add.
            image_path (str): Path to watermark logo image.
            position (str): "top-left", "top-right", "bottom-left", "bottom-right", "center"
            opacity (float): Opacity level from 0.0 to 1.0.
        """
        super().__init__()
        if text is None and image_path is None:
            raise ValueError("Either text or image_path must be provided for watermark")
        self.text = text
        self.image_path = image_path
        self.position = position
        self.opacity = opacity
    
    def map(self, data: dict) -> dict:
        image = data.get("image")
        image_id = data.get("image_id", "unknown")
        
        if image is None or image.size == 0:
            print(f"[WARN] {image_id}: empty image, skip watermark")
            return data
        
        try:
            if self.text:
                result = self._add_text_watermark(image, self.text)
            elif self.image_path:
                result = self._add_image_watermark(image, self.image_path)
            else:
                result = image
            
            data["image"] = result
            data["watermarked"] = True
            print(f"[INFO] {image_id}: watermark added")
        except Exception as e:
            print(f"[ERROR] {image_id}: watermark failed: {e}")
            data["error"] = str(e)
        
        return data
    
    def _add_text_watermark(self, image, text):
        """Add text watermark with transparency."""
        h, w = image.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Scale font size based on image width
        font_scale = w / 1000.0 * 1.5 
        thickness = max(1, int(font_scale * 2))
        color = (255, 255, 255) # White
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x, y = self._calc_position(w, h, text_size[0], text_size[1])
        
        # Adjust y because putText uses bottom-left baseline
        y += text_size[1]
        
        # Create overlay for blending
        overlay = image.copy()
        cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
        
        # Blend overlay with original image
        return cv2.addWeighted(image, 1 - self.opacity, overlay, self.opacity, 0)
    
    def _add_image_watermark(self, image, wm_path):
        """Add image watermark (logo) with alpha transparency support."""
        wm = cv2.imread(wm_path, cv2.IMREAD_UNCHANGED)
        if wm is None:
            raise FileNotFoundError(f"Watermark image not found: {wm_path}")
        
        h, w = image.shape[:2]
        wm_h, wm_w = wm.shape[:2]
        
        # Scale watermark to fit (max 20% of image width or height)
        max_wm_w = int(w * 0.2)
        max_wm_h = int(h * 0.2)
        
        if wm_w > max_wm_w or wm_h > max_wm_h:
            ratio = min(max_wm_w / wm_w, max_wm_h / wm_h)
            wm_w = int(wm_w * ratio)
            wm_h = int(wm_h * ratio)
            wm = cv2.resize(wm, (wm_w, wm_h), interpolation=cv2.INTER_AREA)
        
        x, y = self._calc_position(w, h, wm_w, wm_h)
        
        # Region of interest in the image
        roi = image[y:y+wm_h, x:x+wm_w]
        
        # Handle alpha channel if present
        if wm.shape[2] == 4:
            # Split channels
            wm_bgr = wm[:, :, :3]
            wm_alpha = wm[:, :, 3] / 255.0
            
            # Apply opacity
            wm_alpha *= self.opacity
            
            # Blend
            for c in range(3):
                roi[:, :, c] = roi[:, :, c] * (1 - wm_alpha) + wm_bgr[:, :, c] * wm_alpha
        else:
            # No alpha channel, simple blend
            blended = cv2.addWeighted(roi, 1 - self.opacity, wm, self.opacity, 0)
            image[y:y+wm_h, x:x+wm_w] = blended
            
        return image
    
    def _calc_position(self, img_w, img_h, obj_w, obj_h):
        """Calculate coordinates based on predefined positions."""
        margin = int(min(img_w, img_h) * 0.05)
        
        if self.position == "top-left":
            return (margin, margin)
        elif self.position == "top-right":
            return (img_w - obj_w - margin, margin)
        elif self.position == "bottom-left":
            return (margin, img_h - obj_h - margin)
        elif self.position == "center":
            return ((img_w - obj_w) // 2, ((img_h - obj_h) // 2))
        else: # bottom-right default
            return (img_w - obj_w - margin, img_h - obj_h - margin)
