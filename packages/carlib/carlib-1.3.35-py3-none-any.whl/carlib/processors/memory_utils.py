"""
GPU Memory Management Utilities
Optimized memory management to reduce excessive torch.cuda.empty_cache() overhead
"""
import torch
import time
from typing import Optional


class GPUMemoryManager:
    """Smart GPU memory management to reduce cache clearing overhead"""
    
    def __init__(self, cache_interval: float = 5.0, memory_threshold: float = 0.8):
        """
        Initialize memory manager
        
        Args:
            cache_interval: Minimum seconds between cache clears
            memory_threshold: Memory usage threshold to trigger cache clear (0-1)
        """
        self.cache_interval = cache_interval
        self.memory_threshold = memory_threshold
        self._last_cache_clear = 0
        self._batch_counter = 0
        
    def maybe_clear_cache(self, force: bool = False) -> bool:
        """
        Conditionally clear GPU cache based on time and memory usage
        
        Args:
            force: Force cache clearing regardless of conditions
            
        Returns:
            True if cache was cleared, False otherwise
        """
        if not torch.cuda.is_available():
            return False
            
        current_time = time.time()
        time_since_last = current_time - self._last_cache_clear
        
        # Force clear or check conditions
        should_clear = (
            force or
            time_since_last >= self.cache_interval or
            self._memory_usage_high()
        )
        
        if should_clear:
            torch.cuda.empty_cache()
            self._last_cache_clear = current_time
            return True
            
        return False
    
    def _memory_usage_high(self) -> bool:
        """Check if GPU memory usage is above threshold"""
        try:
            allocated = torch.cuda.memory_allocated()
            reserved = torch.cuda.memory_reserved()
            if reserved > 0:
                usage_ratio = allocated / reserved
                return usage_ratio > self.memory_threshold
        except Exception:
            pass
        return False
    
    def clear_on_batch_boundary(self, batch_size: int = 32) -> bool:
        """Clear cache only on batch boundaries to reduce overhead"""
        self._batch_counter += 1
        if self._batch_counter % batch_size == 0:
            return self.maybe_clear_cache()
        return False
    
    def clear_on_error(self):
        """Force clear cache on errors"""
        self.maybe_clear_cache(force=True)
    
    def get_memory_stats(self) -> dict:
        """Get current GPU memory statistics"""
        if not torch.cuda.is_available():
            return {}
        
        try:
            return {
                'allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                'reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                'max_allocated_gb': torch.cuda.max_memory_allocated() / 1024**3,
                'max_reserved_gb': torch.cuda.max_memory_reserved() / 1024**3
            }
        except Exception:
            return {}


# Global memory manager instance
_memory_manager = GPUMemoryManager()


def smart_empty_cache(force: bool = False) -> bool:
    """Smart cache clearing with reduced overhead"""
    return _memory_manager.maybe_clear_cache(force=force)


def batch_boundary_cache_clear(batch_size: int = 32) -> bool:
    """Clear cache only on batch boundaries"""
    return _memory_manager.clear_on_batch_boundary(batch_size)


def error_cache_clear():
    """Force clear cache on errors"""
    _memory_manager.clear_on_error()


def get_gpu_memory_stats() -> dict:
    """Get GPU memory statistics"""
    return _memory_manager.get_memory_stats()