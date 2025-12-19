"""
Shared utilities for processors package - Fixed BFloat16 support
"""
import io
import json
import hashlib
import gzip
import torch
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

try:
    import h5py
except ImportError:
    h5py = None

try:
    import webdataset as wds
except ImportError:
    wds = None

try:
    import tensorflow as tf
except ImportError:
    tf = None

class CARHandler:
    """Handler for Content Addressable aRchive (CAR) format"""
    
    @staticmethod
    def _convert_tensor_to_numpy(tensor: torch.Tensor) -> Tuple[np.ndarray, str]:
        """
        Convert PyTorch tensor to numpy array, handling BFloat16 and other edge cases.
        
        Returns:
            (numpy_array, original_dtype_info)
        """
        original_dtype = str(tensor.dtype)
        
        # Handle BFloat16 tensors - convert to float32 for numpy compatibility
        if tensor.dtype == torch.bfloat16:
            print(f"⚠️  Converting BFloat16 tensor to float32 for numpy compatibility")
            numpy_array = tensor.float().detach().cpu().numpy()
            return numpy_array, f"bfloat16_as_float32"
        
        # Handle other unsupported dtypes
        elif tensor.dtype == torch.complex64:
            print(f"⚠️  Converting complex64 tensor to float32 (real part only)")
            numpy_array = tensor.real.float().detach().cpu().numpy()
            return numpy_array, f"complex64_real_as_float32"
        
        elif tensor.dtype == torch.complex128:
            print(f"⚠️  Converting complex128 tensor to float32 (real part only)")
            numpy_array = tensor.real.float().detach().cpu().numpy()
            return numpy_array, f"complex128_real_as_float32"
        
        # Standard conversion for supported dtypes
        else:
            try:
                numpy_array = tensor.detach().cpu().numpy()
                return numpy_array, original_dtype
            except Exception as e:
                # Fallback: convert to float32
                print(f"⚠️  Fallback conversion of {original_dtype} to float32: {e}")
                numpy_array = tensor.float().detach().cpu().numpy()
                return numpy_array, f"{original_dtype}_as_float32"
    
    @staticmethod
    def optimize_numpy_dtype(arr: np.ndarray) -> np.ndarray:
        """
        Optimize numpy array dtype based on value range to minimize memory usage.
        Uses the cosmos tokenizer approach for efficiency.
        """
        if not np.issubdtype(arr.dtype, np.integer):
            return arr
        
        vmax = int(arr.max())
        vmin = int(arr.min())
        
        # Choose the most efficient integer type - favor cosmos approach
        if vmin >= 0:  # Unsigned integers
            if vmax < 256:
                dtype = np.uint8
            elif vmax < 65536:
                dtype = np.uint16  # Most common for cosmos tokens
            elif vmax < 4294967296:
                dtype = np.uint32
            else:
                dtype = np.uint64
        else:  # Signed integers needed
            if vmin >= -128 and vmax < 128:
                dtype = np.int8
            elif vmin >= -32768 and vmax < 32768:
                dtype = np.int16
            elif vmin >= -2147483648 and vmax < 2147483648:
                dtype = np.int32
            else:
                dtype = np.int64
        
        return arr.astype(dtype, copy=False)  # Use copy=False for efficiency
    
    @staticmethod
    def _optimize_tensor_direct(tensor: torch.Tensor) -> Tuple[torch.Tensor, str]:
        """
        Directly optimize tensor dtype without redundant conversions.
        
        OPTIMIZED: Avoids BFloat16→Float32→NumPy→optimize→NumPy→Torch chain
        Returns (optimized_tensor, log_info)
        """
        original_dtype = tensor.dtype
        log_info = ""
        
        # For integer tensors, optimize dtype based on value range
        if tensor.dtype in [torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8, torch.uint16, torch.uint32, torch.uint64]:
            # Get min/max values efficiently without numpy conversion
            vmin = int(tensor.min().item())
            vmax = int(tensor.max().item())
            
            # Determine optimal dtype
            if vmin >= 0:  # Unsigned
                if vmax < 256:
                    target_dtype = torch.uint8
                elif vmax < 65536:
                    target_dtype = torch.uint16  # Most common for tokenizer outputs
                else:
                    return tensor.contiguous(), log_info  # Keep as is
            else:  # Signed
                if vmin >= -128 and vmax < 128:
                    target_dtype = torch.int8
                elif vmin >= -32768 and vmax < 32768:
                    target_dtype = torch.int16
                else:
                    return tensor.contiguous(), log_info  # Keep as is
            
            # Apply optimization if beneficial
            if target_dtype != original_dtype:
                try:
                    optimized_tensor = tensor.to(target_dtype)
                    log_info = f"{original_dtype} → {target_dtype} (vocab: {vmax + 1})"
                    return optimized_tensor.contiguous(), log_info
                except Exception:
                    pass  # Fall back to no optimization
        
        # For BFloat16, convert to float16 for better compatibility
        elif tensor.dtype == torch.bfloat16:
            optimized_tensor = tensor.to(torch.float16)
            log_info = f"bfloat16 → float16 (memory optimization)"
            return optimized_tensor.contiguous(), log_info
        
        # No optimization needed/possible
        return tensor.contiguous(), log_info
    
    @staticmethod
    def optimize_tensor_data(data_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Optimize tensor dtypes in a data dictionary and return optimization log.
        Returns (optimized_dict_with_torch_tensors, optimization_log)
        
        OPTIMIZED: Avoids redundant BFloat16→Float32→NumPy→optimize→NumPy→Torch conversion chain
        """
        optimized_dict = {}
        optimization_log = {}
        
        for key, value in data_dict.items():
            if isinstance(value, torch.Tensor):
                # OPTIMIZED: Direct dtype optimization without redundant conversions
                optimized_tensor, log_info = CARHandler._optimize_tensor_direct(value)
                optimized_dict[key] = optimized_tensor
                if log_info:
                    optimization_log[key] = log_info
                
            elif isinstance(value, list) and value and isinstance(value[0], torch.Tensor):
                # Handle list of tensors (like SNAC hierarchical codes) - OPTIMIZED
                optimized_list = []
                for i, tensor in enumerate(value):
                    optimized_tensor, log_info = CARHandler._optimize_tensor_direct(tensor)
                    optimized_list.append(optimized_tensor)
                    if log_info:
                        optimization_log[f"{key}[{i}]"] = log_info
                optimized_dict[key] = optimized_list
            else:
                # Keep non-tensor data as is
                optimized_dict[key] = value
        
        return optimized_dict, optimization_log
    
    @staticmethod
    def _serialize_numpy_dict(data_dict: Dict[str, Any]) -> bytes:
        """
        Custom numpy-only serialization that stores data in a compact binary format.
        Format: [num_items][item1_header][item1_data][item2_header][item2_data]...
        """
        buffer = io.BytesIO()
        
        # Write number of items
        buffer.write(len(data_dict).to_bytes(4, byteorder='little'))
        
        for key, value in data_dict.items():
            # Write key
            key_bytes = key.encode('utf-8')
            buffer.write(len(key_bytes).to_bytes(4, byteorder='little'))
            buffer.write(key_bytes)
            
            if isinstance(value, np.ndarray):
                # Type marker for numpy array
                buffer.write(b'NPAR')
                
                # Array metadata
                dtype_str = str(value.dtype)
                dtype_bytes = dtype_str.encode('utf-8')
                buffer.write(len(dtype_bytes).to_bytes(4, byteorder='little'))
                buffer.write(dtype_bytes)
                
                # Shape
                buffer.write(len(value.shape).to_bytes(4, byteorder='little'))
                for dim in value.shape:
                    buffer.write(dim.to_bytes(8, byteorder='little'))
                
                # Data
                contiguous_array = np.ascontiguousarray(value)
                data_bytes = contiguous_array.tobytes()
                buffer.write(len(data_bytes).to_bytes(8, byteorder='little'))
                buffer.write(data_bytes)
                
            elif isinstance(value, list) and value and isinstance(value[0], np.ndarray):
                # Type marker for list of numpy arrays
                buffer.write(b'LIST')
                buffer.write(len(value).to_bytes(4, byteorder='little'))
                
                for arr in value:
                    # Same as single array serialization
                    dtype_str = str(arr.dtype)
                    dtype_bytes = dtype_str.encode('utf-8')
                    buffer.write(len(dtype_bytes).to_bytes(4, byteorder='little'))
                    buffer.write(dtype_bytes)
                    
                    buffer.write(len(arr.shape).to_bytes(4, byteorder='little'))
                    for dim in arr.shape:
                        buffer.write(dim.to_bytes(8, byteorder='little'))
                    
                    contiguous_array = np.ascontiguousarray(arr)
                    data_bytes = contiguous_array.tobytes()
                    buffer.write(len(data_bytes).to_bytes(8, byteorder='little'))
                    buffer.write(data_bytes)
            else:
                # Type marker for JSON-serializable data
                buffer.write(b'JSON')
                json_bytes = json.dumps(value, ensure_ascii=False).encode('utf-8')
                buffer.write(len(json_bytes).to_bytes(8, byteorder='little'))
                buffer.write(json_bytes)
        
        return buffer.getvalue()
    
    @staticmethod
    def _deserialize_numpy_dict(data_bytes: bytes) -> Dict[str, Any]:
        """
        Deserialize custom numpy format back to dictionary.
        """
        buffer = io.BytesIO(data_bytes)
        result = {}
        
        # Read number of items
        num_items = int.from_bytes(buffer.read(4), byteorder='little')
        
        for _ in range(num_items):
            # Read key
            key_len = int.from_bytes(buffer.read(4), byteorder='little')
            key = buffer.read(key_len).decode('utf-8')
            
            # Read type marker
            type_marker = buffer.read(4)
            
            if type_marker == b'NPAR':
                # Read numpy array
                dtype_len = int.from_bytes(buffer.read(4), byteorder='little')
                dtype_str = buffer.read(dtype_len).decode('utf-8')
                
                # Read shape
                ndim = int.from_bytes(buffer.read(4), byteorder='little')
                shape = tuple(int.from_bytes(buffer.read(8), byteorder='little') for _ in range(ndim))
                
                # Read data
                data_len = int.from_bytes(buffer.read(8), byteorder='little')
                data_bytes_chunk = buffer.read(data_len)
                
                # Reconstruct array
                arr = np.frombuffer(data_bytes_chunk, dtype=dtype_str).reshape(shape)
                result[key] = arr
                
            elif type_marker == b'LIST':
                # Read list of numpy arrays
                list_len = int.from_bytes(buffer.read(4), byteorder='little')
                arr_list = []
                
                for _ in range(list_len):
                    dtype_len = int.from_bytes(buffer.read(4), byteorder='little')
                    dtype_str = buffer.read(dtype_len).decode('utf-8')
                    
                    ndim = int.from_bytes(buffer.read(4), byteorder='little')
                    shape = tuple(int.from_bytes(buffer.read(8), byteorder='little') for _ in range(ndim))
                    
                    data_len = int.from_bytes(buffer.read(8), byteorder='little')
                    data_bytes_chunk = buffer.read(data_len)
                    
                    arr = np.frombuffer(data_bytes_chunk, dtype=dtype_str).reshape(shape)
                    arr_list.append(arr)
                
                result[key] = arr_list
                
            elif type_marker == b'JSON':
                # Read JSON data
                json_len = int.from_bytes(buffer.read(8), byteorder='little')
                json_bytes = buffer.read(json_len)
                result[key] = json.loads(json_bytes.decode('utf-8'))
        
        return result
    
    @staticmethod
    def _create_car_format(np_data, metadata: dict, compress: bool = False, compression_level: int = 6) -> bytes:
        """Create CAR format directly from numpy data (bytes or memoryview)"""
        try:
            # Convert memoryview to bytes if needed
            if isinstance(np_data, memoryview):
                np_data_bytes = bytes(np_data)
            else:
                np_data_bytes = np_data
            
            # Optionally compress the numpy data
            original_size = len(np_data_bytes)
            if compress:
                np_data_bytes = gzip.compress(np_data_bytes, compresslevel=compression_level)
                compressed_size = len(np_data_bytes)
                
                # Add compression info to metadata
                metadata = metadata.copy()
                metadata['compression'] = {
                    'enabled': True,
                    'method': 'gzip',
                    'level': compression_level,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': original_size / compressed_size if compressed_size > 0 else 1.0
                }
            else:
                metadata = metadata.copy()
                metadata['compression'] = {'enabled': False}
            
            # Create content hash (of compressed data if compression is used)
            data_hash = hashlib.sha256(np_data_bytes).digest()
            metadata_json = json.dumps(metadata, sort_keys=True).encode('utf-8')
            metadata_hash = hashlib.sha256(metadata_json).digest()
            
            # CAR format: header + data blocks
            car_data = io.BytesIO()
            
            # Write header
            header = {
                "version": 1,
                "format": "direct_bytes",  # Mark as direct bytes format
                "roots": [data_hash.hex(), metadata_hash.hex()],
                "created_at": datetime.now().isoformat()
            }
            header_json = json.dumps(header).encode('utf-8')
            header_length = len(header_json)
            
            car_data.write(header_length.to_bytes(4, byteorder='big'))
            car_data.write(header_json)
            
            # Write data block
            car_data.write(len(data_hash).to_bytes(4, byteorder='big'))
            car_data.write(data_hash)
            car_data.write(len(np_data_bytes).to_bytes(8, byteorder='big'))
            car_data.write(np_data_bytes)
            
            # Write metadata block
            car_data.write(len(metadata_hash).to_bytes(4, byteorder='big'))
            car_data.write(metadata_hash)
            car_data.write(len(metadata_json).to_bytes(8, byteorder='big'))
            car_data.write(metadata_json)
            
            return car_data.getvalue()
            
        except Exception as e:
            raise RuntimeError(f"Failed to create direct CAR format: {e}")
    
    @staticmethod
    def _extract_from_car_format(car_data: bytes) -> Tuple[bytes, dict]:
        """Extract numpy data and metadata directly from CAR format"""
        try:
            car_stream = io.BytesIO(car_data)
            
            # Read header
            header_length = int.from_bytes(car_stream.read(4), byteorder='big')
            header_json = car_stream.read(header_length)
            header = json.loads(header_json.decode('utf-8'))
            
            # Read data block (potentially compressed)
            data_hash_length = int.from_bytes(car_stream.read(4), byteorder='big')
            stored_data_hash = car_stream.read(data_hash_length)
            np_data_length = int.from_bytes(car_stream.read(8), byteorder='big')
            np_data = car_stream.read(np_data_length)
            
            # Read metadata block
            metadata_hash_length = int.from_bytes(car_stream.read(4), byteorder='big')
            stored_metadata_hash = car_stream.read(metadata_hash_length)
            metadata_length = int.from_bytes(car_stream.read(8), byteorder='big')
            metadata_json = car_stream.read(metadata_length)
            
            # Verify data integrity (of compressed data)
            computed_data_hash = hashlib.sha256(np_data).digest()
            if computed_data_hash != stored_data_hash:
                raise ValueError("Data integrity check failed - data has been corrupted")
            
            computed_metadata_hash = hashlib.sha256(metadata_json).digest()
            if computed_metadata_hash != stored_metadata_hash:
                raise ValueError("Metadata integrity check failed - metadata has been corrupted")
            
            # Parse metadata
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Decompress data if it was compressed
            compression_info = metadata.get('compression', {})
            if compression_info.get('enabled', False):
                if compression_info.get('method') == 'gzip':
                    try:
                        np_data = gzip.decompress(np_data)
                        # Verify decompressed size matches expected
                        expected_size = compression_info.get('original_size')
                        if expected_size and len(np_data) != expected_size:
                            raise ValueError(f"Decompressed size {len(np_data)} doesn't match expected {expected_size}")
                    except Exception as e:
                        raise ValueError(f"Failed to decompress gzip data: {e}")
                else:
                    raise ValueError(f"Unsupported compression method: {compression_info.get('method')}")
            
            return np_data, metadata
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract from direct CAR format: {e}")
    
    @staticmethod
    def np_to_car(data_dict: Dict[str, Any], metadata: dict, compress: bool = False, 
                  compression_level: int = 6, optimize_dtypes: bool = True) -> bytes:
        """
        Convert dictionary with tensors to CAR format using direct bytes approach.
        
        Args:
            data_dict: Dictionary containing tensors and other data
            metadata: Metadata dictionary  
            compress: Whether to apply gzip compression
            compression_level: Compression level 1-9
            optimize_dtypes: Whether to optimize tensor dtypes for memory efficiency
        
        Returns:
            CAR format bytes with direct tensor→numpy→bytes conversion
        """
        try:
            # Find the main tensor data (encoded_indices, encoded_latents, or audio_codes)
            main_tensor_key = None
            main_tensor = None
            
            for key in ['encoded_indices', 'encoded_latents', 'audio_codes']:
                if key in data_dict:
                    value = data_dict[key]
                    if isinstance(value, torch.Tensor):
                        main_tensor_key = key
                        main_tensor = value
                        break
                    elif isinstance(value, list) and value and isinstance(value[0], torch.Tensor):
                        # Handle hierarchical codes (like SNAC audio_codes)
                        main_tensor_key = key
                        main_tensor = value  # Keep as list for now
                        break
            
            if main_tensor is None:
                raise ValueError("No main tensor data found (encoded_indices, encoded_latents, or audio_codes)")
            
            # Handle different tensor formats
            if isinstance(main_tensor, list):
                # Hierarchical codes (like SNAC) - concatenate into single tensor for storage
                all_codes = torch.cat([code.flatten() for code in main_tensor], dim=0)
                np_array, dtype_info = CARHandler._convert_tensor_to_numpy(all_codes)
                
                # Check if optimization is possible - handle BFloat16 case
                original_was_bfloat16 = any(code.dtype == torch.bfloat16 for code in main_tensor)
                if optimize_dtypes:
                    # For BFloat16 or if array contains integer-like values
                    if original_was_bfloat16 or np.issubdtype(np_array.dtype, np.integer):
                        # Check if all values are actually integers (even if stored as floats)
                        if np.allclose(np_array, np_array.astype(int)) if np_array.dtype.kind == 'f' else True:
                            vmax = int(np_array.max()) if np_array.size > 0 else None
                        else:
                            vmax = None
                    else:
                        vmax = None
                else:
                    vmax = None
                    
            else:
                # Single tensor
                np_array, dtype_info = CARHandler._convert_tensor_to_numpy(main_tensor)
                
                # Check if optimization is possible - handle BFloat16 case  
                original_was_bfloat16 = main_tensor.dtype == torch.bfloat16
                if optimize_dtypes:
                    # For BFloat16 or if array contains integer-like values
                    if original_was_bfloat16 or np.issubdtype(np_array.dtype, np.integer):
                        # Check if all values are actually integers (even if stored as floats)
                        if np.allclose(np_array, np_array.astype(int)) if np_array.dtype.kind == 'f' else True:
                            vmax = int(np_array.max()) if np_array.size > 0 else None
                        else:
                            vmax = None
                    else:
                        vmax = None
                else:
                    vmax = None
            
            # Optimize dtype based on value range (cosmos approach)
            optimization_log = {}
            if optimize_dtypes and vmax is not None:
                dtype = np.uint16 if vmax < 65536 else np.uint32
                tokens = np_array.astype(dtype, copy=False)
                optimization_log[main_tensor_key] = f"{np_array.dtype} → {dtype.__name__} (vmax: {vmax})"
                print(f"🔧 Optimized {main_tensor_key}: {optimization_log[main_tensor_key]}")
            else:
                tokens = np.ascontiguousarray(np_array)
                dtype = tokens.dtype
            
            # Direct bytes conversion with memoryview for efficiency
            bin_data = memoryview(tokens.tobytes(order="C"))
            
            # Create enhanced metadata with array info
            enhanced_metadata = metadata.copy()
            enhanced_metadata.update({
                'format': 'direct_bytes',
                'tensor_info': {
                    'key': main_tensor_key,
                    'dtype': np.dtype(dtype).name,  # Convert to dtype object first, then get name
                    'shape': list(tokens.shape),
                    'nbytes': tokens.nbytes
                }
            })
            
            # Track original tensor dtype for restoration
            if isinstance(main_tensor, list):
                original_dtype = str(main_tensor[0].dtype) if main_tensor else "unknown"
            else:
                original_dtype = str(main_tensor.dtype)
                
            enhanced_metadata['original_tensor_dtype'] = original_dtype
            
            # Add dtype conversion info if applicable
            if dtype_info != original_dtype:
                enhanced_metadata['dtype_conversions'] = {main_tensor_key: f"{original_dtype} → {dtype_info}"}
            
            if optimization_log:
                enhanced_metadata['dtype_optimizations'] = optimization_log
            
            # Store any additional non-tensor data
            other_data = {k: v for k, v in data_dict.items() 
                         if k != main_tensor_key and not isinstance(v, torch.Tensor)}
            if other_data:
                enhanced_metadata['other_data'] = other_data
            
            # Create CAR format directly with binary data
            return CARHandler._create_car_format(bin_data, enhanced_metadata, compress=compress, compression_level=compression_level)
            
        except Exception as e:
            raise RuntimeError(f"Failed to create direct CAR format: {e}")
    
    @staticmethod
    def car_to_np(car_data: bytes, restore_original_dtype: bool = True) -> Tuple[Dict[str, Any], dict]:
        """
        Extract data from direct bytes CAR format and convert to torch tensors.
        
        Args:
            car_data: CAR format bytes
            restore_original_dtype: Whether to attempt restoring original dtypes (like BFloat16)
        
        Returns:
            (torch_data_dict, metadata)
        """
        try:
            # Extract raw binary data and metadata from CAR format
            bin_data, metadata = CARHandler._extract_from_car_format(car_data)
            
            # Check format type
            if metadata.get('format') == 'direct_bytes':
                # Handle direct bytes format
                tensor_info = metadata['tensor_info']
                tensor_key = tensor_info['key']
                dtype_str = tensor_info['dtype']
                shape = tuple(tensor_info['shape'])
                
                # Reconstruct numpy array from raw bytes
                np_array = np.frombuffer(bin_data, dtype=dtype_str).reshape(shape)
                
                # Convert to contiguous torch tensor
                contiguous_array = np.ascontiguousarray(np_array)
                
                # Handle unsupported dtypes for PyTorch
                if contiguous_array.dtype == np.uint16:
                    print(f"🔧 Converting {tensor_key} from uint16 to int32 for PyTorch compatibility")
                    contiguous_array = contiguous_array.astype(np.int32)
                elif contiguous_array.dtype == np.uint32:
                    print(f"🔧 Converting {tensor_key} from uint32 to int64 for PyTorch compatibility")
                    contiguous_array = contiguous_array.astype(np.int64)
                elif contiguous_array.dtype == np.uint64:
                    print(f"🔧 Converting {tensor_key} from uint64 to int64 for PyTorch compatibility")
                    contiguous_array = contiguous_array.astype(np.int64)
                
                torch_tensor = torch.from_numpy(contiguous_array)
                
                # Handle dtype restoration if requested
                if restore_original_dtype and 'original_tensor_dtype' in metadata:
                    original_dtype = metadata['original_tensor_dtype']
                    current_dtype = torch_tensor.dtype
                    
                    # Restore BFloat16 if that was the original
                    if original_dtype == 'torch.bfloat16' and current_dtype != torch.bfloat16:
                        if current_dtype in [torch.float32, torch.float64]:
                            print(f"🔄 Restoring {tensor_key} to BFloat16 from {current_dtype}")
                            torch_tensor = torch_tensor.to(torch.bfloat16)
                        elif current_dtype in [torch.uint8, torch.uint16, torch.uint32, torch.int8, torch.int16, torch.int32]:
                            # Integer dtype - convert to float first, then BFloat16
                            print(f"🔄 Restoring {tensor_key}: {current_dtype} → float32 → BFloat16")
                            torch_tensor = torch_tensor.to(torch.float32).to(torch.bfloat16)
                        else:
                            print(f"⚠️  Cannot restore {tensor_key} to BFloat16 from {current_dtype}")
                    
                    # Handle other potential restorations
                    elif 'dtype_conversions' in metadata:
                        conversion_info = metadata['dtype_conversions'].get(tensor_key, "")
                        if "complex" in conversion_info:
                            print(f"⚠️  Cannot restore complex tensor {tensor_key} - real part only was saved")
                
                # Create result dictionary
                torch_data = {tensor_key: torch_tensor}
                
                # Add any additional data stored in metadata
                if 'other_data' in metadata:
                    torch_data.update(metadata['other_data'])
                
                # Log conversion and restoration info
                print(f"📄 Loaded {tensor_key}: {list(torch_tensor.shape)} {torch_tensor.dtype}")
                
                if 'original_tensor_dtype' in metadata:
                    original = metadata['original_tensor_dtype']
                    current = str(torch_tensor.dtype)
                    if original != current:
                        if restore_original_dtype:
                            print(f"🔄 Attempted restoration: {original} → {current}")
                        else:
                            print(f"ℹ️  Original dtype was {original}, loaded as {current} (restoration disabled)")
                
                if 'dtype_conversions' in metadata:
                    print(f"ℹ️  Save-time conversions:")
                    for key, change in metadata['dtype_conversions'].items():
                        print(f"   {key}: {change}")
                
                if 'dtype_optimizations' in metadata:
                    print(f"🔧 Storage optimizations:")
                    for key, change in metadata['dtype_optimizations'].items():
                        print(f"   {key}: {change}")
                
                return torch_data, metadata
                
            else:
                # Fallback to custom serialization format
                np_data_dict = CARHandler._deserialize_numpy_dict(bin_data)
                
                # Convert numpy arrays to torch tensors
                torch_data = {}
                for key, value in np_data_dict.items():
                    if isinstance(value, np.ndarray):
                        contiguous_array = np.ascontiguousarray(value)
                        torch_data[key] = torch.from_numpy(contiguous_array)
                    elif isinstance(value, list) and value and isinstance(value[0], np.ndarray):
                        torch_data[key] = [torch.from_numpy(np.ascontiguousarray(arr)) for arr in value]
                    else:
                        torch_data[key] = value
                
                return torch_data, metadata
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract data from CAR format: {e}")
    
    
    @staticmethod
    def verify_car_integrity(car_data: bytes) -> bool:
        """Verify the integrity of a CAR file without extracting data"""
        try:
            CARHandler._extract_from_car_format(car_data)
            return True
        except:
            return False
    
    @staticmethod
    def get_car_metadata(car_data: bytes) -> dict:
        """Extract only metadata from CAR file without loading tensor data"""
        try:
            car_stream = io.BytesIO(car_data)
            
            # Read header
            header_length = int.from_bytes(car_stream.read(4), byteorder='big')
            header_json = car_stream.read(header_length)
            header = json.loads(header_json.decode('utf-8'))
            
            # Skip data block
            data_hash_length = int.from_bytes(car_stream.read(4), byteorder='big')
            car_stream.read(data_hash_length)  # Skip data hash
            np_data_length = int.from_bytes(car_stream.read(8), byteorder='big')
            car_stream.read(np_data_length)  # Skip numpy data
            
            # Read metadata block
            metadata_hash_length = int.from_bytes(car_stream.read(4), byteorder='big')
            car_stream.read(metadata_hash_length)  # Skip metadata hash
            metadata_length = int.from_bytes(car_stream.read(8), byteorder='big')
            metadata_json = car_stream.read(metadata_length)
            
            # Parse and return metadata
            metadata = json.loads(metadata_json.decode('utf-8'))
            metadata['car_header'] = header  # Include CAR header info
            
            return metadata
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract metadata from CAR format: {e}")
    
    @staticmethod
    def np_to_hdf5(data_dict: Dict[str, Any], output_path: str, 
                   optimize_dtypes: bool = True, compression: str = 'gzip', 
                   compression_opts: int = 6) -> None:
        """
        Convert numpy data dictionary to HDF5 format.
        
        Args:
            data_dict: Dictionary containing numpy arrays and other data
            output_path: Path to output HDF5 file
            optimize_dtypes: Whether to optimize array dtypes for memory efficiency
            compression: HDF5 compression method ('gzip', 'lzf', 'szip', or None)
            compression_opts: Compression level (0-9 for gzip)
        """
        if h5py is None:
            raise ImportError("h5py is required for HDF5 export. Install with: pip install h5py")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Optimize dtypes if requested
        if optimize_dtypes:
            optimized_dict, optimization_log = CARHandler.optimize_tensor_data(data_dict)
            if optimization_log:
                print("🔧 Optimized dtypes for HDF5 export:")
                for key, change in optimization_log.items():
                    print(f"   {key}: {change}")
        else:
            optimized_dict = data_dict
        
        try:
            with h5py.File(str(output_path), 'w') as hf:
                for key, value in optimized_dict.items():
                    if isinstance(value, torch.Tensor):
                        np_array, dtype_info = CARHandler._convert_tensor_to_numpy(value)
                        np_array = np.ascontiguousarray(np_array)
                        
                        # Create dataset with compression
                        hf.create_dataset(
                            key, 
                            data=np_array,
                            compression=compression,
                            compression_opts=compression_opts,
                            shuffle=True if compression else False
                        )
                        
                    elif isinstance(value, list) and value and isinstance(value[0], torch.Tensor):
                        # Handle list of tensors (hierarchical codes)
                        grp = hf.create_group(key)
                        for i, tensor in enumerate(value):
                            np_array, dtype_info = CARHandler._convert_tensor_to_numpy(tensor)
                            np_array = np.ascontiguousarray(np_array)
                            grp.create_dataset(
                                f'level_{i}',
                                data=np_array,
                                compression=compression,
                                compression_opts=compression_opts,
                                shuffle=True if compression else False
                            )
                            
                    elif isinstance(value, np.ndarray):
                        np_array = np.ascontiguousarray(value)
                        hf.create_dataset(
                            key,
                            data=np_array,
                            compression=compression,
                            compression_opts=compression_opts,
                            shuffle=True if compression else False
                        )
                        
                    elif isinstance(value, (dict, list)):
                        # Store as JSON string attribute
                        hf.attrs[key] = json.dumps(value)
                        
                    else:
                        # Store as attribute
                        hf.attrs[key] = value
                        
            print(f"✅ Exported to HDF5: {output_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to export to HDF5: {e}")
    
    @staticmethod
    def np_to_webdataset(data_dict: Dict[str, Any], output_path: str, 
                        sample_key: Optional[str] = None, optimize_dtypes: bool = True) -> None:
        """
        Convert numpy data dictionary to WebDataset tar format.
        
        Args:
            data_dict: Dictionary containing numpy arrays and other data
            output_path: Path to output tar file
            sample_key: Sample key for WebDataset (defaults to filename)
            optimize_dtypes: Whether to optimize array dtypes for memory efficiency
        """
        if wds is None:
            raise ImportError("webdataset is required for WebDataset export. Install with: pip install webdataset")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if sample_key is None:
            sample_key = output_path.stem
        
        # Optimize dtypes if requested
        if optimize_dtypes:
            optimized_dict, optimization_log = CARHandler.optimize_tensor_data(data_dict)
            if optimization_log:
                print("🔧 Optimized dtypes for WebDataset export:")
                for key, change in optimization_log.items():
                    print(f"   {key}: {change}")
        else:
            optimized_dict = data_dict
        
        try:
            with wds.TarWriter(str(output_path)) as writer:
                sample_data = {"__key__": sample_key}
                
                for key, value in optimized_dict.items():
                    if isinstance(value, torch.Tensor):
                        np_array, dtype_info = CARHandler._convert_tensor_to_numpy(value)
                        np_array = np.ascontiguousarray(np_array)
                        sample_data[f"{key}.npy"] = np_array.tobytes()
                        
                        # Store metadata
                        metadata = {
                            "shape": list(np_array.shape),
                            "dtype": str(np_array.dtype)
                        }
                        sample_data[f"{key}_meta.json"] = json.dumps(metadata).encode('utf-8')
                        
                    elif isinstance(value, list) and value and isinstance(value[0], torch.Tensor):
                        # Handle list of tensors (hierarchical codes)
                        for i, tensor in enumerate(value):
                            np_array, dtype_info = CARHandler._convert_tensor_to_numpy(tensor)
                            np_array = np.ascontiguousarray(np_array)
                            sample_data[f"{key}_level_{i}.npy"] = np_array.tobytes()
                            
                            # Store metadata
                            metadata = {
                                "shape": list(np_array.shape),
                                "dtype": str(np_array.dtype),
                                "level": i
                            }
                            sample_data[f"{key}_level_{i}_meta.json"] = json.dumps(metadata).encode('utf-8')
                            
                    elif isinstance(value, np.ndarray):
                        np_array = np.ascontiguousarray(value)
                        sample_data[f"{key}.npy"] = np_array.tobytes()
                        
                        # Store metadata
                        metadata = {
                            "shape": list(np_array.shape),
                            "dtype": str(np_array.dtype)
                        }
                        sample_data[f"{key}_meta.json"] = json.dumps(metadata).encode('utf-8')
                        
                    elif isinstance(value, (dict, list)):
                        # Store as JSON
                        sample_data[f"{key}.json"] = json.dumps(value).encode('utf-8')
                        
                    elif isinstance(value, (str, bytes)):
                        # Store as text
                        if isinstance(value, str):
                            sample_data[f"{key}.txt"] = value.encode('utf-8')
                        else:
                            sample_data[f"{key}.bin"] = value
                            
                writer.write(sample_data)
                
            print(f"✅ Exported to WebDataset: {output_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to export to WebDataset: {e}")
    
    @staticmethod
    def _bytes_feature(value):
        """Returns a bytes_list from a string / byte."""
        if hasattr(value, 'numpy'):  # Handle TensorFlow tensors
            value = value.numpy()
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

    @staticmethod
    def _int64_feature(value):
        """Returns an int64_list from a bool / enum / int / uint."""
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

    @staticmethod
    def _float_feature(value):
        """Returns a float_list from a float / double."""
        return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))
    
    @staticmethod
    def np_to_tfrecord(data_dict: Dict[str, Any], output_path: str, 
                      sample_key: Optional[str] = None, optimize_dtypes: bool = True) -> None:
        """
        Convert numpy data dictionary to TFRecord format.
        
        Args:
            data_dict: Dictionary containing numpy arrays and other data
            output_path: Path to output tfrecord file
            sample_key: Sample key for TFRecord (defaults to filename)
            optimize_dtypes: Whether to optimize array dtypes for memory efficiency
        """
        if tf is None:
            raise ImportError("tensorflow is required for TFRecord export. Install with: pip install tensorflow")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if sample_key is None:
            sample_key = output_path.stem
        
        # Optimize dtypes if requested
        if optimize_dtypes:
            optimized_dict, optimization_log = CARHandler.optimize_tensor_data(data_dict)
            if optimization_log:
                print("🔧 Optimized dtypes for TFRecord export:")
                for key, change in optimization_log.items():
                    print(f"   {key}: {change}")
        else:
            optimized_dict = data_dict
        
        try:
            with tf.io.TFRecordWriter(str(output_path)) as writer:
                features = {'sample_key': CARHandler._bytes_feature(sample_key.encode('utf-8'))}
                
                for key, value in optimized_dict.items():
                    if isinstance(value, torch.Tensor):
                        np_array, dtype_info = CARHandler._convert_tensor_to_numpy(value)
                        np_array = np.ascontiguousarray(np_array)
                        
                        # Store tensor data
                        features[f'{key}_data'] = CARHandler._bytes_feature(np_array.tobytes())
                        features[f'{key}_shape'] = CARHandler._bytes_feature(json.dumps(list(np_array.shape)).encode('utf-8'))
                        features[f'{key}_dtype'] = CARHandler._bytes_feature(str(np_array.dtype).encode('utf-8'))
                        
                    elif isinstance(value, list) and value and isinstance(value[0], torch.Tensor):
                        # Handle list of tensors (hierarchical codes)
                        features[f'{key}_count'] = CARHandler._int64_feature(len(value))
                        
                        for i, tensor in enumerate(value):
                            np_array, dtype_info = CARHandler._convert_tensor_to_numpy(tensor)
                            np_array = np.ascontiguousarray(np_array)
                            
                            features[f'{key}_level_{i}_data'] = CARHandler._bytes_feature(np_array.tobytes())
                            features[f'{key}_level_{i}_shape'] = CARHandler._bytes_feature(json.dumps(list(np_array.shape)).encode('utf-8'))
                            features[f'{key}_level_{i}_dtype'] = CARHandler._bytes_feature(str(np_array.dtype).encode('utf-8'))
                            
                    elif isinstance(value, np.ndarray):
                        np_array = np.ascontiguousarray(value)
                        
                        features[f'{key}_data'] = CARHandler._bytes_feature(np_array.tobytes())
                        features[f'{key}_shape'] = CARHandler._bytes_feature(json.dumps(list(np_array.shape)).encode('utf-8'))
                        features[f'{key}_dtype'] = CARHandler._bytes_feature(str(np_array.dtype).encode('utf-8'))
                        
                    elif isinstance(value, (dict, list)):
                        # Store as JSON
                        json_str = json.dumps(value)
                        features[f'{key}_data'] = CARHandler._bytes_feature(json_str.encode('utf-8'))
                        
                    elif isinstance(value, str):
                        features[f'{key}_data'] = CARHandler._bytes_feature(value.encode('utf-8'))
                        
                    elif isinstance(value, (int, np.integer)):
                        features[f'{key}_data'] = CARHandler._int64_feature(int(value))
                        
                    elif isinstance(value, (float, np.floating)):
                        features[f'{key}_data'] = CARHandler._float_feature(float(value))
                        
                    elif isinstance(value, bytes):
                        features[f'{key}_data'] = CARHandler._bytes_feature(value)
                        features[f'{key}_size'] = CARHandler._int64_feature(len(value))
                        
                    else:
                        # Fallback: convert to string
                        features[f'{key}_data'] = CARHandler._bytes_feature(str(value).encode('utf-8'))
                
                # Create tf.train.Example
                example = tf.train.Example(features=tf.train.Features(feature=features))
                writer.write(example.SerializeToString())
                
            print(f"✅ Exported to TFRecord: {output_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to export to TFRecord: {e}")