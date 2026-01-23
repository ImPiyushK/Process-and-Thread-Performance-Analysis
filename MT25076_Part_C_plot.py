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
    # Plot 1: Combined Dashboard (2x2 grid)
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Part C: Program A (fork) vs Program B (pthread) - Complete Analysis', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    x = np.arange(len(workers))
    width = 0.35
    
    # CPU Usage (top-left)
    ax = axes[0, 0]
    for i, prog in enumerate(programs):
        subset = df[df["Program"] == prog]
        cpu_vals = [subset[subset["Function"] == w][cpu_col].values[0] if len(subset[subset["Function"] == w]) > 0 else 0 for w in workers]
        bars = ax.bar(x + i*width, cpu_vals, width, label=prog.replace('program', 'Program '), 
                     color=COLORS.get(prog, f'C{i}'), edgecolor='white', linewidth=1.5)
        add_value_labels(ax, bars, suffix='%')
    
    ax.set_xlabel('Worker Type', fontweight='bold')
    ax.set_ylabel('CPU Usage (%)', fontweight='bold')
    ax.set_title('CPU Utilization', fontsize=13, fontweight='bold')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels([w.upper() for w in workers])
    ax.legend(loc='upper right')
    ax.set_ylim(0, max(df[cpu_col]) * 1.3)
    ax.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='100% threshold')
    
    # Memory Usage (top-right)
    ax = axes[0, 1]
    for i, prog in enumerate(programs):
        subset = df[df["Program"] == prog]
        mem_vals = [subset[subset["Function"] == w][mem_col].values[0] if len(subset[subset["Function"] == w]) > 0 else 0 for w in workers]
        bars = ax.bar(x + i*width, mem_vals, width, label=prog.replace('program', 'Program '), 
                     color=COLORS.get(prog, f'C{i}'), edgecolor='white', linewidth=1.5)
        add_value_labels(ax, bars, fmt='.2f', suffix=' MB')
    
    ax.set_xlabel('Worker Type', fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)', fontweight='bold')
    ax.set_title('Memory Consumption', fontsize=13, fontweight='bold')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels([w.upper() for w in workers])
    ax.legend(loc='upper right')
    
    # I/O Usage (bottom-left)
    ax = axes[1, 0]
    for i, prog in enumerate(programs):
        subset = df[df["Program"] == prog]
        io_vals = [subset[subset["Function"] == w][io_col].values[0] if len(subset[subset["Function"] == w]) > 0 else 0 for w in workers]
        bars = ax.bar(x + i*width, io_vals, width, label=prog.replace('program', 'Program '), 
                     color=COLORS.get(prog, f'C{i}'), edgecolor='white', linewidth=1.5)
        if "GB" in io_col:
            add_value_labels(ax, bars, fmt='.3f', suffix=' GB')
        else:
            add_value_labels(ax, bars, fmt='.1f')
    
    ax.set_xlabel('Worker Type', fontweight='bold')
    ax.set_ylabel(io_label, fontweight='bold')
    ax.set_title('I/O Activity', fontsize=13, fontweight='bold')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels([w.upper() for w in workers])
    ax.legend(loc='upper right')
    
    # Execution Time (bottom-right)
    ax = axes[1, 1]
    if time_col and time_col in df.columns:
        for i, prog in enumerate(programs):
            subset = df[df["Program"] == prog]
            time_vals = [subset[subset["Function"] == w][time_col].values[0] if len(subset[subset["Function"] == w]) > 0 else 0 for w in workers]
            bars = ax.bar(x + i*width, time_vals, width, label=prog.replace('program', 'Program '), 
                         color=COLORS.get(prog, f'C{i}'), edgecolor='white', linewidth=1.5)
            add_value_labels(ax, bars, fmt='.2f', suffix='s')
        
        ax.set_xlabel('Worker Type', fontweight='bold')
        ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
        ax.set_title('Execution Time', fontsize=13, fontweight='bold')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels([w.upper() for w in workers])
        ax.legend(loc='upper right')
    else:
        ax.text(0.5, 0.5, 'No timing data available', ha='center', va='center', 
                fontsize=14, transform=ax.transAxes)
        ax.set_title('Execution Time', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_dashboard_fork.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_dashboard_fork.png")
    
    # =========================================================================
    # Plot 2: Heatmap of Normalized Metrics
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prepare data for heatmap
    metrics = [cpu_col, mem_col, io_col]
    if time_col:
        metrics.append(time_col)
    
    heatmap_data = []
    row_labels = []
    
    for prog in programs:
        for func in workers:
            subset = df[(df["Program"] == prog) & (df["Function"] == func)]
            if len(subset) > 0:
                row = [subset[m].values[0] for m in metrics]
                heatmap_data.append(row)
                row_labels.append(f"{prog.replace('program', 'Prog')}+{func.upper()}")
    
    heatmap_array = np.array(heatmap_data)
    
    # Normalize each column independently
    normalized = np.zeros_like(heatmap_array)
    for i in range(heatmap_array.shape[1]):
        col = heatmap_array[:, i]
        min_val, max_val = col.min(), col.max()
        if max_val > min_val:
            normalized[:, i] = (col - min_val) / (max_val - min_val)
        else:
            normalized[:, i] = 0.5
    
    # Create heatmap with values
    im = ax.imshow(normalized, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Normalized Value (0=Low, 1=High)', fontweight='bold')
    
    # Set ticks and labels
    metric_labels = ['CPU %', 'Memory (MB)', io_label.split('(')[0].strip()]
    if time_col:
        metric_labels.append('Time (s)')
    
    ax.set_xticks(np.arange(len(metric_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(metric_labels, fontsize=11, fontweight='bold')
    ax.set_yticklabels(row_labels, fontsize=10)
    
    # Add text annotations with actual values
    for i in range(len(row_labels)):
        for j in range(len(metric_labels)):
            val = heatmap_array[i, j]
            # Format based on column
            if j == 0:  # CPU
                text = f'{val:.1f}%'
            elif j == 1:  # Memory
                text = f'{val:.1f}'
            elif j == 2:  # IO
                text = f'{val:.3f}' if "GB" in io_col else f'{val:.1f}'
            else:  # Time
                text = f'{val:.2f}s'
            
            color = 'white' if normalized[i, j] > 0.5 else 'black'
            ax.text(j, i, text, ha='center', va='center', color=color, fontsize=10, fontweight='bold')
    
    ax.set_title('Part C: Metric Comparison Heatmap\n(Normalized - Green=Low, Red=High)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_heatmap.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_heatmap.png")
    
    # =========================================================================
    # Plot 3: Radar Chart - Task Profiles
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), subplot_kw=dict(projection='polar'))
    fig.suptitle('Part C: Worker Type Profiles by Program', fontsize=14, fontweight='bold', y=1.02)
    
    categories = ['CPU', 'Memory', 'I/O']
    if time_col:
        categories.append('Time')
    
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the polygon
    
    for idx, prog in enumerate(programs):
        ax = axes[idx]
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
        
        worker_colors = {'cpu': COLORS['cpu'], 'mem': COLORS['mem'], 'io': COLORS['io']}
        
        for func in workers:
            subset = df[(df["Program"] == prog) & (df["Function"] == func)]
            if len(subset) > 0:
                values = [
                    subset[cpu_col].values[0],
                    subset[mem_col].values[0] * 10,  # Scale for visibility
                    subset[io_col].values[0] * 100 if "GB" in io_col else subset[io_col].values[0] / 10
                ]
                if time_col:
                    values.append(subset[time_col].values[0] * 10)
                
                # Normalize for radar
                max_vals = [150, 100, 100, 100] if time_col else [150, 100, 100]
                values_norm = [min(v / m * 100, 100) for v, m in zip(values, max_vals)]
                values_norm += values_norm[:1]
                
                ax.plot(angles, values_norm, 'o-', linewidth=2, label=func.upper(), 
                       color=worker_colors[func], markersize=6)
                ax.fill(angles, values_norm, alpha=0.15, color=worker_colors[func])
        
        ax.set_ylim(0, 100)
        ax.set_title(prog.replace('program', 'Program ').upper(), fontsize=13, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_radar.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_radar.png")
    
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
    mem_col = "Mem(MB)" if "Mem(MB)" in df.columns else "Mem"
    if "IO(MB)" in df.columns:
        io_col = "IO(MB)"
    elif "IO(GB)" in df.columns:
        io_col = "IO(GB)"
    else:
        io_col = "IO(kB/s)" if "IO(kB/s)" in df.columns else "IO"
    time_col = "Time(s)" if "Time(s)" in df.columns else None
    
    # Convert numeric columns safely
    df["Count"] = pd.to_numeric(df["Count"], errors="coerce").fillna(0).astype(int)
    df[cpu_col] = pd.to_numeric(df[cpu_col], errors="coerce").fillna(0)
    df[mem_col] = pd.to_numeric(df[mem_col], errors="coerce").fillna(0)
    df[io_col] = pd.to_numeric(df[io_col], errors="coerce").fillna(0)
    if time_col:
        df[time_col] = pd.to_numeric(df[time_col], errors="coerce").fillna(0)
    
    # Separate data
    proc_data = df[df["Program"] == "programA"].sort_values("Count")
    thread_data = df[df["Program"] == "programB"].sort_values("Count")
    
    # =========================================================================
    # Plot 1: Combined Dashboard for Scaling
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Part D: Scaling Analysis - Processes vs Threads', fontsize=16, fontweight='bold', y=1.02)
    
    # CPU Scaling (top-left)
    ax = axes[0, 0]
    if len(proc_data) > 0:
        ax.plot(proc_data["Count"], proc_data[cpu_col], 'o-', linewidth=2.5, markersize=10,
               color=COLORS['programA'], label='Program A (processes)')
        for x, y in zip(proc_data["Count"], proc_data[cpu_col]):
            ax.annotate(f'{y:.0f}%', xy=(x, y), xytext=(0, 8), textcoords='offset points',
                       ha='center', fontsize=9, fontweight='bold', color=COLORS['programA'])
    
    if len(thread_data) > 0:
        ax.plot(thread_data["Count"], thread_data[cpu_col], 's-', linewidth=2.5, markersize=10,
               color=COLORS['programB'], label='Program B (threads)')
        for x, y in zip(thread_data["Count"], thread_data[cpu_col]):
            ax.annotate(f'{y:.0f}%', xy=(x, y), xytext=(0, -15), textcoords='offset points',
                       ha='center', fontsize=9, fontweight='bold', color=COLORS['programB'])
    
    ax.set_xlabel('Number of Processes/Threads', fontweight='bold')
    ax.set_ylabel('CPU Usage (%)', fontweight='bold')
    ax.set_title('CPU Scaling', fontsize=13, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Memory Scaling (top-right)
    ax = axes[0, 1]
    if len(proc_data) > 0:
        ax.plot(proc_data["Count"], proc_data[mem_col], 'o-', linewidth=2.5, markersize=10,
               color=COLORS['programA'], label='Program A (processes)')
    if len(thread_data) > 0:
        ax.plot(thread_data["Count"], thread_data[mem_col], 's-', linewidth=2.5, markersize=10,
               color=COLORS['programB'], label='Program B (threads)')
    
    ax.set_xlabel('Number of Processes/Threads', fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)', fontweight='bold')
    ax.set_title('Memory Scaling', fontsize=13, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Time Scaling Bar Chart (bottom-left)
    ax = axes[1, 0]
    if time_col and len(proc_data) > 0 and len(thread_data) > 0:
        width = 0.35
        x_proc = np.arange(len(proc_data))
        x_thread = np.arange(len(thread_data))
        
        ax.bar(x_proc - width/2, proc_data[time_col].values, width, 
               label='Program A', color=COLORS['programA'], alpha=0.8)
        
        # Only plot matching counts for threads
        max_proc = len(proc_data)
        ax.bar(x_thread[:max_proc] + width/2, thread_data[time_col].values[:max_proc], width, 
               label='Program B', color=COLORS['programB'], alpha=0.8)
        
        ax.set_xlabel('Process/Thread Count Index', fontweight='bold')
        ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
        ax.set_title('Execution Time Comparison', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    # Efficiency Plot (bottom-right) - CPU per process/thread
    ax = axes[1, 1]
    if len(proc_data) > 0:
        efficiency_proc = proc_data[cpu_col] / proc_data["Count"]
        ax.plot(proc_data["Count"], efficiency_proc, 'o-', linewidth=2.5, markersize=10,
               color=COLORS['programA'], label='Program A (processes)')
    
    if len(thread_data) > 0:
        efficiency_thread = thread_data[cpu_col] / thread_data["Count"]
        ax.plot(thread_data["Count"], efficiency_thread, 's-', linewidth=2.5, markersize=10,
               color=COLORS['programB'], label='Program B (threads)')
    
    ax.set_xlabel('Number of Processes/Threads', fontweight='bold')
    ax.set_ylabel('CPU% per Process/Thread', fontweight='bold')
    ax.set_title('CPU Efficiency (Lower = More Overhead)', fontsize=13, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "MT25076_dashboard_thread.png"), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  - Saved: MT25076_dashboard_thread.png")
    
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
    print("    - MT25076_dashboard_fork.png   (Combined 2x2 grid)")
    print("    - MT25076_heatmap.png          (Normalized metrics heatmap)")
    print("    - MT25076_radar.png            (Worker type profiles)")
    print("    - MT25076_comparison.png       (Detailed bar comparison)")
    print("  Part D:")
    print("    - MT25076_dashboard_thread.png (Scaling analysis grid)")
    print("    - MT25076_scaling.png         (CPU scaling line charts)")

if __name__ == "__main__":
    main()