#ifndef WORKERS_H
#define WORKERS_H

/**
 * CPU-intensive worker function
 * Performs heavy arithmetic calculations
 * @param count Number of iterations
 */
void cpu_worker(int count);

/**
 * Memory-intensive worker function
 * Performs repeated memory allocation and traversal
 * @param count Number of iterations
 */
void mem_worker(int count);

/**
 * I/O-intensive worker function
 * Performs repeated disk write operations
 * @param count Number of iterations
 */
void io_worker(int count);

#endif /* WORKERS_H */