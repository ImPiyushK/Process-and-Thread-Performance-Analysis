#!/bin/bash
# =============================================================================
# Part D: Scaling Analysis - Vary process/thread counts with all worker types
# Roll Number: MT25076
# 
# Tests ALL worker types (cpu, mem, io) with varying:
#   - Number of processes in Program A: 2, 3, 4, 5
#   - Number of threads in Program B: 2, 3, 4, 5, 6, 7, 8
#
# Uses:
#   - top: to record CPU% consumed by the program
#   - taskset: to pin program to specific CPU
#   - Program-reported IO: worker functions report their own IO bytes
#   - time: to measure execution time
# =============================================================================

set -e  # Exit on error

# Directories - flat structure
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Output file
OUTPUT_FILE="$PROJECT_DIR/MT25076_Part_D_CSV.csv"
TEMP_DIR="/tmp/partD_$$"
IO_REPORT_FILE="/tmp/io_bytes_report.txt"
mkdir -p "$TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
    rm -f "$PROJECT_DIR"/io_temp_*.bin 2>/dev/null || true
    rm -f "$IO_REPORT_FILE" 2>/dev/null || true
}
trap cleanup EXIT

# Process counts for Program A (as per assignment)
PROC_COUNTS=(2 3 4 5)

# Thread counts for Program B (as per assignment)
THREAD_COUNTS=(2 3 4 5 6 7 8)

# Worker types
WORKERS=("cpu" "mem" "io")

# Initialize CSV with header (matching requested format)
echo "Program,Worker_Type,number of process/threads,CPU%,MEM,IO" > "$OUTPUT_FILE"

echo "=========================================="
echo "Running Part D Scaling Experiments"
echo "=========================================="

# =============================================================================
# Program A: Scaling with Processes (2, 3, 4, 5) for all worker types
# =============================================================================

echo ""
echo "Testing Program A (fork) with varying process counts..."
echo "Process counts: ${PROC_COUNTS[*]}"
echo "Worker types: ${WORKERS[*]}"
echo "--------------------------------------------------------"

