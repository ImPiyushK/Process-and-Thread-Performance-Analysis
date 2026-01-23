#!/bin/bash
# =============================================================================
# Part C: Run all 6 combinations of Program + Worker
# Roll Number: MT25076
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
OUTPUT_FILE="$PROJECT_DIR/MT25076_Part_C_CSV.csv"
TEMP_DIR="/tmp/partC_$$"
IO_REPORT_FILE="/tmp/io_bytes_report.txt"
mkdir -p "$TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
    rm -f "$PROJECT_DIR"/io_temp_*.bin 2>/dev/null || true
    rm -f "$IO_REPORT_FILE" 2>/dev/null || true
}
trap cleanup EXIT

# Programs and worker functions
PROGRAMS=("programA" "programB")
FUNCTIONS=("cpu" "mem" "io")

# Compile programs
echo "Compiling programs..."
gcc -Wall -O2 -DNUM_PROC=2 "$PROJECT_DIR/MT25076_Part_A_Program_A.c" "$PROJECT_DIR/MT25076_Part_A_workers.c" \
    -o "$PROJECT_DIR/programA" -pthread -lm
gcc -Wall -O2 -DTHREADS=2 "$PROJECT_DIR/MT25076_Part_B_Program_B.c" "$PROJECT_DIR/MT25076_Part_A_workers.c" \
    -o "$PROJECT_DIR/programB" -pthread -lm
echo "Compilation complete."

# Initialize CSV with header (IO in MB)
echo "Program+Function,CPU%,Mem(MB),IO(MB),Time(s)" > "$OUTPUT_FILE"

echo "=========================================="
echo "Running Part C Experiments"
echo "=========================================="

