"""
Processors module for CarLib

This module contains processor classes for different media types and codecs.
"""

try:
    from .audio_codecs import AudioProcessor, AudioConfig
    from .image_codecs import CosmosImageProcessor, ImageConfig
    from .video_codecs import CosmosVideoProcessor, VideoConfig
    from .utils import CARHandler
    
    __all__ = [
        "AudioProcessor",
        "AudioConfig", 
        "CosmosImageProcessor",
        "ImageConfig",
        "CosmosVideoProcessor", 
        "VideoConfig",
        "CARHandler"
    ]
    
except ImportError as e:
    import warnings
    warnings.warn(
        f"Some processor dependencies are not available: {e}",
        ImportWarning
    )
    __all__ = []