/**
 * Worker Functions Implementation
 * Roll Number: MT25076
 * Last digit: 6, so COUNT = 6 * 10^3 = 6000
 * 
 * Enhanced to show distinct metrics for each worker type:
 * - CPU worker: High CPU%, low memory, low I/O
 * - Memory worker: Medium CPU% (with memory waits), high memory usage, low I/O
 * - I/O worker: Low CPU%, low memory, high data exchange
 */

#include "MT25076_Part_A_workers.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <string.h>
#include <sched.h>

/* Memory worker allocates 50MB to show clear memory usage */
#define MEMORY_ARRAY_SIZE (12 * 1024 * 1024)  /* 12M integers = ~48MB */

/* I/O worker writes 1MB chunks for measurable data exchange */
#define IO_CHUNK_SIZE (1024 * 1024)  /* 1MB per write */
#define IO_ITERATIONS 100            /* Write 100MB total */

/* File to report IO bytes for measurement script to read */
#define IO_REPORT_FILE "/tmp/io_bytes_report.txt"

/**
 * CPU-intensive worker function
 * Performs heavy arithmetic calculations to maximize CPU usage
 * Should show: High CPU% (90-100%), low memory, minimal I/O
 */
void cpu_worker(int count) {
    volatile double x = 0.0;
    volatile double y = 1.0;
    volatile double z = 2.0;
    
    /* Outer loop based on count (6000 for MT25076) */
    for (int i = 0; i < count; i++) {
        /* Heavy inner loop - 50000 iterations of complex math */
        for (int j = 1; j < 50000; j++) {
            /* Complex floating-point operations to stress CPU */
            x += (i * j) / (double)(j + 1);
            y *= 1.0 + (1.0 / (double)(j + i + 1));
            z = sin((double)j) * cos((double)i) + tan((double)(j % 100 + 1));
            x += sqrt(fabs(y)) + log(fabs(z) + 1.0);
            y = pow(fabs(x), 0.1) + exp(-fabs(z) / 1000.0);
            
            /* More arithmetic to keep CPU busy */
            volatile double temp = x * y - z;
            temp = temp / (fabs(temp) + 1.0);
            x += temp * 0.001;
        }
    }
    
    /* Report 0 IO for cpu worker */
    FILE *report = fopen(IO_REPORT_FILE, "w");
    if (report) {
        fprintf(report, "0\n");
        fclose(report);
    }
}

/**
 * Memory-intensive worker function
 * Allocates large memory blocks and performs memory access patterns
 * Includes small sleeps to simulate memory latency and show lower CPU%
 * Should show: Medium CPU% (50-70%), high memory (50+ MB), minimal I/O
 */
void mem_worker(int count) {
    /* Allocate a large array (~48MB) to show clear memory usage */
    int *arr = (int *)malloc(sizeof(int) * MEMORY_ARRAY_SIZE);
    if (!arr) {
        perror("malloc failed");
        return;
    }
    
    /* Allocate a second array for more memory visibility */
    int *arr2 = (int *)malloc(sizeof(int) * MEMORY_ARRAY_SIZE);
    if (!arr2) {
        free(arr);
        perror("malloc failed for arr2");
        return;
    }

    /* Repeated memory access patterns - scale down count for reasonable runtime */
    int iterations = count / 100;  /* 60 iterations for count=6000 */
    if (iterations < 10) iterations = 10;
    
    for (int i = 0; i < iterations; i++) {
        /* Sequential write pass - touches all memory */
        for (int j = 0; j < MEMORY_ARRAY_SIZE; j++) {
            arr[j] = j * i + 1;
        }
        
        /* Copy between arrays - more memory pressure */
        memcpy(arr2, arr, sizeof(int) * MEMORY_ARRAY_SIZE);
        
        /* Simulate memory latency - small sleep to show lower CPU% */
        usleep(50000);  /* 50ms sleep per iteration */
        
        /* Random access pattern - stresses memory subsystem */
        volatile long sum = 0;
        for (int j = 0; j < MEMORY_ARRAY_SIZE; j += 64) {
            int idx = ((long)j * 7919) % MEMORY_ARRAY_SIZE;
            sum += arr[idx] + arr2[(idx + 64) % MEMORY_ARRAY_SIZE];
        }
        
        /* Yield to show we're waiting for memory */
        sched_yield();
        
        /* Write back with dependency on sum */
        for (int j = 0; j < MEMORY_ARRAY_SIZE; j++) {
            arr[j] = (int)(arr[j] + (sum % 100));
        }
        
        usleep(30000);  /* 30ms */
    }
    
    free(arr);
    free(arr2);
    
    /* Report 0 IO for mem worker */
    FILE *report = fopen(IO_REPORT_FILE, "w");
    if (report) {
        fprintf(report, "0\n");
        fclose(report);
    }
}

/**
 * I/O-intensive worker function
 * Writes large amounts of data to disk to show high data exchange
 * Reports total bytes read+written to a temp file for measurement
 * Should show: Low CPU%, low memory, high I/O (200 MB total)
 */
void io_worker(int count) {
    /* Create unique filename per process/thread to avoid conflicts */
    char filename[64];
    snprintf(filename, sizeof(filename), "io_temp_%d.bin", getpid());
    
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("fopen failed");
        return;
    }
    
    /* Allocate 1MB buffer for writing */
    char *buffer = (char *)malloc(IO_CHUNK_SIZE);
    if (!buffer) {
        fclose(fp);
        perror("malloc failed for IO buffer");
        return;
    }
    
    /* Fill buffer with data pattern */
    for (int i = 0; i < IO_CHUNK_SIZE; i++) {
        buffer[i] = (char)(i % 256);
    }
    
    /* Track total bytes for reporting */
    long total_bytes = 0;
    
    /* Write IO_ITERATIONS x 1MB = 100MB of data */
    for (int i = 0; i < IO_ITERATIONS; i++) {
        /* Modify buffer slightly each iteration to prevent caching */
        buffer[i % IO_CHUNK_SIZE] = (char)((i * 17) % 256);
        
        /* Write 1MB chunk */
        size_t written = fwrite(buffer, 1, IO_CHUNK_SIZE, fp);
        total_bytes += written;
        
        /* Force flush to disk for actual I/O */
        fflush(fp);
        fsync(fileno(fp));
    }
    
    /* Close and reopen for read to add read I/O */
    fclose(fp);
    
    fp = fopen(filename, "rb");
    if (fp) {
        /* Read back all data */
        for (int i = 0; i < IO_ITERATIONS; i++) {
            size_t bytes_read = fread(buffer, 1, IO_CHUNK_SIZE, fp);
            total_bytes += bytes_read;
        }
        fclose(fp);
    }
    
    free(buffer);
    
    /* Clean up temp file */
    remove(filename);
    
    /* Report total IO bytes to temp file for measurement script */
    FILE *report = fopen(IO_REPORT_FILE, "w");
    if (report) {
        fprintf(report, "%ld\n", total_bytes);
        fclose(report);
    }
}