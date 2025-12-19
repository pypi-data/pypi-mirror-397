#!/usr/bin/env python3
"""
Folder Benchmark Script for Multi-Modal Latent Generation vs CAR Loading

This script:
1. Recursively scans folders for media files (audio/image/video)
2. Benchmarks latent generation vs CAR loading for each file
3. Uses multiprocessing for parallel GPU processing
4. Saves comprehensive results to JSON
5. Supports single modality processing per run
6. Automatically loads base metadata from JSON files
7. Includes warm-up run (first run ignored) for accurate timing

Usage:
    python folder_benchmark.py /path/to/dataset --modality audio --gpus 4 --output results.json
    python folder_benchmark.py /path/to/webdataset --modality webdataset --webdataset-modality audio --gpus 4
    python folder_benchmark.py /path/to/hdf5files --modality hdf5 --hdf5-modality image --gpus 2

GPU Usage (automatically optimized):
    - Audio: 4 workers per GPU (EnCodec is memory efficient)
    - Image: 2 workers per GPU (moderate VRAM usage)
    - Video: 1 worker per GPU (video processing is VRAM intensive)
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import traceback
from datetime import datetime

# Import carlib functionality
try:
    # Try to import from carlib if we're within the package
    from ..processors.audio_codecs import AudioProcessor, AudioConfig
    from ..processors.image_codecs import CosmosImageProcessor, ImageConfig
    from ..processors.video_codecs import CosmosVideoProcessor, VideoConfig
    from .. import convert_dataset_to_car, load_single_car
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from processors.audio_codecs import AudioProcessor, AudioConfig
    from processors.image_codecs import CosmosImageProcessor, ImageConfig
    from processors.video_codecs import CosmosVideoProcessor, VideoConfig
    try:
        from carlib import convert_dataset_to_car, load_single_car
    except ImportError:
        convert_dataset_to_car = None
        load_single_car = None


def benchmark_single_file_with_carlib(file_path: str, output_path: str, 
                                     modality: str, target_modality: str,
                                     model_config: Optional[Dict] = None, 
                                     metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Benchmark single file conversion using carlib's convert_dataset_to_car function.
    
    This is a wrapper around carlib's functionality specifically for benchmarking purposes.
    """
    try:
        # Create temporary directory for the single file
        temp_dir = Path(file_path).parent / "temp_benchmark"
        temp_dir.mkdir(exist_ok=True)
        
        # Use carlib's convert function for single file
        start_time = time.perf_counter()
        
        if convert_dataset_to_car is not None:
            convert_dataset_to_car(
                input_path=str(Path(file_path).parent),
                output_path=output_path,
                modality="vanilla",  # Single files are vanilla
                target_modality=target_modality,
                parallel=False,  # Single file, no need for parallel
                max_files=1,
                model_config=model_config,
                recursive=False
            )
        else:
            # Fallback to direct processor usage if carlib functions not available
            return None
            
        generation_time = (time.perf_counter() - start_time) * 1000
        
        return {
            'status': 'success',
            'generation_time_ms': generation_time,
            'car_path': str(Path(output_path) / Path(file_path).with_suffix('.car').name)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def load_car_with_carlib(car_path: str) -> Dict[str, Any]:
    """Load CAR file using carlib's loading functionality."""
    try:
        start_time = time.perf_counter()
        
        if load_single_car is not None:
            result = load_single_car(car_path)
            loading_time = (time.perf_counter() - start_time) * 1000
            
            return {
                'status': 'success',
                'loading_time_ms': loading_time,
                'data': result
            }
        else:
            # Fallback if carlib functions not available
            return None
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@dataclass
class BenchmarkResult:
    """Result structure for individual file benchmark"""
    file_path: str
    file_size_mb: float
    file_duration_or_pixels: float  # Duration for audio/video, pixels for images
    car_size_mb: float
    generation_time_ms: float
    loading_time_ms: float
    speedup_factor: float
    time_savings_ms: float
    compression_ratio: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    # Multi-format results
    format_results: Optional[Dict[str, Dict[str, float]]] = None  # {format: {size_mb, loading_time_ms}}


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution"""
    folder_path: str
    modality: str  # 'audio', 'image', 'video', 'webdataset', or 'hdf5'
    output_file: str
    num_gpus: int = 1
    device: str = "auto"
    num_runs: int = 3
    max_files: Optional[int] = None
    file_extensions: Optional[List[str]] = None
    model_config: Optional[Dict[str, Any]] = None
    gpu_id: Optional[int] = None  # Specific GPU ID for single worker
    webdataset_modality: str = "audio"  # Target modality for webdataset files
    hdf5_modality: str = "audio"  # Target modality for HDF5 files


# File extension mappings
EXTENSIONS = {
    'audio': ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac', '.wma'],
    'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.wmv', '.flv'],
    'webdataset': ['.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2'],
    'hdf5': ['.hdf5', '.h5', '.hdf']
}

# Default model configurations
DEFAULT_CONFIGS = {
    'audio': {
        'model_name': 'facebook/encodec_32khz',
        'model_type': 'encodec',
        'output_format': 'car'
    },
    'image': {
        'model_name': 'CI8x8',
        'output_format': 'car'
    },
    'video': {
        'model_name': 'DV4x8x8',
        'temporal_window': 17,
        'output_format': 'car'
    }
}


def detect_device():
    """Detect the best available device (CUDA or CPU)"""
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA detected: {gpu_name} ({gpu_count} GPU{'s' if gpu_count > 1 else ''})")
            return device, gpu_count
        else:
            device = "cpu"
            print("ℹ️ CUDA not available, using CPU")
            return device, 0
    except ImportError:
        device = "cpu"
        print("ℹ️ PyTorch not available, using CPU")
        return device, 0


def find_webdataset_samples(tar_path: str, modality: str, max_files: Optional[int] = None) -> List[Tuple[str, Any]]:
    """
    Load samples from webdataset tar file without extraction
    
    Args:
        tar_path: Path to webdataset tar file
        modality: Target modality ('audio', 'image', 'video')
        max_files: Maximum files to process (per file - used for sampling)
        
    Returns:
        List of (sample_key, sample_data) tuples
    """
    try:
        import webdataset as wds
    except ImportError:
        print("❌ webdataset library not found. Install with: pip install webdataset")
        return []
    
    samples = []
    
    try:
        print(f"📦 Loading webdataset: {Path(tar_path).name}")
        
        # Create webdataset
        dataset = wds.WebDataset(tar_path)
        
        # Configure decoder based on modality
        if modality == 'audio':
            # Get raw bytes and let benchmark function handle decoding
            # This is more reliable than trying to decode in webdataset
            dataset = dataset.to_tuple('wav;flac;mp3', 'json', handler=wds.ignore_and_continue)
            
        elif modality == 'image':
            # Decode image files and metadata  
            dataset = dataset.decode('pil').to_tuple('jpg;jpeg;png', 'json', handler=wds.ignore_and_continue)
        elif modality == 'video':
            # For video, we'll handle decoding manually since it's more complex
            dataset = dataset.to_tuple('mp4;avi;mov', 'json', handler=wds.ignore_and_continue)
        else:
            print(f"❌ Unsupported modality for webdataset: {modality}")
            return []
        
        # First pass: count total samples if we need to sample
        if max_files is not None:
            # Convert dataset to list to enable sampling
            all_samples = list(dataset)
            total_samples = len(all_samples)
            
            if total_samples > max_files:
                # Sample evenly across the dataset
                import random
                sample_indices = sorted(random.sample(range(total_samples), max_files))
                selected_samples = [all_samples[i] for i in sample_indices]
                print(f"   🎯 Sampling {max_files} from {total_samples} available samples")
            else:
                selected_samples = all_samples
                print(f"   ✅ Using all {total_samples} available samples")
            
            # Create sample tuples with keys
            for i, sample in enumerate(selected_samples):
                sample_key = f"{Path(tar_path).stem}_{i:06d}"
                samples.append((sample_key, sample))
        else:
            # No sampling needed, collect all samples
            for i, sample in enumerate(dataset):
                sample_key = f"{Path(tar_path).stem}_{i:06d}"
                samples.append((sample_key, sample))
            
        print(f"   ✅ Loaded {len(samples)} {modality} samples from {Path(tar_path).name}")
        
    except Exception as e:
        print(f"   ❌ Failed to load webdataset {Path(tar_path).name}: {str(e)}")
    
    return samples



def find_hdf5_samples(hdf5_path: str, modality: str, max_files: Optional[int] = None) -> List[Tuple[str, str, int]]:
    """
    Load sample keys from HDF5 file without loading data into memory
    
    Args:
        hdf5_path: Path to HDF5 file
        modality: Target modality ('audio', 'image', 'video')
        max_files: Maximum files to process (per file - used for sampling)
        
    Returns:
        List of (sample_key, hdf5_path, index) tuples for lazy loading
    """
    try:
        import h5py
    except ImportError:
        print("❌ h5py library not found. Install with: pip install h5py")
        return []
    
    samples = []
    
    try:
        print(f"📊 Loading HDF5 dataset: {Path(hdf5_path).name}")
        
        with h5py.File(hdf5_path, 'r') as hdf5_file:
            # Common HDF5 dataset structures for different modalities
            if modality == 'audio':
                # Look for common audio dataset names
                dataset_names = ['audio', 'waveforms', 'data', 'samples']
            elif modality == 'image':
                # Look for common image dataset names
                dataset_names = ['images', 'data', 'pixels', 'frames']
            elif modality == 'video':
                # Look for common video dataset names
                dataset_names = ['videos', 'frames', 'data', 'sequences']
            else:
                print(f"❌ Unsupported modality for HDF5: {modality}")
                return []
            
            # Find the main dataset - prioritize 'file_data' for raw file bytes
            main_dataset = None
            
            # First check for file_data which contains raw file bytes
            if 'file_data' in hdf5_file:
                main_dataset = hdf5_file['file_data']
                print(f"   Using dataset: file_data (raw file bytes)")
            else:
                # Try original dataset names
                for dataset_name in dataset_names:
                    if dataset_name in hdf5_file:
                        main_dataset = hdf5_file[dataset_name]
                        print(f"   Using dataset: {dataset_name}")
                        break
            
            if main_dataset is None:
                # Fallback: use the first dataset found, but skip metadata-only datasets
                available_keys = list(hdf5_file.keys())
                # Filter out common metadata/extension datasets
                metadata_keys = ['extensions', 'metadata', 'info', 'labels', 'keys', '__key__']
                data_keys = [k for k in available_keys if k not in metadata_keys]
                
                if data_keys:
                    main_dataset = hdf5_file[data_keys[0]]
                    print(f"   Using dataset: {data_keys[0]}")
                elif available_keys:
                    # If only metadata keys available, the file structure is not supported
                    print(f"   ❌ Only metadata datasets found in {Path(hdf5_path).name}: {available_keys}")
                    return []
                else:
                    print(f"   ❌ No datasets found in {Path(hdf5_path).name}")
                    return []
            
            # Get dataset info
            if hasattr(main_dataset, 'shape'):
                total_samples = main_dataset.shape[0] if len(main_dataset.shape) > 0 else 1
                print(f"   Dataset shape: {main_dataset.shape}")
            else:
                # Handle group datasets
                if hasattr(main_dataset, 'keys'):
                    total_samples = len(list(main_dataset.keys()))
                else:
                    total_samples = 1
            
            # Create sample references with sampling strategy
            if max_files is not None and total_samples > max_files:
                # Sample evenly across the dataset
                import random
                sample_indices = sorted(random.sample(range(total_samples), max_files))
                print(f"   🎯 Sampling {max_files} from {total_samples} available samples")
                
                for i, sample_idx in enumerate(sample_indices):
                    sample_key = f"{Path(hdf5_path).stem}_{i:06d}"
                    samples.append((sample_key, hdf5_path, sample_idx))  # Use original index for lazy loading
            else:
                # Use all samples or as many as requested
                num_samples = min(total_samples, max_files) if max_files else total_samples
                print(f"   ✅ Using all {num_samples} available samples")
                
                for i in range(num_samples):
                    sample_key = f"{Path(hdf5_path).stem}_{i:06d}"
                    samples.append((sample_key, hdf5_path, i))  # Include index for lazy loading
                
        print(f"   ✅ Found {len(samples)} {modality} samples in {Path(hdf5_path).name}")
        
    except Exception as e:
        print(f"   ❌ Failed to load HDF5 file {Path(hdf5_path).name}: {str(e)}")
    
    return samples


def get_modality_workers_per_gpu(modality: str) -> int:
    """
    Get the recommended number of workers per GPU for different modalities
    
    Args:
        modality: Target modality ('audio', 'image', 'video')
        
    Returns:
        Number of workers that can efficiently run per GPU
    """
    modality_workers = {
        'audio': 8,   # Audio processing is memory efficient
        'image': 8,   # Image processing needs more VRAM
        'video': 4    # Video processing is VRAM intensive
    }
    return modality_workers.get(modality, 1)  # Default to 1 for unknown modalities


def get_optimal_worker_config(target_modality: str, requested_workers: int, available_gpus: int) -> Tuple[int, List[int]]:
    """
    Calculate optimal number of workers and their GPU assignments based on modality
    
    Args:
        target_modality: Target modality ('audio', 'image', 'video')
        requested_workers: Number of workers requested by user
        available_gpus: Number of available GPUs
        
    Returns:
        Tuple of (actual_workers, gpu_assignments)
    """
    if available_gpus == 0:
        # CPU only processing
        return requested_workers, [None] * requested_workers
    
    workers_per_gpu = get_modality_workers_per_gpu(target_modality)
    max_workers = available_gpus * workers_per_gpu
    
    # Use the minimum of requested workers and what we can efficiently support
    actual_workers = min(requested_workers, max_workers)
    
    # If user requested more workers than optimal, warn them
    if requested_workers > max_workers:
        print(f"⚠️ Requested {requested_workers} workers, but {target_modality} modality supports max {max_workers} workers")
        print(f"   ({available_gpus} GPUs × {workers_per_gpu} workers/GPU = {max_workers} max workers)")
        print(f"   Using {actual_workers} workers for optimal performance")
    
    # Assign workers to GPUs
    gpu_assignments = []
    for i in range(actual_workers):
        gpu_id = i % available_gpus
        gpu_assignments.append(gpu_id)
    
    return actual_workers, gpu_assignments


def get_gpu_assignments(num_workers: int, available_gpus: int) -> List[int]:
    """
    Assign GPU device IDs to workers (legacy function for backward compatibility)
    
    Args:
        num_workers: Number of parallel workers requested
        available_gpus: Number of available GPUs
        
    Returns:
        List of GPU device IDs for each worker
    """
    if available_gpus == 0:
        return [None] * num_workers  # CPU processing
    
    # Distribute workers across available GPUs
    gpu_assignments = []
    for i in range(num_workers):
        gpu_id = i % available_gpus
        gpu_assignments.append(gpu_id)
    
    return gpu_assignments


def process_samples_parallel(all_samples: List[Tuple], 
                           benchmark_function: callable,
                           config: BenchmarkConfig, 
                           target_modality: str,
                           available_gpus: int) -> Tuple[List[BenchmarkResult], int, int]:
    """
    Process samples in parallel across multiple GPUs
    
    Args:
        all_samples: List of sample tuples (sample_key, data/path, index)
        benchmark_function: Function to benchmark each sample
        config: BenchmarkConfig object
        target_modality: Target modality for processing
        available_gpus: Number of available GPUs
        
    Returns:
        Tuple of (results_list, successful_count, failed_count)
    """
    results = []
    successful_count = 0
    failed_count = 0
    
    # Calculate optimal worker configuration based on modality
    actual_workers, gpu_assignments = get_optimal_worker_config(target_modality, config.num_gpus, available_gpus)
    
    print(f"🎯 Target modality: {target_modality} ({get_modality_workers_per_gpu(target_modality)} workers/GPU)")
    print(f"🎯 GPU assignments: {gpu_assignments}")
    print(f"📦 Processing {len(all_samples)} samples with {actual_workers} worker{'s' if actual_workers > 1 else ''}")
    
    # Process samples with multiprocessing
    if actual_workers > 1:
        print(f"🔀 Using {actual_workers} parallel workers...")
        
        # Create per-worker configurations
        worker_configs = []
        for worker_id, gpu_id in enumerate(gpu_assignments):
            worker_config = BenchmarkConfig(
                folder_path=config.folder_path,
                modality=config.modality,
                output_file=config.output_file,
                num_gpus=1,  # Each worker handles 1 assigned GPU
                device=config.device,
                num_runs=config.num_runs,
                max_files=config.max_files,
                file_extensions=config.file_extensions,
                model_config=config.model_config,
                gpu_id=gpu_id,
                webdataset_modality=getattr(config, 'webdataset_modality', 'audio'),
                hdf5_modality=getattr(config, 'hdf5_modality', 'audio'),
            )
            worker_configs.append(worker_config)
        
        # Distribute samples among workers
        samples_per_worker = len(all_samples) // actual_workers
        remaining_samples = len(all_samples) % actual_workers
        
        benchmark_args = []
        sample_idx = 0
        
        for worker_id, worker_config in enumerate(worker_configs):
            # Calculate number of samples for this worker
            worker_samples = samples_per_worker + (1 if worker_id < remaining_samples else 0)
            
            # Assign samples to this worker
            for _ in range(worker_samples):
                if sample_idx < len(all_samples):
                    sample_tuple = all_samples[sample_idx]
                    benchmark_args.append((sample_tuple, worker_config, target_modality))
                    sample_idx += 1
        
        with ProcessPoolExecutor(max_workers=actual_workers) as executor:
            # Submit all jobs
            futures = {
                executor.submit(benchmark_function, args): args[0] 
                for args in benchmark_args
            }
            
            # Process completed jobs with progress tracking
            completed_count = 0
            for future in as_completed(futures):
                sample_tuple = futures[future]
                sample_key = sample_tuple[0] if isinstance(sample_tuple, tuple) else str(sample_tuple)
                completed_count += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        successful_count += 1
                        status = f"✅ {result.speedup_factor:.1f}x speedup"
                    else:
                        failed_count += 1
                        status = f"❌ {result.error[:50]}..." if result.error else "❌ Unknown error"
                    
                    # Enhanced progress reporting for parallel processing
                    progress_percent = (completed_count / len(all_samples)) * 100
                    print(f"   [{completed_count}/{len(all_samples)} ({progress_percent:.1f}%)] {sample_key}: {status}")
                    
                except Exception as e:
                    failed_count += 1
                    progress_percent = (completed_count / len(all_samples)) * 100
                    print(f"   [{completed_count}/{len(all_samples)} ({progress_percent:.1f}%)] {sample_key}: ❌ {str(e)}")
                    
                    # Create error result
                    results.append(BenchmarkResult(
                        file_path=sample_key,
                        file_size_mb=0.0,
                        file_duration_or_pixels=0.0,
                        car_size_mb=0.0,
                        generation_time_ms=0.0,
                        loading_time_ms=0.0,
                        speedup_factor=0.0,
                        time_savings_ms=0.0,
                        compression_ratio=0.0,
                        success=False,
                        error=str(e),
                        metadata={}
                    ))
    else:
        print("🔄 Using single worker processing...")
        
        # Create single worker configuration
        single_worker_config = BenchmarkConfig(
            folder_path=config.folder_path,
            modality=config.modality,
            output_file=config.output_file,
            num_gpus=1,
            device=config.device,
            num_runs=config.num_runs,
            max_files=config.max_files,
            file_extensions=config.file_extensions,
            model_config=config.model_config,
            gpu_id=gpu_assignments[0] if gpu_assignments[0] is not None else None,
            webdataset_modality=getattr(config, 'webdataset_modality', 'audio'),
            hdf5_modality=getattr(config, 'hdf5_modality', 'audio'),
        )
        
        # Process samples sequentially
        for i, sample_tuple in enumerate(all_samples):
            sample_key = sample_tuple[0] if isinstance(sample_tuple, tuple) else str(sample_tuple)
            
            try:
                args = (sample_tuple, single_worker_config, target_modality)
                result = benchmark_function(args)
                results.append(result)
                
                if result.success:
                    successful_count += 1
                    status = f"✅ {result.speedup_factor:.1f}x speedup"
                else:
                    failed_count += 1
                    status = f"❌ {result.error[:50]}..." if result.error else "❌ Unknown error"
                
                print(f"   [{i+1}/{len(all_samples)}] {sample_key}: {status}")
                
            except Exception as e:
                failed_count += 1
                print(f"   [{i+1}/{len(all_samples)}] {sample_key}: ❌ {str(e)}")
                
                results.append(BenchmarkResult(
                    file_path=sample_key,
                    file_size_mb=0.0,
                    file_duration_or_pixels=0.0,
                    car_size_mb=0.0,
                    generation_time_ms=0.0,
                    loading_time_ms=0.0,
                    speedup_factor=0.0,
                    time_savings_ms=0.0,
                    compression_ratio=0.0,
                    success=False,
                    error=str(e),
                    metadata={}
                ))
    
    return results, successful_count, failed_count


def find_media_files(folder_path: str, modality: str, max_files: Optional[int] = None, 
                    file_extensions: Optional[List[str]] = None) -> List[str]:
    """
    Recursively find all media files of specified modality, including webdataset and HDF5 files
    
    Args:
        folder_path: Root folder to search
        modality: 'audio', 'image', 'video', 'webdataset', or 'hdf5'
        max_files: Maximum number of files to return (None for no limit)
        file_extensions: Custom file extensions (None for defaults)
    
    Returns:
        List of file paths (for regular files) or sample identifiers (for webdataset/HDF5)
    """
    extensions = file_extensions or EXTENSIONS[modality]
    extensions = [ext.lower() for ext in extensions]
    
    media_files = []
    folder_path = Path(folder_path)
    
    print(f"🔍 Scanning {folder_path} for {modality} files...")
    print(f"   Looking for extensions: {extensions}")
    
    # Handle webdataset format
    if modality == 'webdataset':
        # Find tar files and extract samples
        webdataset_extensions = EXTENSIONS['webdataset']
        for ext in webdataset_extensions:
            pattern = f"**/*{ext}"
            for tar_path in folder_path.rglob(pattern):
                if tar_path.is_file():
                    # For webdataset, we need to specify the target modality
                    # This should be passed as a parameter or inferred
                    print(f"📦 Found webdataset: {tar_path}")
                    media_files.append(str(tar_path))
                    
                    if max_files and len(media_files) >= max_files:
                        print(f"   Reached max_files limit ({max_files})")
                        return media_files
    
    # Handle HDF5 format
    elif modality == 'hdf5':
        # Find HDF5 files
        hdf5_extensions = EXTENSIONS['hdf5']
        for ext in hdf5_extensions:
            pattern = f"**/*{ext}"
            for hdf5_path in folder_path.rglob(pattern):
                if hdf5_path.is_file():
                    print(f"📊 Found HDF5 file: {hdf5_path}")
                    media_files.append(str(hdf5_path))
                    
                    if max_files and len(media_files) >= max_files:
                        print(f"   Reached max_files limit ({max_files})")
                        return media_files
    
    else:
        # Handle regular media files
        # Use Path.rglob for recursive search
        for ext in extensions:
            pattern = f"**/*{ext}"
            for file_path in folder_path.rglob(pattern):
                if file_path.is_file():
                    media_files.append(str(file_path))
                    
                    if max_files and len(media_files) >= max_files:
                        print(f"   Reached max_files limit ({max_files})")
                        return media_files
        
        # Also check uppercase extensions
        for ext in [e.upper() for e in extensions]:
            pattern = f"**/*{ext}"
            for file_path in folder_path.rglob(pattern):
                if file_path.is_file() and str(file_path) not in media_files:
                    media_files.append(str(file_path))
                    
                    if max_files and len(media_files) >= max_files:
                        print(f"   Reached max_files limit ({max_files})")
                        return media_files
    
    print(f"✅ Found {len(media_files)} {modality} files")
    return sorted(media_files)


def get_file_duration_or_size(file_path: str, modality: str) -> Tuple[float, Dict[str, Any]]:
    """
    Get file duration (for audio/video) or pixel count (for images)
    
    Returns:
        (duration_or_pixels, metadata_dict)
    """
    metadata = {}
    
    try:
        if modality == 'audio':
            import librosa
            audio_data, sr = librosa.load(file_path, sr=None)
            duration = len(audio_data) / sr
            metadata = {
                'sample_rate': sr,
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[0],
                'samples': len(audio_data)
            }
            return duration, metadata
            
        elif modality == 'image':
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.size
                pixels = width * height
                metadata = {
                    'width': width,
                    'height': height,
                    'mode': img.mode,
                    'format': img.format
                }
                return pixels, metadata
                
        elif modality == 'video':
            import subprocess
            import json as json_module
            
            # Get video info using ffprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json_module.loads(result.stdout)
            
            # Extract duration and video stream info
            duration = float(info['format']['duration'])
            
            video_stream = next(
                (s for s in info['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if video_stream:
                metadata = {
                    'duration': duration,
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'codec': video_stream.get('codec_name', 'unknown')
                }
            else:
                metadata = {'duration': duration}
            
            return duration, metadata
            
    except Exception as e:
        print(f"⚠️ Could not get metadata for {file_path}: {e}")
        return 0.0, {'error': str(e)}


def load_base_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load base metadata from JSON file with same name as media file
    
    Args:
        file_path: Path to media file
        
    Returns:
        Base metadata dictionary if JSON file exists, None otherwise
    """
    try:
        # Create JSON file path by replacing extension
        json_path = str(Path(file_path).with_suffix('.json'))
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                base_metadata = json.load(f)
                print(f"  📄 Loaded base metadata from {Path(json_path).name}")
                return base_metadata
        else:
            return None
            
    except Exception as e:
        print(f"⚠️ Failed to load base metadata for {file_path}: {e}")
        return None


def benchmark_webdataset_sample(args: Tuple[Tuple[str, Any], BenchmarkConfig, str]) -> BenchmarkResult:
    """
    Benchmark a single webdataset sample with multi-format support
    
    This measures file size and loading time for all four formats:
    1. CAR format (original)
    2. HDF5 format 
    3. WebDataset format
    
    Args:
        args: ((sample_key, sample_data), config, target_modality) tuple for multiprocessing
        
    Returns:
        BenchmarkResult object with multi-format results
    """
    (sample_key, sample_data), config, target_modality = args
    
    import tempfile
    import os
    import time
    from pathlib import Path
    
    temp_files = []  # Track temporary files for cleanup
    
    try:
        # Extract the actual media data and metadata
        if target_modality == 'audio':
            media_data, metadata = sample_data[0], sample_data[1] if len(sample_data) > 1 else {}
        elif target_modality == 'image':
            media_data, metadata = sample_data[0], sample_data[1] if len(sample_data) > 1 else {}
        elif target_modality == 'video':
            media_data, metadata = sample_data[0], sample_data[1] if len(sample_data) > 1 else {}
        else:
            raise ValueError(f"Unsupported target modality: {target_modality}")
        
        # Parse JSON metadata if it's in bytes format (from webdataset)
        if isinstance(metadata, bytes):
            try:
                import json
                metadata = json.loads(metadata.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                print(f"⚠️ Failed to parse JSON metadata for {sample_key}")
                metadata = {}
        
        # Clean metadata to remove any bytes objects that could cause issues
        clean_metadata = {}
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if not isinstance(value, bytes):  # Skip bytes objects
                    clean_metadata[key] = value
        
        # Determine device string (include GPU ID if specified)
        if config.gpu_id is not None and config.device.startswith('cuda'):
            device_str = f"cuda:{config.gpu_id}"
        else:
            device_str = config.device
        
        # Initialize processor based on modality
        if target_modality == 'audio':
            processor_config = AudioConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['audio'], **(config.model_config or {})}
            )
            processor = AudioProcessor(processor_config)
            
        elif target_modality == 'image':
            processor_config = ImageConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['image'], **(config.model_config or {})}
            )
            processor = CosmosImageProcessor(processor_config)
            
        elif target_modality == 'video':
            processor_config = VideoConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['video'], **(config.model_config or {})}
            )
            processor = CosmosVideoProcessor(processor_config)
        
        # Create temporary media file from webdataset data
        if target_modality == 'audio':
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_media_path = temp_file.name
                temp_file.write(media_data)
            temp_files.append(temp_media_path)
            
        elif target_modality == 'image':
            from PIL import Image
            import numpy as np
            
            # Handle different image data formats from WebDataset
            if isinstance(media_data, bytes):
                # Raw image bytes (JPEG, PNG, etc.)
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_media_path = temp_file.name
                    temp_file.write(media_data)
                temp_files.append(temp_media_path)
                
            elif hasattr(media_data, 'save'):
                # PIL Image object
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_media_path = temp_file.name
                temp_files.append(temp_media_path)
                media_data.save(temp_media_path, 'PNG')
                
            elif hasattr(media_data, 'shape'):
                # Tensor or numpy array
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_media_path = temp_file.name
                temp_files.append(temp_media_path)
                
                if hasattr(media_data, 'numpy'):
                    img_array = media_data.numpy()
                else:
                    img_array = np.array(media_data)
                
                # Handle different array shapes and dtypes
                if len(img_array.shape) == 4 and img_array.shape[0] == 1:
                    # Remove batch dimension (1, H, W, C) -> (H, W, C)
                    img_array = img_array.squeeze(0)
                elif len(img_array.shape) == 3 and img_array.shape[0] in [1, 3]:
                    # Convert from (C, H, W) to (H, W, C) if needed
                    if img_array.shape[0] in [1, 3] and img_array.shape[0] < img_array.shape[1]:
                        img_array = np.transpose(img_array, (1, 2, 0))
                
                # Handle different dtype ranges
                if img_array.dtype == np.float32 or img_array.dtype == np.float64:
                    if img_array.max() <= 1.0:
                        img_array = (img_array * 255).astype(np.uint8)
                    else:
                        img_array = img_array.astype(np.uint8)
                elif img_array.dtype != np.uint8:
                    img_array = img_array.astype(np.uint8)
                
                # Handle grayscale vs RGB
                if len(img_array.shape) == 2:
                    # Grayscale
                    pil_image = Image.fromarray(img_array, mode='L')
                elif len(img_array.shape) == 3:
                    if img_array.shape[2] == 1:
                        # Grayscale with channel dimension
                        pil_image = Image.fromarray(img_array.squeeze(2), mode='L')
                    elif img_array.shape[2] == 3:
                        # RGB
                        pil_image = Image.fromarray(img_array, mode='RGB')
                    elif img_array.shape[2] == 4:
                        # RGBA
                        pil_image = Image.fromarray(img_array, mode='RGBA')
                    else:
                        raise ValueError(f"Unsupported image channels: {img_array.shape[2]}")
                else:
                    raise ValueError(f"Unsupported image shape: {img_array.shape}")
                
                pil_image.save(temp_media_path, 'PNG')
                
            else:
                raise ValueError(f"Unsupported image data type: {type(media_data)}")
                
        elif target_modality == 'video':
            import cv2
            import numpy as np
            
            # Handle different video data formats from WebDataset
            if isinstance(media_data, bytes):
                # Raw video bytes (MP4, AVI, etc.)
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    temp_media_path = temp_file.name
                    temp_file.write(media_data)
                temp_files.append(temp_media_path)
                
            elif hasattr(media_data, 'shape'):
                # Tensor or numpy array
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    temp_media_path = temp_file.name
                temp_files.append(temp_media_path)
                
                # Convert to numpy array
                if hasattr(media_data, 'numpy'):
                    video_array = media_data.numpy()
                else:
                    video_array = np.array(media_data)
                
                # Handle different video array shapes
                if len(video_array.shape) == 5 and video_array.shape[0] == 1:
                    # Remove batch dimension (1, T, H, W, C) -> (T, H, W, C)
                    video_array = video_array.squeeze(0)
                elif len(video_array.shape) == 4:
                    # Handle (T, H, W, C) or (T, C, H, W)
                    if video_array.shape[1] <= 4 and video_array.shape[1] < video_array.shape[2]:
                        # Convert from (T, C, H, W) to (T, H, W, C)
                        video_array = np.transpose(video_array, (0, 2, 3, 1))
                elif len(video_array.shape) == 3:
                    # Single frame or grayscale video (H, W, C) or (T, H, W)
                    if video_array.shape[0] < video_array.shape[1]:
                        # Likely (T, H, W) grayscale - add channel dimension
                        video_array = np.expand_dims(video_array, axis=-1)
                    else:
                        # Single frame (H, W, C) - add time dimension
                        video_array = np.expand_dims(video_array, axis=0)
                else:
                    raise ValueError(f"Unsupported video shape: {video_array.shape}")
                
                # Ensure we have (T, H, W, C) format
                if len(video_array.shape) != 4:
                    raise ValueError(f"Expected 4D video array (T, H, W, C), got {video_array.shape}")
                
                # Handle different dtype ranges
                if video_array.dtype == np.float32 or video_array.dtype == np.float64:
                    if video_array.max() <= 1.0:
                        video_array = (video_array * 255).astype(np.uint8)
                    else:
                        video_array = video_array.astype(np.uint8)
                elif video_array.dtype != np.uint8:
                    video_array = video_array.astype(np.uint8)
                
                # Get video properties
                num_frames, height, width, channels = video_array.shape
                fps = metadata.get('fps', 30)
                
                # Handle grayscale vs RGB
                if channels == 1:
                    # Convert grayscale to BGR for OpenCV
                    video_array = np.repeat(video_array, 3, axis=-1)
                elif channels == 3:
                    # RGB to BGR for OpenCV
                    video_array = video_array[:, :, :, ::-1]  # RGB -> BGR
                elif channels == 4:
                    # RGBA to BGR (ignore alpha)
                    video_array = video_array[:, :, :, :3][:, :, :, ::-1]  # RGBA -> BGR
                else:
                    raise ValueError(f"Unsupported video channels: {channels}")
                
                # Write video using OpenCV
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_media_path, fourcc, fps, (width, height))
                
                for frame_idx in range(num_frames):
                    frame = video_array[frame_idx]
                    out.write(frame)
                
                out.release()
                
            else:
                raise ValueError(f"Unsupported video data type: {type(media_data)}")
        
        # Calculate original file size and duration/pixels
        file_size_mb = os.path.getsize(temp_media_path) / (1024 * 1024)
        
        if target_modality == 'audio':
            try:
                import torchaudio
                info = torchaudio.info(temp_media_path)
                duration_or_pixels = info.num_frames / info.sample_rate
            except:
                duration_or_pixels = metadata.get('duration', 10.0)
        elif target_modality == 'image':
            from PIL import Image
            with Image.open(temp_media_path) as img:
                width, height = img.size
                duration_or_pixels = width * height
        elif target_modality == 'video':
            try:
                import cv2
                cap = cv2.VideoCapture(temp_media_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration_or_pixels = frame_count / fps if fps > 0 else metadata.get('duration', 5.0)
                cap.release()
            except:
                duration_or_pixels = metadata.get('duration', 5.0)
        
        # Process the file once to generate all formats
        # Generate output paths for all formats
        base_output_path = temp_media_path.replace(Path(temp_media_path).suffix, '')
        output_paths = {
            'car': f"{base_output_path}.car",
            'hdf5': f"{base_output_path}.h5", 
            'webdataset': f"{base_output_path}.tar",
        }
        
        # Add output files to cleanup list
        for path in output_paths.values():
            temp_files.append(path)
        
        # Process file ONCE to generate all formats
        generation_start = time.perf_counter()
        result = processor.process_single_file(temp_media_path, output_paths['car'], clean_metadata)
        generation_time_ms = (time.perf_counter() - generation_start) * 1000
        
        if result['status'] != 'success':
            raise Exception(f"Processing failed: {result.get('error', 'Unknown error')}")
        
        # Measure file sizes for all formats
        format_results = {}
        car_size_mb = 0.0
        
        for format_name, file_path in output_paths.items():
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                format_results[format_name] = {'size_mb': size_mb, 'loading_times': []}
                
                if format_name == 'car':
                    car_size_mb = size_mb
            else:
                print(f"⚠️ {format_name} file not created: {file_path}")
                format_results[format_name] = {'size_mb': 0.0, 'loading_times': []}
        
        # Benchmark loading times for all formats
        # Include one extra run for warm-up (will be discarded)
        total_runs = config.num_runs + 1
        
        for run in range(total_runs):
            is_warmup = (run == 0)
            
            # Benchmark each format's loading time
            for format_name, file_path in output_paths.items():
                if not os.path.exists(file_path):
                    continue
                    
                try:
                    start_time = time.perf_counter()
                    
                    # Load from specific format
                    if format_name == 'car':
                        processor.load_from_car(file_path)
                    else:
                        # For other formats, we simulate loading by reading the file
                        # since the processors don't have format-specific loading methods yet
                        with open(file_path, 'rb') as f:
                            f.read()
                    
                    loading_time = (time.perf_counter() - start_time) * 1000
                    
                    # Skip warm-up run
                    if not is_warmup:
                        format_results[format_name]['loading_times'].append(loading_time)
                        
                except Exception as e:
                    print(f"⚠️ {format_name} loading failed for {sample_key}: {e}")
                    continue
        
        # Calculate average loading times for each format
        for format_name in format_results:
            loading_times = format_results[format_name]['loading_times']
            if loading_times:
                avg_loading_time = sum(loading_times) / len(loading_times)
                format_results[format_name]['avg_loading_time_ms'] = avg_loading_time
            else:
                format_results[format_name]['avg_loading_time_ms'] = 0.0
        
        # Calculate overall metrics (using CAR as baseline)
        car_loading_times = format_results.get('car', {}).get('loading_times', [])
        if car_loading_times:
            avg_car_loading = sum(car_loading_times) / len(car_loading_times)
            speedup_factor = generation_time_ms / avg_car_loading if avg_car_loading > 0 else 0.0
            time_savings = generation_time_ms - avg_car_loading
        else:
            avg_car_loading = 0.0
            speedup_factor = 0.0
            time_savings = 0.0
        
        compression_ratio = file_size_mb / car_size_mb if car_size_mb > 0 else 0.0
        
        # Clean up format results for cleaner output
        clean_format_results = {}
        for format_name, results in format_results.items():
            clean_format_results[format_name] = {
                'size_mb': results['size_mb'],
                'loading_time_ms': results['avg_loading_time_ms']
            }
        
        return BenchmarkResult(
            file_path=sample_key,
            file_size_mb=file_size_mb,
            file_duration_or_pixels=duration_or_pixels,
            car_size_mb=car_size_mb,
            generation_time_ms=generation_time_ms,
            loading_time_ms=avg_car_loading,
            speedup_factor=speedup_factor,
            time_savings_ms=time_savings,
            compression_ratio=compression_ratio,
            success=True,
            error=None,
            metadata={
                **clean_metadata,
                'workflow': 'webdataset_multiformat_benchmark',
                'processing_type': 'multi_format_comparison',
                'formats_tested': list(format_results.keys())
            },
            format_results=clean_format_results
        )
        
    except Exception as e:
        return BenchmarkResult(
            file_path=sample_key,
            file_size_mb=0.0,
            file_duration_or_pixels=0.0,
            car_size_mb=0.0,
            generation_time_ms=0.0,
            loading_time_ms=0.0,
            speedup_factor=0.0,
            time_savings_ms=0.0,
            compression_ratio=0.0,
            success=False,
            error=f"Multi-format benchmark failed: {str(e)}\n{traceback.format_exc()}",
            metadata={},
            format_results={}
        )
    finally:
        # Clean up all temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass


def benchmark_hdf5_sample(args: Tuple[Tuple[str, str, int], BenchmarkConfig, str]) -> BenchmarkResult:
    """
    Benchmark a single HDF5 sample with multi-format support
    
    This measures file size and loading time for all four formats:
    1. CAR format (original)
    2. HDF5 format 
    3. WebDataset format
    
    Args:
        args: ((sample_key, hdf5_path, index), config, target_modality) tuple for multiprocessing
        
    Returns:
        BenchmarkResult object with multi-format results
    """
    (sample_key, hdf5_path, index), config, target_modality = args
    
    import tempfile
    import os
    import time
    from pathlib import Path
    
    temp_files = []  # Track temporary files for cleanup
    
    try:
        import h5py
        
        # Lazy load the specific sample
        with h5py.File(hdf5_path, 'r') as hdf5_file:
            # Find the dataset (same logic as in find_hdf5_samples)
            if target_modality == 'audio':
                dataset_names = ['audio', 'waveforms', 'data', 'samples']
            elif target_modality == 'image':
                dataset_names = ['images', 'data', 'pixels', 'frames']
            elif target_modality == 'video':
                dataset_names = ['videos', 'frames', 'data', 'sequences']
            else:
                raise ValueError(f"Unsupported target modality: {target_modality}")
            
            # Find the main dataset - prioritize 'file_data' for raw file bytes
            main_dataset = None
            
            # First check for file_data which contains raw file bytes
            if 'file_data' in hdf5_file:
                main_dataset = hdf5_file['file_data']
            else:
                # Try original dataset names
                for dataset_name in dataset_names:
                    if dataset_name in hdf5_file:
                        main_dataset = hdf5_file[dataset_name]
                        break
            
            if main_dataset is None:
                available_keys = list(hdf5_file.keys())
                # Filter out common metadata/extension datasets
                metadata_keys = ['extensions', 'metadata', 'info', 'labels', 'keys', '__key__']
                data_keys = [k for k in available_keys if k not in metadata_keys]
                
                if data_keys:
                    main_dataset = hdf5_file[data_keys[0]]
                elif available_keys:
                    # If only metadata keys available, the file structure is not supported
                    raise ValueError(f"Only metadata datasets found in HDF5 file: {available_keys}")
                else:
                    raise ValueError("No datasets found in HDF5 file")
            
            # Load the specific sample
            if hasattr(main_dataset, 'shape') and len(main_dataset.shape) > 0:
                sample_data = main_dataset[index]
            else:
                # Handle group datasets
                keys = list(main_dataset.keys())
                if index < len(keys):
                    sample_data = main_dataset[keys[index]][...]
                else:
                    raise IndexError(f"Index {index} out of range")
            
            # Get metadata from attributes if available
            metadata = dict(main_dataset.attrs) if hasattr(main_dataset, 'attrs') else {}
            
        # Clean metadata to remove any bytes objects that could cause issues
        clean_metadata = {}
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if not isinstance(value, bytes):  # Skip bytes objects
                    clean_metadata[key] = value
        
        # Calculate sample info - handle raw file bytes for HDF5 format
        if isinstance(sample_data, bytes) or (hasattr(sample_data, 'dtype') and sample_data.dtype == 'object'):
            # Raw file bytes (FLAC/MP4/PNG data)
            if isinstance(sample_data, bytes):
                file_size_mb = len(sample_data) / (1024 * 1024)
            else:
                file_size_mb = len(bytes(sample_data)) / (1024 * 1024)
            
            # Try to get metadata for duration/pixels
            if target_modality == 'audio':
                duration_or_pixels = clean_metadata.get('duration_seconds', 10.0)  # Default fallback
            elif target_modality == 'image':
                duration_or_pixels = clean_metadata.get('width', 256) * clean_metadata.get('height', 256)
            elif target_modality == 'video':
                duration_or_pixels = clean_metadata.get('duration_seconds', 10.0)
        elif hasattr(sample_data, 'shape'):
            # Array data (legacy format)
            if target_modality == 'audio':
                sample_rate = metadata.get('sample_rate', 16000)
                duration_or_pixels = len(sample_data) / sample_rate
                file_size_mb = sample_data.nbytes / (1024 * 1024)
            elif target_modality == 'image':
                if len(sample_data.shape) >= 2:
                    duration_or_pixels = sample_data.shape[0] * sample_data.shape[1]
                else:
                    duration_or_pixels = sample_data.size
                file_size_mb = sample_data.nbytes / (1024 * 1024)
            elif target_modality == 'video':
                fps = metadata.get('fps', 30)
                if len(sample_data.shape) >= 3:
                    num_frames = sample_data.shape[0]
                    duration_or_pixels = num_frames / fps
                else:
                    duration_or_pixels = 1.0
                file_size_mb = sample_data.nbytes / (1024 * 1024)
        else:
            duration_or_pixels = 1.0
            file_size_mb = 0.1
        
        # Determine device string (include GPU ID if specified)
        if config.gpu_id is not None and config.device.startswith('cuda'):
            device_str = f"cuda:{config.gpu_id}"
        else:
            device_str = config.device
        
        # Initialize processor based on modality
        if target_modality == 'audio':
            processor_config = AudioConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['audio'], **(config.model_config or {})}
            )
            processor = AudioProcessor(processor_config)
            
        elif target_modality == 'image':
            processor_config = ImageConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['image'], **(config.model_config or {})}
            )
            processor = CosmosImageProcessor(processor_config)
            
        elif target_modality == 'video':
            processor_config = VideoConfig(
                device=device_str,
                **{**DEFAULT_CONFIGS['video'], **(config.model_config or {})}
            )
            processor = CosmosVideoProcessor(processor_config)
        
        # Create temporary media file from HDF5 data
        import json
        
        # Get extension and metadata for proper file handling
        with h5py.File(hdf5_path, 'r') as hdf5_file:
            if 'extensions' in hdf5_file and 'metadata' in hdf5_file:
                extension = hdf5_file['extensions'][index].decode('utf-8') if isinstance(hdf5_file['extensions'][index], bytes) else hdf5_file['extensions'][index]
                metadata_json = hdf5_file['metadata'][index].decode('utf-8') if isinstance(hdf5_file['metadata'][index], bytes) else hdf5_file['metadata'][index]
                metadata_dict = json.loads(metadata_json)
                clean_metadata.update(metadata_dict)
            else:
                # Default extensions based on modality
                if target_modality == 'audio':
                    extension = '.flac'
                elif target_modality == 'image':
                    extension = '.png'
                elif target_modality == 'video':
                    extension = '.mp4'
        
        # Create temporary file with correct extension
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_media_path = temp_file.name
            # Write raw file bytes directly 
            if isinstance(sample_data, bytes):
                temp_file.write(sample_data)
            else:
                # Convert numpy array of bytes to actual bytes
                temp_file.write(bytes(sample_data))
        
        temp_files.append(temp_media_path)
        
        # Calculate original file size and duration/pixels
        file_size_mb = os.path.getsize(temp_media_path) / (1024 * 1024)
        
        # Process the file once to generate all formats
        # Generate output paths for all formats
        base_output_path = temp_media_path.replace(Path(temp_media_path).suffix, '')
        output_paths = {
            'car': f"{base_output_path}.car",
            'hdf5': f"{base_output_path}.h5", 
            'webdataset': f"{base_output_path}.tar",
        }
        
        # Add output files to cleanup list
        for path in output_paths.values():
            temp_files.append(path)
        
        # Process file ONCE to generate all formats
        generation_start = time.perf_counter()
        result = processor.process_single_file(temp_media_path, output_paths['car'], clean_metadata)
        generation_time_ms = (time.perf_counter() - generation_start) * 1000
        
        if result['status'] != 'success':
            raise Exception(f"Processing failed: {result.get('error', 'Unknown error')}")
        
        # Get duration from result metadata or use calculated value
        duration_from_result = result.get('metadata', {}).get('duration', 0.0)
        if duration_from_result > 0.0:
            duration_or_pixels = duration_from_result
        
        # Measure file sizes for all formats
        format_results = {}
        car_size_mb = 0.0
        
        for format_name, file_path in output_paths.items():
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                format_results[format_name] = {'size_mb': size_mb, 'loading_times': []}
                
                if format_name == 'car':
                    car_size_mb = size_mb
            else:
                print(f"⚠️ {format_name} file not created: {file_path}")
                format_results[format_name] = {'size_mb': 0.0, 'loading_times': []}
        
        # Benchmark loading times for all formats
        # Include one extra run for warm-up (will be discarded)
        total_runs = config.num_runs + 1
        
        for run in range(total_runs):
            is_warmup = (run == 0)
            
            # Benchmark each format's loading time
            for format_name, file_path in output_paths.items():
                if not os.path.exists(file_path):
                    continue
                    
                try:
                    start_time = time.perf_counter()
                    
                    # Load from specific format
                    if format_name == 'car':
                        processor.load_from_car(file_path)
                    else:
                        # For other formats, we simulate loading by reading the file
                        with open(file_path, 'rb') as f:
                            f.read()
                    
                    loading_time = (time.perf_counter() - start_time) * 1000
                    
                    # Skip warm-up run
                    if not is_warmup:
                        format_results[format_name]['loading_times'].append(loading_time)
                        
                except Exception as e:
                    print(f"⚠️ {format_name} loading failed for {sample_key}: {e}")
                    continue
        
        # Calculate average loading times for each format
        for format_name in format_results:
            loading_times = format_results[format_name]['loading_times']
            if loading_times:
                avg_loading_time = sum(loading_times) / len(loading_times)
                format_results[format_name]['avg_loading_time_ms'] = avg_loading_time
            else:
                format_results[format_name]['avg_loading_time_ms'] = 0.0
        
        # Calculate overall metrics (using CAR as baseline)
        car_loading_times = format_results.get('car', {}).get('loading_times', [])
        if car_loading_times:
            avg_car_loading = sum(car_loading_times) / len(car_loading_times)
            speedup_factor = generation_time_ms / avg_car_loading if avg_car_loading > 0 else 0.0
            time_savings = generation_time_ms - avg_car_loading
        else:
            avg_car_loading = 0.0
            speedup_factor = 0.0
            time_savings = 0.0
        
        compression_ratio = file_size_mb / car_size_mb if car_size_mb > 0 else 0.0
        
        # Clean up format results for cleaner output
        clean_format_results = {}
        for format_name, results in format_results.items():
            clean_format_results[format_name] = {
                'size_mb': results['size_mb'],
                'loading_time_ms': results['avg_loading_time_ms']
            }
        
        return BenchmarkResult(
            file_path=sample_key,
            file_size_mb=file_size_mb,
            file_duration_or_pixels=duration_or_pixels,
            car_size_mb=car_size_mb,
            generation_time_ms=generation_time_ms,
            loading_time_ms=avg_car_loading,
            speedup_factor=speedup_factor,
            time_savings_ms=time_savings,
            compression_ratio=compression_ratio,
            success=True,
            error=None,
            metadata={
                **clean_metadata,
                'workflow': 'hdf5_multiformat_benchmark',
                'processing_type': 'multi_format_comparison',
                'formats_tested': list(format_results.keys())
            },
            format_results=clean_format_results
        )
        
    except Exception as e:
        return BenchmarkResult(
            file_path=sample_key,
            file_size_mb=0.0,
            file_duration_or_pixels=0.0,
            car_size_mb=0.0,
            generation_time_ms=0.0,
            loading_time_ms=0.0,
            speedup_factor=0.0,
            time_savings_ms=0.0,
            compression_ratio=0.0,
            success=False,
            error=f"Multi-format benchmark failed: {str(e)}\n{traceback.format_exc()}",
            metadata={},
            format_results={}
        )
    finally:
        # Clean up all temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass



