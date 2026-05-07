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
            
            # Use original if not specified
            target_w = self.width if self.width is not None else original_w
            target_h = self.height if self.height is not None else original_h
            
            if self.preserve_aspect and self.width and self.height:
                # Fit image keeping aspect ratio
                ratio = min(self.width / original_w, self.height / original_h)
                target_w = int(original_w * ratio)
                target_h = int(original_h * ratio)
            
            # Perform resize
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
