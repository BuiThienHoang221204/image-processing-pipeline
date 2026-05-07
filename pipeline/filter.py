import cv2
import numpy as np
from pipeline.pipeline import Pipeline

class ImageFilter(Pipeline):
    """Apply color/tone filters to image."""
    
    FILTER_TYPES = ["grayscale", "sepia", "brightness", "contrast", "blur"]
    
    def __init__(self, filter_type="grayscale", intensity=1.0):
        """
        Args:
            filter_type (str): One of FILTER_TYPES
            intensity (float): Multiplier for effect (e.g. brightness alpha, blur kernel size)
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
                # Convert back to 3-channel for consistency in the pipeline
                filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
            elif self.filter_type == "sepia":
                kernel = np.array([[0.272, 0.534, 0.131],
                                   [0.349, 0.686, 0.168],
                                   [0.393, 0.769, 0.189]])
                filtered = cv2.transform(image, kernel)
                filtered = np.clip(filtered, 0, 255).astype(np.uint8)
            elif self.filter_type == "brightness":
                # alpha is intensity, beta is 0. 
                # alpha > 1: brighter, alpha < 1: darker
                filtered = cv2.convertScaleAbs(image, alpha=self.intensity, beta=0)
            elif self.filter_type == "contrast":
                # Simple contrast adjustment using alpha
                mid = 127
                filtered = cv2.convertScaleAbs(image, alpha=self.intensity, beta=mid*(1-self.intensity))
            elif self.filter_type == "blur":
                ksize = int(5 * self.intensity)
                if ksize % 2 == 0: ksize += 1 # kernel size must be odd
                filtered = cv2.GaussianBlur(image, (ksize, ksize), 0)
            else:
                filtered = image
            
            data["image"] = filtered
            data["filter_applied"] = self.filter_type
            print(f"[INFO] {image_id}: applied filter '{self.filter_type}'")
        except Exception as e:
            print(f"[ERROR] {image_id}: filter failed: {e}")
            data["error"] = str(e)
        
        return data
