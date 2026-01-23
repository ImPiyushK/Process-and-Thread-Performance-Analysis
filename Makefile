# =============================================================================
# Makefile for MT25076_PA01
# Process and Thread Performance Analysis Assignment
# Flat directory structure - all files in root folder
# =============================================================================

CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -pthread -lm

# Default targets
all: programA programB
	@echo "Build complete. Run 'make run-partC' or 'make run-partD' to execute experiments."

# Program A: Multi-process using fork()
programA: MT25076_Part_A_Program_A.c MT25076_Part_A_workers.c MT25076_Part_A_workers.h
	$(CC) $(CFLAGS) -DNUM_PROC=2 MT25076_Part_A_Program_A.c MT25076_Part_A_workers.c -o programA $(LDFLAGS)

# Program B: Multi-threaded using pthread
programB: MT25076_Part_B_Program_B.c MT25076_Part_A_workers.c MT25076_Part_A_workers.h
	$(CC) $(CFLAGS) -DTHREADS=2 MT25076_Part_B_Program_B.c MT25076_Part_A_workers.c -o programB $(LDFLAGS)

# Build with specific process count: make programA_N NUM=4
programA_N: MT25076_Part_A_Program_A.c MT25076_Part_A_workers.c MT25076_Part_A_workers.h
	$(CC) $(CFLAGS) -DNUM_PROC=$(NUM) MT25076_Part_A_Program_A.c MT25076_Part_A_workers.c -o programA $(LDFLAGS)

# Build with specific thread count: make programB_N NUM=4
programB_N: MT25076_Part_B_Program_B.c MT25076_Part_A_workers.c MT25076_Part_A_workers.h
	$(CC) $(CFLAGS) -DTHREADS=$(NUM) MT25076_Part_B_Program_B.c MT25076_Part_A_workers.c -o programB $(LDFLAGS)

# Run Part C experiments
run-partC:
	@chmod +x MT25076_Part_C_shell.sh
	@bash MT25076_Part_C_shell.sh

# Run Part D experiments
run-partD:
	@chmod +x MT25076_Part_D_shell.sh
	@bash MT25076_Part_D_shell.sh

# Generate plots
plots:
	@python3 MT25076_Part_C_plot.py

# Run all experiments and generate plots
run-all: run-partC run-partD plots
	@echo "All experiments completed and plots generated."

# Clean build artifacts
clean:
	rm -f programA programB io_temp*.bin io_temp*.txt

# Clean all generated files including data and plots
cleanall: clean
	rm -f *.csv *.png

# Help target
help:
	@echo "Available targets:"
	@echo "  make all        - Build both programs"
	@echo "  make programA   - Build Program A (fork)"
	@echo "  make programB   - Build Program B (pthread)"
	@echo "  make run-partC  - Run Part C experiments"
	@echo "  make run-partD  - Run Part D experiments"
	@echo "  make plots      - Generate visualization plots"
	@echo "  make run-all    - Run all experiments and plots"
	@echo "  make clean      - Remove executables"
	@echo "  make cleanall   - Remove all generated files"

.PHONY: all run-partC run-partD plots run-all clean cleanall help