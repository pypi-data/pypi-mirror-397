"""
CarLib Evaluation Module

This module provides benchmarking and analysis tools for CarLib datasets.
It allows users to easily benchmark dataset conversion performance and analyze results.
"""

from .benchmark import BenchmarkConfig, BenchmarkResult, run_folder_benchmark
from .analyze_results import analyze_benchmark_results

__all__ = [
    "BenchmarkConfig",
    "BenchmarkResult", 
    "run_folder_benchmark",
    "analyze_benchmark_results"
]