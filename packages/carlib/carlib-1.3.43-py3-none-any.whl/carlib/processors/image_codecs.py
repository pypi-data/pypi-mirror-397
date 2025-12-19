import torch
from torch.utils.data import Dataset, DataLoader
import os
import glob
import json
import numpy as np
from typing import Optional, Dict, Any, List,Tuple
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import mediapy as media
from dataclasses import dataclass
from PIL import Image
from .utils import CARHandler
from ..checkpoints import ensure_checkpoint
from .memory_utils import smart_empty_cache, error_cache_clear

# Import Cosmos tokenizers
try:
    # import cosmos_tokenizer.image_lib
    from cosmos_tokenizer.image_lib import ImageTokenizer
    TOKENIZER_AVAILABLE = True
    print("✅ Cosmos image tokenizer available")
except ImportError:
    TOKENIZER_AVAILABLE = False
    print("❌ Cosmos image tokenizer not available - please install cosmos_tokenizer")

@dataclass
class ImageConfig:
    """Configuration for image processing"""
    model_name: str = "CI8x8"  # CI8x8, DI16x16, etc.
    image_size: Tuple[int, int] = (224, 224)
    maintain_aspect_ratio: bool = False
    normalize_images: bool = True
    checkpoint_dir: str = "pretrained_ckpts"
    device: str = "cuda"
    dtype: str = "bfloat16"
    quality_threshold: float = 0.0
    output_format: str = "pt"  # "pt" or "car"

# Model configurations mapping
IMAGE_TOKENIZER_CONFIGS = {
    'CI8x8': 'Cosmos-0.1-Tokenizer-CI8x8',
    'CI16x16': 'Cosmos-0.1-Tokenizer-CI16x16',
    'DI8x8': 'Cosmos-0.1-Tokenizer-DI8x8',
    'DI16x16': 'Cosmos-0.1-Tokenizer-DI16x16',
    'CI8x8-v1': 'Cosmos-1.0-Tokenizer-CI8x8',
    'DI16x16-v1': 'Cosmos-1.0-Tokenizer-DI16x16'
}

