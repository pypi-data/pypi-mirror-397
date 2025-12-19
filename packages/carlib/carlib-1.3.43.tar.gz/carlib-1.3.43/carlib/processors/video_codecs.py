import torch
from torch.utils.data import Dataset, DataLoader
import os
import glob
import json
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import gc
from dataclasses import dataclass
from datetime import datetime
from .utils import CARHandler
from .memory_utils import smart_empty_cache, batch_boundary_cache_clear, error_cache_clear

# Import Cosmos tokenizers
try:
    # import cosmos_tokenizer.video_lib
    from cosmos_tokenizer.video_lib import CausalVideoTokenizer
    TOKENIZER_AVAILABLE = True
    print("✅ Cosmos video tokenizer available")
except ImportError:
    TOKENIZER_AVAILABLE = False
    print("❌ Cosmos video tokenizer not available - please install cosmos_tokenizer")

@dataclass
class VideoConfig:
    """Configuration for video processing"""
    model_name: str = "DV4x8x8"  # CV8x8x8, DV8x16x16, etc.
    tokenizer_type: str = "video"  # Tokenizer type identifier
    max_frames: Optional[int] = None  # No frame limit - process full video
    frame_size: Tuple[int, int] = (224, 224)
    frame_skip: int = 1
    target_fps: Optional[float] = None
    normalize_frames: bool = True
    checkpoint_dir: str = "pretrained_ckpts"
    device: str = "cuda"
    dtype: str = "bfloat16"
    min_duration: Optional[float] = 1.0
    max_duration: Optional[float] = None
    output_format: str = "pt"  # "pt" or "car"
    temporal_window: int = 17  # Temporal window size for chunked encoding/decoding (reduced for memory)
    car_compression: bool = False  # Enable ZIP compression for CAR files (disabled by default for stability)
    car_compression_level: int = 6  # ZIP compression level (1=fast, 9=best compression)
    car_compression_size_limit_mb: int = 100  # Skip compression if file is larger than this (MB)

# Model configurations mapping
VIDEO_TOKENIZER_CONFIGS = {
    'CV4x8x8': 'Cosmos-0.1-Tokenizer-CV4x8x8',
    'CV8x8x8': 'Cosmos-0.1-Tokenizer-CV8x8x8', 
    'CV8x16x16': 'Cosmos-0.1-Tokenizer-CV8x16x16',
    'DV4x8x8': 'Cosmos-0.1-Tokenizer-DV4x8x8',
    'DV8x8x8': 'Cosmos-0.1-Tokenizer-DV8x8x8',
    'DV8x16x16': 'Cosmos-0.1-Tokenizer-DV8x16x16',
    'CV8x8x8-v1': 'Cosmos-1.0-Tokenizer-CV8x8x8',
    'DV8x16x16-v1': 'Cosmos-1.0-Tokenizer-DV8x16x16'
}


