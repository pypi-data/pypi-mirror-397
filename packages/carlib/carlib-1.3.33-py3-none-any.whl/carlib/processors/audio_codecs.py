import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import os
import glob
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import librosa
from transformers import EncodecModel, AutoProcessor
import torchaudio
from dataclasses import dataclass
from .utils import CARHandler
from .memory_utils import smart_empty_cache, batch_boundary_cache_clear, error_cache_clear

# Import DAC (Descript Audio Codec)
try:
    import dac
    from audiotools import AudioSignal
    DAC_AVAILABLE = True
    print("✅ Descript Audio Codec (DAC) available")
except ImportError:
    DAC_AVAILABLE = False
    print("❌ Descript Audio Codec (DAC) not available - please install: pip install descript-audio-codec audiotools")

# Import SNAC (Multi-Scale Neural Audio Codec)
try:
    from snac import SNAC
    SNAC_AVAILABLE = True
    print("✅ SNAC (Multi-Scale Neural Audio Codec) available")
except ImportError:
    SNAC_AVAILABLE = False
    print("❌ SNAC not available - please install: pip install snac")


@dataclass
class AudioConfig:
    """Configuration for audio processing"""
    model_name: str = "facebook/encodec_32khz"
    device: str = "cuda"
    max_duration: Optional[float] = None
    target_sample_rate: int = 32000
    quality_threshold: float = 0.0
    output_format: str = "pt"  # "pt" or "car"
    model_type: str = "encodec"  # "encodec", "dac", or "snac"

# DAC model configurations
DAC_MODEL_CONFIGS = {
    'dac_44khz': '44khz',
    'dac_24khz': '24khz', 
    'dac_16khz': '16khz',
    'dac_8khz': '8khz'
}

# SNAC model configurations
SNAC_MODEL_CONFIGS = {
    'snac_24khz': 'hubertsiuzdak/snac_24khz',
    'snac_32khz': 'hubertsiuzdak/snac_32khz', 
    'snac_44khz': 'hubertsiuzdak/snac_44khz'
}


