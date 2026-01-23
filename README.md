# MT25076_PA01: Process and Thread Performance Analysis

## Roll Number: MT25076

## Overview

This project analyzes the performance characteristics of CPU-intensive, memory-intensive, and I/O-intensive workloads using two different concurrency models:

- **Program A (MT25076_Part_A_Program_A.c)**: Multi-process implementation using `fork()` system call
- **Program B (MT25076_Part_B_Program_B.c)**: Multi-threaded implementation using POSIX `pthread` library

The assignment measures and compares:
- CPU utilization (%)
- Memory consumption (MB)
- I/O data exchange (MB)
- Execution time (seconds)

## File Naming Convention

All files follow the pattern: `MT25076_Part_<Part>_<Description>.<extension>`

## Directory Structure

```
MT25076_PA01/
├── Makefile                        # Build automation (standard naming)
├── README.md                       # This documentation (standard naming)
│
├── Part A - Source Files
│   ├── MT25076_Part_A_Program_A.c  # Multi-process program using fork()
│   ├── MT25076_Part_A_workers.c    # Worker function implementations
│   └── MT25076_Part_A_workers.h    # Worker function declarations
│
├── Part B - Source Files
│   └── MT25076_Part_B_Program_B.c  # Multi-threaded program using pthread
│
├── Part C - Experiment Scripts & Results
│   ├── MT25076_Part_C_shell.sh     # Part C experiment automation script
│   ├── MT25076_Part_C_CSV.csv      # Part C measurement results
│   └── MT25076_Part_C_plot.py      # Python visualization script
│
├── Part D - Scaling Analysis
│   ├── MT25076_Part_D_shell.sh     # Part D scaling experiment script
│   └── MT25076_Part_D_CSV.csv      # Part D measurement results
│
└── Generated Plots (MT25076_*.png)
    ├── MT25076_comparison.png      # Detailed bar comparison
    └── MT25076_scaling.png         # CPU scaling line charts
```

## Requirements

- **GCC** with pthread support
- **bc** (basic calculator for bash arithmetic)
- **taskset** (for CPU pinning, part of util-linux)
- **Python 3** with `pandas`, `matplotlib`, and `numpy`

### Installing Dependencies (Ubuntu/Debian)

```bash
sudo apt-get install build-essential bc util-linux python3-pandas python3-matplotlib python3-numpy
```

## Building the Programs

```bash
make all          # Build both programs (programA and programB)
make programA     # Build Program A only
make programB     # Build Program B only
make clean        # Remove executables
make cleanall     # Remove executables, CSVs, and PNGs
```

### Building with Custom Process/Thread Counts

```bash
make programA_N NUM=4    # Build Program A with 4 processes
make programB_N NUM=8    # Build Program B with 8 threads
```

## Implementation Details

### Worker Functions (MT25076_Part_A_workers.c)

Based on roll number MT25076, the **COUNT = 6 × 10³ = 6000** (last digit = 6).

#### 1. CPU-intensive Worker (`cpu_worker`)
- Performs heavy floating-point arithmetic operations
- Uses `sin()`, `cos()`, `tan()`, `sqrt()`, `log()`, `exp()`, `pow()` functions
- Inner loop: 50,000 iterations per count
- **Expected metrics**: ~90-100% CPU, low memory, minimal I/O

#### 2. Memory-intensive Worker (`mem_worker`)
- Allocates 2 × 48MB arrays (~96MB total)
- Performs sequential writes, `memcpy` operations, and random access patterns
- Includes small sleeps to simulate memory latency
- **Expected metrics**: ~50-70% CPU, high memory (50+ MB), minimal I/O

#### 3. I/O-intensive Worker (`io_worker`)
- Writes 100MB in 1MB chunks with `fflush()` and `fsync()`
- Reads back 100MB for total ~200MB data exchange
- Reports actual bytes transferred to measurement script
- **Expected metrics**: Low CPU, low memory, high I/O (~200 MB)

### Program A - Multi-Process (fork)

