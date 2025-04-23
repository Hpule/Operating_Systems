#include <stdio.h>
#include <stdlib.h>

#include "lwp.h"
/*
    SAVE_STATE()
    RESTORE_STATE()
    SetSP()
    GetSP()
*/

// Global Pointer that gets stack pointers
lwp_context lwp_ptable[LWP_PROC_LIMIT]; 
int lwp_processes = 0; 
int curr_process = -1; 
unsigned long curr_pid_process = 0; 
ptr_int_t *global_sp = NULL; 
schedfun scheduler_function = NULL; 

/* lwp functions */
int new_lwp(lwpfun function ,void *arg, size_t stacksize); 
int  lwp_getpid();
void lwp_yield();
void lwp_exit();
void lwp_start();
void lwp_stop(); // 
void lwp_set_scheduler(schedfun sched);

/* helper functions*/
void ribbed_robin(){
    if(curr_process ==  lwp_processes - 1){
        curr_process = 0; 
    } else{
        curr_process++; 
    } 
}

void based_scheduler(){
    if(scheduler_function == NULL){ // Default Scheduler
        ribbed_robin(); 
    }else{ // Other Schedulers
        curr_process = (scheduler_function)(); // 
    }
}


// This works
int new_lwp(lwpfun function, void *arg, size_t stacksize){
    
    if(lwp_processes >= LWP_PROC_LIMIT){ // Checking the number of LWP's active 
        // printf("Error: Reached LWP process limit\n");
        return -1; 
    }

    ptr_int_t *stack_pointer = malloc(stacksize * 4); 

    lwp_ptable[lwp_processes].stack = stack_pointer;

    stack_pointer += stacksize; 
    stack_pointer -= 1; 

    *stack_pointer = (ptr_int_t) arg; 
    stack_pointer -= 1; 

    *stack_pointer = (ptr_int_t) lwp_exit; //Why?
    stack_pointer -= 1; 

    *stack_pointer = (ptr_int_t) function;
    stack_pointer -= 1; 

    *stack_pointer = (ptr_int_t) 0xFEEDBEEF;
    
    // address of the bogus base paonter 
    // Restore stable add to EBP 

    ptr_int_t base_pointer = (ptr_int_t) stack_pointer;
    stack_pointer -= 7; 
    *stack_pointer = base_pointer; 

    // Uncomment to make sure thatr lsit is correct
    // Copy Stuff
    curr_pid_process++; 
    lwp_ptable[lwp_processes].pid = curr_pid_process; 
    lwp_ptable[lwp_processes].sp = stack_pointer; 
    lwp_ptable[lwp_processes].stacksize = stacksize; 
    lwp_processes++; 

    return lwp_ptable[lwp_processes - 1].pid;
}

int  lwp_getpid(){
    if (curr_process == -1) {
        return 0; // No LWP is currently running
    }
    return lwp_ptable[curr_process].pid;
    // return 0; 
}

void lwp_yield(){ // Soft-Bullies LWP's
   
    SAVE_STATE(); 
    GetSP(lwp_ptable[curr_process].sp);
    
    based_scheduler(); 
    
    SetSP(lwp_ptable[curr_process].sp); 
    RESTORE_STATE(); 
}

void lwp_exit(){
    // printf("LWP end\n"); 
    free(lwp_ptable[curr_process].stack);
    lwp_processes--; 

    if(lwp_processes > 0 ){
        int curr = 0; 
        for(curr = curr_process; curr < lwp_processes; curr++){
            lwp_ptable[curr] = lwp_ptable[curr + 1]; 
        }
    } else{
        SetSP(global_sp);  
        RESTORE_STATE();
        return; 
    }

    SetSP(lwp_ptable[curr_process].sp); 
    RESTORE_STATE(); 
}


// When lwp_start() is called:
void lwp_start(){
    // Check if there are processes to run
    if (lwp_processes <= 0) {
        return;
    }
    
    // Save the main thread's context
    SAVE_STATE();
    
    // Get the main thread's stack pointer
    GetSP(global_sp);
    
    // Set the current process to the first one
    curr_process = 0;
    
    // Switch to the first process
    SetSP(lwp_ptable[curr_process].sp);
    
    // Restore the new context (this will start running the first LWP)
    RESTORE_STATE();
}


void lwp_stop(){
    SAVE_STATE(); 
    
    GetSP(lwp_ptable[curr_process].sp);
    SetSP(global_sp); 
    
    RESTORE_STATE(); 
}

void lwp_set_scheduler(schedfun sched){
    scheduler_function = sched;
}