for prog in "${PROGRAMS[@]}"; do
    for func in "${FUNCTIONS[@]}"; do
        echo ""
        echo "Testing: $prog + $func"
        echo "----------------------------"
        
        cd "$PROJECT_DIR"
        
        # Initialize temp files
        TOP_LOG="$TEMP_DIR/top_${prog}_${func}.log"
        
        # Clear IO report file
        rm -f "$IO_REPORT_FILE" 2>/dev/null || true
        
        # Run program with taskset (pinned to CPU 0)
        echo "  Running with taskset -c 0..."
        
        taskset -c 0 ./$prog $func > /dev/null 2>&1 &
        PROG_PID=$!
        
        # Initialize measurement variables
        CPU_SAMPLES=()
        MEM_MAX=0
        
        # Give process time to start
        sleep 0.3
        
        # Monitor with top every 0.5 second while process is running
        echo "  Monitoring with top..."
        
        while ps -p $PROG_PID > /dev/null 2>&1; do
            if [ "$prog" == "programA" ]; then
                # Get all related PIDs (parent + children)
                ALL_PIDS="$PROG_PID"
                CHILD_PIDS=$(pgrep -P $PROG_PID 2>/dev/null || echo "")
                if [ -n "$CHILD_PIDS" ]; then
                    ALL_PIDS="$PROG_PID,$(echo $CHILD_PIDS | tr ' ' ',')"
                fi
                
                # Use top to get CPU% and memory
                TOP_OUTPUT=$(top -b -n 1 -p "$ALL_PIDS" 2>/dev/null | \
                    tail -n +8 | awk '{cpu+=$9; mem+=$6} END {print cpu, mem}' || echo "0 0")
            else
                # For threads, all are under one PID
                TOP_OUTPUT=$(top -b -n 1 -p $PROG_PID 2>/dev/null | \
                    tail -n +8 | awk '{print $9, $6}' | head -1 || echo "0 0")
            fi
            
            CPU_NOW=$(echo "$TOP_OUTPUT" | awk '{print $1}')
            MEM_NOW=$(echo "$TOP_OUTPUT" | awk '{print $2}')
            
            # Convert memory to MB
            MEM_NOW_MB=$(echo "scale=2; $MEM_NOW / 1024" | bc 2>/dev/null || echo "0")
            
            # Store CPU sample
            if [ -n "$CPU_NOW" ] && [ "$CPU_NOW" != "0" ]; then
                CPU_SAMPLES+=("$CPU_NOW")
            fi
            
            # Track max memory
            if [ -n "$MEM_NOW_MB" ]; then
                IS_GREATER=$(echo "$MEM_NOW_MB > $MEM_MAX" | bc -l 2>/dev/null || echo "0")
                if [ "$IS_GREATER" -eq 1 ]; then
                    MEM_MAX=$MEM_NOW_MB
                fi
            fi
            
            echo "$(date +%T) CPU=$CPU_NOW MEM=$MEM_NOW_MB" >> "$TOP_LOG"
            sleep 0.5
        done
        
        # Wait for process to fully complete
        wait $PROG_PID 2>/dev/null || true
        
        # Read IO bytes from report file (written by the worker)
        IO_BYTES=0
        if [ -f "$IO_REPORT_FILE" ]; then
            IO_BYTES=$(cat "$IO_REPORT_FILE" 2>/dev/null || echo "0")
        fi
        
        # Measure execution time with a separate run
        echo "  Measuring execution time..."
        rm -f "$IO_REPORT_FILE" 2>/dev/null || true
        EXEC_TIME=$( { time taskset -c 0 ./$prog $func > /dev/null 2>&1; } 2>&1 | \
            grep real | awk '{print $2}' | sed 's/m/*60+/;s/s//' | bc 2>/dev/null || echo "0" )
        
        # Calculate average CPU%
        if [ ${#CPU_SAMPLES[@]} -gt 0 ]; then
            CPU_SUM=0
            for sample in "${CPU_SAMPLES[@]}"; do
                CPU_SUM=$(echo "$CPU_SUM + $sample" | bc 2>/dev/null || echo "$CPU_SUM")
            done
            CPU_AVG=$(echo "scale=2; $CPU_SUM / ${#CPU_SAMPLES[@]}" | bc 2>/dev/null || echo "0")
        else
            CPU_AVG=0
        fi
        
        # Convert IO bytes to MB (1 MB = 1048576 bytes)
        IO_MB=$(echo "scale=2; $IO_BYTES / 1048576" | bc 2>/dev/null || echo "0")
        
        # Ensure valid values
        [ -z "$CPU_AVG" ] && CPU_AVG=0
        [ -z "$MEM_MAX" ] && MEM_MAX=0
        [ -z "$IO_MB" ] && IO_MB=0
        [ -z "$EXEC_TIME" ] && EXEC_TIME=0
        
        # Output results
        echo "  Results:"
        echo "    CPU%: $CPU_AVG (averaged over ${#CPU_SAMPLES[@]} samples)"
        echo "    Mem(MB): $MEM_MAX (max RSS)"
        echo "    IO(MB): $IO_MB (total data read+written)"
        echo "    Time(s): $EXEC_TIME"
        
        # Append to CSV
        echo "${prog}+${func},$CPU_AVG,$MEM_MAX,$IO_MB,$EXEC_TIME" >> "$OUTPUT_FILE"
        
        sleep 1
    done
done

echo ""
echo "=========================================="
echo "Part C Complete!"
echo "Results saved to: $OUTPUT_FILE"
echo "=========================================="

# Display summary
echo ""
echo "Summary:"
echo ""
printf "%-20s %-10s %-10s %-10s %-10s\n" "Program+Function" "CPU%" "Mem(MB)" "IO(MB)" "Time(s)"
printf "%-20s %-10s %-10s %-10s %-10s\n" "--------------------" "------" "------" "-------" "-------"
tail -n +2 "$OUTPUT_FILE" | while IFS=',' read -r name cpu mem io time; do
    printf "%-20s %-10s %-10s %-10s %-10s\n" "$name" "$cpu" "$mem" "$io" "$time"
done