class CosmosImageProcessor:
    """Simplified processor to convert image files to Cosmos tokenizer .pt files"""
    
    def __init__(self, config: ImageConfig):
        self.config = config
        
        if not TOKENIZER_AVAILABLE:
            raise ImportError("Cosmos tokenizers not available. Please install: pip install cosmos_tokenizer")
        
        # Initialize tokenizer
        self._init_tokenizer()
    
    def _init_tokenizer(self):
        """Initialize the Cosmos image tokenizer"""
        model_full_name = IMAGE_TOKENIZER_CONFIGS.get(self.config.model_name, self.config.model_name)
        
        # Try to ensure checkpoint is available (auto-download if needed)
        try:
            checkpoint_dir = ensure_checkpoint(self.config.model_name)
            print(f"✅ Using checkpoint: {checkpoint_dir}")
        except RuntimeError as e:
            print(f"⚠️  Checkpoint auto-download failed: {e}")
            print(f"   Falling back to configured checkpoint_dir: {self.config.checkpoint_dir}")
            checkpoint_dir = f"{self.config.checkpoint_dir}/{model_full_name}"
        
        encoder_ckpt = f"{checkpoint_dir}/encoder.jit"
        decoder_ckpt = f"{checkpoint_dir}/decoder.jit"
        
        if not (os.path.exists(encoder_ckpt) and os.path.exists(decoder_ckpt)):
            raise FileNotFoundError(
                f"Tokenizer checkpoints not found: {model_full_name}\n"
                f"  Expected: {encoder_ckpt} and {decoder_ckpt}\n"
                f"  Try running: carlib setup download {self.config.model_name}\n"
                f"  Checkpoints are downloaded automatically from our public S3 bucket"
            )
        
        self.tokenizer = ImageTokenizer(
            checkpoint_enc=encoder_ckpt,
            checkpoint_dec=decoder_ckpt,
            device=self.config.device,
            dtype=self.config.dtype
        )
        
        print(f"✓ Image tokenizer initialized: {model_full_name}")
        print(f"  Device: {self.config.device}")
        print(f"  Checkpoint: {checkpoint_dir}")
        print(f"  Image size: {self.config.image_size}")
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get basic image information"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format_type = img.format
                file_size = os.path.getsize(image_path)
                
                return {
                    'path': image_path,
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'format': format_type,
                    'file_size': file_size,
                    'aspect_ratio': width / height if height > 0 else 0
                }
        except Exception as e:
            return {'error': f'Cannot open image: {image_path}'}
    
    def load_image(self, image_path: str, resize: bool = False) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Load and preprocess image
        
        Args:
            image_path: Path to the image file
            resize: Whether to resize image to target size (default: False)
        """
        try:
            # Read image using mediapy (handles various formats)
            image_rgb = media.read_image(image_path)[..., :3]  # Ensure RGB
            
            if image_rgb is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            original_height, original_width = image_rgb.shape[:2]
            
            # Conditionally resize image
            if resize:
                target_size = self.config.image_size
                if self.config.maintain_aspect_ratio:
                    image_processed = self._resize_with_aspect_ratio(image_rgb, target_size)
                else:
                    image_processed = cv2.resize(image_rgb, target_size)
                processed_size = target_size
            else:
                image_processed = image_rgb
                processed_size = (original_width, original_height)
            
            # Ensure proper format for tokenizer
            if image_processed.dtype != np.uint8:
                if image_processed.max() <= 1.0:
                    image_processed = (image_processed * 255).astype(np.uint8)
                else:
                    image_processed = image_processed.astype(np.uint8)
            
            # Metadata
            metadata = {
                'original_path': image_path,
                'original_size': (original_width, original_height),
                'processed_size': processed_size,
                'resized': resize,
                'maintain_aspect_ratio': self.config.maintain_aspect_ratio if resize else False,
                'original_channels': image_rgb.shape[2] if len(image_rgb.shape) > 2 else 1,
                'model_name': self.config.model_name
            }
            
            return image_processed, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")
    
    def encode_image(self, image: np.ndarray, metadata: Dict[str, Any], base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode image using Cosmos tokenizer"""
        print(f"🔄 Encoding image with shape {image.shape}...")
        
        # Clear GPU memory before processing large images
        smart_empty_cache(force=True)
        
        # Auto-resize extremely large images to prevent OOM
        max_size = 2048  # Maximum dimension to prevent OOM
        original_shape = image.shape
        if max(image.shape[:2]) > max_size:
            scale_factor = max_size / max(image.shape[:2])
            new_height = int(image.shape[0] * scale_factor)
            new_width = int(image.shape[1] * scale_factor)
            image = cv2.resize(image, (new_width, new_height))
            print(f"⚠️  Resized large image: {original_shape[:2]} -> {image.shape[:2]} to prevent OOM")
        
        # Prepare image tensor for tokenizer
        batched_image = np.expand_dims(image, axis=0)  # (1, H, W, 3)
        
        # Extend metadata with base_metadata if provided
        extended_metadata = metadata.copy()
        if base_metadata is not None:
            extended_metadata.update(base_metadata)
        
        encoded_data = {
            'model_name': self.config.model_name,
            'metadata': extended_metadata
        }
        
        try:
            # For encoding, convert to tensor format expected by encode method
            input_tensor = torch.from_numpy(batched_image).float()
            input_tensor = input_tensor.permute(0, 3, 1, 2)  # (1, H, W, 3) -> (1, 3, H, W)
            input_tensor = (input_tensor / 255.0) * 2.0 - 1.0  # [0, 255] -> [-1, 1]
            
            # Move to device
            device = self.config.device
            dtype = getattr(torch, self.config.dtype)
            input_tensor = input_tensor.to(device=device, dtype=dtype)
            
            # Clear cache before heavy computation
            smart_empty_cache(force=True)
            
            # Encode using tokenizer
            with torch.no_grad():
                encoded_output = self.tokenizer.encode(input_tensor)
            
            # Handle different tokenizer outputs
            if 'DI' in self.config.model_name:
                # DI tokenizer returns indices (and optionally discrete codes)
                if isinstance(encoded_output, tuple):
                    if len(encoded_output) == 2:
                        indices, discrete_codes = encoded_output
                        encoded_data['encoded_indices'] = indices.cpu().squeeze(0) if indices.dim() > 2 else indices.cpu()
                        encoded_data['encoded_latents'] = discrete_codes.cpu().squeeze(0) if discrete_codes.dim() > 3 else discrete_codes.cpu()
                        print(f"✅ DI - Encoded indices: {encoded_data['encoded_indices'].shape}")
                        print(f"✅ DI - Encoded latents: {encoded_data['encoded_latents'].shape}")
                    else:
                        indices = encoded_output[0]
                        encoded_data['encoded_indices'] = indices.cpu().squeeze(0) if indices.dim() > 2 else indices.cpu()
                        print(f"✅ DI - Encoded indices: {encoded_data['encoded_indices'].shape}")
                else:
                    indices = encoded_output
                    encoded_data['encoded_indices'] = indices.cpu().squeeze(0) if indices.dim() > 2 else indices.cpu()
                    print(f"✅ DI - Encoded indices: {encoded_data['encoded_indices'].shape}")
            else:
                # CI tokenizer returns continuous latent tensor
                if isinstance(encoded_output, torch.Tensor):
                    latent_tensor = encoded_output.cpu().squeeze(0) if encoded_output.dim() > 3 else encoded_output.cpu()
                elif isinstance(encoded_output, tuple) and len(encoded_output) == 1:
                    latent_tensor = encoded_output[0].cpu().squeeze(0) if encoded_output[0].dim() > 3 else encoded_output[0].cpu()
                else:
                    raise ValueError(f"Unexpected CI output format: {type(encoded_output)}")
                
                encoded_data['encoded_latents'] = latent_tensor
                print(f"✅ CI - Encoded latents: {latent_tensor.shape}")
            
            # Calculate compression metrics
            original_elements = np.prod(image.shape)
            if 'encoded_latents' in encoded_data:
                compressed_elements = np.prod(encoded_data['encoded_latents'].shape)
                compression_ratio = original_elements / compressed_elements
                encoded_data['compression_ratio'] = float(compression_ratio)
            
            print(f"✅ Image encoding successful!")
            
            # Clear GPU memory after processing
            smart_empty_cache(force=True)
            
            return encoded_data
            
        except Exception as e:
            print(f"❌ Failed to encode image: {e}")
            # Clear GPU memory on error
            error_cache_clear()
            import traceback
            traceback.print_exc()
            raise
    
    def decode_image(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode compressed image data back to image"""
        # Check if model name in encoded data differs from current tokenizer
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        if encoded_model_name and encoded_model_name != self.config.model_name:
            print(f"🔄 Model mismatch detected: {self.config.model_name} -> {encoded_model_name}")
            print(f"   Reinitializing tokenizer...")
            # Update config and reinitialize tokenizer
            self.config.model_name = encoded_model_name
            self._init_tokenizer()
        
        # Move data to correct device
        if 'encoded_indices' in encoded_data and 'DI' in self.config.model_name:
            # DI tokenizer
            indices = encoded_data['encoded_indices'].to(self.config.device)
            if indices.dim() == 2:
                indices = indices.unsqueeze(0)  # Add batch dimension
            
            # DI models expect long tensors for indices (for embedding lookups)
            if indices.dtype != torch.long:
                indices = indices.long()
            
            with torch.no_grad():
                decoded_tensor = self.tokenizer.decode(indices)
            
        elif 'encoded_latents' in encoded_data:
            # CI tokenizer
            latents = encoded_data['encoded_latents'].to(self.config.device)
            if latents.dim() == 3:
                latents = latents.unsqueeze(0)  # Add batch dimension
            
            # Convert to model's expected dtype for latents
            dtype = getattr(torch, self.config.dtype)
            latents = latents.to(dtype=dtype)
            
            with torch.no_grad():
                decoded_tensor = self.tokenizer.decode(latents)
        else:
            raise ValueError("No encoded data found for decoding")
        
        # Process output to standard format: (H, W, 3) in [0, 255]
        processed_image = self._process_decoded_image(decoded_tensor)
        print(f"✅ Decoded image: {processed_image.shape}")
        return processed_image
    
    def _resize_with_aspect_ratio(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize
        resized = cv2.resize(image, (new_w, new_h))
        
        # Create padded image
        padded = np.zeros((target_h, target_w, 3), dtype=image.dtype)
        
        # Center the image
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        padded[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        
        return padded
    
    def _process_decoded_image(self, decoded_tensor: torch.Tensor) -> torch.Tensor:
        """Process decoded image tensor to standard format"""
        # Handle batch dimension
        if decoded_tensor.dim() == 4 and decoded_tensor.shape[0] == 1:
            image_tensor = decoded_tensor.squeeze(0)  # (1,3,H,W) -> (3,H,W)
        else:
            image_tensor = decoded_tensor
        
        # Convert from (3,H,W) to (H,W,3)
        if image_tensor.dim() == 3 and image_tensor.shape[0] == 3:
            image_tensor = image_tensor.permute(1, 2, 0)  # (3,H,W) -> (H,W,3)
        
        # Convert from [-1,1] to [0,255] range
        image_tensor = (image_tensor + 1.0) / 2.0 * 255.0
        image_tensor = torch.clamp(image_tensor, 0, 255)
        image_tensor = image_tensor.cpu().float()
        
        print(f"Processed decoded image: {image_tensor.shape}, range: [{image_tensor.min():.1f}, {image_tensor.max():.1f}]")
        return image_tensor
    
    def save_decoded_image(self, image_tensor: torch.Tensor, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded image tensor to file
        
        Args:
            image_tensor: Decoded image with shape (H, W, 3) in [0, 255] range
            output_path: Path to save the image file
            metadata: Optional metadata
            
        Returns:
            Path to saved image file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to numpy
        if isinstance(image_tensor, torch.Tensor):
            image_np = image_tensor.numpy()
        else:
            image_np = image_tensor
        
        # Ensure proper format
        if image_np.max() <= 1.0:
            image_uint8 = (image_np * 255).astype(np.uint8)
        else:
            image_uint8 = image_np.astype(np.uint8)
        
        try:
            # Save using mediapy
            media.write_image(output_path, image_uint8)
            print(f"✅ Saved decoded image: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving image {output_path}: {e}")
            return None
        
    def load_from_car(self, car_path: str) -> Dict[str, Any]:
        """Load compressed audio data from CAR format"""
        # Fallback: use CARHandler directly
        from .utils import CARHandler
        with open(car_path, 'rb') as f:
            car_data = f.read()
        encoded_data, metadata = CARHandler.car_to_np(car_data)
        return {
            'status': 'success',
            'data': encoded_data,
            'metadata': metadata,
            'file_path': car_path
        }
        
    def process_single_file(self, image_path: str, output_path: Optional[str]=None, base_metadata: Optional[Dict[str, Any]] = None, 
                           save_car: bool = True, save_hdf5: bool = False, save_webdataset: bool = False, save_tfrecord: bool = False) -> Dict[str, Any]:
        """Process a single image file and save in selected formats
        
        Args:
            image_path: Path to input image
            output_path: Output path (optional)
            base_metadata: Additional metadata (optional)
            save_car: Save in CAR format (default: True)
            save_hdf5: Save in HDF5 format (default: False)
            save_webdataset: Save in WebDataset format (default: False)
            save_tfrecord: Save in TFRecord format (default: False)
        """
        try:
            # Generate base output path if not provided
            if output_path is None:
                base_output = os.path.splitext(image_path)[0]
            else:
                base_output = os.path.splitext(output_path)[0]
            
            # Load image
            image, metadata = self.load_image(image_path, resize=False)
            
            # Encode
            encoded_data = self.encode_image(image, metadata, base_metadata)
            
            # Calculate file sizes for reporting
            original_size = np.prod(image.shape) * 1  # uint8 = 1 byte
            
            # Prepare metadata for exports
            export_metadata = {
                "media_type": "image",
                "processor": "CosmosImageProcessor",
                "model_name": self.config.model_name,
                "image_size": list(self.config.image_size),
                "original_size": list(metadata.get('original_size', [0, 0]))
            }
            
            # Save in selected formats
            saved_files = {}
            
            # 1. Save as CAR format
            if save_car:
                try:
                    car_path = f"{base_output}.car"
                    os.makedirs(os.path.dirname(car_path), exist_ok=True)
                    car_data = CARHandler.np_to_car(encoded_data, export_metadata, optimize_dtypes=True)
                    with open(car_path, 'wb') as f:
                        f.write(car_data)
                    saved_files['car'] = car_path
                    print(f"✅ Saved CAR: {car_path}")
                except Exception as e:
                    print(f"❌ Failed to save CAR: {e}")
            
            # 2. Save as HDF5 format
            if save_hdf5:
                try:
                    hdf5_path = f"{base_output}.h5"
                    CARHandler.np_to_hdf5(encoded_data, hdf5_path, optimize_dtypes=True)
                    saved_files['hdf5'] = hdf5_path
                    print(f"✅ Saved HDF5: {hdf5_path}")
                except Exception as e:
                    print(f"❌ Failed to save HDF5: {e}")
            
            # 3. Save as WebDataset format
            if save_webdataset:
                try:
                    webdataset_path = f"{base_output}.tar"
                    sample_key = os.path.splitext(os.path.basename(image_path))[0]
                    CARHandler.np_to_webdataset(encoded_data, webdataset_path, sample_key=sample_key, optimize_dtypes=True)
                    saved_files['webdataset'] = webdataset_path
                    print(f"✅ Saved WebDataset: {webdataset_path}")
                except Exception as e:
                    print(f"❌ Failed to save WebDataset: {e}")
            
            # 4. Save as TFRecord format
            if save_tfrecord:
                try:
                    tfrecord_path = f"{base_output}.tfrecord"
                    sample_key = os.path.splitext(os.path.basename(image_path))[0]
                    CARHandler.np_to_tfrecord(encoded_data, tfrecord_path, sample_key=sample_key, optimize_dtypes=True)
                    saved_files['tfrecord'] = tfrecord_path
                    print(f"✅ Saved TFRecord: {tfrecord_path}")
                except Exception as e:
                    print(f"❌ Failed to save TFRecord: {e}")
            
            # Calculate compression info using CAR file if available
            if 'car' in saved_files:
                compressed_size = os.path.getsize(saved_files['car'])
                file_ratio = original_size / compressed_size
                
                compression_info = {
                    'spatial_ratio': encoded_data.get('compression_ratio', 'unknown'),
                    'file_size_ratio': file_ratio,
                    'original_size_kb': original_size / 1024,
                    'compressed_size_kb': compressed_size / 1024,
                    'output_formats': list(saved_files.keys())
                }
                
                print(f"   Spatial compression: {compression_info['spatial_ratio']:.0f}:1" if isinstance(compression_info['spatial_ratio'], float) else f"   Spatial compression: {compression_info['spatial_ratio']}")
                print(f"   File size: {compression_info['original_size_kb']:.1f}KB → {compression_info['compressed_size_kb']:.1f}KB ({file_ratio:.1f}x)")
            else:
                compression_info = {
                    'spatial_ratio': encoded_data.get('compression_ratio', 'unknown'),
                    'file_size_ratio': 'N/A',
                    'original_size_kb': original_size / 1024,
                    'compressed_size_kb': 'N/A',
                    'output_formats': list(saved_files.keys())
                }
                print(f"   Spatial compression: {compression_info['spatial_ratio']:.0f}:1" if isinstance(compression_info['spatial_ratio'], float) else f"   Spatial compression: {compression_info['spatial_ratio']}")
            
            # Clear GPU cache to prevent memory buildup during batch processing
            if torch.cuda.is_available():
                smart_empty_cache(force=True)

            return {
                'status': 'success',
                'input_path': image_path,
                'output_files': saved_files,
                'compression': compression_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'input_path': image_path,
                'error': str(e)
            }
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        image_extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'),
        num_workers: int = 1,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all image files in a directory"""
        
        # Find image files
        pattern = "**/*" if recursive else "*"
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext}"),
                recursive=recursive
            ))
            image_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext.upper()}"),
                recursive=recursive
            ))
        
        print(f"Found {len(image_files)} image files")
        
        if not image_files:
            return {'status': 'no_files', 'processed': 0, 'errors': 0}
        
        # Prepare tasks
        tasks = []
        file_ext = ".car" if self.config.output_format == "car" else ".pt"
        for image_path in image_files:
            rel_path = os.path.relpath(image_path, input_dir)
            name_without_ext = os.path.splitext(rel_path)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}{file_ext}")
            tasks.append((image_path, output_path))
        
        # Process files
        results = []
        successful = 0
        errors = 0
        
        if num_workers == 1:
            # Single-threaded processing
            for image_path, output_path in tqdm(tasks, desc="Processing images"):
                result = self.process_single_file(image_path, output_path)
                results.append(result)
                
                if result['status'] == 'success':
                    successful += 1
                elif result['status'] == 'error':
                    errors += 1
        else:
            # Multi-threaded processing (limited by GPU memory)
            print(f"Processing with {num_workers} workers...")
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                future_to_task = {
                    executor.submit(self.process_single_file, image_path, output_path): (image_path, output_path)
                    for image_path, output_path in tasks
                }
                
                for future in tqdm(as_completed(future_to_task), total=len(tasks), desc="Processing"):
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'success':
                        successful += 1
                    elif result['status'] == 'error':
                        errors += 1
        
        # Save processing report
        report = {
            'config': self.config.__dict__,
            'input_dir': input_dir,
            'output_dir': output_dir,
            'total_files': len(image_files),
            'successful': successful,
            'errors': errors,
            'results': results
        }
        
        report_path = os.path.join(output_dir, "preprocessing_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Processing complete!")
        print(f"   Successful: {successful}")
        print(f"   Errors: {errors}")
        print(f"   Report saved: {report_path}")
        
        return report


