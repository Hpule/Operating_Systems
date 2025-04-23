#include <stdio.h>
#include <stdlib.h>
#include "lwp.h"

/* Simple thread function that allocates memory and exits */
void thread_function(void *arg) {
    int thread_number = (int)(long)arg;
    int i; // Declare loop variable before the loop
    
    // Allocate some memory
    int *memory = (int *)malloc(sizeof(int) * 100);
    if (memory == NULL) {
        return;
    }
    
    // Initialize the memory
    for (i = 0; i < 100; i++) {
        memory[i] = thread_number * 100 + i;
    }
    
    // Free the memory before exiting
    free(memory);
}
int main() {
    int i;
    int num_threads = 3;
    
    /* Create threads */
    for (i = 1; i <= num_threads; i++) {
        new_lwp(thread_function, (void*)(long)i, 2048);
    }
    
    lwp_start();
    
    /* Restart threads to test stopping and restarting */
    lwp_start();
    
    return 0;
}