# End of multi-format benchmark functions
def benchmark_single_file(args: Tuple[str, BenchmarkConfig]) -> BenchmarkResult:
    """
    Benchmark a single file (generation vs CAR loading)
    Designed to run in separate process
    
    Args:
        args: (file_path, config) tuple for multiprocessing
    
    Returns:
        BenchmarkResult object
    """
    file_path, config = args
    
    try:
        # Get file info
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        duration_or_pixels, metadata = get_file_duration_or_size(file_path, config.modality)
        
        # Load base metadata if available
        base_metadata = load_base_metadata(file_path)
        
        # Determine device string (include GPU ID if specified)
        if config.gpu_id is not None and config.device.startswith('cuda'):
            device_str = f"cuda:{config.gpu_id}"
        else:
            device_str = config.device
        
        # Generate CAR file using carlib functions
        car_path = str(Path(file_path).with_suffix('.car'))
        output_dir = str(Path(car_path).parent)
        
        # Combine model config with device info
        model_config_with_device = {**DEFAULT_CONFIGS[config.modality], **(config.model_config or {})}
        if device_str != "auto":
            model_config_with_device['device'] = device_str
        
        # Try to use carlib functions first, fallback to direct processors
        result = benchmark_single_file_with_carlib(
            file_path=file_path,
            output_path=output_dir,
            modality=config.modality,
            target_modality=config.modality,
            model_config=model_config_with_device,
            metadata=base_metadata
        )
        
        if result is None:
            # Fallback to direct processor usage
            if config.modality == 'audio':
                processor_config = AudioConfig(
                    device=device_str,
                    **model_config_with_device
                )
                processor = AudioProcessor(processor_config)
                
            elif config.modality == 'image':
                processor_config = ImageConfig(
                    device=device_str,
                    **model_config_with_device
                )
                processor = CosmosImageProcessor(processor_config)
                
            elif config.modality == 'video':
                processor_config = VideoConfig(
                    device=device_str,
                    **model_config_with_device
                )
                processor = CosmosVideoProcessor(processor_config)
            
            # Process file to generate CAR (fallback method)
            result = processor.process_single_file(file_path, car_path, base_metadata)
        
        if result['status'] != 'success':
            return BenchmarkResult(
                file_path=file_path,
                file_size_mb=file_size_mb,
                file_duration_or_pixels=duration_or_pixels,
                car_size_mb=0.0,
                generation_time_ms=0.0,
                loading_time_ms=0.0,
                speedup_factor=0.0,
                time_savings_ms=0.0,
                compression_ratio=0.0,
                success=False,
                error=f"CAR generation failed: {result.get('error')}",
                metadata=metadata
            )
        
        car_size_mb = os.path.getsize(car_path) / (1024 * 1024)
        compression_ratio = file_size_mb / car_size_mb if car_size_mb > 0 else 0.0
        
        # Benchmark generation vs loading (with warm-up run)
        generation_times = []
        loading_times = []
        
        # Include one extra run for warm-up (will be discarded)
        total_runs = config.num_runs + 1
        
        for run in range(total_runs):
            is_warmup = (run == 0)
            
            # Time generation
            start_time = time.perf_counter()
            try:
                if config.modality == 'audio':
                    audio, audio_metadata = processor.load_audio(file_path)
                    encoded_data = processor.encode_audio(audio, audio_metadata, base_metadata)
                elif config.modality == 'image':
                    image, image_metadata = processor.load_image(file_path)
                    encoded_data = processor.encode_image(image, image_metadata, base_metadata)
                elif config.modality == 'video':
                    frames, video_metadata = processor.load_video(file_path)
                    encoded_data = processor.encode_video(frames, video_metadata, base_metadata=base_metadata)
                
                generation_time = (time.perf_counter() - start_time) * 1000
                
                # Skip warm-up run
                if not is_warmup:
                    generation_times.append(generation_time)
                
            except Exception as e:
                print(f"⚠️ Generation failed for {file_path}: {e}")
                continue
            
            # Time CAR loading using carlib functions
            try:
                # Try carlib loading first
                car_load_result = load_car_with_carlib(car_path)
                
                if car_load_result and car_load_result['status'] == 'success':
                    loading_time = car_load_result['loading_time_ms']
                else:
                    # Fallback to direct processor loading
                    start_time = time.perf_counter()
                    car_result = processor.load_from_car(car_path)
                    loading_time = (time.perf_counter() - start_time) * 1000
                
                # Skip warm-up run
                if not is_warmup:
                    loading_times.append(loading_time)
                
            except Exception as e:
                print(f"⚠️ CAR loading failed for {file_path}: {e}")
                continue
        
        # Calculate results (warm-up run excluded)
        if generation_times and loading_times:
            avg_generation = sum(generation_times) / len(generation_times)
            avg_loading = sum(loading_times) / len(loading_times)
            speedup = avg_generation / avg_loading if avg_loading > 0 else 0.0
            time_savings = avg_generation - avg_loading
            
            # Clean up CAR file
            try:
                os.remove(car_path)
            except:
                pass
            
            return BenchmarkResult(
                file_path=file_path,
                file_size_mb=file_size_mb,
                file_duration_or_pixels=duration_or_pixels,
                car_size_mb=car_size_mb,
                generation_time_ms=avg_generation,
                loading_time_ms=avg_loading,
                speedup_factor=speedup,
                time_savings_ms=time_savings,
                compression_ratio=compression_ratio,
                success=True,
                metadata=metadata
            )
        else:
            return BenchmarkResult(
                file_path=file_path,
                file_size_mb=file_size_mb,
                file_duration_or_pixels=duration_or_pixels,
                car_size_mb=car_size_mb,
                generation_time_ms=0.0,
                loading_time_ms=0.0,
                speedup_factor=0.0,
                time_savings_ms=0.0,
                compression_ratio=compression_ratio,
                success=False,
                error="No successful benchmark runs completed",
                metadata=metadata
            )
        
    except Exception as e:
        return BenchmarkResult(
            file_path=file_path,
            file_size_mb=0.0,
            file_duration_or_pixels=0.0,
            car_size_mb=0.0,
            generation_time_ms=0.0,
            loading_time_ms=0.0,
            speedup_factor=0.0,
            time_savings_ms=0.0,
            compression_ratio=0.0,
            success=False,
            error=f"Benchmark failed: {str(e)}\n{traceback.format_exc()}",
            metadata={}
        )