class CosmosVideoProcessor:
    """Simplified processor to convert video files to Cosmos tokenizer .pt files"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        # Cache for spatial padding calculations to avoid repeated computation
        self._padding_cache = {}
        
        if not TOKENIZER_AVAILABLE:
            raise ImportError("Cosmos tokenizers not available. Please install: pip install cosmos_tokenizer")
        
        # Initialize tokenizer
        self._init_tokenizer()
    
    def _get_spatial_padding(self, height: int, width: int, downsample_factor: int = 16) -> Tuple[int, int]:
        """Get cached spatial padding for given dimensions"""
        cache_key = (height, width, downsample_factor)
        
        if cache_key not in self._padding_cache:
            pad_h = (downsample_factor - height % downsample_factor) % downsample_factor
            pad_w = (downsample_factor - width % downsample_factor) % downsample_factor
            self._padding_cache[cache_key] = (pad_h, pad_w)
        
        return self._padding_cache[cache_key]
    
    def _init_tokenizer(self):
        """Initialize the Cosmos video tokenizer"""
        model_full_name = VIDEO_TOKENIZER_CONFIGS.get(self.config.model_name, self.config.model_name)
        
        encoder_ckpt = f"{self.config.checkpoint_dir}/{model_full_name}/encoder.jit"
        decoder_ckpt = f"{self.config.checkpoint_dir}/{model_full_name}/decoder.jit"
        
        if not (os.path.exists(encoder_ckpt) and os.path.exists(decoder_ckpt)):
            raise FileNotFoundError(f"Tokenizer checkpoints not found: {model_full_name}")
        
        self.tokenizer = CausalVideoTokenizer(
            checkpoint_enc=encoder_ckpt,
            checkpoint_dec=decoder_ckpt,
            device=self.config.device,
            dtype=self.config.dtype
        )
        
        print(f"✓ Video tokenizer initialized: {model_full_name}")
        print(f"  Device: {self.config.device}")
        print(f"  Max frames: {self.config.max_frames}")
        print(f"  Frame size: {self.config.frame_size}")
    
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get basic video information"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'error': f'Cannot open video: {video_path}'}
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            return {
                'path': video_path,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'aspect_ratio': width / height if height > 0 else 0
            }
        finally:
            cap.release()
    
    def load_video(self, video_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Load and preprocess video frames"""
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Check duration limits
            if self.config.min_duration and duration < self.config.min_duration:
                raise ValueError(f"Video too short: {duration}s < {self.config.min_duration}s")
            
            # Check existing duration limits
            if hasattr(self.config, 'max_duration') and self.config.max_duration and duration > self.config.max_duration:
                print(f"Video will be truncated: {duration}s > {self.config.max_duration}s")
            
            # Calculate frame sampling
            frame_skip = self.config.frame_skip
            if self.config.target_fps and fps > 0:
                frame_skip = max(1, int(fps / self.config.target_fps))
            
            frames = []
            frame_count = 0
            
            while self.config.max_frames is None or len(frames) < self.config.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Check max duration limit
                if self.config.max_duration:
                    current_time = frame_count / fps if fps > 0 else 0
                    if current_time > self.config.max_duration:
                        break
                
                if frame_count % frame_skip == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert to float32 and normalize to [0, 1] range
                    if self.config.normalize_frames:
                        frame_normalized = frame_rgb.astype(np.float32) / 255.0
                    else:
                        frame_normalized = frame_rgb.astype(np.float32)
                    
                    frames.append(frame_normalized)
                
                frame_count += 1
            
            if not frames:
                raise ValueError("No frames could be extracted")
            
            # Convert to numpy array
            frames_array = np.array(frames)
            
            # Metadata - only essential data needed for decoding
            actual_duration = len(frames) / fps if fps > 0 else 0
            metadata = {
                'original_fps': fps,  # Needed for video saving
                'extracted_frames': len(frames),  # Needed for fallback/dummy video
                'actual_duration': actual_duration  # Needed for API response
            }
            
            return frames_array, metadata
            
        finally:
            cap.release()
    
    def encode_video(self, frames: np.ndarray, metadata: Dict[str, Any], temporal_window: Optional[int] = None, base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode video frames using Cosmos tokenizer with temporal windowing"""
        if temporal_window is None:
            temporal_window = self.config.temporal_window
            
        print(f"🔄 Encoding video with {len(frames)} frames using temporal_window={temporal_window}...")
        
        # Extend metadata with base_metadata if provided
        extended_metadata = metadata.copy()
        if base_metadata is not None:
            extended_metadata.update(base_metadata)
        
        encoded_data = {
            'metadata': extended_metadata,
            'model_name': self.config.model_name,  # Needed for tokenizer selection
            'temporal_window': temporal_window,  # Needed for decoding
            'config': {
                'original_spatial_size': (frames.shape[1], frames.shape[2])  # (H, W) for cropping padding
            },
            'chunk_info': []  # Needed for chunked decoding
        }
        
        try:
            num_frames = len(frames)
            # Initialize storage that will be concatenated at the end (not a growing list)
            processed_chunks = []
            total_expected_size = 0
            
            # Process in temporal chunks
            latent_start_idx = 0
            for chunk_idx in range(0, num_frames, temporal_window):
                end_idx = min(chunk_idx + temporal_window, num_frames)
                chunk_frames = frames[chunk_idx:end_idx]
                actual_chunk_size = end_idx - chunk_idx
                
                # Pad chunk to consistent temporal window size to avoid dimension mismatches
                if actual_chunk_size < temporal_window:
                    print(f"  Padding chunk {chunk_idx//temporal_window + 1}: {actual_chunk_size} -> {temporal_window} frames")
                    # Repeat the last frame to pad to temporal_window size
                    last_frame = chunk_frames[-1:] if len(chunk_frames) > 0 else chunk_frames[:1]
                    padding_needed = temporal_window - actual_chunk_size
                    padding_frames = np.repeat(last_frame, padding_needed, axis=0)
                    chunk_frames = np.concatenate([chunk_frames, padding_frames], axis=0)
                
                print(f"  Encoding chunk {chunk_idx//temporal_window + 1}: frames {chunk_idx}-{end_idx-1} (size: {chunk_frames.shape[0]})")
                
                # Prepare chunk for tokenizer
                chunk_tensor = self._prepare_video_for_tokenizer(chunk_frames)
                
                # Encode chunk
                with torch.no_grad():
                    try:
                        encoded_output = self.tokenizer.encode(chunk_tensor)
                    except RuntimeError as e:
                        print(f"❌ Encoding failed for chunk tensor shape: {chunk_tensor.shape}")
                        print(f"❌ Error details: {e}")
                        # Try with different downsampling factor if the current one fails
                        if "The size of tensor a" in str(e) and "must match the size of tensor b" in str(e):
                            print(f"❌ Tensor dimension mismatch detected - this suggests incorrect spatial alignment")
                            print(f"❌ Current chunk tensor shape: {chunk_tensor.shape} = (B, C, T, H, W)")
                            print(f"❌ Spatial dimensions H={chunk_tensor.shape[3]}, W={chunk_tensor.shape[4]}")
                        raise
                    
                    # Clear chunk tensor from GPU memory immediately
                    del chunk_tensor
                    # Use smart cache clearing instead of aggressive clearing
                    smart_empty_cache()
                
                # Handle different tokenizer outputs
                if 'DV' in self.config.model_name:
                    if isinstance(encoded_output, tuple) and len(encoded_output) == 2:
                        indices, discrete_codes = encoded_output
                        # Handle batch dimension properly with validation
                        chunk_indices = indices.cpu()
                        if chunk_indices.dim() == 4:
                            chunk_indices = chunk_indices.squeeze(0)  # Remove batch dim
                        elif chunk_indices.dim() != 3:
                            raise ValueError(f"Unexpected DV indices shape: {tuple(chunk_indices.shape)} (expected [T,H,W] or [B,T,H,W])")
                        
                        # Store chunk info BEFORE appending to avoid keeping references
                        indices_shape = chunk_indices.shape
                        indices_end_idx = latent_start_idx + indices_shape[0]  # temporal dimension for indices
                        
                        # Immediately move to processed_chunks to avoid growing list references
                        processed_chunks.append(chunk_indices.clone())  # Clone to detach from computation graph
                        
                        # Clear GPU memory immediately after moving to CPU
                        del encoded_output, indices, discrete_codes, chunk_indices
                        # Use smart cache clearing - only when needed
                        smart_empty_cache()
                        encoded_data['chunk_info'].append({
                            'original_start': chunk_idx,
                            'original_end': end_idx,
                            'actual_frames': actual_chunk_size,  # How many real (non-padded) frames
                            'latent_start': latent_start_idx,
                            'latent_end': indices_end_idx
                        })
                        latent_start_idx = indices_end_idx
                        total_expected_size += indices_shape[0]
                    else:
                        raise ValueError(f"Expected tuple output for DV tokenizer, got {type(encoded_output)}")
                else:
                    # CV tokenizer
                    if isinstance(encoded_output, torch.Tensor):
                        chunk_latents = encoded_output.cpu().squeeze(0) if encoded_output.dim() == 5 else encoded_output.cpu()
                    elif isinstance(encoded_output, tuple) and len(encoded_output) == 1:
                        chunk_latents = encoded_output[0].cpu().squeeze(0) if encoded_output[0].dim() == 5 else encoded_output[0].cpu()
                    else:
                        raise ValueError(f"Unexpected CV output format: {type(encoded_output)}")
                    
                    # Store chunk info BEFORE appending to avoid keeping references
                    latents_shape = chunk_latents.shape
                    latent_end_idx = latent_start_idx + latents_shape[1]  # temporal dimension
                    
                    # Immediately move to processed_chunks to avoid growing list references
                    processed_chunks.append(chunk_latents.clone())  # Clone to detach from computation graph
                    
                    # Clear GPU memory immediately after getting chunk_latents
                    del encoded_output, chunk_latents
                    # Use smart cache clearing to reduce overhead
                    smart_empty_cache()
                    encoded_data['chunk_info'].append({
                        'original_start': chunk_idx,
                        'original_end': end_idx,
                        'actual_frames': actual_chunk_size,  # How many real (non-padded) frames
                        'latent_start': latent_start_idx,
                        'latent_end': latent_end_idx
                    })
                    latent_start_idx = latent_end_idx
                    total_expected_size += latents_shape[1]
            
            # Efficiently concatenate all chunks at once
            if processed_chunks:
                if 'DV' in self.config.model_name:
                    # For DV: concatenate indices along time dimension (dim=0)
                    final_tensor = torch.cat(processed_chunks, dim=0)
                    print(f"✅ DV - Encoded indices: {final_tensor.shape}")
                    encoded_data['encoded_indices'] = final_tensor
                else:
                    # For CV: concatenate latents along time dimension (dim=1)
                    final_tensor = torch.cat(processed_chunks, dim=1)
                    print(f"✅ CV - Encoded latents: {final_tensor.shape}")
                    encoded_data['encoded_latents'] = final_tensor
                
                # Clear processed chunks immediately after concatenation
                del processed_chunks, final_tensor
                gc.collect()
                smart_empty_cache(force=True)
            
            # Get chunk count from stored metadata (lists already deleted)
            chunk_count = len(encoded_data.get('chunk_info', []))
            print(f"✅ Video encoding successful with {chunk_count} chunks!")
            
            # Final memory cleanup and logging
            gc.collect()
            # Only clear cache at end of processing, not after every chunk
            smart_empty_cache(force=True)
            
            # Log GPU memory usage
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
                memory_reserved = torch.cuda.memory_reserved() / 1024**3   # GB
                print(f"📊 GPU Memory - Allocated: {memory_allocated:.2f}GB, Reserved: {memory_reserved:.2f}GB")
            
            return encoded_data
            
        except Exception as e:
            print(f"❌ Failed to encode video: {e}")
            # Emergency memory cleanup on error
            error_cache_clear()
            gc.collect()
            import traceback
            traceback.print_exc()
            raise
    
    def decode_video(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode compressed video data back to frames using temporal windowing"""
        # Check if model name in encoded data differs from current tokenizer
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        if encoded_model_name and encoded_model_name != self.config.model_name:
            print(f"🔄 Model mismatch detected: {self.config.model_name} -> {encoded_model_name}")
            print(f"   Reinitializing tokenizer...")
            # Update config and reinitialize tokenizer
            self.config.model_name = encoded_model_name
            self._init_tokenizer()
        
        # Get temporal window size used during encoding
        temporal_window = encoded_data.get('temporal_window', 17)
        # Get original spatial dimensions for cropping padding
        original_spatial_size = encoded_data.get('config', {}).get('original_spatial_size')
        print(f"🔄 Decoding video using temporal_window={temporal_window}...")
        if original_spatial_size:
            print(f"🔄 Original spatial size for cropping: {original_spatial_size}")
        
        
        # Emergency memory cleanup before decoding
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        gc.collect()
        
        # Move data to correct device and decode in chunks
        if 'encoded_indices' in encoded_data:
            # DV tokenizer - decode using indices (discrete tokens)
            # Keep data on CPU initially to save GPU memory
            indices_cpu = encoded_data['encoded_indices']
            chunk_info = encoded_data.get('chunk_info', [])
            
            if not chunk_info:
                # Fallback: decode entire sequence if no chunk info
                print(f"  No chunk info - decoding entire DV sequence: {indices_cpu.shape}")
                # Move to GPU and ensure proper dtype for model (DV models expect long for embeddings)
                indices = indices_cpu.to(self.config.device)
                if indices.dtype != torch.long:
                    indices = indices.long()
                if indices.dim() == 3:
                    indices = indices.unsqueeze(0)  # Add batch dimension
                
                with torch.no_grad():
                    decoded_tensor = self.tokenizer.decode(indices)
                    # Clear GPU memory immediately
                    del indices
                    # Use smart cache clearing to reduce overhead
                    smart_empty_cache()
                
                processed_video = self._process_decoded_video(decoded_tensor, original_spatial_size)
                print(f"✅ Decoded DV video: {processed_video.shape}")
                return processed_video
            
            # Chunked decoding using stored chunk boundaries
            print(f"  Decoding {len(chunk_info)} DV chunks using original boundaries...")
            all_decoded_chunks = []
            
            for i, chunk in enumerate(chunk_info):
                latent_start = chunk['latent_start']
                latent_end = chunk['latent_end']
                original_start = chunk['original_start']
                original_end = chunk['original_end']
                
                print(f"    Decoding DV chunk {i+1}: latent frames {latent_start}-{latent_end-1} -> original frames {original_start}-{original_end-1}")
                
                # Extract chunk from CPU data using latent boundaries
                chunk_indices_cpu = indices_cpu[latent_start:latent_end]  # (chunk_T, H, W)
                
                # Validate chunk has valid dimensions
                if chunk_indices_cpu.shape[0] == 0:
                    print(f"        Skipping empty chunk with shape {chunk_indices_cpu.shape}")
                    continue
                
                # Ensure contiguous memory layout before moving to device
                chunk_indices_np = np.ascontiguousarray(chunk_indices_cpu.numpy())
                chunk_indices = torch.from_numpy(chunk_indices_np).to(self.config.device)
                # DV models expect long tensors for indices (for embedding lookups)
                if chunk_indices.dtype != torch.long:
                    chunk_indices = chunk_indices.long()
                
                if chunk_indices.dim() == 3:
                    chunk_indices = chunk_indices.unsqueeze(0)  # Add batch dimension
                
                # Decode chunk using indices
                with torch.no_grad():
                    decoded_chunk = self.tokenizer.decode(chunk_indices)
                
                # Clear chunk data from GPU memory immediately
                del chunk_indices_cpu, chunk_indices
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                gc.collect()
                
                # Process chunk output
                processed_chunk = self._process_decoded_video(decoded_chunk, original_spatial_size)
                
                # Trim padded frames if necessary
                actual_frames = chunk.get('actual_frames', processed_chunk.shape[0])
                if actual_frames < processed_chunk.shape[0]:
                    print(f"Trimming padded frames: {processed_chunk.shape[0]} -> {actual_frames}")
                    processed_chunk = processed_chunk[:actual_frames]
                
                all_decoded_chunks.append(processed_chunk.clone())  # Clone to avoid reference issues
                
                # Additional cleanup after processing
                del decoded_chunk, processed_chunk
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            # Concatenate all decoded chunks along time dimension
            if len(all_decoded_chunks) == 1:
                final_video = all_decoded_chunks[0]
            else:
                final_video = torch.cat(all_decoded_chunks, dim=0)  # Concatenate along time (T, H, W, C)
            
            print(f"✅ Decoded DV video: {final_video.shape} from {len(all_decoded_chunks)} chunks")
            return final_video
            
        elif 'encoded_latents' in encoded_data:
            # CV tokenizer - decode using the same chunks as encoding
            # Keep data on CPU initially to save GPU memory
            latents_cpu = encoded_data['encoded_latents']
            chunk_info = encoded_data.get('chunk_info', [])
            
            if not chunk_info:
                # Fallback: decode entire sequence if no chunk info
                print(f"  No chunk info - decoding entire sequence: {latents_cpu.shape}")
                # Move to GPU and ensure proper dtype for model
                latents = latents_cpu.to(self.config.device)
                target_dtype = getattr(torch, self.config.dtype)
                if latents.dtype != target_dtype:
                    latents = latents.to(target_dtype)
                if latents.dim() == 4:
                    latents = latents.unsqueeze(0)  # Add batch dimension
                
                with torch.no_grad():
                    decoded_tensor = self.tokenizer.decode(latents)
                    # Clear GPU memory immediately
                    del latents
                    # Use smart cache clearing to reduce overhead
                    smart_empty_cache()
                
                processed_video = self._process_decoded_video(decoded_tensor, original_spatial_size)
                print(f"✅ Decoded video: {processed_video.shape}")
                return processed_video
            
            # Chunked decoding using stored chunk boundaries
            print(f"  Decoding {len(chunk_info)} chunks using original boundaries...")
            all_decoded_chunks = []
            
            for i, chunk in enumerate(chunk_info):
                latent_start = chunk['latent_start']
                latent_end = chunk['latent_end']
                
                print(f"    Decoding chunk {i+1}: latent frames {latent_start}-{latent_end-1} -> original frames {chunk['original_start']}-{chunk['original_end']-1}")
                
                # Extract chunk from CPU data and move to GPU only when needed
                chunk_latents_cpu = latents_cpu[:, latent_start:latent_end]  # (C, chunk_T, H, W)
                
                # Validate chunk has valid dimensions
                if chunk_latents_cpu.shape[1] == 0:
                    print(f"        Skipping empty chunk with shape {chunk_latents_cpu.shape}")
                    continue
                
                chunk_latents = chunk_latents_cpu.to(self.config.device)
                # CV models expect specific dtype for latents
                target_dtype = getattr(torch, self.config.dtype)
                if chunk_latents.dtype != target_dtype:
                    chunk_latents = chunk_latents.to(target_dtype)
                
                if chunk_latents.dim() == 4:
                    chunk_latents = chunk_latents.unsqueeze(0)  # Add batch dimension
                
                # Decode chunk
                with torch.no_grad():
                    decoded_chunk = self.tokenizer.decode(chunk_latents)
                
                # Clear chunk data from GPU memory immediately
                del chunk_latents_cpu, chunk_latents
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                gc.collect()
                
                # Process chunk output
                processed_chunk = self._process_decoded_video(decoded_chunk, original_spatial_size)
                
                # Trim padded frames if necessary
                actual_frames = chunk.get('actual_frames', processed_chunk.shape[0])
                if actual_frames < processed_chunk.shape[0]:
                    print(f"        Trimming padded frames: {processed_chunk.shape[0]} -> {actual_frames}")
                    processed_chunk = processed_chunk[:actual_frames]
                
                all_decoded_chunks.append(processed_chunk.clone())  # Clone to avoid reference issues
                
                # Additional cleanup after processing
                del decoded_chunk, processed_chunk
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            # Concatenate all decoded chunks along time dimension
            if len(all_decoded_chunks) == 1:
                final_video = all_decoded_chunks[0]
            else:
                final_video = torch.cat(all_decoded_chunks, dim=0)  # Concatenate along time (T, H, W, C)
            
            print(f"✅ Decoded video: {final_video.shape} from {len(all_decoded_chunks)} chunks")
            return final_video
        else:
            raise ValueError("No encoded data found for decoding")
    
    def _prepare_video_for_tokenizer(self, frames: np.ndarray) -> torch.Tensor:
        """Prepare video tensor for CausalVideoTokenizer with minimal memory allocation"""
        # Ensure spatial dimensions are compatible with model downsampling
        # The model has multiple downsampling layers that reduce dimensions by factors of 2
        # We need to ensure H and W are divisible by the total downsampling factor
        original_shape = frames.shape  # (T, H, W, 3)
        T, H, W, C = original_shape
        
        # For DV models, there are typically 3-4 downsampling stages, so we need divisibility by 8 or 16
        # Let's try 16 first (2^4) to handle multiple downsampling layers
        downsample_factor = 16
        
        # Get cached padding calculation (avoids repeated computation)
        pad_h, pad_w = self._get_spatial_padding(H, W, downsample_factor)
        
        print(f"📐 Input spatial dimensions: ({H}, {W})")
        print(f"📐 Downsample factor: {downsample_factor}")
        print(f"📐 Padding needed: H+{pad_h}, W+{pad_w}")
        
        if pad_h > 0 or pad_w > 0:
            print(f"📐 Padding spatial dimensions: ({H}, {W}) -> ({H + pad_h}, {W + pad_w})")
            # Pad the spatial dimensions (H, W) with edge replication to avoid black borders
            frames_padded = np.pad(frames, ((0, 0), (0, pad_h), (0, pad_w), (0, 0)), mode='edge')
        else:
            frames_padded = frames
            print(f"📐 No spatial padding needed - dimensions already aligned")
        
        # Normalize to [-1, 1] range (tokenizer expects this)
        frames_normalized = frames_padded * 2.0 - 1.0
        
        # Convert to tensor: (T, H, W, 3) -> (1, 3, T, H, W) with minimal intermediate copies
        frames_tensor = torch.from_numpy(frames_normalized).float()
        del frames_normalized, frames_padded  # Free numpy arrays immediately
        
        # Combine permutations to minimize intermediate tensors
        # (T, H, W, 3) -> (T, 3, H, W) -> (1, T, 3, H, W) -> (1, 3, T, H, W)
        frames_tensor = frames_tensor.permute(0, 3, 1, 2).unsqueeze(0).permute(0, 2, 1, 3, 4)
        
        # Move to device and convert dtype in one operation
        device = self.config.device
        dtype = getattr(torch, self.config.dtype)
        frames_tensor = frames_tensor.to(device=device, dtype=dtype, non_blocking=True)
        
        print(f"📹 Prepared video tensor: {frames_tensor.shape} on {frames_tensor.device}")
        print(f"   Value range: [{frames_tensor.min():.3f}, {frames_tensor.max():.3f}]")
        
        # Force immediate GPU memory allocation if needed
        if torch.cuda.is_available() and frames_tensor.device.type == 'cuda':
            torch.cuda.synchronize()  # Ensure tensor is fully allocated
        
        return frames_tensor
    
    def _process_decoded_video(self, decoded_tensor: torch.Tensor, original_spatial_size: tuple = None) -> torch.Tensor:
        """Process decoded video tensor to standard format"""
        # Handle batch dimension
        if decoded_tensor.dim() == 5 and decoded_tensor.shape[0] == 1:
            video_tensor = decoded_tensor.squeeze(0)  # (1,3,T,H,W) -> (3,T,H,W)
        else:
            video_tensor = decoded_tensor
        
        # Convert from (3,T,H,W) to (T,H,W,3)
        if video_tensor.dim() == 4 and video_tensor.shape[0] == 3:
            video_tensor = video_tensor.permute(1, 2, 3, 0)  # (3,T,H,W) -> (T,H,W,3)
        
        # Convert from [-1,1] to [0,1] range
        video_tensor = (video_tensor + 1.0) / 2.0
        video_tensor = torch.clamp(video_tensor, 0, 1)
        video_tensor = video_tensor.cpu().float()
        
        # Crop spatial padding if original size was provided
        if original_spatial_size is not None:
            orig_h, orig_w = original_spatial_size
            current_h, current_w = video_tensor.shape[1], video_tensor.shape[2]
            if current_h > orig_h or current_w > orig_w:
                print(f"📐 Cropping spatial padding: ({current_h}, {current_w}) -> ({orig_h}, {orig_w})")
                video_tensor = video_tensor[:, :orig_h, :orig_w, :]
        
        print(f"Processed decoded video: {video_tensor.shape}, range: [{video_tensor.min():.3f}, {video_tensor.max():.3f}]")
        return video_tensor
    
    def save_decoded_video(self, video_tensor: torch.Tensor, output_path: str, fps: float = 30.0, metadata: Dict[str, Any] = None) -> str:
        """Save decoded video tensor to MP4 file
        
        Args:
            video_tensor: Decoded video with shape (T, H, W, 3) in [0, 1] range
            output_path: Path to save the MP4 file
            fps: Frame rate for the output video
            metadata: Optional metadata for fps information
            
        Returns:
            Path to saved video file
        """
        # Use original fps if available in metadata
        if metadata:
            original_fps = metadata.get('original_fps', fps)
            fps = original_fps if original_fps > 0 else fps
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to numpy and scale to [0, 255]
        if isinstance(video_tensor, torch.Tensor):
            frames_np = video_tensor.numpy()
        else:
            frames_np = video_tensor
        
        # Ensure proper range and type
        if frames_np.max() <= 1.0:
            frames_uint8 = (frames_np * 255).astype(np.uint8)
        else:
            frames_uint8 = frames_np.astype(np.uint8)
        
        # Get video properties
        num_frames, height, width = frames_uint8.shape[:3]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            print(f"❌ Failed to create video writer for {output_path}")
            return None
        
        try:
            # Write frames
            for i in range(num_frames):
                frame = frames_uint8[i]
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                writer.write(frame_bgr)
            
            writer.release()
            print(f"✅ Saved decoded video: {output_path} ({num_frames} frames @ {fps:.1f}fps)")
            return output_path
            
        except Exception as e:
            print(f"❌ Error writing video {output_path}: {e}")
            writer.release()
            # Clean up partial file
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
        
    def _dummy_decode_output(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Create dummy decoded output when decoding fails"""
        metadata = encoded_data.get('metadata', {})
        num_frames = metadata.get('extracted_frames', 8)
        height, width = self.config.frame_size
        
        dummy_video = torch.zeros(num_frames, height, width, 3).float()
        print(f"⚠️ Created dummy decoded video: {dummy_video.shape}")
        return dummy_video
    
    def load_from_car(self, car_path: str) -> Dict[str, Any]:
        """Load compressed audio data from CAR format"""
        with open(car_path, 'rb') as f:
            car_data = f.read()
        encoded_data, metadata = CARHandler.car_to_np(car_data)
        return {
            'status': 'success',
            'data': encoded_data,
            'metadata': metadata,
            'file_path': car_path
        }
    
    def process_single_file(self, video_path: str, output_path: Optional[str]=None, base_metadata: Optional[Dict[str, Any]] = None,
                           save_car: bool = True, save_hdf5: bool = False, save_webdataset: bool = False, save_tfrecord: bool = False) -> Dict[str, Any]:
        """Process a single video file and save in selected formats
        
        Args:
            video_path: Path to input video
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
                base_output = os.path.splitext(video_path)[0]
            else:
                base_output = os.path.splitext(output_path)[0]
            
            # Load video
            frames, metadata = self.load_video(video_path)
            
            # Encode and get compression ratio
            encoded_data = self.encode_video(frames, metadata, base_metadata=base_metadata)
            
            # Calculate compression ratio for logging (was removed from encoded_data to save space)
            compression_ratio = 'unknown'
            if 'encoded_latents' in encoded_data:
                original_elements = np.prod(frames.shape)
                compressed_elements = np.prod(encoded_data['encoded_latents'].shape)
                compression_ratio = original_elements / compressed_elements
            
            # Calculate original size before deleting frames
            original_size = np.prod(frames.shape) * 4  # float32 = 4 bytes
            
            # Clear frames from memory immediately after encoding
            del frames
            gc.collect()  # Force garbage collection to free CPU memory
            
            # Prepare metadata for exports
            export_metadata = {
                "media_type": "video",
                "processor": "CosmosVideoProcessor", 
                "model_name": self.config.model_name,
                "duration": metadata['actual_duration'],
                "frames": metadata['extracted_frames']
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
                    sample_key = os.path.splitext(os.path.basename(video_path))[0]
                    CARHandler.np_to_webdataset(encoded_data, webdataset_path, sample_key=sample_key, optimize_dtypes=True)
                    saved_files['webdataset'] = webdataset_path
                    print(f"✅ Saved WebDataset: {webdataset_path}")
                except Exception as e:
                    print(f"❌ Failed to save WebDataset: {e}")
            
            # 4. Save as TFRecord format
            if save_tfrecord:
                try:
                    tfrecord_path = f"{base_output}.tfrecord"
                    sample_key = os.path.splitext(os.path.basename(video_path))[0]
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
                    'temporal_ratio': compression_ratio,
                    'file_size_ratio': file_ratio,
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': compressed_size / (1024 * 1024),
                    'output_formats': list(saved_files.keys())
                }
                
                print(f"   Temporal compression: {compression_info['temporal_ratio']:.0f}:1" if isinstance(compression_info['temporal_ratio'], float) else f"   Temporal compression: {compression_info['temporal_ratio']}")
                print(f"   File size: {compression_info['original_size_mb']:.1f}MB → {compression_info['compressed_size_mb']:.1f}MB ({file_ratio:.1f}x)")
            else:
                compression_info = {
                    'temporal_ratio': compression_ratio,
                    'file_size_ratio': 'N/A',
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': 'N/A',
                    'output_formats': list(saved_files.keys())
                }
                print(f"   Temporal compression: {compression_info['temporal_ratio']:.0f}:1" if isinstance(compression_info['temporal_ratio'], float) else f"   Temporal compression: {compression_info['temporal_ratio']}")
            
            return {
                'status': 'success',
                'input_path': video_path,
                'output_files': saved_files,
                'duration': metadata['actual_duration'],
                'frames': metadata['extracted_frames'],
                'compression': compression_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'input_path': video_path,
                'error': str(e)
            }
    
    def _process_batch(self, task_batch: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        Process a batch of video files in a single process.
        
        This reduces process spawn overhead by processing multiple files per worker.
        """
        batch_results = []
        
        for video_path, output_path in task_batch:
            try:
                result = self.process_single_file(video_path, output_path)
                batch_results.append(result)
            except Exception as e:
                # Handle individual file errors gracefully
                batch_results.append({
                    'status': 'error',
                    'input_path': video_path,
                    'error': str(e)
                })
        
        return batch_results
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        video_extensions: Tuple[str, ...] = ('.mp4', '.avi', '.mov', '.mkv', '.webm'),
        num_workers: int = 1,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all video files in a directory"""
        
        # Find video files efficiently with single glob pattern
        # Create pattern like **/*.{mp4,MP4,avi,AVI,mov,MOV,mkv,MKV,webm,WEBM}
        exts_lower = [ext.lstrip('.') for ext in video_extensions]
        exts_upper = [ext.upper() for ext in exts_lower]
        all_exts = ','.join(exts_lower + exts_upper)
        
        pattern = "**/*" if recursive else "*"
        glob_pattern = os.path.join(input_dir, f"{pattern}.{{{all_exts}}}")
        
        video_files = glob.glob(glob_pattern, recursive=recursive)
        
        print(f"Found {len(video_files)} video files")
        
        if not video_files:
            return {'status': 'no_files', 'processed': 0, 'errors': 0}
        
        # Prepare tasks
        tasks = []
        file_ext = ".car" if self.config.output_format == "car" else ".pt"
        for video_path in video_files:
            rel_path = os.path.relpath(video_path, input_dir)
            name_without_ext = os.path.splitext(rel_path)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}{file_ext}")
            tasks.append((video_path, output_path))
        
        # Process files
        results = []
        successful = 0
        errors = 0
        
        if num_workers == 1:
            # Single-threaded processing
            for video_path, output_path in tqdm(tasks, desc="Processing videos"):
                result = self.process_single_file(video_path, output_path)
                results.append(result)
                
                if result['status'] == 'success':
                    successful += 1
                elif result['status'] == 'error':
                    errors += 1
        else:
            # Optimized multi-process processing with batching
            print(f"Processing with {num_workers} workers using batched processing...")
            
            # Calculate optimal chunk size: avoid too many small batches or too few large ones
            chunk_size = max(1, min(10, len(tasks) // (num_workers * 2)))
            print(f"Using chunk size: {chunk_size} files per batch")
            
            # Create batches of tasks
            task_batches = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]
            
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                future_to_batch = {
                    executor.submit(self._process_batch, batch): batch
                    for batch in task_batches
                }
                
                for future in tqdm(as_completed(future_to_batch), total=len(task_batches), desc="Processing batches"):
                    batch_results = future.result()
                    results.extend(batch_results)
                    
                    # Count results from this batch
                    for result in batch_results:
                        if result['status'] == 'success':
                            successful += 1
                        elif result['status'] == 'error':
                            errors += 1
        
        # Save processing report
        report = {
            'config': self.config.__dict__,
            'input_dir': input_dir,
            'output_dir': output_dir,
            'total_files': len(video_files),
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


class CosmosVideoDataset(Dataset):
    """PyTorch Dataset for loading Cosmos tokenized video files"""
    
    def __init__(
        self,
        data_dir: str,
        return_decoded: bool = False,
        return_codes: bool = True,
        max_frames: Optional[int] = None,
        device: str = "cpu",
        cache_decoded: bool = False,
        save_decoded: bool = False,
        decoded_output_dir: str = "./decoded_videos"
    ):
        """Initialize the dataset
        
        Args:
            data_dir: Directory containing .pt files
            return_decoded: Return decoded video frames
            return_codes: Return encoded video codes/latents
            max_frames: Maximum number of frames (for padding/truncation)
            device: Device to load tensors on
            cache_decoded: Cache decoded videos in memory (use carefully!)
            save_decoded: Save decoded videos to MP4 files
            decoded_output_dir: Directory to save decoded MP4 files
        """
        self.data_dir = data_dir
        self.return_decoded = return_decoded
        self.return_codes = return_codes
        self.max_frames = max_frames
        self.device = device
        self.cache_decoded = cache_decoded
        self.save_decoded = save_decoded
        self.decoded_output_dir = decoded_output_dir
        
        # Create output directory if saving decoded videos
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
                # Use optimized CAR loading
                sample_data, _ = CARHandler.car_to_np(car_data)
            else:
                sample_data = torch.load(sample_file, map_location='cpu')
            config_dict = sample_data.get('config', {})
            
            print("Loading Cosmos video tokenizer for decoding...")
            try:
                model_name = config_dict.get('model_name', 'CV8x8x8')
                model_full_name = VIDEO_TOKENIZER_CONFIGS.get(model_name, model_name)
                checkpoint_dir = config_dict.get('checkpoint_dir', 'pretrained_ckpts')
                
                encoder_ckpt = f"{checkpoint_dir}/{model_full_name}/encoder.jit"
                decoder_ckpt = f"{checkpoint_dir}/{model_full_name}/decoder.jit"
                
                if os.path.exists(encoder_ckpt) and os.path.exists(decoder_ckpt):
                    # from cosmos_tokenizer.video_lib import CausalVideoTokenizer
                    self.tokenizer = CausalVideoTokenizer(
                        checkpoint_enc=encoder_ckpt,
                        checkpoint_dec=decoder_ckpt,
                        device=device,
                        dtype=config_dict.get('dtype', 'bfloat16')
                    )
                    self.tokenizer.eval()
                    print(f"✓ Tokenizer loaded: {model_name}")
                else:
                    print(f"⚠️ Tokenizer checkpoints not found, decoding disabled")
                    self.return_decoded = False
                    self.save_decoded = False
            except Exception as e:
                print(f"⚠️ Failed to load tokenizer: {e}")
                self.return_decoded = False
                self.save_decoded = False
        
        # Cache for decoded videos
        self.decoded_cache = {} if cache_decoded else None
        
        # Track saved videos to avoid re-saving
        self.saved_videos = set()
        
        # Load metadata from first file
        sample_file = self.file_paths[0]
        if sample_file.endswith('.car'):
            with open(sample_file, 'rb') as f:
                car_data = f.read()
            # Use optimized CAR loading
            sample_data, _ = CARHandler.car_to_np(car_data)
        else:
            sample_data = torch.load(sample_file, map_location='cpu')
        self.model_name = sample_data.get('model_name', 'unknown')
        
        print(f"✓ Dataset ready: {len(self)} videos")
        print(f"   Model: {self.model_name}")
        print(f"   Returns: {'decoded' if return_decoded else ''} {'codes' if return_codes else ''}")
        if self.save_decoded:
            print(f"   Saving decoded videos to: {self.decoded_output_dir}")
    
    
    def __len__(self) -> int:
        return len(self.file_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        file_path = self.file_paths[idx]
        
        # Load encoded data based on file extension
        if file_path.endswith('.car'):
            # Load CAR file with optimized loading
            with open(file_path, 'rb') as f:
                car_data = f.read()
            encoded_data, metadata = CARHandler.car_to_np(car_data)
        else:
            # Load PT file
            encoded_data = torch.load(file_path, map_location='cpu')
        
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "metadata": encoded_data["metadata"]
        }
        
        # Return encoded codes if requested
        if self.return_codes:
            if 'encoded_latents' in encoded_data:
                latents = encoded_data['encoded_latents']
                
                # Handle sequence length
                if self.max_frames:
                    if latents.shape[1] > self.max_frames:  # Assuming shape is (C, T, H, W)
                        latents = latents[:, :self.max_frames]
                    elif latents.shape[1] < self.max_frames:
                        pad_frames = self.max_frames - latents.shape[1]
                        pad_shape = (latents.shape[0], pad_frames, latents.shape[2], latents.shape[3])
                        padding = torch.zeros(pad_shape, dtype=latents.dtype)
                        latents = torch.cat([latents, padding], dim=1)
                
                result["encoded_latents"] = latents  # Keep on CPU, move to device in collate_fn
            
            if 'encoded_indices' in encoded_data:
                indices = encoded_data['encoded_indices']
                
                # Handle sequence length for indices
                if self.max_frames:
                    if indices.shape[0] > self.max_frames:  # Assuming shape is (T, H, W)
                        indices = indices[:self.max_frames]
                    elif indices.shape[0] < self.max_frames:
                        pad_frames = self.max_frames - indices.shape[0]
                        pad_shape = (pad_frames, indices.shape[1], indices.shape[2])
                        padding = torch.zeros(pad_shape, dtype=indices.dtype)
                        indices = torch.cat([indices, padding], dim=0)
                
                result["encoded_indices"] = indices  # Keep on CPU, move to device in collate_fn
        
        # Handle decoded video (for returning and/or saving)
        decoded_video = None
        if self.return_decoded or self.save_decoded:
            # Check cache first
            if self.cache_decoded and idx in self.decoded_cache:
                decoded_video = self.decoded_cache[idx]
            else:
                # Decode video
                if self.tokenizer is None:
                    # Create dummy decoded video - use default dimensions if not available
                    num_frames = encoded_data["metadata"].get("extracted_frames", 8)
                    # Use reasonable default dimensions since frame_size is no longer stored
                    height, width = 224, 224
                    decoded_video = torch.zeros(num_frames, height, width, 3).float()
                    print(f"⚠️ Created dummy decoded video: {decoded_video.shape}")
                else:
                    try:
                        decoded_video = self._decode_video_data(encoded_data)
                    except Exception as e:
                        print(f"⚠️ Decoding failed: {e}")
                        num_frames = encoded_data["metadata"].get("extracted_frames", 8)
                        # Use reasonable default dimensions since frame_size is no longer stored
                        height, width = 224, 224
                        decoded_video = torch.zeros(num_frames, height, width, 3).float()
                
                # Cache if enabled
                if self.cache_decoded:
                    self.decoded_cache[idx] = decoded_video
            
            # Save decoded video if requested
            if self.save_decoded and idx not in self.saved_videos:
                video_name = os.path.splitext(result["file_name"])[0]
                output_path = os.path.join(self.decoded_output_dir, f"{video_name}_decoded.mp4")
                
                # Get original fps from metadata
                metadata = encoded_data.get("metadata", {})
                fps = metadata.get("original_fps", 30.0)
                
                saved_path = self.save_decoded_video(decoded_video, output_path, fps, metadata)
                if saved_path:
                    result["decoded_video_path"] = saved_path
                    self.saved_videos.add(idx)
        
        # Return decoded video tensor if requested
        if self.return_decoded and decoded_video is not None:
            # Handle video length
            if self.max_frames:
                if decoded_video.shape[0] > self.max_frames:
                    decoded_video = decoded_video[:self.max_frames]
                elif decoded_video.shape[0] < self.max_frames:
                    pad_frames = self.max_frames - decoded_video.shape[0]
                    pad_shape = (pad_frames, decoded_video.shape[1], decoded_video.shape[2], decoded_video.shape[3])
                    padding = torch.zeros(pad_shape, dtype=decoded_video.dtype)
                    decoded_video = torch.cat([decoded_video, padding], dim=0)
            
            result["video"] = decoded_video  # Keep on CPU, move to device in collate_fn
        
        return result
    
    def _decode_video_data(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode video data using the tokenizer"""
        config = encoded_data.get('config', {})
        model_name = encoded_data.get('model_name', config.get('model_name', 'CV8x8x8'))
        
        # Prepare latents for decoding
        if 'DV' in model_name and 'encoded_indices' in encoded_data:
            # For DV models, use indices with contiguous memory layout
            indices_tensor = encoded_data['encoded_indices']
            if isinstance(indices_tensor, torch.Tensor):
                indices_np = np.ascontiguousarray(indices_tensor.cpu().numpy())
                latents = torch.from_numpy(indices_np).to(self.device)
            else:
                latents = indices_tensor.to(self.device)
            # DV models expect long tensors for indices (for embedding lookups)
            if latents.dtype != torch.long:
                latents = latents.long()
            if latents.dim() == 3:
                latents = latents.unsqueeze(0)  # Add batch dimension
        elif 'encoded_latents' in encoded_data:
            # For CV models, use latents
            latents = encoded_data['encoded_latents'].to(self.device)
            # Convert to correct dtype for CV models
            target_dtype = getattr(torch, config.get('dtype', 'bfloat16'))
            if latents.dtype != target_dtype:
                latents = latents.to(target_dtype)
            if latents.dim() == 4:
                latents = latents.unsqueeze(0)  # Add batch dimension
        else:
            raise ValueError("No suitable encoded data found for decoding")
        
        # Decode
        with torch.no_grad():
            decoded_tensor = self.tokenizer.decode(latents)
        
        # Process output to standard format: (T, H, W, 3) in [0, 1]
        if decoded_tensor.dim() == 5 and decoded_tensor.shape[0] == 1:
            decoded_tensor = decoded_tensor.squeeze(0)  # Remove batch dim
        
        if decoded_tensor.dim() == 4 and decoded_tensor.shape[0] == 3:
            decoded_tensor = decoded_tensor.permute(1, 2, 3, 0)  # (3,T,H,W) -> (T,H,W,3)
        
        # Convert from [-1,1] to [0,1]
        decoded_tensor = (decoded_tensor + 1.0) / 2.0
        decoded_tensor = torch.clamp(decoded_tensor, 0, 1)
        decoded_tensor = decoded_tensor.cpu().float()
        
        return decoded_tensor
    
    def save_decoded_video(self, video_tensor: torch.Tensor, output_path: str, fps: float = 30.0, metadata: Dict[str, Any] = None) -> str:
        """Save decoded video tensor to MP4 file
        
        Args:
            video_tensor: Decoded video with shape (T, H, W, 3) in [0, 1] range
            output_path: Path to save the MP4 file
            fps: Frame rate for the output video
            metadata: Optional metadata for fps information
            
        Returns:
            Path to saved video file
        """
        # Use original fps if available in metadata
        if metadata:
            original_fps = metadata.get('original_fps', fps)
            fps = original_fps if original_fps > 0 else fps
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to numpy and scale to [0, 255]
        if isinstance(video_tensor, torch.Tensor):
            frames_np = video_tensor.numpy()
        else:
            frames_np = video_tensor
        
        # Ensure proper range and type
        if frames_np.max() <= 1.0:
            frames_uint8 = (frames_np * 255).astype(np.uint8)
        else:
            frames_uint8 = frames_np.astype(np.uint8)
        
        # Get video properties
        num_frames, height, width = frames_uint8.shape[:3]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            print(f"❌ Failed to create video writer for {output_path}")
            return None
        
        try:
            # Write frames
            for i in range(num_frames):
                frame = frames_uint8[i]
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                writer.write(frame_bgr)
            
            writer.release()
            print(f"✅ Saved decoded video: {output_path} ({num_frames} frames @ {fps:.1f}fps)")
            return output_path
            
        except Exception as e:
            print(f"❌ Error writing video {output_path}: {e}")
            writer.release()
            # Clean up partial file
            if os.path.exists(output_path):
                os.remove(output_path)
            return None


def collate_fn_video(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Custom collate function for batching Cosmos video data"""
    
    # Collect all keys
    keys = set()
    for item in batch:
        keys.update(item.keys())
    
    collated = {}
    
    for key in keys:
        values = [item.get(key) for item in batch if key in item]
        
        if key in ["video", "encoded_latents", "encoded_indices"]:
            # Handle variable length sequences
            if values and isinstance(values[0], torch.Tensor):
                # Find max length in batch
                if key == "encoded_latents":
                    # Optimized padding using torch.nn.functional.pad (much more efficient)
                    max_len = max(v.shape[1] for v in values)  # Time dimension is 1 for latents
                    padded_values = []
                    for v in values:
                        if v.shape[1] < max_len:
                            pad_frames = max_len - v.shape[1]
                            # Use F.pad instead of creating zeros and concatenating
                            # pad=(left, right, top, bottom, front, back) for last 3 dims
                            v = torch.nn.functional.pad(v, (0, 0, 0, 0, 0, pad_frames), mode='constant', value=0)
                        padded_values.append(v)
                else:
                    # Optimized padding using torch.nn.functional.pad
                    max_len = max(v.shape[0] for v in values)  # Time dimension is 0 for others
                    padded_values = []
                    for v in values:
                        if v.shape[0] < max_len:
                            pad_frames = max_len - v.shape[0]
                            # Pad at the end of the time dimension (dim=0)
                            if key == "encoded_indices":
                                # For 3D tensors (T, H, W): pad=(0,0,0,0,0,pad_frames)
                                v = torch.nn.functional.pad(v, (0, 0, 0, 0, 0, pad_frames), mode='constant', value=0)
                            else:  # video 4D tensors (T, C, H, W)
                                # For 4D tensors: pad=(0,0,0,0,0,0,0,pad_frames)
                                v = torch.nn.functional.pad(v, (0, 0, 0, 0, 0, 0, 0, pad_frames), mode='constant', value=0)
                        padded_values.append(v)
                
                collated[key] = torch.stack(padded_values)
            else:
                collated[key] = values
        else:
            # Other values (metadata, paths, etc.)
            collated[key] = values
    
    return collated


# ============ USAGE EXAMPLES ============

def preprocess_video_dataset(
    input_dir: str,
    output_dir: str,
    model_name: str = "CV8x8x8",
    max_frames: int = 32,
    frame_size: Tuple[int, int] = (224, 224),
    temporal_window: int = 17,
    num_workers: int = 1
):
    """Preprocess an entire video dataset"""
    
    config = VideoConfig(
        model_name=model_name,
        max_frames=max_frames,
        frame_size=frame_size,
        temporal_window=temporal_window,
        normalize_frames=True
    )
    
    processor = CosmosVideoProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        recursive=True
    )
    
    return report


def create_video_dataloader(
    data_dir: str,
    batch_size: int = 4,
    return_decoded: bool = False,
    return_codes: bool = True,
    max_frames: Optional[int] = None,
    num_workers: int = 2,
    shuffle: bool = True,
    save_decoded: bool = False,
    decoded_output_dir: str = "./decoded_videos"
) -> DataLoader:
    """Create a DataLoader for Cosmos video data"""
    
    dataset = CosmosVideoDataset(
        data_dir=data_dir,
        return_decoded=return_decoded,
        return_codes=return_codes,
        max_frames=max_frames,
        save_decoded=save_decoded,
        decoded_output_dir=decoded_output_dir
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn_video,
        pin_memory=torch.cuda.is_available()
    )
    
    return dataloader


def decode_and_save_all_videos(
    data_dir: str,
    output_dir: str = "./decoded_videos",
    max_videos: Optional[int] = None
):
    """Decode and save all videos in a dataset to MP4 files"""
    
    dataset = CosmosVideoDataset(
        data_dir=data_dir,
        return_decoded=False,  # Don't return tensors, just save
        return_codes=False,
        save_decoded=True,
        decoded_output_dir=output_dir
    )
    
    print(f"🎬 Decoding and saving {len(dataset)} videos to {output_dir}")
    
    max_videos = max_videos or len(dataset)
    saved_count = 0
    
    for i in tqdm(range(min(max_videos, len(dataset))), desc="Decoding videos"):
        try:
            item = dataset[i]  # This will trigger decoding and saving
            if "decoded_video_path" in item:
                saved_count += 1
        except Exception as e:
            print(f"❌ Failed to decode video {i}: {e}")
    
    print(f"✅ Successfully decoded and saved {saved_count}/{max_videos} videos")
    return saved_count


def example_usage():
    """Example usage of the video pipeline"""
    
    # Initialize processor
    processor = CosmosVideoProcessor(VideoConfig())
    
    # Example 1: Compress a video file
    print("=== COMPRESSION EXAMPLE ===")
    input_file = "/content/Cosmos-Tokenizer/test_data/video.mp4"
    compressed_file =  "/content/Cosmos-Tokenizer/test_data/compressed_video.pt"
    
    if os.path.exists(input_file):
        # Load and encode
        frames, metadata = processor.load_video(input_file)
        encoded_data = processor.encode_video(frames, metadata)
        
        # Save
        torch.save(encoded_data, compressed_file)
        print(f"✅ Compression complete: {compressed_file}")
    
    # Example 2: Dataset and DataLoader
    print("\n=== DATASET EXAMPLE ===")
    
    # Create dataset that returns encoded codes
    try:
        dataset = CosmosVideoDataset(
            data_dir="/content/Cosmos-Tokenizer/test_data",
            return_decoded=False,      # Set to True if you want decoded video frames
            return_codes=True,         # Return encoded latents/codes
            max_frames=32             # Max frames for padding
        )
        
        # Create dataloader
        dataloader = DataLoader(
            dataset,
            batch_size=4,
            shuffle=True,
            num_workers=2,
            collate_fn=collate_fn_video,
            pin_memory=True
        )
        
        # Test the dataloader
        print("=== TESTING DATALOADER ===")
        for batch_idx, batch in enumerate(dataloader):
            print(f"Batch {batch_idx + 1}:")
            
            if 'encoded_latents' in batch:
                print(f"  Encoded latents shape: {batch['encoded_latents'].shape}")
            
            if 'encoded_indices' in batch:
                print(f"  Encoded indices shape: {batch['encoded_indices'].shape}")
            
            if 'video' in batch:
                print(f"  Decoded video shape: {batch['video'].shape}")
            
            print(f"  Files: {batch['file_name']}")
            print(f"  Metadata count: {len(batch['metadata'])}")
            
            if batch_idx >= 2:  # Just show first 3 batches
                break
        
        print("✅ Video dataset pipeline test complete!")
        decode_and_save_all_videos(
            data_dir="/content/Cosmos-Tokenizer/test_data",
            output_dir="/content/Cosmos-Tokenizer/test_data/decoded_output",
            max_videos=10
        )
        
        
    except Exception as e:
        print(f"Dataset test failed: {e}")
        print("Create compressed videos first using preprocess_video_dataset()")


# ============ BATCH PROCESSING UTILITIES ============

def batch_compress_video_directory(input_dir: str, output_dir: str, **kwargs):
    """Compress all video files in a directory"""
    config = VideoConfig(**kwargs)
    processor = CosmosVideoProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=kwargs.get('num_workers', 1)
    )
    
    print(f"✅ Batch compression complete: {output_dir}")
    return report