- Creates `NUM_PROC` child processes (default: 2)
- Each child executes the specified worker function
- Parent waits for all children using `waitpid()`
- Memory is duplicated for each process (higher total memory usage)

### Program B - Multi-Threaded (pthread)

- Creates `THREADS` worker threads (default: 2)
- All threads share the same memory space
- Main thread waits using `pthread_join()`
- More memory efficient than fork-based approach

## Running Experiments

### Part C: 6 Combinations (2 programs × 3 workers)

```bash
make run-partC
# OR
bash MT25076_Part_C_shell.sh
```

Tests all combinations:
- programA + cpu, programA + mem, programA + io
- programB + cpu, programB + mem, programB + io

Uses `taskset -c 0` to pin programs to CPU 0 for consistent measurements.

### Part D: Scaling Analysis

```bash
make run-partD
# OR
bash MT25076_Part_D_shell.sh
```

Tests scaling behavior:
- Program A with 2, 3, 4, 5 processes (all worker types)
- Program B with 2, 3, 4, 5, 6, 7, 8 threads (all worker types)

### Run All Experiments with Plots

```bash
make run-all    # Runs Part C, Part D, and generates all plots
```

## Output Files

### Part C Results: `MT25076_Part_C_CSV.csv`

```csv
Program+Function,CPU%,Mem(MB),IO(MB),Time(s)
programA+cpu,95.0,2.5,0,5.23
programA+mem,45.0,98.5,0,8.12
programA+io,15.0,3.2,200,2.45
programB+cpu,98.0,2.3,0,4.89
...
```

### Part D Results: `MT25076_Part_D_CSV.csv`

```csv
Program,Worker_Type,number of process/threads,CPU%,MEM,IO
A,cpu,2,94,1024,0
A,cpu,3,96,1536,0
...
B,io,8,12,2048,200
```

## Generating Plots

```bash
make plots
# OR
python3 MT25076_Part_C_plot.py
```

### Generated Visualizations

| Plot File | Description |
|-----------|-------------|
| `MT25076_comparison.png` | Part C: Detailed grouped bar comparison |
| `MT25076_scaling.png` | Part D: Detailed CPU scaling line charts |

## Manual Execution

```bash
# Run individual programs with specific workers
./programA cpu              # Run Program A with CPU worker
./programB mem              # Run Program B with Memory worker
./programA io               # Run Program A with I/O worker

# Pin to specific CPU for consistent measurements
taskset -c 0 ./programA cpu

# Measure with time command
time ./programB io
```

## Expected Results

### CPU Worker
- Should show highest CPU% (~90-100%)
- Program A and B should have similar CPU utilization
- Thread overhead slightly lower than fork overhead

### Memory Worker  
- Should show highest memory consumption
- Program A (fork) uses more total memory due to process duplication
- Program B (pthread) shares memory, more efficient

### I/O Worker
- Should show highest I/O data exchange (~200 MB)
- CPU% should be low (waiting for disk)
- Similar I/O performance for both programs

### Scaling Behavior (Part D)
- CPU% may increase sub-linearly with more processes/threads
- Memory scales linearly for processes, less for threads
- Thread creation has lower overhead than fork

## Measurement Methodology

1. **CPU Measurement**: Uses `top` command to sample CPU% during execution
2. **Memory Measurement**: Tracks max RSS (Resident Set Size) in KB
3. **I/O Measurement**: Worker functions report actual bytes read/written to a temp file
4. **Time Measurement**: Uses shell `time` command for wall-clock time
5. **CPU Pinning**: `taskset -c 0` ensures all work runs on single CPU for fair comparison

## Troubleshooting

### Build Errors
```bash
make clean && make all    # Clean rebuild
```

### Permission Issues
```bash
chmod +x MT25076_Part_C_shell.sh MT25076_Part_D_shell.sh
```

### Python Dependencies
```bash
pip3 install pandas matplotlib numpy
```

## Author

- **Roll Number**: MT25076
- **Assignment**: PA01 - Process and Thread Performance Analysis
- **Course**: Graduate Studies in Computer Science