def run_folder_benchmark(config: BenchmarkConfig) -> Dict[str, Any]:
    """
    Run benchmark on all files in folder using multiple GPUs
    
    Args:
        config: BenchmarkConfig object
    
    Returns:
        Dictionary with benchmark results and metadata
        
    Note:
        - Each GPU worker processes files independently
        - Audio processing can handle multiple workers per GPU
        - Image/Video processing typically requires 1 worker per GPU due to VRAM usage
    """
    print("🚀 Starting Folder Benchmark")
    print("=" * 60)
    
    # Detect device and available GPUs if auto
    if config.device == "auto":
        config.device, available_gpus = detect_device()
    else:
        # If device is manually specified, try to detect GPU count
        try:
            import torch
            if config.device.startswith('cuda') and torch.cuda.is_available():
                available_gpus = torch.cuda.device_count()
            else:
                available_gpus = 0
        except ImportError:
            available_gpus = 0
    
    # Validate GPU configuration
    if config.num_gpus > available_gpus and available_gpus > 0:
        print(f"⚠️ Warning: Requested {config.num_gpus} workers but only {available_gpus} GPUs available")
        print(f"   Will distribute workers across {available_gpus} GPUs")
    
    print(f"📁 Folder: {config.folder_path}")
    print(f"🎯 Modality: {config.modality}")
    print(f"🎮 Workers: {config.num_gpus}")
    print(f"🔧 Available GPUs: {available_gpus}")
    print(f"🔄 Runs per file: {config.num_runs}")
    print(f"💻 Device: {config.device}")
    
    # Handle different dataset types
    if config.modality == 'webdataset':
        # Find webdataset files and extract samples
        webdataset_files = find_media_files(
            config.folder_path, 
            config.modality, 
            None,  # Don't limit webdataset files themselves
            config.file_extensions
        )
        
        if not webdataset_files:
            print("❌ No webdataset files found!")
            return {
                'config': asdict(config),
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
        
        # Extract samples from webdataset files with distributed sampling
        print(f"📦 Extracting samples from {len(webdataset_files)} webdataset files...")
        
        # Get target modality from config
        target_modality = getattr(config, 'webdataset_modality', 'audio')
        
        all_samples = []
        if config.max_files:
            # Distribute max_files across webdataset files
            samples_per_file = max(1, config.max_files // len(webdataset_files))
            remaining_samples = config.max_files % len(webdataset_files)
            
            print(f"   🎯 Distributing {config.max_files} samples across {len(webdataset_files)} webdataset files")
            print(f"   📊 Base samples per file: {samples_per_file}")
            
            for i, tar_path in enumerate(webdataset_files):
                # Give extra samples to first few files for remainder
                file_sample_limit = samples_per_file + (1 if i < remaining_samples else 0)
                samples = find_webdataset_samples(tar_path, target_modality, file_sample_limit)
                all_samples.extend(samples)
                
                print(f"   📦 {Path(tar_path).name}: {len(samples)} samples (limit: {file_sample_limit})")
        else:
            # No limit, extract all samples
            for tar_path in webdataset_files:
                samples = find_webdataset_samples(tar_path, target_modality, None)
                all_samples.extend(samples)
        
        if not all_samples:
            print("❌ No samples found in webdataset files!")
            return {
                'config': asdict(config),
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
        
        print(f"✅ Extracted {len(all_samples)} samples from webdataset files")
        print(f"\n⏱️ Benchmarking {len(all_samples)} samples...")
        
        # Process webdataset samples in parallel
        # Note: Some webdataset samples with complex objects may not be pickle-able for multiprocessing
        try:
            results, successful_count, failed_count = process_samples_parallel(
                all_samples, 
                benchmark_webdataset_sample, 
                config, 
                target_modality, 
                available_gpus
            )
        except Exception as e:
            if "pickle" in str(e).lower() or "serialize" in str(e).lower():
                print(f"⚠️ Multiprocessing failed ({str(e)[:100]}...), falling back to sequential processing")
                # Fallback to sequential processing for webdataset
                results = []
                successful_count = 0
                failed_count = 0
                
                for i, (sample_key, sample_data) in enumerate(all_samples):
                    try:
                        result = benchmark_webdataset_sample(((sample_key, sample_data), config, target_modality))
                        results.append(result)
                        
                        if result.success:
                            successful_count += 1
                            status = f"✅ {result.speedup_factor:.1f}x speedup"
                        else:
                            failed_count += 1
                            status = f"❌ {result.error[:50]}..." if result.error else "❌ Unknown error"
                        
                        print(f"   [{i+1}/{len(all_samples)}] {sample_key}: {status}")
                        
                    except Exception as sample_e:
                        failed_count += 1
                        print(f"   [{i+1}/{len(all_samples)}] {sample_key}: ❌ {str(sample_e)}")
                        
                        results.append(BenchmarkResult(
                            file_path=sample_key,
                            file_size_mb=0.0,
                            file_duration_or_pixels=0.0,
                            car_size_mb=0.0,
                            generation_time_ms=0.0,
                            loading_time_ms=0.0,
                            speedup_factor=0.0,
                            time_savings_ms=0.0,
                            compression_ratio=0.0,
                            success=False,
                            error=str(sample_e),
                            metadata={}
                        ))
            else:
                raise e
        
        total_files = len(all_samples)
        
    elif config.modality == 'hdf5':
        # Handle HDF5 files similarly
        hdf5_files = find_media_files(
            config.folder_path, 
            config.modality, 
            None,  # Don't limit HDF5 files themselves
            config.file_extensions
        )
        
        if not hdf5_files:
            print("❌ No HDF5 files found!")
            return {
                'config': asdict(config),
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
        
        # Get target modality from config
        target_modality = getattr(config, 'hdf5_modality', 'audio')
        
        # Extract samples from HDF5 files with distributed sampling
        print(f"📊 Extracting samples from {len(hdf5_files)} HDF5 files...")
        all_samples = []
        if config.max_files:
            # Distribute max_files across HDF5 files
            samples_per_file = max(1, config.max_files // len(hdf5_files))
            remaining_samples = config.max_files % len(hdf5_files)
            
            print(f"   🎯 Distributing {config.max_files} samples across {len(hdf5_files)} HDF5 files")
            print(f"   📊 Base samples per file: {samples_per_file}")
            
            for i, hdf5_path in enumerate(hdf5_files):
                # Give extra samples to first few files for remainder
                file_sample_limit = samples_per_file + (1 if i < remaining_samples else 0)
                samples = find_hdf5_samples(hdf5_path, target_modality, file_sample_limit)
                all_samples.extend(samples)
                
                print(f"   📊 {Path(hdf5_path).name}: {len(samples)} samples (limit: {file_sample_limit})")
        else:
            # No limit, extract all samples
            for hdf5_path in hdf5_files:
                samples = find_hdf5_samples(hdf5_path, target_modality, None)
                all_samples.extend(samples)
        
        if not all_samples:
            print("❌ No samples found in HDF5 files!")
            return {
                'config': asdict(config),
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
        
        print(f"✅ Extracted {len(all_samples)} samples from HDF5 files")
        print(f"\n⏱️ Benchmarking {len(all_samples)} samples...")
        
        # Process HDF5 samples in parallel
        results, successful_count, failed_count = process_samples_parallel(
            all_samples, 
            benchmark_hdf5_sample, 
            config, 
            target_modality, 
            available_gpus
        )
        
        total_files = len(all_samples)
        
    else:
        # Handle regular media files
        media_files = find_media_files(
            config.folder_path, 
            config.modality, 
            config.max_files,
            config.file_extensions
        )
        
        if not media_files:
            print("❌ No media files found!")
            return {
                'config': asdict(config),
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
        
        print(f"\n⏱️ Benchmarking {len(media_files)} files...")
        
        # Calculate optimal worker configuration for regular media files
        actual_workers, gpu_assignments = get_optimal_worker_config(config.modality, config.num_gpus, available_gpus)
        
        print(f"🎯 Target modality: {config.modality} ({get_modality_workers_per_gpu(config.modality)} workers/GPU)")
        print(f"🎯 GPU assignments: {gpu_assignments}")
        print(f"📦 Processing {len(media_files)} files with {actual_workers} worker{'s' if actual_workers > 1 else ''}")
        
        results = []
        successful_count = 0
        failed_count = 0
        total_files = len(media_files)
        
        # Process files with multiprocessing
        if actual_workers > 1:
            print(f"🔀 Using {actual_workers} parallel workers...")
            
            # Create per-worker configurations
            worker_configs = []
            for worker_id, gpu_id in enumerate(gpu_assignments):
                worker_config = BenchmarkConfig(
                    folder_path=config.folder_path,
                    modality=config.modality,
                    output_file=config.output_file,
                    num_gpus=1,  # Each worker handles 1 assigned GPU
                    device=config.device,
                    num_runs=config.num_runs,
                    max_files=config.max_files,
                    file_extensions=config.file_extensions,
                    model_config=config.model_config,
                    gpu_id=gpu_id
                )
                worker_configs.append(worker_config)
            
            # Distribute files among workers
            files_per_worker = len(media_files) // actual_workers
            remaining_files = len(media_files) % actual_workers
            
            benchmark_args = []
            file_idx = 0
            
            for worker_id, worker_config in enumerate(worker_configs):
                # Calculate number of files for this worker
                worker_files = files_per_worker + (1 if worker_id < remaining_files else 0)
                
                # Assign files to this worker
                for _ in range(worker_files):
                    if file_idx < len(media_files):
                        benchmark_args.append((media_files[file_idx], worker_config))
                        file_idx += 1
            
            with ProcessPoolExecutor(max_workers=actual_workers) as executor:
                # Submit all jobs
                futures = {
                    executor.submit(benchmark_single_file, args): args[0] 
                    for args in benchmark_args
                }
                
                # Process completed jobs
                for i, future in enumerate(as_completed(futures)):
                    file_path = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if result.success:
                            successful_count += 1
                            status = f"✅ {result.speedup_factor:.1f}x speedup"
                        else:
                            failed_count += 1
                            status = f"❌ {result.error[:50]}..."
                        
                        print(f"   [{i+1}/{len(media_files)}] {Path(file_path).name}: {status}")
                        
                    except Exception as e:
                        failed_count += 1
                        print(f"   [{i+1}/{len(media_files)}] {Path(file_path).name}: ❌ {str(e)}")
                        
                        # Create error result
                        results.append(BenchmarkResult(
                            file_path=file_path,
                            file_size_mb=0.0,
                            file_duration_or_pixels=0.0,
                            car_size_mb=0.0,
                            generation_time_ms=0.0,
                            loading_time_ms=0.0,
                            speedup_factor=0.0,
                            time_savings_ms=0.0,
                            compression_ratio=0.0,
                            success=False,
                            error=str(e),
                            metadata={}
                        ))
        else:
            print("🔄 Using single worker processing...")
            
            # Create single worker configuration
            single_worker_config = BenchmarkConfig(
                folder_path=config.folder_path,
                modality=config.modality,
                output_file=config.output_file,
                num_gpus=1,
                device=config.device,
                num_runs=config.num_runs,
                max_files=config.max_files,
                file_extensions=config.file_extensions,
                model_config=config.model_config,
                gpu_id=gpu_assignments[0] if gpu_assignments[0] is not None else None
            )
            
            # Prepare arguments for single worker processing
            benchmark_args = [(file_path, single_worker_config) for file_path in media_files]
            
            for i, args in enumerate(benchmark_args):
                file_path = args[0]
                try:
                    result = benchmark_single_file(args)
                    results.append(result)
                    
                    if result.success:
                        successful_count += 1
                        status = f"✅ {result.speedup_factor:.1f}x speedup"
                    else:
                        failed_count += 1
                        status = f"❌ {result.error[:50]}..." if result.error else "❌ Unknown error"
                    
                    print(f"   [{i+1}/{len(media_files)}] {Path(file_path).name}: {status}")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"   [{i+1}/{len(media_files)}] {Path(file_path).name}: ❌ {str(e)}")
                    
                    results.append(BenchmarkResult(
                        file_path=file_path,
                        file_size_mb=0.0,
                        file_duration_or_pixels=0.0,
                        car_size_mb=0.0,
                        generation_time_ms=0.0,
                        loading_time_ms=0.0,
                        speedup_factor=0.0,
                        time_savings_ms=0.0,
                        compression_ratio=0.0,
                        success=False,
                        error=str(e),
                        metadata={}
                    ))
    
    # Calculate summary statistics
    successful_results = [r for r in results if r.success]
    
    if successful_results:
        speedups = [r.speedup_factor for r in successful_results]
        time_savings = [r.time_savings_ms for r in successful_results]
        compression_ratios = [r.compression_ratio for r in successful_results]
        
        summary = {
            'avg_speedup': sum(speedups) / len(speedups),
            'min_speedup': min(speedups),
            'max_speedup': max(speedups),
            'avg_time_savings_ms': sum(time_savings) / len(time_savings),
            'total_time_savings_ms': sum(time_savings),
            'avg_compression_ratio': sum(compression_ratios) / len(compression_ratios),
            'total_file_size_mb': sum(r.file_size_mb for r in successful_results),
            'total_car_size_mb': sum(r.car_size_mb for r in successful_results)
        }
    else:
        summary = {}
    
    # Create final result dictionary
    final_result = {
        'config': asdict(config),
        'results': [asdict(result) for result in results],
        'summary': summary,
        'timestamp': datetime.now().isoformat(),
        'total_files': total_files,
        'successful_files': successful_count,
        'failed_files': failed_count
    }
    
    # Save results to JSON
    print(f"\n💾 Saving results to {config.output_file}...")
    with open(config.output_file, 'w') as f:
        json.dump(final_result, f, indent=2)
    
    # Print summary
    print(f"\n📊 Benchmark Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Successful: {successful_count}")
    print(f"   Failed: {failed_count}")
    
    if successful_results:
        print(f"   Average speedup: {summary['avg_speedup']:.1f}x")
        print(f"   Speedup range: {summary['min_speedup']:.1f}x - {summary['max_speedup']:.1f}x")
        print(f"   Total time savings: {summary['total_time_savings_ms']/1000:.1f} seconds")
        print(f"   Average compression: {summary['avg_compression_ratio']:.1f}x")
    
    print(f"\n✅ Results saved to: {config.output_file}")
    
    return final_result


def main():
    parser = argparse.ArgumentParser(description="Folder benchmark for latent generation vs CAR loading")
    
    parser.add_argument("folder", help="Path to folder containing media files")
    parser.add_argument("--modality", choices=['audio', 'image', 'video', 'webdataset', 'hdf5'], required=True,
                        help="Type of media to process")
    parser.add_argument("--webdataset-modality", choices=['audio', 'image', 'video'], default='audio',
                        help="Target modality for webdataset files (required when --modality=webdataset)")
    parser.add_argument("--hdf5-modality", choices=['audio', 'image', 'video'],
                        help="Target modality for HDF5 files (required when --modality=hdf5)")
    parser.add_argument("--output", default="benchmark_results.json",
                        help="Output JSON file path")
    parser.add_argument("--gpus", type=int, default=1,
                        help="Number of parallel workers (auto-optimized: audio=4/GPU, image=2/GPU, video=1/GPU)")
    parser.add_argument("--device", default="auto",
                        help="Device to use (auto, cuda, cpu)")
    parser.add_argument("--runs", type=int, default=3,
                        help="Number of runs per file for averaging (excludes 1 warm-up run)")
    parser.add_argument("--max-files", type=int, default=100,
                        help="Maximum number of files to process")
    parser.add_argument("--extensions", nargs="+",
                        help="Custom file extensions to look for")
    
    # Model configuration arguments
    parser.add_argument("--model-name",
                        help="Model name to use for encoding")
    parser.add_argument("--model-type",
                        help="Model type (for audio: encodec, dac, snac)")
    
    args = parser.parse_args()
    
    # Validate folder path
    if not os.path.isdir(args.folder):
        print(f"❌ Folder not found: {args.folder}")
        sys.exit(1)
    
    # Validate webdataset parameters
    if args.modality == 'webdataset' and not args.webdataset_modality:
        print("❌ --webdataset-modality is required when using --modality=webdataset")
        sys.exit(1)
    
    # Validate HDF5 parameters
    if args.modality == 'hdf5' and not args.hdf5_modality:
        print("❌ --hdf5-modality is required when using --modality=hdf5")
        sys.exit(1)
    
    # Build model config
    model_config = {}
    if args.model_name:
        model_config['model_name'] = args.model_name
    if args.model_type:
        model_config['model_type'] = args.model_type
    
    # Create configuration
    config = BenchmarkConfig(
        folder_path=args.folder,
        modality=args.modality,
        output_file=args.output,
        num_gpus=args.gpus,
        device=args.device,
        num_runs=args.runs,
        max_files=args.max_files,
        file_extensions=args.extensions,
        model_config=model_config if model_config else None,
        webdataset_modality=args.webdataset_modality,
        hdf5_modality=args.hdf5_modality or args.webdataset_modality,  # Fallback to webdataset_modality if hdf5_modality not set
    )
    
    # Run benchmark
    try:
        run_folder_benchmark(config)
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()