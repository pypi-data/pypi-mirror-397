"""
CarLib - Efficient ML Training with CAR Format

A comprehensive Python library and CLI tool for neural network training with tokenized 
datasets. CarLib provides:

🔄 Dataset Conversion: Convert various formats to efficient CAR format using advanced tokenizers
📊 ML Data Loaders: PyTorch/JAX loaders optimized for training
🎯 Decode Utilities: Validation and visualization tools
📈 Evaluation & Benchmarking: Performance analysis and dataset comparison tools

Supported input formats:
- vanilla: Regular media files (audio, image, video)
- webdataset: WebDataset tar archives  
- hdf5: HDF5 data files
- tfrecord: TensorFlow record files

Supported target modalities:
- audio: Audio tokenization with advanced audio tokenizers
- image: Image tokenization with advanced image tokenizers
- video: Video tokenization with advanced video tokenizers

Example usage:
    # 1. Convert datasets to CAR format
    from carlib import convert_dataset_to_car
    
    convert_dataset_to_car(
        input_path="/path/to/dataset",
        output_path="/path/to/output",
        modality="vanilla", 
        target_modality="audio",
        num_gpus=2
    )
    
    # 2. Load CAR files for ML training (encoded tokens)
    from carlib import CARDataset, CARLoader
    
    dataset = CARDataset("/path/to/car/files")
    loader = CARLoader(dataset, batch_size=32)
    
    for batch in loader:
        tokens = batch['data']['codes']  # Train on tokenized representations
        loss = model(tokens)
    
    # 3. Decode for validation/visualization only
    from carlib import decode_car_file
    
    decoded = decode_car_file("/path/to/sample.car", "/path/to/output.wav")
    
    # 4. Benchmark dataset performance (optional evaluation module)
    from carlib import BenchmarkConfig, run_folder_benchmark, analyze_benchmark_results
    
    config = BenchmarkConfig(
        folder_path="/path/to/dataset", 
        modality="audio",
        output_file="benchmark_results.json"
    )
    results = run_folder_benchmark(config)
    analysis = analyze_benchmark_results("benchmark_results.json")

CLI usage:
    carlib convert /path/to/dataset --modality vanilla --target-modality audio -o /output
"""

__version__ = "1.3.43"
__author__ = "Rightsify"
__email__ = "dev@rightsify.com"
__license__ = "MIT"
__description__ = "Comprehensive library for efficient ML traininweg with tokenized CAR format - conversion, loading, and decode utilities"

# Import main functions for programmatic use
try:
    from .dataset_to_car import convert_dataset_to_car, load_config_from_yaml
    from .loaders import (
        CARDataset, CARIterableDataset, CARLoader, JAXCARLoader,
        GrainCARDataSource, GrainCARLoader,
        load_car_pytorch, load_car_jax, load_car_grain, load_single_car
    )
    from .decode import (
        decode_car_file, decode_encoded_data, decode_car_directory,
        CARDecoder, decode_audio_car, decode_image_car, decode_video_car
    )
    # Note: DecodeTransform available but not recommended for training
    # Decoding should be used only for validation/visualization
    from .transforms import ModalityFilter, create_modality_filter
    
    # Import evaluation functionality
    try:
        from .evaluation import (
            BenchmarkConfig, BenchmarkResult, run_folder_benchmark, analyze_benchmark_results
        )
        _evaluation_available = True
    except ImportError:
        BenchmarkConfig = None
        BenchmarkResult = None 
        run_folder_benchmark = None
        analyze_benchmark_results = None
        _evaluation_available = False
    
    __all__ = [
        "convert_dataset_to_car",
        "load_config_from_yaml",
        "CARDataset",
        "CARIterableDataset", 
        "CARLoader",
        "JAXCARLoader",
        "GrainCARDataSource",
        "GrainCARLoader",
        "load_car_pytorch",
        "load_car_jax",
        "load_car_grain",
        "load_single_car",
        "decode_car_file",
        "decode_encoded_data", 
        "decode_car_directory",
        "CARDecoder",
        "decode_audio_car",
        "decode_image_car", 
        "decode_video_car",
        "ModalityFilter",
        "create_modality_filter",
        "__version__",
        "__author__",
        "__email__",
        "__license__",
        "__description__",
    ]
    
    # Add evaluation functions to __all__ if available
    if _evaluation_available:
        __all__.extend([
            "BenchmarkConfig",
            "BenchmarkResult",
            "run_folder_benchmark", 
            "analyze_benchmark_results"
        ])
    
except ImportError as e:
    # Handle case where dependencies aren't installed
    import warnings
    warnings.warn(
        f"Some CarLib dependencies are not available: {e}. "
        "Install with 'pip install carlib[all]' for full functionality.",
        ImportWarning
    )
    __all__ = [
        "__version__",
        "__author__", 
        "__email__",
        "__license__",
        "__description__",
    ]