/**
 * Program B: Multi-threaded implementation using pthreads
 * Roll Number: MT25076
 * 
 * Creates THREADS threads, each executing the specified worker function.
 * Default: 2 threads (can be changed via -DTHREADS=n during compilation)
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include "MT25076_Part_A_workers.h"

/* Number of threads to create */
#ifndef THREADS
#define THREADS 2
#endif

/* Loop count = last digit of roll number * 10^3 */
/* MT25076: last digit = 6, so COUNT = 6 * 10^3 = 6000 */
#define COUNT 6000

/* Structure to pass arguments to thread function */
typedef struct {
    int thread_id;
    char worker_type[16];
} thread_args_t;

/**
 * Thread function
 * Executes the appropriate worker based on type
 */
void* thread_func(void *arg) {
    thread_args_t *args = (thread_args_t *)arg;
    
    printf("  Thread %d (TID: %lu) starting '%s' worker\n", 
           args->thread_id, (unsigned long)pthread_self(), args->worker_type);

    if (strcmp(args->worker_type, "cpu") == 0) {
        cpu_worker(COUNT);
    } 
    else if (strcmp(args->worker_type, "mem") == 0) {
        mem_worker(COUNT);
    } 
    else if (strcmp(args->worker_type, "io") == 0) {
        io_worker(COUNT);
    }

    printf("  Thread %d (TID: %lu) completed\n", 
           args->thread_id, (unsigned long)pthread_self());

    return NULL;
}

/**
 * Main function
 * Usage: ./programB <cpu|mem|io>
 */
int main(int argc, char *argv[]) {
    /* Validate command line arguments */
    if (argc != 2) {
        fprintf(stderr, "Usage:  %s <cpu|mem|io>\n", argv[0]);
        fprintf(stderr, "  cpu - CPU-intensive workload\n");
        fprintf(stderr, "  mem - Memory-intensive workload\n");
        fprintf(stderr, "  io  - I/O-intensive workload\n");
        exit(EXIT_FAILURE);
    }

    /* Validate worker type */
    if (strcmp(argv[1], "cpu") != 0 && 
        strcmp(argv[1], "mem") != 0 && 
        strcmp(argv[1], "io") != 0) {
        fprintf(stderr, "Error: Invalid worker type '%s'\n", argv[1]);
        fprintf(stderr, "Valid options: cpu, mem, io\n");
        exit(EXIT_FAILURE);
    }

    printf("Program B: Creating %d threads for '%s' worker\n", THREADS, argv[1]);

    pthread_t threads[THREADS];
    thread_args_t thread_args[THREADS];
    int ret;

    /* Create THREADS threads */
    for (int i = 0; i < THREADS; i++) {
        thread_args[i].thread_id = i + 1;
        strncpy(thread_args[i].worker_type, argv[1], sizeof(thread_args[i].worker_type) - 1);
        thread_args[i].worker_type[sizeof(thread_args[i].worker_type) - 1] = '\0';

        ret = pthread_create(&threads[i], NULL, thread_func, &thread_args[i]);
        if (ret != 0) {
            fprintf(stderr, "Error:  pthread_create failed for thread %d (error:  %d)\n", i + 1, ret);
            exit(EXIT_FAILURE);
        }
    }

    /* Wait for all threads to complete */
    for (int i = 0; i < THREADS; i++) {
        ret = pthread_join(threads[i], NULL);
        if (ret != 0) {
            fprintf(stderr, "Error: pthread_join failed for thread %d (error: %d)\n", i + 1, ret);
        }
    }

    printf("Program B: All threads completed\n");
    return EXIT_SUCCESS;
}