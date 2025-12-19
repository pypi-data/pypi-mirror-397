#!/usr/bin/env python3
"""
Benchmark Results Analysis Script

This script analyzes the JSON output from benchmark.py and creates various plots:
1. File size vs generation/loading times
2. CAR loading time median analysis
3. Speedup factor analysis
4. Compression ratio analysis
5. Multi-format comparison plots (CAR, HDF5, WebDataset, TFRecord)
6. Format performance heatmaps
7. Cross-format speedup analysis

Supports both legacy single-format and new multi-format benchmark results.

Usage:
    python analyze_results.py results.json
    python analyze_results.py results.json --output-dir custom_analysis_dir
"""

import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import seaborn as sns

# Try to import carlib functions for enhanced analysis
try:
    from .. import CARDataset, load_single_car
    _carlib_available = True
except ImportError:
    try:
        from carlib import CARDataset, load_single_car
        _carlib_available = True
    except ImportError:
        CARDataset = None
        load_single_car = None
        _carlib_available = False

# Set style
plt.style.use('default')
sns.set_palette("husl")

def load_benchmark_results(json_file: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def create_dataframe(results: List[Dict]) -> pd.DataFrame:
    """Convert results list to pandas DataFrame for easier analysis"""
    successful_results = [r for r in results if r['success']]
    if not successful_results:
        raise ValueError("No successful benchmark results found")
    
    df = pd.DataFrame(successful_results)
    
    # Handle format_results field - expand into separate columns
    if 'format_results' in df.columns and df['format_results'].notna().any():
        for idx, row in df.iterrows():
            if pd.notna(row.get('format_results')):
                format_results = row['format_results']
                for format_name, metrics in format_results.items():
                    df.loc[idx, f'{format_name}_size_mb'] = metrics.get('size_mb', 0)
                    df.loc[idx, f'{format_name}_loading_time_ms'] = metrics.get('loading_time_ms', 0)
    
    return df

def plot_file_size_vs_times(df: pd.DataFrame, output_dir: str):
    """Plot file size vs generation/loading times"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # File size vs generation time
    ax1.scatter(df['file_size_mb'], df['generation_time_ms'], alpha=0.6, s=50)
    ax1.set_xlabel('File Size (MB)')
    ax1.set_ylabel('Generation Time (ms)')
    ax1.set_title('File Size vs Generation Time')
    ax1.grid(True, alpha=0.3)
    
    # Add trendline
    z1 = np.polyfit(df['file_size_mb'], df['generation_time_ms'], 1)
    p1 = np.poly1d(z1)
    ax1.plot(df['file_size_mb'].sort_values(), p1(df['file_size_mb'].sort_values()), 
             "r--", alpha=0.8, linewidth=2)
    
    # File size vs loading time
    ax2.scatter(df['file_size_mb'], df['loading_time_ms'], alpha=0.6, s=50, color='orange')
    ax2.set_xlabel('File Size (MB)')
    ax2.set_ylabel('CAR Loading Time (ms)')
    ax2.set_title('File Size vs CAR Loading Time')
    ax2.grid(True, alpha=0.3)
    
    # Add trendline
    z2 = np.polyfit(df['file_size_mb'], df['loading_time_ms'], 1)
    p2 = np.poly1d(z2)
    ax2.plot(df['file_size_mb'].sort_values(), p2(df['file_size_mb'].sort_values()), 
             "r--", alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/file_size_vs_times.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_car_loading_analysis(df: pd.DataFrame, output_dir: str):
    """Analyze CAR loading times with median and distribution"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Histogram of CAR loading times
    ax1.hist(df['loading_time_ms'], bins=30, alpha=0.7, edgecolor='black')
    ax1.axvline(df['loading_time_ms'].median(), color='red', linestyle='--', 
                linewidth=2, label=f'Median: {df["loading_time_ms"].median():.1f}ms')
    ax1.axvline(df['loading_time_ms'].mean(), color='orange', linestyle='--', 
                linewidth=2, label=f'Mean: {df["loading_time_ms"].mean():.1f}ms')
    ax1.set_xlabel('CAR Loading Time (ms)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of CAR Loading Times')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot(df['loading_time_ms'])
    ax2.set_ylabel('CAR Loading Time (ms)')
    ax2.set_title('CAR Loading Time Box Plot')
    ax2.grid(True, alpha=0.3)
    
    # CAR size vs loading time
    ax3.scatter(df['car_size_mb'], df['loading_time_ms'], alpha=0.6, s=50, color='green')
    ax3.set_xlabel('CAR File Size (MB)')
    ax3.set_ylabel('CAR Loading Time (ms)')
    ax3.set_title('CAR Size vs Loading Time')
    ax3.grid(True, alpha=0.3)
    
    # Add trendline
    z = np.polyfit(df['car_size_mb'], df['loading_time_ms'], 1)
    p = np.poly1d(z)
    ax3.plot(df['car_size_mb'].sort_values(), p(df['car_size_mb'].sort_values()), 
             "r--", alpha=0.8, linewidth=2)
    
    # Speedup factor distribution
    ax4.hist(df['speedup_factor'], bins=30, alpha=0.7, edgecolor='black', color='purple')
    ax4.axvline(df['speedup_factor'].median(), color='red', linestyle='--', 
                linewidth=2, label=f'Median: {df["speedup_factor"].median():.1f}x')
    ax4.set_xlabel('Speedup Factor')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Speedup Factor Distribution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/car_loading_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_compression_analysis(df: pd.DataFrame, output_dir: str):
    """Analyze compression ratios"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Compression ratio distribution
    ax1.hist(df['compression_ratio'], bins=30, alpha=0.7, edgecolor='black', color='teal')
    ax1.axvline(df['compression_ratio'].median(), color='red', linestyle='--', 
                linewidth=2, label=f'Median: {df["compression_ratio"].median():.1f}x')
    ax1.axvline(df['compression_ratio'].mean(), color='orange', linestyle='--', 
                linewidth=2, label=f'Mean: {df["compression_ratio"].mean():.1f}x')
    ax1.set_xlabel('Compression Ratio')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Compression Ratio Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # File size vs compression ratio
    ax2.scatter(df['file_size_mb'], df['compression_ratio'], alpha=0.6, s=50, color='coral')
    ax2.set_xlabel('Original File Size (MB)')
    ax2.set_ylabel('Compression Ratio')
    ax2.set_title('File Size vs Compression Ratio')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/compression_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_performance_overview(df: pd.DataFrame, output_dir: str):
    """Create overview plot comparing generation vs loading times"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Sort by file size for better visualization
    df_sorted = df.sort_values('file_size_mb')
    
    x = range(len(df_sorted))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], df_sorted['generation_time_ms'], 
           width, label='Generation Time', alpha=0.7)
    ax.bar([i + width/2 for i in x], df_sorted['loading_time_ms'], 
           width, label='CAR Loading Time', alpha=0.7)
    
    ax.set_xlabel('Files (sorted by size)')
    ax.set_ylabel('Time (ms)')
    ax.set_title('Generation vs CAR Loading Times by File')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Only show some x-axis labels to avoid crowding
    step = max(1, len(df_sorted) // 10)
    ax.set_xticks([i for i in x[::step]])
    ax.set_xticklabels([f"{size:.1f}MB" for size in df_sorted['file_size_mb'].iloc[::step]], 
                       rotation=45)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_overview.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_multi_format_comparison(df: pd.DataFrame, output_dir: str):
    """Create comprehensive multi-format comparison plots"""
    # Detect available formats from dataframe columns
    format_columns = {}
    for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
        size_col = f'{format_name}_size_mb'
        time_col = f'{format_name}_loading_time_ms'
        if size_col in df.columns and time_col in df.columns:
            format_columns[format_name] = {'size': size_col, 'time': time_col}
    
    if not format_columns:
        print("⚠️  No multi-format data found, skipping multi-format comparison plots")
        return
    
    # Create comparison plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. File size comparison across formats
    format_names = list(format_columns.keys())
    avg_sizes = []
    for format_name in format_names:
        size_col = format_columns[format_name]['size']
        avg_size = df[size_col].mean()
        avg_sizes.append(avg_size)
    
    bars1 = ax1.bar(format_names, avg_sizes, alpha=0.7, color=['blue', 'green', 'orange', 'red'][:len(format_names)])
    ax1.set_ylabel('Average File Size (MB)')
    ax1.set_title('Average File Size by Format')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, size in zip(bars1, avg_sizes):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{size:.2f}MB', ha='center', va='bottom')
    
    # 2. Loading time comparison across formats  
    avg_times = []
    for format_name in format_names:
        time_col = format_columns[format_name]['time']
        avg_time = df[time_col].mean()
        avg_times.append(avg_time)
    
    bars2 = ax2.bar(format_names, avg_times, alpha=0.7, color=['blue', 'green', 'orange', 'red'][:len(format_names)])
    ax2.set_ylabel('Average Loading Time (ms)')
    ax2.set_title('Average Loading Time by Format')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, time in zip(bars2, avg_times):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{time:.1f}ms', ha='center', va='bottom')
    
    # 3. Scatter plot: Size vs Loading Time for all formats (deduplicated by file size)
    colors = ['blue', 'green', 'orange', 'red']
    
    # Group by unique file sizes to avoid redundancy
    unique_df = df.groupby('file_size_mb').first().reset_index()
    
    for i, (format_name, cols) in enumerate(format_columns.items()):
        size_col, time_col = cols['size'], cols['time']
        # Use unique file sizes, but format-specific loading times
        ax3.scatter(unique_df['file_size_mb'], unique_df[time_col], alpha=0.6, s=50, 
                   color=colors[i], label=format_name.upper())
    
    ax3.set_xlabel('Original File Size (MB)')
    ax3.set_ylabel('Loading Time (ms)')
    ax3.set_title('File Size vs Loading Time (All Formats, Unique Files)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Performance relative to CAR (if CAR data exists, using unique files)
    if 'car' in format_columns:
        car_time_col = format_columns['car']['time']
        speedup_data = []
        format_labels = []
        
        for format_name, cols in format_columns.items():
            if format_name != 'car':
                time_col = cols['time']
                # Calculate speedup relative to CAR using unique files only
                speedup = unique_df[car_time_col] / unique_df[time_col]
                speedup_avg = speedup.mean()
                speedup_data.append(speedup_avg)
                format_labels.append(format_name.upper())
        
        if speedup_data:
            bars4 = ax4.bar(format_labels, speedup_data, alpha=0.7, 
                           color=['green', 'orange', 'red'][:len(format_labels)])
            ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='CAR baseline')
            ax4.set_ylabel('Speedup Factor (relative to CAR)')
            ax4.set_title('Loading Speed Relative to CAR Format (Unique Files)')
            ax4.legend()
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, speedup in zip(bars4, speedup_data):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{speedup:.2f}x', ha='center', va='bottom')
    else:
        ax4.text(0.5, 0.5, 'No CAR baseline data\navailable for comparison', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Speedup Relative to CAR (N/A)')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/multi_format_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_format_performance_heatmap(df: pd.DataFrame, output_dir: str):
    """Create heatmap showing performance metrics across formats"""
    # Detect available formats
    format_columns = {}
    for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
        size_col = f'{format_name}_size_mb'
        time_col = f'{format_name}_loading_time_ms'
        if size_col in df.columns and time_col in df.columns:
            format_columns[format_name] = {'size': size_col, 'time': time_col}
    
    if len(format_columns) < 2:
        print("⚠️  Need at least 2 formats for heatmap, skipping")
        return
    
    # Use unique files to avoid redundancy
    unique_df = df.groupby('file_size_mb').first().reset_index()
    
    # Create metrics matrix
    metrics_data = {}
    format_names = list(format_columns.keys())
    
    for format_name in format_names:
        size_col = format_columns[format_name]['size'] 
        time_col = format_columns[format_name]['time']
        
        metrics_data[format_name.upper()] = {
            'Avg Size (MB)': unique_df[size_col].mean(),
            'Med Size (MB)': unique_df[size_col].median(),
            'Avg Load Time (ms)': unique_df[time_col].mean(),
            'Med Load Time (ms)': unique_df[time_col].median(),
            'Min Load Time (ms)': unique_df[time_col].min(),
            'Max Load Time (ms)': unique_df[time_col].max(),
        }
    
    metrics_df = pd.DataFrame(metrics_data).T
    
    # Create heatmap
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Normalize data for better visualization
    normalized_df = metrics_df.div(metrics_df.max(axis=0), axis=1)
    
    sns.heatmap(normalized_df, annot=True, cmap='RdYlGn_r', center=0.5,
                square=True, linewidths=0.5, fmt='.3f', ax=ax)
    
    ax.set_title('Performance Metrics Heatmap (Normalized, Unique Files)\nLower is Better', fontsize=14)
    ax.set_xlabel('Performance Metrics')
    ax.set_ylabel('Formats')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/format_performance_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save raw metrics table
    metrics_df.to_csv(f"{output_dir}/format_metrics_table.csv")
    
    return metrics_df

def create_extrapolation_models(df: pd.DataFrame, output_dir: str):
    """Create predictive models for extrapolation using unique file sizes"""
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import r2_score
    import joblib
    
    # Use unique files to avoid redundancy in training data
    unique_df = df.groupby('file_size_mb').first().reset_index()
    print(f"📊 Training models on {len(unique_df)} unique file sizes")
    
    models = {}
    
    # File size -> Generation time model
    X = unique_df[['file_size_mb']].values
    y_gen = unique_df['generation_time_ms'].values
    
    gen_model = LinearRegression()
    gen_model.fit(X, y_gen)
    gen_r2 = r2_score(y_gen, gen_model.predict(X))
    models['generation_time'] = {
        'model': gen_model,
        'r2_score': gen_r2,
        'features': ['file_size_mb'],
        'target': 'generation_time_ms',
        'coefficient': gen_model.coef_[0],
        'intercept': gen_model.intercept_
    }
    
    # Legacy CAR loading time model (if available)
    if 'loading_time_ms' in unique_df.columns:
        y_load = unique_df['loading_time_ms'].values
        load_model = LinearRegression()
        load_model.fit(X, y_load)
        load_r2 = r2_score(y_load, load_model.predict(X))
        models['legacy_car_loading'] = {
            'model': load_model,
            'r2_score': load_r2,
            'features': ['file_size_mb'],
            'target': 'loading_time_ms',
            'coefficient': load_model.coef_[0],
            'intercept': load_model.intercept_
        }
    
    # Format-specific loading time models
    format_models = {}
    for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
        time_col = f'{format_name}_loading_time_ms'
        size_col = f'{format_name}_size_mb'
        
        if time_col in unique_df.columns and size_col in unique_df.columns:
            # Model 1: Original file size -> Format loading time
            y_time = unique_df[time_col].values
            time_model = LinearRegression()
            time_model.fit(X, y_time)
            time_r2 = r2_score(y_time, time_model.predict(X))
            
            format_models[f'{format_name}_loading_from_filesize'] = {
                'model': time_model,
                'r2_score': time_r2,
                'features': ['file_size_mb'],
                'target': time_col,
                'coefficient': time_model.coef_[0],
                'intercept': time_model.intercept_,
                'format': format_name
            }
            
            # Model 2: Format file size -> Format loading time
            X_format = unique_df[[size_col]].values
            format_size_model = LinearRegression()
            format_size_model.fit(X_format, y_time)
            format_size_r2 = r2_score(y_time, format_size_model.predict(X_format))
            
            format_models[f'{format_name}_loading_from_formatsize'] = {
                'model': format_size_model,
                'r2_score': format_size_r2,
                'features': [size_col],
                'target': time_col,
                'coefficient': format_size_model.coef_[0],
                'intercept': format_size_model.intercept_,
                'format': format_name
            }
    
    models.update(format_models)
    
    # Polynomial models for better fit (only for generation time)
    poly_gen = Pipeline([
        ('poly', PolynomialFeatures(degree=2)),
        ('linear', LinearRegression())
    ])
    poly_gen.fit(X, y_gen)
    poly_gen_r2 = r2_score(y_gen, poly_gen.predict(X))
    
    if poly_gen_r2 > gen_r2:
        models['generation_time_poly'] = {
            'model': poly_gen,
            'r2_score': poly_gen_r2,
            'features': ['file_size_mb'],
            'target': 'generation_time_ms',
            'type': 'polynomial'
        }
    
    # Save models
    joblib.dump(models, f"{output_dir}/prediction_models.pkl")
    
    # Create comprehensive extrapolation report
    with open(f"{output_dir}/extrapolation_report.txt", 'w') as f:
        f.write("EXTRAPOLATION MODELS (Unique File Sizes)\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Training Data: {len(unique_df)} unique files\n")
        f.write(f"File Size Range: {unique_df['file_size_mb'].min():.2f} - {unique_df['file_size_mb'].max():.2f} MB\n\n")
        
        # Generation models
        f.write("GENERATION TIME MODELS:\n")
        f.write("-" * 25 + "\n")
        for name, info in models.items():
            if 'generation' in name:
                f.write(f"{name.replace('_', ' ').title()}:\n")
                f.write(f"  R² Score: {info['r2_score']:.4f}\n")
                f.write(f"  Features: {info['features']}\n")
                if 'coefficient' in info:
                    f.write(f"  Equation: y = {info['coefficient']:.4f}x + {info['intercept']:.4f}\n")
                f.write("\n")
        
        # Format-specific models
        f.write("FORMAT-SPECIFIC LOADING TIME MODELS:\n")
        f.write("-" * 35 + "\n")
        for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
            format_models_found = [name for name in models.keys() if format_name in name]
            if format_models_found:
                f.write(f"{format_name.upper()} Format:\n")
                for model_name in format_models_found:
                    info = models[model_name]
                    f.write(f"  {model_name.split('_')[-1].title()} Predictor:\n")
                    f.write(f"    R² Score: {info['r2_score']:.4f}\n")
                    f.write(f"    Features: {info['features']}\n")
                    if 'coefficient' in info:
                        f.write(f"    Equation: y = {info['coefficient']:.4f}x + {info['intercept']:.4f}\n")
                    f.write("\n")
                f.write("\n")
    
    return models

def predict_performance(file_sizes_mb: List[float], models_file: str = None) -> Dict:
    """Predict performance for given file sizes using trained models"""
    import joblib
    
    if models_file and Path(models_file).exists():
        models = joblib.load(models_file)
    else:
        raise FileNotFoundError("Models file not found. Run analysis first to create models.")
    
    predictions = {}
    
    for size in file_sizes_mb:
        size_array = np.array([[size]])
        
        # Generation time prediction
        if 'generation_time' in models:
            gen_time = models['generation_time']['model'].predict(size_array)[0]
        else:
            gen_time = 0
        
        size_prediction = {
            'generation_time_ms': gen_time,
            'format_loading_times': {},
            'format_speedups': {},
            'format_time_savings': {}
        }
        
        # Format-specific predictions
        formats_found = []
        for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
            model_key = f'{format_name}_loading_from_filesize'
            if model_key in models:
                formats_found.append(format_name)
                load_time = models[model_key]['model'].predict(size_array)[0]
                
                size_prediction['format_loading_times'][format_name] = load_time
                
                if gen_time > 0:
                    speedup = gen_time / load_time if load_time > 0 else 0
                    time_savings = gen_time - load_time
                    
                    size_prediction['format_speedups'][format_name] = speedup
                    size_prediction['format_time_savings'][format_name] = time_savings
        
        # Legacy single loading time (for backwards compatibility)
        if 'legacy_car_loading' in models:
            legacy_load_time = models['legacy_car_loading']['model'].predict(size_array)[0]
            size_prediction['loading_time_ms'] = legacy_load_time
            
            if gen_time > 0:
                size_prediction['speedup_factor'] = gen_time / legacy_load_time if legacy_load_time > 0 else 0
                size_prediction['time_savings_ms'] = gen_time - legacy_load_time
        
        # Summary statistics
        if size_prediction['format_loading_times']:
            loading_times = list(size_prediction['format_loading_times'].values())
            size_prediction['best_format'] = min(size_prediction['format_loading_times'], 
                                               key=size_prediction['format_loading_times'].get)
            size_prediction['worst_format'] = max(size_prediction['format_loading_times'], 
                                                key=size_prediction['format_loading_times'].get)
            size_prediction['avg_loading_time_ms'] = np.mean(loading_times)
            size_prediction['format_range_ms'] = max(loading_times) - min(loading_times)
        
        predictions[f"{size}MB"] = size_prediction
    
    return predictions

def create_summary_stats(df: pd.DataFrame, summary: Dict, output_dir: str):
    """Create and save summary statistics"""
    stats = {
        'File Statistics': {
            'Total Files Analyzed': len(df),
            'Average File Size (MB)': f"{df['file_size_mb'].mean():.2f}",
            'Median File Size (MB)': f"{df['file_size_mb'].median():.2f}",
            'File Size Range (MB)': f"{df['file_size_mb'].min():.2f} - {df['file_size_mb'].max():.2f}",
        },
        'Performance Statistics': {
            'Average Generation Time (ms)': f"{df['generation_time_ms'].mean():.2f}",
            'Median Generation Time (ms)': f"{df['generation_time_ms'].median():.2f}",
            'Average CAR Loading Time (ms)': f"{df['loading_time_ms'].mean():.2f}",
            'Median CAR Loading Time (ms)': f"{df['loading_time_ms'].median():.2f}",
            'Average Speedup Factor': f"{df['speedup_factor'].mean():.2f}x",
            'Median Speedup Factor': f"{df['speedup_factor'].median():.2f}x",
            'Max Speedup Factor': f"{df['speedup_factor'].max():.2f}x",
        },
        'Compression Statistics': {
            'Average Compression Ratio': f"{df['compression_ratio'].mean():.2f}x",
            'Median Compression Ratio': f"{df['compression_ratio'].median():.2f}x",
            'Best Compression Ratio': f"{df['compression_ratio'].max():.2f}x",
            'Average CAR Size (MB)': f"{df['car_size_mb'].mean():.2f}",
        },
        'Time Savings': {
            'Total Time Saved (seconds)': f"{df['time_savings_ms'].sum() / 1000:.2f}",
            'Average Time Saved per File (ms)': f"{df['time_savings_ms'].mean():.2f}",
            'Median Time Saved per File (ms)': f"{df['time_savings_ms'].median():.2f}",
        }
    }
    
    # Add multi-format statistics if available (using unique files to avoid redundancy)
    format_stats = {}
    has_format_data = any(f'{fmt}_size_mb' in df.columns for fmt in ['car', 'hdf5', 'webdataset', 'tfrecord'])
    
    if has_format_data:
        unique_df = df.groupby('file_size_mb').first().reset_index()
        
        for format_name in ['car', 'hdf5', 'webdataset', 'tfrecord']:
            size_col = f'{format_name}_size_mb'
            time_col = f'{format_name}_loading_time_ms'
            
            if size_col in df.columns and time_col in df.columns:
                format_stats[f'{format_name.upper()} Format (Unique Files)'] = {
                    'Average Size (MB)': f"{unique_df[size_col].mean():.2f}",
                    'Median Size (MB)': f"{unique_df[size_col].median():.2f}",
                    'Average Loading Time (ms)': f"{unique_df[time_col].mean():.2f}",
                    'Median Loading Time (ms)': f"{unique_df[time_col].median():.2f}",
                    'Min Loading Time (ms)': f"{unique_df[time_col].min():.2f}",
                    'Max Loading Time (ms)': f"{unique_df[time_col].max():.2f}",
                }
    
    # Add format statistics to main stats
    stats.update(format_stats)
    
    # Save to JSON
    with open(f"{output_dir}/summary_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Create text report
    with open(f"{output_dir}/summary_report.txt", 'w') as f:
        f.write("BENCHMARK ANALYSIS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        for category, metrics in stats.items():
            f.write(f"{category}:\n")
            f.write("-" * len(category) + "\n")
            for metric, value in metrics.items():
                f.write(f"  {metric}: {value}\n")
            f.write("\n")
    
    return stats


def analyze_car_files_with_carlib(df: pd.DataFrame, output_dir: str) -> Dict[str, Any]:
    """
    Perform enhanced analysis of CAR files using carlib functions.
    
    This function leverages carlib's advanced loading capabilities to provide
    deeper insights into CAR file structure and performance.
    """
    if not _carlib_available:
        return {"error": "Carlib functions not available"}
    
    analysis_results = {
        "total_files_analyzed": 0,
        "successful_loads": 0,
        "failed_loads": 0,
        "metadata_insights": {},
        "load_performance": [],
        "error_patterns": []
    }
    
    # Find CAR file paths in the benchmark results
    car_paths = []
    if 'file_path' in df.columns:
        # Generate expected CAR paths from original file paths
        car_paths = [str(Path(fp).with_suffix('.car')) for fp in df['file_path'].values]
    
    for car_path in car_paths[:10]:  # Analyze first 10 CAR files as sample
        if not Path(car_path).exists():
            continue
            
        try:
            # Time the loading using carlib
            import time
            start_time = time.perf_counter()
            car_data = load_single_car(car_path)
            load_time_ms = (time.perf_counter() - start_time) * 1000
            
            analysis_results["successful_loads"] += 1
            analysis_results["load_performance"].append({
                "file": str(Path(car_path).name),
                "load_time_ms": load_time_ms,
                "data_keys": list(car_data.keys()) if isinstance(car_data, dict) else "non-dict"
            })
            
            # Extract metadata insights
            if isinstance(car_data, dict):
                for key, value in car_data.items():
                    if key not in analysis_results["metadata_insights"]:
                        analysis_results["metadata_insights"][key] = {"count": 0, "types": set()}
                    analysis_results["metadata_insights"][key]["count"] += 1
                    analysis_results["metadata_insights"][key]["types"].add(type(value).__name__)
            
        except Exception as e:
            analysis_results["failed_loads"] += 1
            analysis_results["error_patterns"].append(str(e))
        
        analysis_results["total_files_analyzed"] += 1
    
    # Convert sets to lists for JSON serialization
    for key, value in analysis_results["metadata_insights"].items():
        value["types"] = list(value["types"])
    
    # Save enhanced analysis results
    output_file = Path(output_dir) / "carlib_enhanced_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"✅ Enhanced CAR analysis completed: {analysis_results['successful_loads']}/{analysis_results['total_files_analyzed']} files loaded successfully")
    
    return analysis_results


def analyze_benchmark_results(results_file: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Main function to analyze benchmark results with carlib integration.
    This provides a programmatic interface to the analysis functionality.
    """
    if output_dir is None:
        output_dir = "analysis_output"
        
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Load and analyze results
    data = load_benchmark_results(results_file)
    df = create_dataframe(data['results'])
    
    # Perform all analysis steps
    analysis_summary = {
        "total_files": len(df),
        "analysis_timestamp": pd.Timestamp.now().isoformat(),
        "carlib_available": _carlib_available
    }
    
    # Enhanced CAR analysis if carlib is available
    if _carlib_available:
        car_analysis = analyze_car_files_with_carlib(df, str(output_path))
        analysis_summary["car_analysis"] = car_analysis
    
    return analysis_summary


def main():
    parser = argparse.ArgumentParser(description="Analyze benchmark results and create plots")
    parser.add_argument("results_file",default="demo_outputs/jsons/benchmark_20251126_134601.json",help="JSON file with benchmark results")
    parser.add_argument("--output-dir", default="demo_outputs/analysis_output", 
                       help="Directory to save plots and analysis")
    
    args = parser.parse_args()
    
    if not Path(args.results_file).exists():
        print(f"❌ Results file not found: {args.results_file}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"📊 Loading results from {args.results_file}")
    
    try:
        # Load and process data
        data = load_benchmark_results(args.results_file)
        df = create_dataframe(data['results'])
        
        print(f"✅ Loaded {len(df)} successful benchmark results")
        
        # Create plots
        print("📈 Creating file size vs times plot...")
        plot_file_size_vs_times(df, str(output_dir))
        
        print("📊 Creating CAR loading analysis...")
        plot_car_loading_analysis(df, str(output_dir))
        
        print("🗜️  Creating compression analysis...")
        plot_compression_analysis(df, str(output_dir))
        
        print("⚡ Creating performance overview...")
        plot_performance_overview(df, str(output_dir))
        
        print("🔄 Creating multi-format comparison plots...")
        plot_multi_format_comparison(df, str(output_dir))
        
        print("🌡️  Creating format performance heatmap...")
        format_metrics = plot_format_performance_heatmap(df, str(output_dir))
        
        print("📋 Creating summary statistics...")
        stats = create_summary_stats(df, data.get('summary', {}), str(output_dir))
        
        print("🔮 Creating extrapolation models...")
        models = create_extrapolation_models(df, str(output_dir))
        
        # Enhanced CAR analysis using carlib functions
        if _carlib_available and 'car_paths' in df.columns:
            print("🚗 Performing enhanced CAR file analysis...")
            car_analysis = analyze_car_files_with_carlib(df, str(output_dir))
        else:
            print("ℹ️ Carlib not available or no CAR paths found - skipping enhanced analysis")
        
        # Example predictions for different file sizes
        example_sizes = [1, 5, 10, 50, 100, 500]  # MB
        try:
            predictions = predict_performance(example_sizes, f"{str(output_dir)}/prediction_models.pkl")
            
            with open(f"{str(output_dir)}/example_predictions.json", 'w') as f:
                json.dump(predictions, f, indent=2)
            
            print(f"📊 Example predictions created for file sizes: {example_sizes} MB")
        except Exception as e:
            print(f"⚠️ Could not create example predictions: {e}")
        
        print(f"\n✅ Analysis complete! Results saved to: {output_dir}")
        print(f"\nQuick Summary:")
        print(f"  Files analyzed: {len(df)}")
        print(f"  Median speedup: {df['speedup_factor'].median():.1f}x")
        print(f"  Median CAR loading time: {df['loading_time_ms'].median():.1f}ms")
        print(f"  Total time saved: {df['time_savings_ms'].sum() / 1000:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())