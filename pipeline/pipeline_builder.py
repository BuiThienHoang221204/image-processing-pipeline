import os
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
    """Configuration for the dynamic image processing pipeline."""
    def __init__(self, **kwargs):
        self.input_path = kwargs.get("input_path")
        self.output_path = kwargs.get("output_path", "output")
        self.out_summary = kwargs.get("out_summary", "summary.json")
        
        # Resize stage config
        self.resize_width = kwargs.get("resize_width")
        self.resize_height = kwargs.get("resize_height")
        self.preserve_aspect = kwargs.get("preserve_aspect", True)
        
        # Filter stage config
        self.filter_type = kwargs.get("filter_type")
        self.filter_intensity = kwargs.get("filter_intensity", 1.0)
        
        # Watermark stage config
        self.watermark_text = kwargs.get("watermark_text")
        self.watermark_image = kwargs.get("watermark_image")
        self.watermark_position = kwargs.get("watermark_position", "bottom-right")
        self.watermark_opacity = kwargs.get("watermark_opacity", 0.7)
        
        # Compression stage config
        self.compress_quality = kwargs.get("compress_quality") # If set, compression is enabled
        
        # Face detection config
        self.prototxt = kwargs.get("prototxt", "./models/face_detector/deploy.prototxt.txt")
        self.model = kwargs.get("model", "./models/face_detector/res10_300x300_ssd_iter_140000.caffemodel")
        self.confidence = kwargs.get("confidence", 0.5)
        self.batch_size = kwargs.get("batch_size", 1)

def build_image_pipeline(config):
    """Factory to build a pipeline based on configuration."""
    
    # 1. Start with Capture
    pipeline = CaptureImages(config.input_path)
    
    # 2. Add Resize if configured
    if config.resize_width is not None or config.resize_height is not None:
        pipeline = pipeline | Resize(
            width=config.resize_width, 
            height=config.resize_height, 
            preserve_aspect=config.preserve_aspect
        )
    
    # 3. Add Filter if configured
    if config.filter_type:
        pipeline = pipeline | Filter(
            filter_type=config.filter_type, 
            intensity=config.filter_intensity
        )
    
    # 4. Add Watermark if configured
    if config.watermark_text or config.watermark_image:
        pipeline = pipeline | Watermark(
            text=config.watermark_text,
            image_path=config.watermark_image,
            position=config.watermark_position,
            opacity=config.watermark_opacity
        )
    
    # 5. Always include Face Detection (core project functionality)
    pipeline = pipeline | DetectFaces(
        prototxt=config.prototxt,
        model=config.model,
        confidence=config.confidence,
        batch_size=config.batch_size
    )
    
    # 6. Save Faces
    pipeline = pipeline | SaveFaces(config.output_path)
    
    # 7. Compression (applied before final summary)
    if config.compress_quality is not None:
        pipeline = pipeline | Compression(quality=config.compress_quality)
    
    # 8. Summary & Display
    summary_file = os.path.join(config.output_path, config.out_summary)
    save_summary = SaveSummary(summary_file)
    pipeline = pipeline | save_summary | DisplaySummary()
    
    return pipeline, save_summary