for worker in "${WORKERS[@]}"; do
    for n in "${PROC_COUNTS[@]}"; do
        echo ""
        echo "Compiling Program A with NUM_PROC=$n..."
        
        # Compile with specific process count
        gcc -Wall -O2 -DNUM_PROC=$n "$PROJECT_DIR/MT25076_Part_A_Program_A.c" "$PROJECT_DIR/MT25076_Part_A_workers.c" \
            -o "$PROJECT_DIR/programA" -pthread -lm
        
        echo "Running Program A with $n processes ($worker worker)..."
        
        cd "$PROJECT_DIR"
        
        # Initialize temp files
        TOP_LOG="$TEMP_DIR/top_A_${worker}_${n}.log"
        
        # Clear IO report file
        rm -f "$IO_REPORT_FILE" 2>/dev/null || true
        
        # Run program with taskset (pinned to CPU 0)
        taskset -c 0 ./programA $worker > /dev/null 2>&1 &
        PROG_PID=$!
        
        # Initialize measurement variables
        CPU_SAMPLES=()
        MEM_MAX=0
        
        # Give process time to start
        sleep 0.3
        
        # Monitor with top every 0.5 second while process is running
        while ps -p $PROG_PID > /dev/null 2>&1; do
            # Get all related PIDs (parent + children)
            ALL_PIDS="$PROG_PID"
            CHILD_PIDS=$(pgrep -P $PROG_PID 2>/dev/null || echo "")
            if [ -n "$CHILD_PIDS" ]; then
                ALL_PIDS="$PROG_PID,$(echo $CHILD_PIDS | tr ' ' ',')"
            fi
            
            # Use top to get CPU% and memory for all processes
            TOP_OUTPUT=$(top -b -n 1 -p "$ALL_PIDS" 2>/dev/null | \
                tail -n +8 | awk '{cpu+=$9; mem+=$6} END {print cpu, mem}' || echo "0 0")
            
            CPU_NOW=$(echo "$TOP_OUTPUT" | awk '{print $1}')
            MEM_NOW=$(echo "$TOP_OUTPUT" | awk '{print $2}')
            
            # Convert memory to KB (keep as integer)
            MEM_NOW_KB=$(echo "$MEM_NOW" | awk '{printf "%.0f", $1}')
            
            # Store CPU sample
            if [ -n "$CPU_NOW" ] && [ "$CPU_NOW" != "0" ]; then
                CPU_SAMPLES+=("$CPU_NOW")
            fi
            
            # Track max memory
            if [ -n "$MEM_NOW_KB" ] && [ "$MEM_NOW_KB" != "0" ]; then
                if [ "$MEM_NOW_KB" -gt "$MEM_MAX" ] 2>/dev/null; then
                    MEM_MAX=$MEM_NOW_KB
                fi
            fi
            
            echo "$(date +%T) CPU=$CPU_NOW MEM=$MEM_NOW_KB" >> "$TOP_LOG"
            sleep 0.5
        done
        
        # Wait for process to fully complete
        wait $PROG_PID 2>/dev/null || true
        
        # Read IO bytes from report file (written by the worker)
        IO_BYTES=0
        if [ -f "$IO_REPORT_FILE" ]; then
            IO_BYTES=$(cat "$IO_REPORT_FILE" 2>/dev/null || echo "0")
        fi
        
        # Calculate average CPU% (as integer)
        if [ ${#CPU_SAMPLES[@]} -gt 0 ]; then
            CPU_SUM=0
            for sample in "${CPU_SAMPLES[@]}"; do
                CPU_SUM=$(echo "$CPU_SUM + $sample" | bc 2>/dev/null || echo "$CPU_SUM")
            done
            CPU_AVG=$(echo "scale=0; $CPU_SUM / ${#CPU_SAMPLES[@]}" | bc 2>/dev/null || echo "0")
        else
            CPU_AVG=0
        fi
        
        # Convert IO bytes to MB (as integer)
        IO_MB=$(echo "scale=0; $IO_BYTES / 1048576" | bc 2>/dev/null || echo "0")
        
        # Ensure valid values
        [ -z "$CPU_AVG" ] && CPU_AVG=0
        [ -z "$MEM_MAX" ] && MEM_MAX=0
        [ -z "$IO_MB" ] && IO_MB=0
        
        # Output results
        echo "  A,$worker,$n: CPU%=$CPU_AVG, MEM=$MEM_MAX, IO=$IO_MB"
        
        # Append to CSV (Program A = A)
        echo "A,$worker,$n,$CPU_AVG,$MEM_MAX,$IO_MB" >> "$OUTPUT_FILE"
        
        sleep 1
    done
done

# =============================================================================
# Program B: Scaling with Threads (2, 3, 4, 5, 6, 7, 8) for all worker types
# =============================================================================

echo ""
echo "Testing Program B (pthread) with varying thread counts..."
echo "Thread counts: ${THREAD_COUNTS[*]}"
echo "Worker types: ${WORKERS[*]}"
echo "----------------------------------------------------------"

for worker in "${WORKERS[@]}"; do
    for t in "${THREAD_COUNTS[@]}"; do
        echo ""
        echo "Compiling Program B with THREADS=$t..."
        
        # Compile with specific thread count
        gcc -Wall -O2 -DTHREADS=$t "$PROJECT_DIR/MT25076_Part_B_Program_B.c" "$PROJECT_DIR/MT25076_Part_A_workers.c" \
            -o "$PROJECT_DIR/programB" -pthread -lm
        
        echo "Running Program B with $t threads ($worker worker)..."
        
        cd "$PROJECT_DIR"
        
        # Initialize temp files
        TOP_LOG="$TEMP_DIR/top_B_${worker}_${t}.log"
        
        # Clear IO report file
        rm -f "$IO_REPORT_FILE" 2>/dev/null || true
        
        # Run program with taskset (pinned to CPU 0)
        taskset -c 0 ./programB $worker > /dev/null 2>&1 &
        PROG_PID=$!
        
        # Initialize measurement variables
        CPU_SAMPLES=()
        MEM_MAX=0
        
        # Give process time to start
        sleep 0.3
        
        # Monitor with top every 0.5 second while process is running
        while ps -p $PROG_PID > /dev/null 2>&1; do
            # For threads, all are under the same PID
            TOP_OUTPUT=$(top -b -n 1 -p $PROG_PID 2>/dev/null | \
                tail -n +8 | awk '{print $9, $6}' | head -1 || echo "0 0")
            
            CPU_NOW=$(echo "$TOP_OUTPUT" | awk '{print $1}')
            MEM_NOW=$(echo "$TOP_OUTPUT" | awk '{print $2}')
            
            # Convert memory to KB (keep as integer)
            MEM_NOW_KB=$(echo "$MEM_NOW" | awk '{printf "%.0f", $1}')
            
            # Store CPU sample
            if [ -n "$CPU_NOW" ] && [ "$CPU_NOW" != "0" ]; then
                CPU_SAMPLES+=("$CPU_NOW")
            fi
            
            # Track max memory
            if [ -n "$MEM_NOW_KB" ] && [ "$MEM_NOW_KB" != "0" ]; then
                if [ "$MEM_NOW_KB" -gt "$MEM_MAX" ] 2>/dev/null; then
                    MEM_MAX=$MEM_NOW_KB
                fi
            fi
            
            echo "$(date +%T) CPU=$CPU_NOW MEM=$MEM_NOW_KB" >> "$TOP_LOG"
            sleep 0.5
        done
        
        # Wait for process to fully complete
        wait $PROG_PID 2>/dev/null || true
        
        # Read IO bytes from report file
        IO_BYTES=0
        if [ -f "$IO_REPORT_FILE" ]; then
            IO_BYTES=$(cat "$IO_REPORT_FILE" 2>/dev/null || echo "0")
        fi
        
        # Calculate average CPU% (as integer)
        if [ ${#CPU_SAMPLES[@]} -gt 0 ]; then
            CPU_SUM=0
            for sample in "${CPU_SAMPLES[@]}"; do
                CPU_SUM=$(echo "$CPU_SUM + $sample" | bc 2>/dev/null || echo "$CPU_SUM")
            done
            CPU_AVG=$(echo "scale=0; $CPU_SUM / ${#CPU_SAMPLES[@]}" | bc 2>/dev/null || echo "0")
        else
            CPU_AVG=0
        fi
        
        # Convert IO bytes to MB (as integer)
        IO_MB=$(echo "scale=0; $IO_BYTES / 1048576" | bc 2>/dev/null || echo "0")
        
        # Ensure valid values
        [ -z "$CPU_AVG" ] && CPU_AVG=0
        [ -z "$MEM_MAX" ] && MEM_MAX=0
        [ -z "$IO_MB" ] && IO_MB=0
        
        # Output results
        echo "  B,$worker,$t: CPU%=$CPU_AVG, MEM=$MEM_MAX, IO=$IO_MB"
        
        # Append to CSV (Program B = B)
        echo "B,$worker,$t,$CPU_AVG,$MEM_MAX,$IO_MB" >> "$OUTPUT_FILE"
        
        sleep 1
    done
done

echo ""
echo "=========================================="
echo "Part D Complete!"
echo "Results saved to: $OUTPUT_FILE"
echo "=========================================="

# Display summary
echo ""
echo "Summary:"
cat "$OUTPUT_FILE"

# Generate plots automatically
echo ""
echo "Generating plots..."
python3 "$PROJECT_DIR/MT25076_Part_C_plot.py"