class CosmosImageDataset(Dataset):
    """PyTorch Dataset for loading Cosmos tokenized image files"""
    
    def __init__(
        self,
        data_dir: str,
        return_decoded: bool = False,
        return_codes: bool = True,
        device: str = "cpu",
        cache_decoded: bool = False,
        save_decoded: bool = False,
        decoded_output_dir: str = "./decoded_images"
    ):
        """Initialize the dataset
        
        Args:
            data_dir: Directory containing .pt files
            return_decoded: Return decoded image
            return_codes: Return encoded image codes/latents
            device: Device to load tensors on
            cache_decoded: Cache decoded images in memory (use carefully!)
            save_decoded: Save decoded images to files
            decoded_output_dir: Directory to save decoded image files
        """
        self.data_dir = data_dir
        self.return_decoded = return_decoded
        self.return_codes = return_codes
        self.device = device
        self.cache_decoded = cache_decoded
        self.save_decoded = save_decoded
        self.decoded_output_dir = decoded_output_dir
        
        # Create output directory if saving decoded images
        if self.save_decoded:
            os.makedirs(self.decoded_output_dir, exist_ok=True)
        
        # Find all .pt and .car files
        pt_files = glob.glob(os.path.join(data_dir, "**/*.pt"), recursive=True)
        car_files = glob.glob(os.path.join(data_dir, "**/*.car"), recursive=True)
        self.file_paths = pt_files + car_files
        print(f"Found {len(pt_files)} .pt files and {len(car_files)} .car files in {data_dir}")
        
        if not self.file_paths:
            raise ValueError(f"No .pt or .car files found in {data_dir}")
        
        # Load tokenizer if we need to decode
        self.tokenizer = None
        if self.return_decoded or self.save_decoded:
            # Load first file to get config
            sample_file = self.file_paths[0]
            if sample_file.endswith('.car'):
                with open(sample_file, 'rb') as f:
                    car_data = f.read()
                sample_data, _ = CARHandler.car_to_np(car_data)
            else:
                sample_data = torch.load(sample_file, map_location='cpu')
            # For optimized files, config info is not stored, use defaults or derive from model_name
            config_dict = sample_data.get('config', {
                'model_name': sample_data.get('model_name', 'CI8x8'),
                'checkpoint_dir': 'pretrained_ckpts',
                'dtype': 'bfloat16'
            })
            
            print("Loading Cosmos image tokenizer for decoding...")
            try:
                model_name = config_dict.get('model_name', 'CI8x8')
                model_full_name = IMAGE_TOKENIZER_CONFIGS.get(model_name, model_name)
                checkpoint_dir = config_dict.get('checkpoint_dir', 'pretrained_ckpts')
                
                encoder_ckpt = f"{checkpoint_dir}/{model_full_name}/encoder.jit"
                decoder_ckpt = f"{checkpoint_dir}/{model_full_name}/decoder.jit"
                
                if os.path.exists(encoder_ckpt) and os.path.exists(decoder_ckpt):
                    # from cosmos_tokenizer.image_lib import ImageTokenizer
                    self.tokenizer = ImageTokenizer(
                        checkpoint_enc=encoder_ckpt,
                        checkpoint_dec=decoder_ckpt,
                        device=device,
                        dtype=config_dict.get('dtype', 'bfloat16')
                    )
                    print(f"✓ Tokenizer loaded: {model_name}")
                else:
                    print(f"⚠️ Tokenizer checkpoints not found, decoding disabled")
                    self.return_decoded = False
                    self.save_decoded = False
            except Exception as e:
                print(f"⚠️ Failed to load tokenizer: {e}")
                self.return_decoded = False
                self.save_decoded = False
        
        # Cache for decoded images
        self.decoded_cache = {} if cache_decoded else None
        
        # Track saved images to avoid re-saving
        self.saved_images = set()
        
        # Load metadata from first file
        sample_file = self.file_paths[0]
        if sample_file.endswith('.car'):
            with open(sample_file, 'rb') as f:
                car_data = f.read()
            sample_data, _ = CARHandler.car_to_np(car_data)
        else:
            sample_data = torch.load(sample_file, map_location='cpu')
        self.model_name = sample_data.get('model_name', 'unknown')
        
        print(f"✓ Dataset ready: {len(self)} images")
        print(f"   Model: {self.model_name}")
        print(f"   Returns: {'decoded' if return_decoded else ''} {'codes' if return_codes else ''}")
        if self.save_decoded:
            print(f"   Saving decoded images to: {self.decoded_output_dir}")
    
    def __len__(self) -> int:
        return len(self.file_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        file_path = self.file_paths[idx]
        
        # Load encoded data based on file extension
        if file_path.endswith('.car'):
            # Load CAR file
            with open(file_path, 'rb') as f:
                car_data = f.read()
            encoded_data, metadata = CARHandler.car_to_np(car_data)
        else:
            # Load PT file
            encoded_data = torch.load(file_path, map_location='cpu')
        
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "metadata": metadata if file_path.endswith('.car') else encoded_data.get("metadata", {})
        }
        
        # Return encoded codes if requested
        if self.return_codes:
            if 'encoded_latents' in encoded_data:
                latents = encoded_data['encoded_latents']
                result["encoded_latents"] = latents.to(self.device)
            
            if 'encoded_indices' in encoded_data:
                indices = encoded_data['encoded_indices']
                result["encoded_indices"] = indices.to(self.device)
        
        # Handle decoded image (for returning and/or saving)
        decoded_image = None
        if self.return_decoded or self.save_decoded:
            # Check cache first
            if self.cache_decoded and idx in self.decoded_cache:
                decoded_image = self.decoded_cache[idx]
            else:
                # Decode image
                if self.tokenizer is None:
                    # Create dummy decoded image
                    height, width = (224, 224)  # Default image size
                    decoded_image = torch.zeros(height, width, 3).float()
                    print(f"⚠️ Created dummy decoded image: {decoded_image.shape}")
                else:
                    try:
                        decoded_image = self._decode_image_data(encoded_data)
                    except Exception as e:
                        print(f"⚠️ Decoding failed: {e}")
                        # Use default image size when config is not available
                        height, width = (224, 224)  # Default image size
                        decoded_image = torch.zeros(height, width, 3).float()
                
                # Cache if enabled
                if self.cache_decoded:
                    self.decoded_cache[idx] = decoded_image
            
            # Save decoded image if requested
            if self.save_decoded and idx not in self.saved_images:
                image_name = os.path.splitext(result["file_name"])[0]
                output_path = os.path.join(self.decoded_output_dir, f"{image_name}_decoded.png")
                
                # Get metadata
                metadata = encoded_data.get("metadata", {})
                
                saved_path = self.save_decoded_image(decoded_image, output_path, metadata)
                if saved_path:
                    result["decoded_image_path"] = saved_path
                    self.saved_images.add(idx)
        
        # Return decoded image tensor if requested
        if self.return_decoded and decoded_image is not None:
            result["image"] = decoded_image.to(self.device)
        
        return result
    
    def _decode_image_data(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode image data using the tokenizer"""
        model_name = encoded_data.get('model_name', 'CI8x8')
        
        # Prepare data for decoding
        if 'DI' in model_name and 'encoded_indices' in encoded_data:
            # For DI models, use indices
            data = encoded_data['encoded_indices'].to(self.device)
            if data.dim() == 2:
                data = data.unsqueeze(0)  # Add batch dimension
                
            # DI models expect long tensors for indices (for embedding lookups)
            if data.dtype != torch.long:
                data = data.long()
                
        elif 'encoded_latents' in encoded_data:
            # For CI models, use latents
            data = encoded_data['encoded_latents'].to(self.device)
            if data.dim() == 3:
                data = data.unsqueeze(0)  # Add batch dimension
                
            # Convert to tokenizer's expected dtype for latents
            data = data.to(dtype=getattr(torch, 'bfloat16'))
        else:
            raise ValueError("No suitable encoded data found for decoding")
        
        # Decode
        with torch.no_grad():
            decoded_tensor = self.tokenizer.decode(data)
        
        # Process output to standard format: (H, W, 3) in [0, 255]
        if decoded_tensor.dim() == 4 and decoded_tensor.shape[0] == 1:
            decoded_tensor = decoded_tensor.squeeze(0)  # Remove batch dim
        
        if decoded_tensor.dim() == 3 and decoded_tensor.shape[0] == 3:
            decoded_tensor = decoded_tensor.permute(1, 2, 0)  # (3,H,W) -> (H,W,3)
        
        # Convert from [-1,1] to [0,255]
        decoded_tensor = (decoded_tensor + 1.0) / 2.0 * 255.0
        decoded_tensor = torch.clamp(decoded_tensor, 0, 255)
        decoded_tensor = decoded_tensor.cpu().float()
        
        return decoded_tensor
    
    def save_decoded_image(self, image_tensor: torch.Tensor, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded image tensor to file"""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to numpy
        if isinstance(image_tensor, torch.Tensor):
            image_np = image_tensor.numpy()
        else:
            image_np = image_tensor
        
        # Ensure proper format
        if image_np.max() <= 1.0:
            image_uint8 = (image_np * 255).astype(np.uint8)
        else:
            image_uint8 = image_np.astype(np.uint8)
        
        try:
            # Save using mediapy
            media.write_image(output_path, image_uint8)
            print(f"✅ Saved decoded image: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving image {output_path}: {e}")
            return None


def collate_fn_image(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Custom collate function for batching Cosmos image data"""
    
    # Collect all keys
    keys = set()
    for item in batch:
        keys.update(item.keys())
    
    collated = {}
    
    for key in keys:
        values = [item.get(key) for item in batch if key in item]
        
        if key in ["image", "encoded_latents", "encoded_indices"]:
            # Stack tensors
            if values and isinstance(values[0], torch.Tensor):
                collated[key] = torch.stack(values)
            else:
                collated[key] = values
        else:
            # Other values (metadata, paths, etc.)
            collated[key] = values
    
    return collated


# ============ USAGE EXAMPLES ============

def preprocess_image_dataset(
    input_dir: str,
    output_dir: str,
    model_name: str = "CI8x8",
    image_size: Tuple[int, int] = (224, 224),
    num_workers: int = 1
):
    """Preprocess an entire image dataset"""
    
    config = ImageConfig(
        model_name=model_name,
        image_size=image_size,
        normalize_images=True
    )
    
    processor = CosmosImageProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        recursive=True
    )
    
    return report


def create_image_dataloader(
    data_dir: str,
    batch_size: int = 4,
    return_decoded: bool = False,
    return_codes: bool = True,
    num_workers: int = 2,
    shuffle: bool = True,
    save_decoded: bool = False,
    decoded_output_dir: str = "./decoded_images"
) -> DataLoader:
    """Create a DataLoader for Cosmos image data"""
    
    dataset = CosmosImageDataset(
        data_dir=data_dir,
        return_decoded=return_decoded,
        return_codes=return_codes,
        save_decoded=save_decoded,
        decoded_output_dir=decoded_output_dir
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn_image,
        pin_memory=torch.cuda.is_available()
    )
    
    return dataloader


def decode_and_save_all_images(
    data_dir: str,
    output_dir: str = "./decoded_images",
    max_images: Optional[int] = None
):
    """Decode and save all images in a dataset to image files"""
    
    dataset = CosmosImageDataset(
        data_dir=data_dir,
        return_decoded=False,  # Don't return tensors, just save
        return_codes=False,
        save_decoded=True,
        decoded_output_dir=output_dir
    )
    
    print(f"🖼️ Decoding and saving {len(dataset)} images to {output_dir}")
    
    max_images = max_images or len(dataset)
    saved_count = 0
    
    for i in tqdm(range(min(max_images, len(dataset))), desc="Decoding images"):
        try:
            item = dataset[i]  # This will trigger decoding and saving
            if "decoded_image_path" in item:
                saved_count += 1
        except Exception as e:
            print(f"❌ Failed to decode image {i}: {e}")
    
    print(f"✅ Successfully decoded and saved {saved_count}/{max_images} images")
    return saved_count


def example_usage():
    """Example usage of the image pipeline with decoding and saving"""
    
    # Initialize processor
    processor = CosmosImageProcessor(ImageConfig())
    
    # Example 1: Compress an image file
    print("=== COMPRESSION EXAMPLE ===")
    input_file = "/content/Cosmos-Tokenizer/test_data/image.png"
    compressed_file = input_file.replace(".png", ".pt")
    
    if os.path.exists(input_file):
        # Load and encode
        image, metadata = processor.load_image(input_file, resize=True)
        encoded_data = processor.encode_image(image, metadata)
        
        # Save
        torch.save(encoded_data, compressed_file)
        print(f"✅ Compression complete: {compressed_file}")
        
        # Example: Decode and save image
        print("\n=== DECODING EXAMPLE ===")
        decoded_image = processor.decode_image(encoded_data)
        output_image_path = "./decoded_example.png"
        saved_path = processor.save_decoded_image(decoded_image, output_image_path, metadata=metadata)
        if saved_path:
            print(f"✅ Decoded image saved: {saved_path}")
    
    # Example 2: Dataset with automatic image saving
    print("\n=== DATASET WITH IMAGE SAVING ===")
    
    try:
        # Create dataset that automatically saves decoded images
        dataset = CosmosImageDataset(
            data_dir="/content/Cosmos-Tokenizer/test_data",
            return_decoded=False,      # Don't return tensors (save memory)
            return_codes=True,         # Return encoded latents/codes
            save_decoded=True,         # Auto-save decoded images
            decoded_output_dir="./decoded_images"  # Where to save image files
        )
        
        print(f"✅ Dataset created with {len(dataset)} images")
        print("   Decoded images will be automatically saved to ./decoded_images/")
        
        # Test loading a few items (this will trigger decoding and saving)
        for i in range(min(3, len(dataset))):
            item = dataset[i]
            print(f"   Processed item {i}: {item['file_name']}")
            if 'decoded_image_path' in item:
                print(f"     → Saved to: {item['decoded_image_path']}")
        
        # Example 3: Batch decode all images
        print("\n=== BATCH DECODING ===")
        saved_count = decode_and_save_all_images(
            data_dir="/content/Cosmos-Tokenizer/test_data",
            output_dir="./all_decoded_images",
            max_images=10  # Limit for demo
        )
        print(f"✅ Batch decoded {saved_count} images")
        
    except Exception as e:
        print(f"Dataset test failed: {e}")
        print("Make sure you have compressed .pt image files first")
    
    # Example 4: DataLoader with image saving
    print("\n=== DATALOADER WITH IMAGE SAVING ===")
    
    try:
        dataloader = create_image_dataloader(
            data_dir="/content/Cosmos-Tokenizer/test_data",
            batch_size=4,
            return_decoded=True,       # Return decoded tensors
            return_codes=True,         # Return encoded codes
            save_decoded=True,         # Also save image files
            decoded_output_dir="./dataloader_decoded",
            shuffle=False,
            num_workers=0  # Avoid multiprocessing issues with GPU
        )
        
        print("Testing DataLoader with image saving...")
        for batch_idx, batch in enumerate(dataloader):
            print(f"Batch {batch_idx + 1}:")
            
            if 'encoded_latents' in batch:
                print(f"  Encoded latents shape: {batch['encoded_latents'].shape}")
            
            if 'image' in batch:
                print(f"  Decoded images shape: {batch['image'].shape}")
            
            print(f"  Files: {batch['file_name']}")
            
            # Check if images were saved
            if 'decoded_image_path' in batch:
                saved_paths = batch['decoded_image_path']
                for i, path in enumerate(saved_paths):
                    if path:
                        print(f"    Image {i} saved to: {path}")
            
            if batch_idx >= 1:  # Just test first 2 batches
                break
        
        print("✅ DataLoader with image saving test complete!")
        
    except Exception as e:
        print(f"DataLoader test failed: {e}")
        
    print("\n🖼️ Image pipeline examples completed!")
    print("📁 Check the following directories for decoded images:")
    print("   - ./decoded_images/")
    print("   - ./all_decoded_images/") 
    print("   - ./dataloader_decoded/")


# ============ BATCH PROCESSING UTILITIES ============

def batch_compress_image_directory(input_dir: str, output_dir: str, **kwargs):
    """Compress all image files in a directory"""
    config = ImageConfig(**kwargs)
    processor = CosmosImageProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=kwargs.get('num_workers', 1)
    )
    
    print(f"✅ Batch compression complete: {output_dir}")
    return report


# Run example if script is executed directly
# if __name__ == "__main__":
# example_usage()