class EncodecAudioProcessor:
    """Simplified processor to convert audio files to EnCodec .pt files"""
    
    def __init__(self, config: AudioConfig):
        """Initialize the EnCodec audio processor
        
        Args:
            config: AudioConfig with processing parameters
        """
        self.config = config
        
        if self.config.device == "auto":
            self.config.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model and processor
        self._init_model()
    
    def _get_sample_rate_from_model_name(self, model_name: str) -> int:
        """Determine sample rate based on model name"""
        if "32khz" in model_name.lower():
            return 32000
        elif "24khz" in model_name.lower():
            return 24000
        elif "48khz" in model_name.lower():
            return 48000
        else:
            # Default fallback
            return 32000
    
    def _is_stereo_model(self, model_name: str) -> bool:
        """Determine if model supports stereo audio"""
        return "48khz" in model_name.lower()
    
    def _init_model(self):
        """Initialize the EnCodec model and processor"""
        print(f"Loading {self.config.model_name} on {self.config.device}...")
        self.model = EncodecModel.from_pretrained(self.config.model_name).to(self.config.device)
        self.processor = AutoProcessor.from_pretrained(self.config.model_name)
        self.sampling_rate = self.processor.sampling_rate
        
        # Update config target_sample_rate based on model
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.config.target_sample_rate != expected_sr:
            print(f"🔄 Updating target sample rate: {self.config.target_sample_rate} -> {expected_sr}")
            self.config.target_sample_rate = expected_sr
        
        print(f"✓ Audio processor initialized: {self.config.model_name}")
        print(f"  Device: {self.config.device}")
        print(f"  Sampling rate: {self.sampling_rate} Hz")
        print(f"  Audio channels: {'Stereo' if self._is_stereo_model(self.config.model_name) else 'Mono'}")
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get basic audio information"""
        try:
            info = torchaudio.info(audio_path)
            file_size = os.path.getsize(audio_path)
            duration = info.num_frames / info.sample_rate
            
            return {
                'path': audio_path,
                'sample_rate': info.sample_rate,
                'num_frames': info.num_frames,
                'num_channels': info.num_channels,
                'duration': duration,
                'file_size': file_size,
                'bits_per_sample': info.bits_per_sample
            }
        except Exception as e:
            return {'error': f'Cannot open audio: {audio_path} - {e}'}
    
    def load_audio(self, audio_path: str, duration: Optional[float] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Load and preprocess audio file"""
        try:
            # Ensure model is initialized with correct sample rate for current config
            expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
            if self.sampling_rate != expected_sr:
                print(f"🔄 Sample rate mismatch in load_audio: {self.sampling_rate} -> {expected_sr}")
                print(f"   Reinitializing model...")
                self._init_model()
            
            # Use duration from config if not specified
            duration = duration or self.config.max_duration
            
            # Load audio - preserve stereo for 48kHz model, mono for others
            is_stereo = self._is_stereo_model(self.config.model_name)
            if is_stereo:
                audio, original_sr = librosa.load(audio_path, sr=self.sampling_rate, duration=duration, mono=False)
                # Ensure we have exactly 2 channels for stereo
                if audio.ndim == 1:
                    # Convert mono to stereo by duplicating the channel
                    audio = np.stack([audio, audio], axis=0)
                elif audio.shape[0] > 2:
                    # Downmix to stereo if more than 2 channels
                    audio = audio[:2]
            else:
                # Load as mono for 24kHz and 32kHz models
                audio, original_sr = librosa.load(audio_path, sr=self.sampling_rate, duration=duration, mono=True)
            
            if audio is None or (audio.ndim == 1 and len(audio) == 0) or (audio.ndim == 2 and audio.shape[1] == 0):
                raise ValueError(f"Cannot read audio: {audio_path}")
            
            # Calculate duration and samples based on audio shape
            if audio.ndim == 1:
                # Mono audio
                num_samples = len(audio)
                num_channels = 1
            else:
                # Stereo audio (channels, samples)
                num_samples = audio.shape[1] if audio.ndim == 2 else audio.shape[0]
                num_channels = audio.shape[0] if audio.ndim == 2 else 1
            
            # Metadata
            metadata = {
                'original_path': audio_path,
                'original_sample_rate': original_sr,
                'processed_sample_rate': self.sampling_rate,
                'duration': num_samples / self.sampling_rate,
                'num_samples': num_samples,
                'num_channels': num_channels,
                'model_name': self.config.model_name
            }
            
            return audio, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to load audio {audio_path}: {e}")
    
    def encode_audio(self, audio: np.ndarray, metadata: Dict[str, Any], base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode audio to compressed representation
        
        Args:
            audio: Audio array (numpy)
            metadata: Audio metadata from load_audio
            base_metadata: Optional base metadata loaded from JSON file with same name as media file
            
        Returns:
            Dictionary containing encoded data and metadata
        """
        print(f"🔄 Encoding audio with {len(audio)} samples...")
        
        # Ensure model is initialized for current config
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.sampling_rate != expected_sr:
            print(f"🔄 Sample rate mismatch detected: {self.sampling_rate} -> {expected_sr}")
            print(f"   Reinitializing model...")
            self._init_model()
        
        # Preprocess audio
        inputs = self.processor(
            raw_audio=audio, 
            sampling_rate=self.sampling_rate, 
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
        
        # Extend metadata with base_metadata if provided
        extended_metadata = metadata.copy()
        if base_metadata is not None:
            extended_metadata.update(base_metadata)
        
        encoded_data = {
            'metadata': extended_metadata,
            'config': self.config.__dict__,
            'model_name': self.config.model_name,
            'original_audio_shape': audio.shape
        }
        
        try:
            # Encode
            with torch.no_grad():
                encoder_outputs = self.model.encode(
                    inputs["input_values"], 
                    inputs["padding_mask"]
                )
            
            # Package results - only data needed for decoding
            encoded_data.update({
                "audio_codes": encoder_outputs.audio_codes,
                "audio_scales": encoder_outputs.audio_scales,
                "padding_mask": inputs["padding_mask"]
            })
            
            print(f"✅ Audio encoding successful!")
            print(f"✅ Encoded audio codes: {encoder_outputs.audio_codes.shape}")
            return encoded_data
            
        except Exception as e:
            print(f"❌ Failed to encode audio: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def decode_audio(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode compressed representation back to audio
        
        Args:
            encoded_data: Dictionary from encode_audio()
            
        Returns:
            Decoded audio tensor
        """
        # Check if model name in encoded data differs from current model
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        if encoded_model_name and encoded_model_name != self.config.model_name:
            print(f"🔄 Model mismatch detected: {self.config.model_name} -> {encoded_model_name}")
            print(f"   Reinitializing model and updating sample rate...")
            # Update config and reinitialize model
            self.config.model_name = encoded_model_name
            expected_sr = self._get_sample_rate_from_model_name(encoded_model_name)
            self.config.target_sample_rate = expected_sr
            self._init_model()
        
        # Move data to correct device and ensure proper dtype for model
        audio_codes = encoded_data["audio_codes"].to(self.config.device)
        # EnCodec models expect int64/long tensors for codes (for embedding lookups)
        if audio_codes.dtype != torch.long:
            audio_codes = audio_codes.long()
        
        padding_mask = encoded_data["padding_mask"].to(self.config.device)
        
        # Handle audio_scales (can be None)
        audio_scales = encoded_data["audio_scales"]
        if audio_scales is not None:
            if isinstance(audio_scales, list):
                audio_scales = [s.to(self.config.device) if s is not None else s for s in audio_scales]
            else:
                audio_scales = audio_scales.to(self.config.device)
        
        # Decode
        with torch.no_grad():
            decoded_audio = self.model.decode(
                audio_codes, 
                audio_scales, 
                padding_mask
            )[0]
        
        print(f"✅ Decoded audio: {decoded_audio.shape}")
        return decoded_audio
    
    def save_decoded_audio(self, audio_tensor: torch.Tensor, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded audio tensor to file
        
        Args:
            audio_tensor: Decoded audio tensor
            output_path: Path to save the audio file
            metadata: Optional metadata for sample rate information
            
        Returns:
            Path to saved audio file
        """
        # Use original or default sample rate
        if metadata:
            sample_rate = metadata.get('processed_sample_rate', self.sampling_rate)
        else:
            sample_rate = self.sampling_rate
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to proper format for saving
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.squeeze(0).cpu().numpy()  # Remove batch dimension only
        else:
            audio_np = audio_tensor
        
        try:
            # Save using torchaudio
            if not output_path.endswith('.wav'):
                output_path += '.wav'
            
            # Ensure proper shape for torchaudio.save
            if audio_np.ndim == 1:
                # Mono: add channel dimension
                audio_tensor_save = torch.from_numpy(audio_np).unsqueeze(0)
            else:
                # Stereo: already has channel dimension
                audio_tensor_save = torch.from_numpy(audio_np)
            
            torchaudio.save(
                output_path, 
                audio_tensor_save, 
                sample_rate=sample_rate
            )
            print(f"✅ Saved decoded audio: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving audio {output_path}: {e}")
            return None
    
    def process_single_file(self, audio_path: str, output_path: Optional[str] = None, base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single audio file and save in all formats (.car, .hdf5, .webdataset, .tfrecord)
        
        Args:
            audio_path: Path to audio file
            output_path: Optional base output path. If None, uses audio filename
            base_metadata: Optional base metadata loaded from JSON file with same name as media file
        """
        try:
            # Generate base output path if not provided
            if output_path is None:
                audio_dir = os.path.dirname(audio_path)
                audio_name = os.path.splitext(os.path.basename(audio_path))[0]
                base_output = os.path.join(audio_dir, f"{audio_name}_audio")
            else:
                base_output = os.path.splitext(output_path)[0]
            
            # Load audio
            audio, metadata = self.load_audio(audio_path)
            
            # Encode
            encoded_data = self.encode_audio(audio, metadata, base_metadata)
            
            # Calculate file sizes for reporting
            if audio.ndim == 1:
                original_size = len(audio) * 4  # float32 = 4 bytes
            else:
                original_size = audio.shape[0] * audio.shape[1] * 4  # channels * samples * 4 bytes
            
            # Prepare metadata for exports
            export_metadata = {
                "media_type": "audio",
                "processor": "EncodecAudioProcessor", 
                "model_name": self.config.model_name,
                "sample_rate": self.sampling_rate,
                "duration": metadata['duration']
            }
            
            # Save in all formats
            saved_files = {}
            
            # 1. Save as CAR format
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
            try:
                hdf5_path = f"{base_output}.h5"
                CARHandler.np_to_hdf5(encoded_data, hdf5_path, optimize_dtypes=True)
                saved_files['hdf5'] = hdf5_path
                print(f"✅ Saved HDF5: {hdf5_path}")
            except Exception as e:
                print(f"❌ Failed to save HDF5: {e}")
            
            # 3. Save as WebDataset format
            try:
                webdataset_path = f"{base_output}.tar"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
                CARHandler.np_to_webdataset(encoded_data, webdataset_path, sample_key=sample_key, optimize_dtypes=True)
                saved_files['webdataset'] = webdataset_path
                print(f"✅ Saved WebDataset: {webdataset_path}")
            except Exception as e:
                print(f"❌ Failed to save WebDataset: {e}")
            
            # 4. Save as TFRecord format
            try:
                tfrecord_path = f"{base_output}.tfrecord"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
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
                    'temporal_ratio': 'N/A',  # EnCodec doesn't provide this metric directly
                    'file_size_ratio': file_ratio,
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': compressed_size / (1024 * 1024),
                    'output_formats': list(saved_files.keys())
                }
                
                print(f"   File size: {compression_info['original_size_mb']:.1f}MB → {compression_info['compressed_size_mb']:.1f}MB ({file_ratio:.1f}x)")
            else:
                compression_info = {
                    'temporal_ratio': 'N/A',
                    'file_size_ratio': 'N/A',
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': 'N/A',
                    'output_formats': list(saved_files.keys())
                }
            
            # Use smart cache clearing to reduce overhead
            smart_empty_cache(force=True)
            
            return {
                'status': 'success',
                'input_path': audio_path,
                'output_files': saved_files,
                'duration': metadata['duration'],
                'samples': metadata['num_samples'],
                'compression': compression_info
            }
            
        except Exception as e:
            # Clear GPU cache on error
            error_cache_clear()
            return {
                'status': 'error',
                'input_path': audio_path,
                'error': str(e)
            }
    
    def load_from_car(self, car_path: str) -> Dict[str, Any]:
        """Load compressed audio data from CAR format
        
        Args:
            car_path: Path to .car file
            
        Returns:
            Dictionary with loaded data and metadata
        """
        try:
            # Read CAR file
            with open(car_path, 'rb') as f:
                car_data = f.read()
            
            # Extract optimized tensor data and metadata
            encoded_data, metadata = CARHandler.car_to_np(car_data)
            
            print(f"✅ Loaded (CAR): {car_path}")
            print(f"   Metadata: {metadata.get('processor', 'unknown')} - {metadata.get('model_name', 'unknown')}")
            print(f"   Duration: {metadata.get('duration', 'unknown')}s")
            
            return {
                'status': 'success',
                'data': encoded_data,
                'metadata': metadata,
                'file_path': car_path
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'file_path': car_path,
                'error': str(e)
            }
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        audio_extensions: Tuple[str, ...] = ('.wav', '.mp3', '.flac', '.m4a', '.ogg'),
        num_workers: int = 1,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all audio files in a directory"""
        
        # Find audio files
        pattern = "**/*" if recursive else "*"
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext}"),
                recursive=recursive
            ))
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext.upper()}"),
                recursive=recursive
            ))
        
        print(f"Found {len(audio_files)} audio files")
        
        if not audio_files:
            return {'status': 'no_files', 'processed': 0, 'errors': 0}
        
        # Prepare tasks
        tasks = []
        for audio_path in audio_files:
            # Save encoding in the same directory as the audio file with _audio suffix
            audio_dir = os.path.dirname(audio_path)
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join(audio_dir, f"{audio_name}_audio.pt")
            tasks.append((audio_path, output_path))
        
        # Process files
        results = []
        successful = 0
        errors = 0
        
        if num_workers == 1:
            # Single-threaded processing
            for audio_path, output_path in tqdm(tasks, desc="Processing audio"):
                result = self.process_single_file(audio_path, output_path)
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
                    executor.submit(self.process_single_file, audio_path, output_path): (audio_path, output_path)
                    for audio_path, output_path in tasks
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
            'total_files': len(audio_files),
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


class DACAudioProcessor:
    """Audio processor using Descript Audio Codec (DAC)"""
    
    def __init__(self, config: AudioConfig):
        """Initialize the DAC audio processor
        
        Args:
            config: AudioConfig with processing parameters
        """
        self.config = config
        
        if not DAC_AVAILABLE:
            raise ImportError("DAC not available. Please install: pip install descript-audio-codec audiotools")
        
        if self.config.device == "auto":
            self.config.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize DAC model
        self._init_model()
    
    def _get_sample_rate_from_model_name(self, model_name: str) -> int:
        """Determine sample rate based on DAC model name"""
        if "44khz" in model_name.lower():
            return 44100
        elif "24khz" in model_name.lower():
            return 24000
        elif "16khz" in model_name.lower():
            return 16000
        elif "8khz" in model_name.lower():
            return 8000
        else:
            return 44100  # Default to highest quality
    
    def _init_model(self):
        """Initialize the DAC model"""
        # Extract DAC model type from model name
        dac_model_type = DAC_MODEL_CONFIGS.get(self.config.model_name, "44khz")
        
        print(f"Loading DAC model: {dac_model_type}")
        
        # Download and load DAC model
        model_path = dac.utils.download(model_type=dac_model_type)
        self.model = dac.DAC.load(model_path)
        self.model.to(self.config.device)
        
        # Update sample rate based on model
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.config.target_sample_rate != expected_sr:
            print(f"🔄 Updating target sample rate: {self.config.target_sample_rate} -> {expected_sr}")
            self.config.target_sample_rate = expected_sr
        
        print(f"✓ DAC processor initialized: {dac_model_type}")
        print(f"  Device: {self.config.device}")
        print(f"  Sample rate: {self.config.target_sample_rate} Hz")
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get basic audio information"""
        try:
            info = torchaudio.info(audio_path)
            file_size = os.path.getsize(audio_path)
            duration = info.num_frames / info.sample_rate
            
            return {
                'path': audio_path,
                'sample_rate': info.sample_rate,
                'num_frames': info.num_frames,
                'num_channels': info.num_channels,
                'duration': duration,
                'file_size': file_size,
                'bits_per_sample': info.bits_per_sample
            }
        except Exception as e:
            return {'error': f'Cannot open audio: {audio_path} - {e}'}
    
    def load_audio(self, audio_path: str, duration: Optional[float] = None) -> Tuple[AudioSignal, Dict[str, Any]]:
        """Load and preprocess audio file using AudioSignal"""
        try:
            # Ensure model is initialized with correct sample rate
            expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
            if self.config.target_sample_rate != expected_sr:
                print(f"🔄 Sample rate mismatch in load_audio: {self.config.target_sample_rate} -> {expected_sr}")
                print(f"   Reinitializing model...")
                self._init_model()
            
            # Load audio using AudioSignal
            signal = AudioSignal(audio_path)
            
            # Resample if needed
            if signal.sample_rate != self.config.target_sample_rate:
                signal = signal.resample(self.config.target_sample_rate)
            
            # Apply duration limit if specified
            if duration or self.config.max_duration:
                max_duration = duration or self.config.max_duration
                max_samples = int(max_duration * signal.sample_rate)
                if signal.length > max_samples:
                    signal = signal[:max_samples]
            
            # Metadata
            metadata = {
                'original_path': audio_path,
                'original_sample_rate': signal.sample_rate,
                'processed_sample_rate': self.config.target_sample_rate,
                'duration': signal.duration,
                'num_samples': signal.length,
                'num_channels': signal.num_channels,
                'model_name': self.config.model_name
            }
            
            return signal, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to load audio {audio_path}: {e}")
    
    def encode_audio(self, signal: AudioSignal, metadata: Dict[str, Any], base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode audio using DAC"""
        print(f"🔄 Encoding audio with DAC ({signal.duration:.2f}s)...")
        
        # Ensure model is initialized for current config
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.config.target_sample_rate != expected_sr:
            print(f"🔄 Sample rate mismatch detected: {self.config.target_sample_rate} -> {expected_sr}")
            print(f"   Reinitializing model...")
            self._init_model()
        
        # Extend metadata with base_metadata if provided
        extended_metadata = metadata.copy()
        if base_metadata is not None:
            extended_metadata.update(base_metadata)
        
        encoded_data = {
            'metadata': extended_metadata,
            'config': self.config.__dict__,
            'model_name': self.config.model_name,
            'original_signal_shape': signal.audio_data.shape
        }
        
        try:
            # Move signal to device and encode
            signal = signal.to(self.model.device)
            
            # Preprocess and encode using DAC's encode method
            x = self.model.preprocess(signal.audio_data, signal.sample_rate)
            print(f"🔍 After preprocess shape: {x.shape}")
            z, _, _, _, _ = self.model.encode(x)
            
            # Store only the tensor needed for decoding
            encoded_data.update({
                "z": z
            })
            
            print(f"✅ DAC encoding successful!")
            print(f"✅ Compressed audio: {signal.duration:.2f}s")
            return encoded_data
            
        except Exception as e:
            print(f"❌ Failed to encode audio with DAC: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def decode_audio(self, encoded_data: Dict[str, Any]) -> AudioSignal:
        """Decode compressed audio data using DAC"""
        # Check if model name in encoded data differs from current model
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        if encoded_model_name and encoded_model_name != self.config.model_name:
            print(f"🔄 Model mismatch detected: {self.config.model_name} -> {encoded_model_name}")
            print(f"   Reinitializing model and updating sample rate...")
            # Update config and reinitialize model
            self.config.model_name = encoded_model_name
            expected_sr = self._get_sample_rate_from_model_name(encoded_model_name)
            self.config.target_sample_rate = expected_sr
            self._init_model()
        
        try:
            # Check if using new tensor-based format or legacy compressed format
            if "z" in encoded_data:
                # New tensor-based format
                z = encoded_data["z"]
                
                # Move to model device for decoding and ensure proper dtype
                if hasattr(z, 'to'):
                    z = z.to(self.model.device)
                    # DAC decode expects float tensors for z (latent representation)
                    if z.dtype != torch.float32:
                        z = z.float()
                
                # Decode using DAC's decode method
                y = self.model.decode(z)
                
                # Convert to AudioSignal  
                from audiotools import AudioSignal
                # Use sample rate from metadata since it's no longer stored in encoded data
                sample_rate = encoded_data.get("metadata", {}).get("processed_sample_rate", self.config.target_sample_rate)
                decoded_signal = AudioSignal(y, sample_rate=sample_rate)
                
            elif "compressed_data" in encoded_data:
                # Legacy compressed format - handle for backward compatibility
                compressed_data = encoded_data["compressed_data"]
                
                if isinstance(compressed_data, dict) and compressed_data.get('is_dac_file'):
                    # DAC file format
                    dac_file_bytes = compressed_data['dac_file_data']
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.dac', delete=False) as tmp:
                        tmp.write(dac_file_bytes)
                        tmp.flush()
                        compressed = dac.DACFile.load(tmp.name)
                    os.unlink(tmp.name)
                    decoded_signal = self.model.decompress(compressed)
                elif hasattr(compressed_data, 'codes') and hasattr(compressed_data, 'save'):
                    # Direct DACFile object
                    decoded_signal = self.model.decompress(compressed_data)
                else:
                    raise ValueError(
                        "Legacy DAC compressed data format detected. "
                        "This encoding was created with an older version and cannot be decoded. "
                        "Please re-encode the original audio file with the updated DAC processor."
                    )
            else:
                raise ValueError("Missing encoded data - neither 'z' nor 'compressed_data' found")
            
            print(f"✅ Decoded audio: {decoded_signal.duration:.2f}s")
            return decoded_signal
            
        except Exception as e:
            print(f"❌ Failed to decode audio with DAC: {e}")
            raise
    
    def save_decoded_audio(self, signal: AudioSignal, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded AudioSignal to file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save using AudioSignal's write method
            signal.write(output_path)
            
            print(f"✅ Saved decoded audio: {output_path}")
            if metadata:  # Use metadata if provided for logging
                print(f"   Original duration: {metadata.get('duration', 'unknown')}s")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving audio {output_path}: {e}")
            return None
    
    def process_single_file(self, audio_path: str, output_path: Optional[str] = None, base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single audio file using DAC and save in all formats (.car, .hdf5, .webdataset, .tfrecord)"""
        try:
            # Generate base output path if not provided
            if output_path is None:
                audio_dir = os.path.dirname(audio_path)
                audio_name = os.path.splitext(os.path.basename(audio_path))[0]
                base_output = os.path.join(audio_dir, f"{audio_name}_dac")
            else:
                base_output = os.path.splitext(output_path)[0]
            
            # Load audio
            signal, metadata = self.load_audio(audio_path)
            
            # Encode using DAC
            encoded_data = self.encode_audio(signal, metadata, base_metadata)
            
            # Calculate file sizes for reporting
            original_size = signal.length * signal.num_channels * 4  # float32 = 4 bytes
            
            # Prepare metadata for exports
            export_metadata = {
                "media_type": "audio",
                "processor": "DACAudioProcessor",
                "model_name": self.config.model_name,
                "sample_rate": self.config.target_sample_rate,
                "duration": metadata['duration']
            }
            
            # Save in all formats
            saved_files = {}
            
            # 1. Save as CAR format
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
            try:
                hdf5_path = f"{base_output}.h5"
                CARHandler.np_to_hdf5(encoded_data, hdf5_path, optimize_dtypes=True)
                saved_files['hdf5'] = hdf5_path
                print(f"✅ Saved HDF5: {hdf5_path}")
            except Exception as e:
                print(f"❌ Failed to save HDF5: {e}")
            
            # 3. Save as WebDataset format
            try:
                webdataset_path = f"{base_output}.tar"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
                CARHandler.np_to_webdataset(encoded_data, webdataset_path, sample_key=sample_key, optimize_dtypes=True)
                saved_files['webdataset'] = webdataset_path
                print(f"✅ Saved WebDataset: {webdataset_path}")
            except Exception as e:
                print(f"❌ Failed to save WebDataset: {e}")
            
            # 4. Save as TFRecord format
            try:
                tfrecord_path = f"{base_output}.tfrecord"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
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
                    'temporal_ratio': 'N/A',  # DAC doesn't provide this directly
                    'file_size_ratio': file_ratio,
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': compressed_size / (1024 * 1024),
                    'output_formats': list(saved_files.keys())
                }
                
                print(f"   File size: {compression_info['original_size_mb']:.1f}MB → {compression_info['compressed_size_mb']:.1f}MB ({file_ratio:.1f}x)")
            else:
                compression_info = {
                    'temporal_ratio': 'N/A',
                    'file_size_ratio': 'N/A',
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': 'N/A',
                    'output_formats': list(saved_files.keys())
                }
            
            # Use smart cache clearing to reduce overhead
            smart_empty_cache(force=True)
            
            return {
                'status': 'success',
                'input_path': audio_path,
                'output_files': saved_files,
                'duration': metadata['duration'],
                'samples': metadata['num_samples'],
                'compression': compression_info
            }
            
        except Exception as e:
            # Clear GPU cache on error
            error_cache_clear()
            return {
                'status': 'error',
                'input_path': audio_path,
                'error': str(e)
            }
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        audio_extensions: Tuple[str, ...] = ('.wav', '.mp3', '.flac', '.m4a', '.ogg'),
        num_workers: int = 1,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all audio files in a directory using DAC"""
        
        # Find audio files
        pattern = "**/*" if recursive else "*"
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext}"),
                recursive=recursive
            ))
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext.upper()}"),
                recursive=recursive
            ))
        
        print(f"Found {len(audio_files)} audio files")
        
        if not audio_files:
            return {'status': 'no_files', 'processed': 0, 'errors': 0}
        
        # Prepare tasks
        tasks = []
        for audio_path in audio_files:
            # Save encoding in the same directory as the audio file with _dac suffix
            audio_dir = os.path.dirname(audio_path)
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            file_ext = ".car" if self.config.output_format == "car" else ".pt"
            output_path = os.path.join(audio_dir, f"{audio_name}_dac{file_ext}")
            tasks.append((audio_path, output_path))
        
        # Process files
        results = []
        successful = 0
        errors = 0
        
        if num_workers == 1:
            # Single-threaded processing
            for audio_path, output_path in tqdm(tasks, desc="Processing audio with DAC"):
                result = self.process_single_file(audio_path, output_path)
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
                    executor.submit(self.process_single_file, audio_path, output_path): (audio_path, output_path)
                    for audio_path, output_path in tasks
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
            'total_files': len(audio_files),
            'successful': successful,
            'errors': errors,
            'results': results
        }
        
        report_path = os.path.join(output_dir, "dac_preprocessing_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ DAC processing complete!")
        print(f"   Successful: {successful}")
        print(f"   Errors: {errors}")
        print(f"   Report saved: {report_path}")
        
        return report


class SNACAudioProcessor:
    """Audio processor using Multi-Scale Neural Audio Codec (SNAC)"""
    
    def __init__(self, config: AudioConfig):
        """Initialize the SNAC audio processor
        
        Args:
            config: AudioConfig with processing parameters
        """
        self.config = config
        
        if not SNAC_AVAILABLE:
            raise ImportError("SNAC not available. Please install: pip install snac")
        
        if self.config.device == "auto":
            self.config.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize SNAC model
        self._init_model()
    
    def _get_sample_rate_from_model_name(self, model_name: str) -> int:
        """Determine sample rate based on SNAC model name"""
        if "44khz" in model_name.lower():
            return 44100
        elif "32khz" in model_name.lower():
            return 32000
        elif "24khz" in model_name.lower():
            return 24000
        else:
            return 44100  # Default to highest quality
    
    def _init_model(self):
        """Initialize the SNAC model"""
        # Get the Hugging Face model name
        snac_model_name = SNAC_MODEL_CONFIGS.get(self.config.model_name, self.config.model_name)
        
        print(f"Loading SNAC model: {snac_model_name}")
        
        # Load SNAC model from pretrained
        self.model = SNAC.from_pretrained(snac_model_name).eval().to(self.config.device)
        
        # Update sample rate based on model
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.config.target_sample_rate != expected_sr:
            print(f"🔄 Updating target sample rate: {self.config.target_sample_rate} -> {expected_sr}")
            self.config.target_sample_rate = expected_sr
        
        print(f"✓ SNAC processor initialized: {snac_model_name}")
        print(f"  Device: {self.config.device}")
        print(f"  Sample rate: {self.config.target_sample_rate} Hz")
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get basic audio information"""
        try:
            info = torchaudio.info(audio_path)
            file_size = os.path.getsize(audio_path)
            duration = info.num_frames / info.sample_rate
            
            return {
                'path': audio_path,
                'sample_rate': info.sample_rate,
                'num_frames': info.num_frames,
                'num_channels': info.num_channels,
                'duration': duration,
                'file_size': file_size,
                'bits_per_sample': info.bits_per_sample
            }
        except Exception as e:
            return {'error': f'Cannot open audio: {audio_path} - {e}'}
    
    def load_audio(self, audio_path: str, duration: Optional[float] = None) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """Load and preprocess audio file"""
        try:
            # Ensure model is initialized with correct sample rate
            expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
            if self.config.target_sample_rate != expected_sr:
                print(f"🔄 Sample rate mismatch in load_audio: {self.config.target_sample_rate} -> {expected_sr}")
                print(f"   Reinitializing model...")
                self._init_model()
            
            # Use duration from config if not specified
            duration = duration or self.config.max_duration
            
            # Load audio - SNAC expects mono audio (B, 1, T)
            audio, original_sr = torchaudio.load(audio_path)
            
            # Convert stereo to mono if needed
            if audio.shape[0] > 1:
                audio = torch.mean(audio, dim=0, keepdim=True)
            
            # Resample if needed
            if original_sr != self.config.target_sample_rate:
                audio = torchaudio.functional.resample(
                    audio, original_sr, self.config.target_sample_rate
                )
            
            # Apply duration limit if specified
            if duration:
                max_samples = int(duration * self.config.target_sample_rate)
                if audio.shape[1] > max_samples:
                    audio = audio[:, :max_samples]
            
            # Add batch dimension: (1, 1, T)
            audio = audio.unsqueeze(0)
            
            # Metadata
            metadata = {
                'original_path': audio_path,
                'original_sample_rate': original_sr,
                'processed_sample_rate': self.config.target_sample_rate,
                'duration': audio.shape[2] / self.config.target_sample_rate,
                'num_samples': audio.shape[2],
                'num_channels': 1,  # SNAC only supports mono
                'model_name': self.config.model_name
            }
            
            return audio, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to load audio {audio_path}: {e}")
    
    def encode_audio(self, audio: torch.Tensor, metadata: Dict[str, Any], base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode audio using SNAC"""
        print(f"🔄 Encoding audio with SNAC ({audio.shape[2] / self.config.target_sample_rate:.2f}s)...")
        
        # Ensure model is initialized for current config
        expected_sr = self._get_sample_rate_from_model_name(self.config.model_name)
        if self.config.target_sample_rate != expected_sr:
            print(f"🔄 Sample rate mismatch detected: {self.config.target_sample_rate} -> {expected_sr}")
            print(f"   Reinitializing model...")
            self._init_model()
        
        # Extend metadata with base_metadata if provided
        extended_metadata = metadata.copy()
        if base_metadata is not None:
            extended_metadata.update(base_metadata)
        
        encoded_data = {
            'metadata': extended_metadata,
            'config': self.config.__dict__,
            'model_name': self.config.model_name,
            'original_audio_shape': audio.shape
        }
        
        try:
            # Move audio to device
            audio = audio.to(self.config.device)
            
            # Encode using SNAC
            with torch.inference_mode():
                codes = self.model.encode(audio)
            
            # Store only the codes needed for decoding
            encoded_data.update({
                "audio_codes": codes  # List of token sequences at different temporal resolutions
            })
            
            print(f"✅ SNAC encoding successful!")
            print(f"✅ Hierarchical codes: {[code.shape[1] for code in codes]} tokens at different resolutions")
            return encoded_data
            
        except Exception as e:
            print(f"❌ Failed to encode audio with SNAC: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def decode_audio(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode compressed audio data using SNAC"""
        # Check if model name in encoded data differs from current model
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        if encoded_model_name and encoded_model_name != self.config.model_name:
            print(f"🔄 Model mismatch detected: {self.config.model_name} -> {encoded_model_name}")
            print(f"   Reinitializing model and updating sample rate...")
            # Update config and reinitialize model
            self.config.model_name = encoded_model_name
            expected_sr = self._get_sample_rate_from_model_name(encoded_model_name)
            self.config.target_sample_rate = expected_sr
            self._init_model()
        
        try:
            # Get hierarchical codes
            codes = encoded_data["audio_codes"]
            
            # Move codes to device and ensure proper dtype for model
            if isinstance(codes, list):
                codes = [code.to(self.config.device) for code in codes]
                # SNAC models expect int64/long tensors for hierarchical codes (for embedding lookups)
                codes = [code.long() if code.dtype != torch.long else code for code in codes]
            else:
                codes = codes.to(self.config.device)
                if codes.dtype != torch.long:
                    codes = codes.long()
            
            # Decode using SNAC
            with torch.inference_mode():
                decoded_audio = self.model.decode(codes)
            
            print(f"✅ Decoded audio: {decoded_audio.shape}")
            return decoded_audio
            
        except Exception as e:
            print(f"❌ Failed to decode audio with SNAC: {e}")
            raise
    
    def save_decoded_audio(self, audio_tensor: torch.Tensor, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded audio tensor to file"""
        try:
            # Use metadata sample rate if available
            if metadata:
                sample_rate = metadata.get('processed_sample_rate', self.config.target_sample_rate)
            else:
                sample_rate = self.config.target_sample_rate
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert tensor to proper format for saving
            if isinstance(audio_tensor, torch.Tensor):
                # Remove batch dimension and move to CPU
                audio_np = audio_tensor.squeeze().cpu()
            else:
                audio_np = audio_tensor
            
            # Ensure we have the right shape for torchaudio.save
            if audio_np.dim() == 1:
                audio_np = audio_np.unsqueeze(0)  # Add channel dimension
            
            # Save using torchaudio
            if not output_path.endswith('.wav'):
                output_path += '.wav'
                
            torchaudio.save(output_path, audio_np, sample_rate=sample_rate)
            
            print(f"✅ Saved decoded audio: {output_path}")
            if metadata:
                print(f"   Original duration: {metadata.get('duration', 'unknown')}s")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving audio {output_path}: {e}")
            return None
    
    def process_single_file(self, audio_path: str, output_path: Optional[str] = None, base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single audio file using SNAC and save in all formats (.car, .hdf5, .webdataset, .tfrecord)"""
        try:
            # Generate base output path if not provided
            if output_path is None:
                audio_dir = os.path.dirname(audio_path)
                audio_name = os.path.splitext(os.path.basename(audio_path))[0]
                base_output = os.path.join(audio_dir, f"{audio_name}_snac")
            else:
                base_output = os.path.splitext(output_path)[0]
            
            # Load audio
            audio, metadata = self.load_audio(audio_path)
            
            # Encode using SNAC
            encoded_data = self.encode_audio(audio, metadata, base_metadata)
            
            # Calculate file sizes and compression ratio
            original_size = audio.numel() * 4  # float32 = 4 bytes
            
            # Calculate temporal compression ratio from hierarchical codes
            total_codes = sum(code.numel() for code in encoded_data["audio_codes"])
            temporal_ratio = audio.shape[2] / total_codes if total_codes > 0 else 1
            
            # Prepare metadata for exports
            export_metadata = {
                "media_type": "audio",
                "processor": "SNACAudioProcessor",
                "model_name": self.config.model_name,
                "sample_rate": self.config.target_sample_rate,
                "duration": metadata['duration']
            }
            
            # Save in all formats
            saved_files = {}
            
            # 1. Save as CAR format
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
            try:
                hdf5_path = f"{base_output}.h5"
                CARHandler.np_to_hdf5(encoded_data, hdf5_path, optimize_dtypes=True)
                saved_files['hdf5'] = hdf5_path
                print(f"✅ Saved HDF5: {hdf5_path}")
            except Exception as e:
                print(f"❌ Failed to save HDF5: {e}")
            
            # 3. Save as WebDataset format
            try:
                webdataset_path = f"{base_output}.tar"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
                CARHandler.np_to_webdataset(encoded_data, webdataset_path, sample_key=sample_key, optimize_dtypes=True)
                saved_files['webdataset'] = webdataset_path
                print(f"✅ Saved WebDataset: {webdataset_path}")
            except Exception as e:
                print(f"❌ Failed to save WebDataset: {e}")
            
            # 4. Save as TFRecord format
            try:
                tfrecord_path = f"{base_output}.tfrecord"
                sample_key = os.path.splitext(os.path.basename(audio_path))[0]
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
                    'temporal_ratio': temporal_ratio,
                    'file_size_ratio': file_ratio,
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': compressed_size / (1024 * 1024),
                    'output_formats': list(saved_files.keys()),
                    'hierarchical_codes': [code.shape for code in encoded_data["audio_codes"]]
                }
                
                print(f"   File size: {compression_info['original_size_mb']:.1f}MB → {compression_info['compressed_size_mb']:.1f}MB ({file_ratio:.1f}x)")
                print(f"   Temporal compression: {temporal_ratio:.1f}x")
            else:
                compression_info = {
                    'temporal_ratio': temporal_ratio,
                    'file_size_ratio': 'N/A',
                    'original_size_mb': original_size / (1024 * 1024),
                    'compressed_size_mb': 'N/A',
                    'output_formats': list(saved_files.keys()),
                    'hierarchical_codes': [code.shape for code in encoded_data["audio_codes"]]
                }
                print(f"   Temporal compression: {temporal_ratio:.1f}x")
            
            # Use smart cache clearing to reduce overhead
            smart_empty_cache(force=True)
            
            return {
                'status': 'success',
                'input_path': audio_path,
                'output_files': saved_files,
                'duration': metadata['duration'],
                'samples': metadata['num_samples'],
                'compression': compression_info
            }
            
        except Exception as e:
            # Clear GPU cache on error
            error_cache_clear()
            return {
                'status': 'error',
                'input_path': audio_path,
                'error': str(e)
            }
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        audio_extensions: Tuple[str, ...] = ('.wav', '.mp3', '.flac', '.m4a', '.ogg'),
        num_workers: int = 1,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all audio files in a directory using SNAC"""
        
        # Find audio files
        pattern = "**/*" if recursive else "*"
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext}"),
                recursive=recursive
            ))
            audio_files.extend(glob.glob(
                os.path.join(input_dir, f"{pattern}{ext.upper()}"),
                recursive=recursive
            ))
        
        print(f"Found {len(audio_files)} audio files")
        
        if not audio_files:
            return {'status': 'no_files', 'processed': 0, 'errors': 0}
        
        # Prepare tasks
        tasks = []
        for audio_path in audio_files:
            # Save encoding in the same directory as the audio file with _snac suffix
            audio_dir = os.path.dirname(audio_path)
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            file_ext = ".car" if self.config.output_format == "car" else ".pt"
            output_path = os.path.join(audio_dir, f"{audio_name}_snac{file_ext}")
            tasks.append((audio_path, output_path))
        
        # Process files
        results = []
        successful = 0
        errors = 0
        
        if num_workers == 1:
            # Single-threaded processing
            for audio_path, output_path in tqdm(tasks, desc="Processing audio with SNAC"):
                result = self.process_single_file(audio_path, output_path)
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
                    executor.submit(self.process_single_file, audio_path, output_path): (audio_path, output_path)
                    for audio_path, output_path in tasks
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
            'total_files': len(audio_files),
            'successful': successful,
            'errors': errors,
            'results': results
        }
        
        report_path = os.path.join(output_dir, "snac_preprocessing_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ SNAC processing complete!")
        print(f"   Successful: {successful}")
        print(f"   Errors: {errors}")
        print(f"   Report saved: {report_path}")
        
        return report


class EncodecAudioDataset(Dataset):
    """PyTorch Dataset for loading EnCodec audio files"""
    
    def __init__(
        self,
        data_dir: str,
        return_decoded: bool = False,
        return_codes: bool = True,
        device: str = "cpu",
        cache_decoded: bool = False,
        save_decoded: bool = False,
        decoded_output_dir: str = "./decoded_audio"
    ):
        """Initialize the dataset
        
        Args:
            data_dir: Directory containing .pt files
            return_decoded: Return decoded audio
            return_codes: Return encoded audio codes
            device: Device to load tensors on
            cache_decoded: Cache decoded audio in memory (use carefully!)
            save_decoded: Save decoded audio to files
            decoded_output_dir: Directory to save decoded audio files
        """
        self.data_dir = data_dir
        self.return_decoded = return_decoded
        self.return_codes = return_codes
        self.device = device
        self.cache_decoded = cache_decoded
        self.save_decoded = save_decoded
        self.decoded_output_dir = decoded_output_dir
        
        # Create output directory if saving decoded audio
        if self.save_decoded:
            os.makedirs(self.decoded_output_dir, exist_ok=True)
        
        # Find all .pt files
        self.file_paths = glob.glob(os.path.join(data_dir, "**/*.pt"), recursive=True)
        print(f"Found {len(self.file_paths)} .pt files in {data_dir}")
        
        if not self.file_paths:
            raise ValueError(f"No .pt files found in {data_dir}")
        
        # Load processor if we need to decode
        self.processor = None
        if self.return_decoded or self.save_decoded:
            # Load first file to get config
            sample_data = torch.load(self.file_paths[0], map_location='cpu')
            config_dict = sample_data.get('config', {})
            
            print("Loading EnCodec processor for decoding...")
            try:
                model_name = config_dict.get('model_name', 'facebook/encodec_32khz')
                
                self.model = EncodecModel.from_pretrained(model_name).to(device)
                self.auto_processor = AutoProcessor.from_pretrained(model_name)
                self.sampling_rate = self.auto_processor.sampling_rate
                
                print(f"✓ Processor loaded: {model_name}")
            except Exception as e:
                print(f"⚠️ Failed to load processor: {e}")
                self.return_decoded = False
                self.save_decoded = False
        
        # Cache for decoded audio
        self.decoded_cache = {} if cache_decoded else None
        
        # Track saved audio to avoid re-saving
        self.saved_audio = set()
        
        # Load metadata from first file
        sample_data = torch.load(self.file_paths[0], map_location='cpu')
        self.model_name = sample_data.get('model_name', 'unknown')
        
        print(f"✓ Dataset ready: {len(self)} audio files")
        print(f"   Model: {self.model_name}")
        print(f"   Returns: {'decoded' if return_decoded else ''} {'codes' if return_codes else ''}")
        if self.save_decoded:
            print(f"   Saving decoded audio to: {self.decoded_output_dir}")
    
    def __len__(self) -> int:
        return len(self.file_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        file_path = self.file_paths[idx]
        
        # Load encoded data
        encoded_data = torch.load(file_path, map_location='cpu')
        
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "metadata": encoded_data["metadata"]
        }
        
        # Return encoded codes if requested
        if self.return_codes:
            if 'audio_codes' in encoded_data:
                codes = encoded_data['audio_codes']
                result["audio_codes"] = codes.to(self.device)
            
            if 'audio_scales' in encoded_data:
                scales = encoded_data['audio_scales']
                if scales is not None:
                    if isinstance(scales, list):
                        result["audio_scales"] = [s.to(self.device) if s is not None else s for s in scales]
                    else:
                        result["audio_scales"] = scales.to(self.device)
            
            if 'padding_mask' in encoded_data:
                mask = encoded_data['padding_mask']
                result["padding_mask"] = mask.to(self.device)
        
        # Handle decoded audio (for returning and/or saving)
        decoded_audio = None
        if self.return_decoded or self.save_decoded:
            # Check cache first
            if self.cache_decoded and idx in self.decoded_cache:
                decoded_audio = self.decoded_cache[idx]
            else:
                # Decode audio
                if self.model is None:
                    # Create dummy decoded audio
                    # Use metadata to get original length instead of stored value
                    num_samples = encoded_data.get("metadata", {}).get("num_samples", 32000)
                    decoded_audio = torch.zeros(1, num_samples).float()
                    print(f"⚠️ Created dummy decoded audio: {decoded_audio.shape}")
                else:
                    try:
                        decoded_audio = self._decode_audio_data(encoded_data)
                    except Exception as e:
                        print(f"⚠️ Decoding failed: {e}")
                        # Use metadata to get original length instead of stored value
                        num_samples = encoded_data.get("metadata", {}).get("num_samples", 32000)
                        decoded_audio = torch.zeros(1, num_samples).float()
                
                # Cache if enabled
                if self.cache_decoded:
                    self.decoded_cache[idx] = decoded_audio
            
            # Save decoded audio if requested
            if self.save_decoded and idx not in self.saved_audio:
                audio_name = os.path.splitext(result["file_name"])[0]
                output_path = os.path.join(self.decoded_output_dir, f"{audio_name}_decoded.wav")
                
                # Get metadata
                metadata = encoded_data.get("metadata", {})
                
                saved_path = self.save_decoded_audio(decoded_audio, output_path, metadata)
                if saved_path:
                    result["decoded_audio_path"] = saved_path
                    self.saved_audio.add(idx)
        
        # Return decoded audio tensor if requested
        if self.return_decoded and decoded_audio is not None:
            result["audio"] = decoded_audio.to(self.device)
        
        return result
    
    def _decode_audio_data(self, encoded_data: Dict[str, Any]) -> torch.Tensor:
        """Decode audio data using the processor"""
        # Move data to correct device
        audio_codes = encoded_data["audio_codes"].to(self.device)
        padding_mask = encoded_data["padding_mask"].to(self.device)
        
        # Handle audio_scales
        audio_scales = encoded_data["audio_scales"]
        if audio_scales is not None:
            if isinstance(audio_scales, list):
                audio_scales = [s.to(self.device) if s is not None else s for s in audio_scales]
            else:
                audio_scales = audio_scales.to(self.device)
        
        # Decode
        with torch.no_grad():
            decoded_audio = self.model.decode(
                audio_codes, 
                audio_scales, 
                padding_mask
            )[0]
        
        decoded_audio = decoded_audio.cpu().float()
        return decoded_audio
    
    def save_decoded_audio(self, audio_tensor: torch.Tensor, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded audio tensor to file"""
        # Use original or default sample rate
        if metadata:
            sample_rate = metadata.get('processed_sample_rate', 32000)
        else:
            sample_rate = 32000
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert tensor to proper format
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.squeeze().cpu().numpy()
        else:
            audio_np = audio_tensor
        
        try:
            # Save using torchaudio
            torchaudio.save(
                output_path, 
                torch.from_numpy(audio_np).unsqueeze(0), 
                sample_rate=sample_rate
            )
            print(f"✅ Saved decoded audio: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving audio {output_path}: {e}")
            return None


def collate_fn_audio(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Custom collate function for batching audio data"""
    
    # Collect all keys
    keys = set()
    for item in batch:
        keys.update(item.keys())
    
    collated = {}
    
    for key in keys:
        values = [item.get(key) for item in batch if key in item]
        
        if key in ["audio", "audio_codes", "padding_mask"]:
            # Handle variable length sequences
            if values and isinstance(values[0], torch.Tensor):
                # Find max length in batch
                max_len = max(v.shape[-1] for v in values)  # Last dimension is usually time
                padded_values = []
                for v in values:
                    if v.shape[-1] < max_len:
                        pad_len = max_len - v.shape[-1]
                        # Pad the last dimension
                        pad_shape = [0, pad_len] + [0, 0] * (v.dim() - 1)
                        v = F.pad(v, pad_shape)
                    padded_values.append(v)
                
                collated[key] = torch.stack(padded_values)
            else:
                collated[key] = values
        else:
            # Other values (metadata, paths, etc.)
            collated[key] = values
    
    return collated


# ============ USAGE EXAMPLES ============

def preprocess_audio_dataset(
    input_dir: str,
    output_dir: str,
    model_name: str = "facebook/encodec_32khz",
    max_duration: Optional[float] = None,
    num_workers: int = 1
):
    """Preprocess an entire audio dataset"""
    
    config = AudioConfig(
        model_name=model_name,
        max_duration=max_duration
    )
    
    processor = EncodecAudioProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        recursive=True
    )
    
    return report


def create_audio_dataloader(
    data_dir: str,
    batch_size: int = 4,
    return_decoded: bool = False,
    return_codes: bool = True,
    num_workers: int = 2,
    shuffle: bool = True,
    save_decoded: bool = False,
    decoded_output_dir: str = "./decoded_audio"
) -> DataLoader:
    """Create a DataLoader for audio data"""
    
    dataset = EncodecAudioDataset(
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
        collate_fn=collate_fn_audio,
        pin_memory=torch.cuda.is_available()
    )
    
    return dataloader


def decode_and_save_all_audio(
    data_dir: str,
    output_dir: str = "./decoded_audio",
    max_audio: Optional[int] = None
):
    """Decode and save all audio in a dataset to audio files"""
    
    dataset = EncodecAudioDataset(
        data_dir=data_dir,
        return_decoded=False,  # Don't return tensors, just save
        return_codes=False,
        save_decoded=True,
        decoded_output_dir=output_dir
    )
    
    print(f"🎵 Decoding and saving {len(dataset)} audio files to {output_dir}")
    
    max_audio = max_audio or len(dataset)
    saved_count = 0
    
    for i in tqdm(range(min(max_audio, len(dataset))), desc="Decoding audio"):
        try:
            item = dataset[i]  # This will trigger decoding and saving
            if "decoded_audio_path" in item:
                saved_count += 1
        except Exception as e:
            print(f"❌ Failed to decode audio {i}: {e}")
    
    print(f"✅ Successfully decoded and saved {saved_count}/{max_audio} audio files")
    return saved_count


def example_usage():
    """Example usage of the audio pipeline"""
    
    # Initialize processor
    processor = EncodecAudioProcessor(AudioConfig())
    
    # Example 1: Compress an audio file
    print("=== COMPRESSION EXAMPLE ===")
    input_file = "/content/test_data/audio.wav"
    
    if os.path.exists(input_file):
        # Process with auto naming
        result = processor.process_single_file(input_file)
        if result['status'] == 'success':
            compressed_file = result['output_path']
            print(f"✅ Compression complete: {compressed_file}")
            
            # Example: Decode and save audio
            print("\n=== DECODING EXAMPLE ===")
            encoded_data = torch.load(compressed_file, map_location='cpu')
            decoded_audio = processor.decode_audio(encoded_data)
            output_audio_path = "./decoded_example.wav"
            saved_path = processor.save_decoded_audio(decoded_audio, output_audio_path, metadata=encoded_data.get('metadata'))
            if saved_path:
                print(f"✅ Decoded audio saved: {saved_path}")
    
    # Example 2: Dataset with automatic audio saving
    print("\n=== DATASET WITH AUDIO SAVING ===")
    
    try:
        # Create dataset that automatically saves decoded audio
        dataset = EncodecAudioDataset(
            data_dir="/content/test_data",
            return_decoded=False,      # Don't return tensors (save memory)
            return_codes=True,         # Return encoded codes
            save_decoded=True,         # Auto-save decoded audio
            decoded_output_dir="./decoded_audio"  # Where to save audio files
        )
        
        print(f"✅ Dataset created with {len(dataset)} audio files")
        print("   Decoded audio will be automatically saved to ./decoded_audio/")
        
        # Test loading a few items (this will trigger decoding and saving)
        for i in range(min(3, len(dataset))):
            item = dataset[i]
            print(f"   Processed item {i}: {item['file_name']}")
            if 'decoded_audio_path' in item:
                print(f"     → Saved to: {item['decoded_audio_path']}")
        
        print("\n✅ Audio pipeline examples completed!")
        
    except Exception as e:
        print(f"Dataset test failed: {e}")
        print("Create compressed audio first using preprocess_audio_dataset()")


# ============ BATCH PROCESSING UTILITIES ============

def batch_compress_audio_directory(input_dir: str, output_dir: str, **kwargs):
    """Compress all audio files in a directory"""
    config = AudioConfig(**kwargs)
    
    # Choose processor based on model type
    model_type = kwargs.get('model_type', 'encodec')
    if model_type == 'dac':
        processor = DACAudioProcessor(config)
    elif model_type == 'snac':
        processor = SNACAudioProcessor(config)
    else:
        processor = EncodecAudioProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=kwargs.get('num_workers', 1)
    )
    
    print(f"✅ Batch compression complete: {output_dir}")
    return report

# ============ DAC-SPECIFIC UTILITIES ============

def preprocess_audio_dataset_dac(
    input_dir: str,
    output_dir: str,
    model_name: str = "dac_44khz",
    max_duration: Optional[float] = None,
    num_workers: int = 1
):
    """Preprocess an entire audio dataset using DAC"""
    
    config = AudioConfig(
        model_name=model_name,
        max_duration=max_duration,
        model_type="dac"
    )
    
    processor = DACAudioProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        recursive=True
    )
    
    return report

# ============ SNAC-SPECIFIC UTILITIES ============

def preprocess_audio_dataset_snac(
    input_dir: str,
    output_dir: str,
    model_name: str = "snac_44khz",
    max_duration: Optional[float] = None,
    num_workers: int = 1
):
    """Preprocess an entire audio dataset using SNAC"""
    
    config = AudioConfig(
        model_name=model_name,
        max_duration=max_duration,
        model_type="snac"
    )
    
    processor = SNACAudioProcessor(config)
    
    report = processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        recursive=True
    )
    
    return report

def example_snac_usage():
    """Example usage of SNAC processor"""
    
    print("=== SNAC PROCESSING EXAMPLE ===")
    
    # Initialize SNAC processor
    try:
        config = AudioConfig(model_name="snac_44khz", model_type="snac")
        processor = SNACAudioProcessor(config)
        
        print("✅ SNAC processor initialized successfully")
        print(f"   Model: {processor.config.model_name}")
        print(f"   Device: {processor.config.device}")
        print(f"   Sample Rate: {processor.config.target_sample_rate} Hz")
        print(f"   Features: Hierarchical encoding with multi-scale tokens")
        print(f"   Use case: Music and sound effects generation")
        
        # Example processing would go here
        # processor.process_single_file("input.wav")
        
    except ImportError as e:
        print(f"❌ SNAC not available: {e}")
        print("Please install: pip install snac")
    except Exception as e:
        print(f"❌ SNAC processor failed: {e}")

def create_audio_processor(model_type: str = "encodec", **config_kwargs) -> Any:
    """Create appropriate audio processor based on model type"""
    config = AudioConfig(**config_kwargs, model_type=model_type)
    
    if model_type == "dac":
        if not DAC_AVAILABLE:
            raise ImportError("DAC not available. Please install: pip install descript-audio-codec audiotools")
        return DACAudioProcessor(config)
    elif model_type == "snac":
        if not SNAC_AVAILABLE:
            raise ImportError("SNAC not available. Please install: pip install snac")
        return SNACAudioProcessor(config)
    else:
        return EncodecAudioProcessor(config)

def example_dac_usage():
    """Example usage of DAC processor"""
    
    print("=== DAC PROCESSING EXAMPLE ===")
    
    # Initialize DAC processor
    try:
        config = AudioConfig(model_name="dac_44khz", model_type="dac")
        processor = DACAudioProcessor(config)
        
        print("✅ DAC processor initialized successfully")
        print(f"   Model: {processor.config.model_name}")
        print(f"   Device: {processor.config.device}")
        
        # Example processing would go here
        # processor.process_single_file("input.wav")
        
    except ImportError as e:
        print(f"❌ DAC not available: {e}")
        print("Please install: pip install descript-audio-codec audiotools")
    except Exception as e:
        print(f"❌ DAC processor failed: {e}")

def get_supported_models() -> Dict[str, List[str]]:
    """Get list of supported model types and their variants"""
    models = {
        "encodec": [
            "facebook/encodec_24khz",
            "facebook/encodec_32khz", 
            "facebook/encodec_48khz"
        ]
    }
    
    # if DAC_AVAILABLE:
    #     models["dac"] = [
    #         "dac_44khz",
    #         "dac_24khz",
    #         "dac_16khz", 
    #         "dac_8khz"
    #     ]
    
    if SNAC_AVAILABLE:
        models["snac"] = [
            "snac_44khz",
            "snac_32khz",
            "snac_24khz"
        ]
    
    return models


class AudioProcessor:
    """Unified audio processor that automatically handles DAC, EnCodec, and SNAC models"""
    
    def __init__(self, config: AudioConfig):
        """Initialize the audio processor with automatic model detection
        
        Args:
            config: AudioConfig with processing parameters
        """
        self.config = config
        self.processor = None
        self._determine_and_init_processor()
    
    def _determine_and_init_processor(self):
        """Determine which processor to use based on model name and initialize it"""
        # Auto-detect model type if not specified
        if self.config.model_type == "encodec" or not hasattr(self.config, 'model_type'):
            if self._is_dac_model(self.config.model_name):
                self.config.model_type = "dac"
            elif self._is_snac_model(self.config.model_name):
                self.config.model_type = "snac"
            else:
                self.config.model_type = "encodec"
        
        # Initialize appropriate processor
        if self.config.model_type == "dac":
            if not DAC_AVAILABLE:
                raise ImportError("DAC not available but DAC model requested. Please install: pip install descript-audio-codec audiotools")
            self.processor = DACAudioProcessor(self.config)
        elif self.config.model_type == "snac":
            if not SNAC_AVAILABLE:
                raise ImportError("SNAC not available but SNAC model requested. Please install: pip install snac")
            self.processor = SNACAudioProcessor(self.config)
        else:
            self.processor = EncodecAudioProcessor(self.config)
        
        print(f"✓ Initialized {self.config.model_type.upper()} processor: {self.config.model_name}")
    
    def _is_dac_model(self, model_name: str) -> bool:
        """Check if model name corresponds to a DAC model"""
        return model_name.lower().startswith('dac_') or model_name in DAC_MODEL_CONFIGS
    
    def _is_snac_model(self, model_name: str) -> bool:
        """Check if model name corresponds to a SNAC model"""
        return (model_name.lower().startswith('snac_') or 
                model_name in SNAC_MODEL_CONFIGS or
                'hubertsiuzdak/snac' in model_name.lower())
    
    def _ensure_compatible_processor(self, encoded_data: Dict[str, Any]):
        """Ensure we have the right processor for the encoded data"""
        # Get model info from encoded data
        encoded_model_name = encoded_data.get('model_name', encoded_data.get('config', {}).get('model_name'))
        encoded_processor_type = encoded_data.get('config', {}).get('model_type')
        
        # Determine required processor type
        if encoded_processor_type:
            required_type = encoded_processor_type
        elif encoded_model_name:
            if self._is_dac_model(encoded_model_name):
                required_type = "dac"
            elif self._is_snac_model(encoded_model_name):
                required_type = "snac"
            else:
                required_type = "encodec"
        else:
            return  # No info available, keep current processor
        
        # Check if we need to switch processors
        if (required_type != self.config.model_type or 
            (encoded_model_name and encoded_model_name != self.config.model_name)):
            
            print(f"🔄 Switching from {self.config.model_type} to {required_type}")
            if encoded_model_name:
                print(f"   Model: {self.config.model_name} -> {encoded_model_name}")
                self.config.model_name = encoded_model_name
            
            self.config.model_type = required_type
            self._determine_and_init_processor()
    
    # Delegate all methods to the underlying processor
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get basic audio information"""
        return self.processor.get_audio_info(audio_path)
    
    def load_audio(self, audio_path: str, duration: Optional[float] = None):
        """Load and preprocess audio file"""
        return self.processor.load_audio(audio_path, duration)
    
    def encode_audio(self, audio_data, metadata: Dict[str, Any], base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encode audio using the appropriate codec"""
        return self.processor.encode_audio(audio_data, metadata, base_metadata)
    
    def decode_audio(self, encoded_data: Dict[str, Any]):
        """Decode audio using the appropriate codec"""
        # Ensure we have the right processor for this data
        self._ensure_compatible_processor(encoded_data)
        return self.processor.decode_audio(encoded_data)
    
    def save_decoded_audio(self, decoded_audio, output_path: str, metadata: Dict[str, Any] = None) -> str:
        """Save decoded audio to file"""
        return self.processor.save_decoded_audio(decoded_audio, output_path, metadata)
    
    def process_single_file(self, audio_path: str, output_path: Optional[str] = None, base_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single audio file"""
        return self.processor.process_single_file(audio_path, output_path, base_metadata)
    
    def process_directory(self, input_dir: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """Process all audio files in a directory"""
        if hasattr(self.processor, 'process_directory'):
            return self.processor.process_directory(input_dir, output_dir, **kwargs)
        else:
            raise NotImplementedError("Directory processing not implemented for this processor")
    
    def load_from_car(self, car_path: str) -> Dict[str, Any]:
        """Load compressed audio data from CAR format"""
        if hasattr(self.processor, 'load_from_car'):
            return self.processor.load_from_car(car_path)
        else:
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
    
    @property
    def model_type(self) -> str:
        """Get the current model type"""
        return self.config.model_type
    
    @property
    def model_name(self) -> str:
        """Get the current model name"""
        return self.config.model_name
    
    @property
    def device(self) -> str:
        """Get the current device"""
        return self.config.device
    
    def __str__(self) -> str:
        return f"AudioProcessor({self.config.model_type}:{self.config.model_name})"
    
    def __repr__(self) -> str:
        return self.__str__()


# ============ UNIFIED UTILITIES ============

def create_unified_audio_processor(model_name: str = None, **config_kwargs) -> AudioProcessor:
    """Create a unified audio processor that auto-detects the codec type
    
    Args:
        model_name: Model name (e.g., 'dac_44khz', 'facebook/encodec_32khz')
        **config_kwargs: Additional configuration parameters
        
    Returns:
        AudioProcessor instance with appropriate codec
    """
    # Set default model if none provided
    if model_name is None:
        if SNAC_AVAILABLE:
            model_name = "snac_44khz"  # Prefer SNAC if available (best quality)
        elif DAC_AVAILABLE:
            model_name = "dac_44khz"  # DAC as second choice
        else:
            model_name = "facebook/encodec_32khz"  # EnCodec as fallback
    
    config = AudioConfig(model_name=model_name, **config_kwargs)
    return AudioProcessor(config)

def batch_process_audio_unified(input_dir: str, output_dir: str, model_name: str = None, **kwargs):
    """Unified batch processing function that auto-detects codec type"""
    processor = create_unified_audio_processor(model_name, **kwargs)
    
    return processor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=kwargs.get('num_workers', 1),
        recursive=kwargs.get('recursive', True)
    )

def example_unified_usage():
    """Example usage of the unified AudioProcessor"""
    
    print("=== UNIFIED AUDIO PROCESSOR EXAMPLE ===")
    
    # Example 1: Auto-detect and use SNAC
    try:
        processor_snac = create_unified_audio_processor("snac_44khz")
        print(f"Created: {processor_snac}")
        
        # Example 2: Auto-detect and use DAC
        processor_dac = create_unified_audio_processor("dac_44khz")
        print(f"Created: {processor_dac}")
        
        # Example 3: Auto-detect and use EnCodec
        processor_encodec = create_unified_audio_processor("facebook/encodec_32khz") 
        print(f"Created: {processor_encodec}")
        
        # Example 4: Process mixed datasets automatically
        print("\n--- Processing workflow ---")
        
        # Create some example encoded data with different models
        config_snac = AudioConfig(model_name="snac_44khz", model_type="snac")
        config_dac = AudioConfig(model_name="dac_44khz", model_type="dac")
        config_encodec = AudioConfig(model_name="facebook/encodec_32khz", model_type="encodec")
        
        # Simulate encoded data from different sources
        snac_encoded = {
            'model_name': config_snac.model_name,
            'config': {'model_type': config_snac.model_type},
            'audio_codes': 'dummy_snac_hierarchical_codes'
        }
        
        dac_encoded = {
            'model_name': config_dac.model_name,
            'config': {'model_type': config_dac.model_type},
            'compressed_data': 'dummy_dac_data'
        }
        
        encodec_encoded = {
            'model_name': config_encodec.model_name, 
            'config': {'model_type': config_encodec.model_type},
            'audio_codes': 'dummy_encodec_data'
        }
        
        # Single processor can handle all three!
        unified_processor = create_unified_audio_processor()
        print(f"Initial processor: {unified_processor}")
        
        # This would automatically switch to SNAC for decoding
        print("Simulating decode of SNAC data...")
        unified_processor._ensure_compatible_processor(snac_encoded)
        print(f"After SNAC data: {unified_processor}")
        
        # This would automatically switch to DAC for decoding
        print("Simulating decode of DAC data...")
        unified_processor._ensure_compatible_processor(dac_encoded)
        print(f"After DAC data: {unified_processor}")
        
        # This would automatically switch to EnCodec for decoding  
        print("Simulating decode of EnCodec data...")
        unified_processor._ensure_compatible_processor(encodec_encoded)
        print(f"After EnCodec data: {unified_processor}")
        
        print("✅ Unified processor can handle SNAC, DAC, and EnCodec seamlessly!")
        
    except ImportError as e:
        print(f"❌ Some codecs not available: {e}")
    except Exception as e:
        print(f"❌ Unified processor demo failed: {e}")


# Run example if script is executed directly
if __name__ == "__main__":
    example_usage()