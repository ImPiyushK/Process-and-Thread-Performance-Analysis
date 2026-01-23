/**
 * Program A:  Multi-process implementation using fork()
 * Roll Number: MT25076
 * 
 * Creates NUM_PROC child processes, each executing the specified worker function. 
 * Default:  2 child processes (can be changed via -DNUM_PROC=n during compilation)
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>
#include "MT25076_Part_A_workers.h"

/* Number of child processes to create */
#ifndef NUM_PROC
#define NUM_PROC 2
#endif

/* Loop count = last digit of roll number * 10^3 */
/* MT25076: last digit = 6, so COUNT = 6 * 10^3 = 6000 */
#define COUNT 6000

/**
 * Main function
 * Usage: ./programA <cpu|mem|io>
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

    printf("Program A: Creating %d child processes for '%s' worker\n", NUM_PROC, argv[1]);

    /* Create NUM_PROC child processes */
    for (int i = 0; i < NUM_PROC; i++) {
        pid_t pid = fork();
        
        if (pid < 0) {
            /* Fork failed */
            perror("fork failed");
            exit(EXIT_FAILURE);
        } 
        else if (pid == 0) {
            /* Child process */
            printf("  Child %d (PID: %d) starting '%s' worker\n", i + 1, getpid(), argv[1]);
            
            if (strcmp(argv[1], "cpu") == 0) {
                cpu_worker(COUNT);
            } 
            else if (strcmp(argv[1], "mem") == 0) {
                mem_worker(COUNT);
            } 
            else if (strcmp(argv[1], "io") == 0) {
                io_worker(COUNT);
            }
            
            printf("  Child %d (PID: %d) completed\n", i + 1, getpid());
            exit(EXIT_SUCCESS);
        }
        /* Parent continues to create more children */
    }

    /* Parent waits for all children to complete */
    int status;
    pid_t child_pid;
    while ((child_pid = wait(&status)) > 0) {
        if (WIFEXITED(status)) {
            printf("  Child PID %d exited with status %d\n", child_pid, WEXITSTATUS(status));
        }
    }

    printf("Program A: All child processes completed\n");
    return EXIT_SUCCESS;
}