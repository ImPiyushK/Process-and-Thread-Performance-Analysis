#!/usr/bin/env python3
"""
Plotting Script for MT25076_PA01
Generates comprehensive visualization plots for Part C and Part D experiments

Roll Number: MT25076

Enhanced Features:
- Combined dashboard with all metrics
- Heatmap for normalized metrics comparison
- Radar/Spider charts for task profiles
- Statistical annotations and improved styling
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# =============================================================================
# Configuration
# =============================================================================

# Use script's directory as project directory (flat structure)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR

# Plot style settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['font.family'] = 'sans-serif'

# Enhanced color palette
COLORS = {
    'programA': '#2E86AB',   # Steel Blue
    'programB': '#E94F37',   # Vermilion
    'cpu': '#28A745',        # Green
    'mem': '#DC3545',        # Red
    'io': '#6F42C1',         # Purple
    'highlight': '#FFC107',  # Amber
    'background': '#F8F9FA'  # Light Gray
}

# =============================================================================
# Helper Functions
# =============================================================================

def add_value_labels(ax, bars, fmt='.1f', suffix='', offset=3):
    """Add value labels on top of bars"""
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height:{fmt}}{suffix}',
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, offset), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

def normalize_data(values):
    """Normalize values to 0-1 range"""
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        return [0.5] * len(values)
    return [(v - min_val) / (max_val - min_val) for v in values]

# =============================================================================
# Part C Plotting Functions
# =============================================================================

def plot_partC():
    """Generate enhanced plots for Part C: Program vs Worker type analysis"""
    
    csv_path = os.path.join(PROJECT_DIR, "MT25076_Part_C_CSV.csv")
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping Part C plots.")
        return
    
    print("Generating Part C plots...")
    
    # Read data
    df = pd.read_csv(csv_path)
    
    # Handle new format with Program+Function column
    if "Program+Function" in df.columns:
        df[["Program", "Function"]] = df["Program+Function"].str.split("+", expand=True)
    
    # Handle column names (support both old and new formats)
    cpu_col = "CPU%" if "CPU%" in df.columns else "CPU"
    mem_col = "Mem(MB)" if "Mem(MB)" in df.columns else "Mem"
    # Support IO(MB) or IO(GB) or IO(kB/s)
    if "IO(MB)" in df.columns:
        io_col = "IO(MB)"
        io_label = "Data Exchange (MB)"
    elif "IO(GB)" in df.columns:
        io_col = "IO(GB)"
        io_label = "Data Exchange (GB)"
    else:
        io_col = "IO(kB/s)" if "IO(kB/s)" in df.columns else "IO"
        io_label = "Disk I/O (kB/s)"
    time_col = "Time(s)" if "Time(s)" in df.columns else None
    
    # Convert numeric columns safely
    df[cpu_col] = pd.to_numeric(df[cpu_col], errors="coerce").fillna(0)
    df[mem_col] = pd.to_numeric(df[mem_col], errors="coerce").fillna(0)
    df[io_col] = pd.to_numeric(df[io_col], errors="coerce").fillna(0)
    if time_col:
        df[time_col] = pd.to_numeric(df[time_col], errors="coerce").fillna(0)
    
    workers = ["cpu", "mem", "io"]
    programs = df["Program"].unique()
    

    
    # =========================================================================
    # Plot 4: Grouped Comparison with Statistics
    # =========================================================================
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Part C: Detailed Metric Comparison with Observations', fontsize=14, fontweight='bold', y=1.02)
    
    metrics_info = [
        (cpu_col, 'CPU Usage (%)', 'CPU-intensive tasks should show highest CPU%'),
        (mem_col, 'Memory (MB)', 'Memory-intensive tasks should show highest memory'),
        (io_col, io_label, 'I/O-intensive tasks should show highest data exchange')
    ]
    
    for idx, (col, ylabel, observation) in enumerate(metrics_info):
        ax = axes[idx]
        
        # Prepare grouped data
        data_a = [df[(df["Program"] == "programA") & (df["Function"] == w)][col].values[0] 
                  if len(df[(df["Program"] == "programA") & (df["Function"] == w)]) > 0 else 0 
                  for w in workers]
        data_b = [df[(df["Program"] == "programB") & (df["Function"] == w)][col].values[0] 
                  if len(df[(df["Program"] == "programB") & (df["Function"] == w)]) > 0 else 0 
                  for w in workers]
        
        x = np.arange(len(workers))
        x = np.arange(len(workers))
        width = 0.35
        bars1 = ax.bar(x - width/2, data_a, width, label='Program A (fork)', 
                      color=COLORS['programA'], edgecolor='white', linewidth=1.5)
        bars2 = ax.bar(x + width/2, data_b, width, label='Program B (pthread)', 
                      color=COLORS['programB'], edgecolor='white', linewidth=1.5)
        
        if "GB" in col:
            add_value_labels(ax, bars1, fmt='.3f')
            add_value_labels(ax, bars2, fmt='.3f')
        elif col == cpu_col:
            add_value_labels(ax, bars1, fmt='.1f', suffix='%')
            add_value_labels(ax, bars2, fmt='.1f', suffix='%')
        else:
            add_value_labels(ax, bars1, fmt='.2f')
            add_value_labels(ax, bars2, fmt='.2f')
        
        ax.set_xlabel('Worker Type', fontweight='bold')
        ax.set_ylabel(ylabel, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([w.upper() for w in workers])
        ax.legend(loc='upper right', fontsize=9)
        
        # Add observation text box
        ax.text(0.5, -0.15, observation, transform=ax.transAxes, fontsize=9,
               ha='center', va='top', style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_comparison.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_comparison.png")

# =============================================================================
# Part D Plotting Functions
# =============================================================================

def plot_partD():
    """Generate enhanced plots for Part D: Scaling analysis"""
    
    csv_path = os.path.join(PROJECT_DIR, "MT25076_Part_D_CSV.csv")
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping Part D plots.")
        return
    
    print("Generating Part D plots...")
    
    # Read data
    df = pd.read_csv(csv_path)
    
    # Handle column names
    cpu_col = "CPU%" if "CPU%" in df.columns else "CPU"
    # Handle MEM column - check for various formats
    if "Mem(MB)" in df.columns:
        mem_col = "Mem(MB)"
    elif "MEM" in df.columns:
        mem_col = "MEM"
    else:
        mem_col = "Mem"
    # Handle IO column
    if "IO(MB)" in df.columns:
        io_col = "IO(MB)"
    elif "IO(GB)" in df.columns:
        io_col = "IO(GB)"
    elif "IO" in df.columns:
        io_col = "IO"
    else:
        io_col = "IO(kB/s)"
    time_col = "Time(s)" if "Time(s)" in df.columns else None
    
    # Convert numeric columns safely
    # Handle different column names for count
    count_col = "Count" if "Count" in df.columns else "number of process/threads"
    df["Count"] = pd.to_numeric(df[count_col], errors="coerce").fillna(0).astype(int)
    df[cpu_col] = pd.to_numeric(df[cpu_col], errors="coerce").fillna(0)
    df[mem_col] = pd.to_numeric(df[mem_col], errors="coerce").fillna(0)
    df[io_col] = pd.to_numeric(df[io_col], errors="coerce").fillna(0)
    if time_col:
        df[time_col] = pd.to_numeric(df[time_col], errors="coerce").fillna(0)
    
    # Separate data - handle both 'programA'/'programB' and 'A'/'B' formats
    if "programA" in df["Program"].values:
        proc_data = df[df["Program"] == "programA"].sort_values("Count")
        thread_data = df[df["Program"] == "programB"].sort_values("Count")
    else:
        proc_data = df[df["Program"] == "A"].sort_values("Count")
        thread_data = df[df["Program"] == "B"].sort_values("Count")
    

    
    # =========================================================================
    # Plot 2: Detailed Scaling Lines
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Part D: CPU Scaling by Program Type', fontsize=14, fontweight='bold', y=1.02)
    
    # Processes
    ax = axes[0]
    if len(proc_data) > 0:
        ax.plot(proc_data["Count"], proc_data[cpu_col], 'o-', linewidth=3, markersize=12,
               color=COLORS['programA'], markeredgecolor='white', markeredgewidth=2)
        
        for x, y in zip(proc_data["Count"], proc_data[cpu_col]):
            ax.annotate(f'{y:.1f}%', xy=(x, y), xytext=(0, 12), textcoords='offset points',
                       ha='center', fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Number of Processes', fontweight='bold', fontsize=12)
    ax.set_ylabel('CPU Usage (%)', fontweight='bold', fontsize=12)
    ax.set_title('Program A: Process Scaling (fork)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1.5, max(proc_data["Count"]) + 0.5 if len(proc_data) > 0 else 5.5)
    
    # Threads
    ax = axes[1]
    if len(thread_data) > 0:
        ax.plot(thread_data["Count"], thread_data[cpu_col], 's-', linewidth=3, markersize=12,
               color=COLORS['programB'], markeredgecolor='white', markeredgewidth=2)
        
        for x, y in zip(thread_data["Count"], thread_data[cpu_col]):
            ax.annotate(f'{y:.1f}%', xy=(x, y), xytext=(0, 12), textcoords='offset points',
                       ha='center', fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Number of Threads', fontweight='bold', fontsize=12)
    ax.set_ylabel('CPU Usage (%)', fontweight='bold', fontsize=12)
    ax.set_title('Program B: Thread Scaling (pthread)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1.5, max(thread_data["Count"]) + 0.5 if len(thread_data) > 0 else 8.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_scaling.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_scaling.png")

# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Main function to generate all plots"""
    
    print("=" * 60)
    print("MT25076_PA01 - Enhanced Plot Generation Script")
    print("=" * 60)
    print()
    
    # Generate Part C plots
    plot_partC()
    print()
    
    # Generate Part D plots
    plot_partD()
    print()
    
    print("=" * 60)
    print(f"All plots saved to: {PROJECT_DIR}")
    print("=" * 60)
    print()
    print("Generated plots:")
    print("  Part C:")
    print("    - MT25076_comparison.png       (Detailed bar comparison)")
    print("  Part D:")
    print("    - MT25076_scaling.png         (CPU scaling line charts)")

if __name__ == "__main__":
    main()