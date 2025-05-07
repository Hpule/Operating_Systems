#!/usr/bin/env python3
import sys
from enum import Enum

class ScheduleType(Enum):
    FIFO = "FIFO"  # First In First Out
    SRTN = "SRTN"  # Shortest Remaining Time Next
    RR = "RR"      # Round Robin

class Job:
    def __init__(self, run_time, arrival_time):
        self.id = None  # Will be assigned based on arrival order
        self.run_time = run_time
        self.arrival_time = arrival_time
        self.remaining_time = run_time
        self.start_time = -1  # Time when job first starts running
        self.finish_time = -1  # Time when job completes
        self.is_started = False  # Flag to track if job has started running

    def __str__(self):
        return f"Job {self.id}: Run={self.run_time}, Arrival={self.arrival_time}, Remaining={self.remaining_time}"

class SchedulerSimulator:
    def __init__(self, job_file, algorithm=ScheduleType.FIFO, quantum=1):
        self.job_file = job_file
        self.algorithm = algorithm
        self.quantum = quantum
        self.jobs = []

        self.current_time = 0
        self.completed_jobs = 0
        self.ready_queue = []
        
        self.debug = True  # Set to False to disable all debug messages

    def read_job_file(self):
        try:
            with open(self.job_file, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        run_time, arrival_time = int(parts[0]), int(parts[1])
                        self.jobs.append(Job(run_time, arrival_time))
        except FileNotFoundError:
            print(f"Error: File '{self.job_file}' not found.")
            sys.exit(1)
        except ValueError:
            print(f"Error: Invalid job format in file '{self.job_file}'.")
            sys.exit(1)

    def assign_job_ids(self):
        self.jobs.sort(key=lambda job: job.arrival_time)
        # Assign IDs based on sorted order
        for i, job in enumerate(self.jobs):
            job.id = i

    def simulate(self):
        if not self.jobs:
            print("No jobs to simulate.")
            return
            
        self.current_time = 0
        self.completed_jobs = 0
        self.ready_queue = []
        
        for job in self.jobs:
            job.remaining_time = job.run_time
            job.start_time = -1
            job.finish_time = -1
            job.is_started = False
            
        if self.algorithm == ScheduleType.FIFO:
            self.simulate_fifo()
        elif self.algorithm == ScheduleType.SRTN:
            self.simulate_srtn()
        elif self.algorithm == ScheduleType.RR:
            self.simulate_rr()
        else:
            self.simulate_fifo()

    def simulate_fifo(self):
        print(f"Needs to be implementd")

    def simulate_srtn(self):
        if self.debug:
            print("Running SRTN simulation")
        
        while self.completed_jobs < len(self.jobs):
            shortest_job_index = -1
            shortest_time = float('inf')
            
            # TODO: Loop through jobs and find the one with shortest remaining time
            # that has arrived but not finished
            for i, job
            
            # 2. If no jobs are ready, advance time
            if shortest_job_index == -1:
                if not self.advance_to_next_arrival():
                    break  # No more jobs will arrive
                continue
            
            # 3. Get the job with shortest remaining time
            job = self.jobs[shortest_job_index]
            
            # 4. Set start time if this is the first time running this job
            if job.start_time == -1:
                job.start_time = self.current_time
            
            # 5. Find when the next job will arrive (for preemption)
            next_arrival = float('inf')
            # TODO: Find the time of the next job arrival
            
            # 6. Determine how long to run the current job
            # Either until completion or until next job arrives
            run_time = 0  # TODO: Calculate run time
            
            # 7. Run the job for the calculated time
            self.current_time += run_time
            job.remaining_time -= run_time
            
            # 8. Check if job is completed
            if job.remaining_time == 0:
                job.finish_time = self.current_time
                self.completed_jobs += 1

    def simulate_rr(self):
        while self.completed_jobs < len(self.jobs):
            self.update_ready_queue()
            
            if not self.ready_queue:  # No jobs ready, advance time
                old_time = self.current_time
                if not self.advance_to_next_arrival():
                    break  # No more jobs
                continue
            
            job_index = self.ready_queue.pop(0)
            job = self.jobs[job_index]
            
            if job.start_time == -1:
                job.start_time = self.current_time

            run_time = min(self.quantum, job.remaining_time)
            old_time = self.current_time
            self.current_time += run_time
            job.remaining_time -= run_time
            
            arrival_times = []
            for i, j in enumerate(self.jobs):
                if (j.arrival_time > old_time and 
                    j.arrival_time <= self.current_time and 
                    j.finish_time == -1 and 
                    i not in self.ready_queue and
                    i != job_index):
                    
                    self.ready_queue.append(i)
                    arrival_times.append((i, j.arrival_time))
            
            if job.remaining_time == 0:
                job.finish_time = self.current_time
                self.completed_jobs += 1
            else:
                self.ready_queue.append(job_index)

    def find_next_arrival_time(self):
        next_time = float('inf')
        for job in self.jobs:
            if job.finish_time == -1 and job.arrival_time > self.current_time:
                next_time = min(next_time, job.arrival_time)
        return next_time

    def advance_to_next_arrival(self):
        next_time = self.find_next_arrival_time()
        if next_time != float('inf'):
            self.current_time = next_time
            return True
        return False

    def update_ready_queue(self):
        new_arrivals = []
        for i, job in enumerate(self.jobs):
            if (job.arrival_time <= self.current_time and 
                job.finish_time == -1 and 
                i not in self.ready_queue):
                self.ready_queue.append(i)
                new_arrivals.append(i)
        
        if self.debug and new_arrivals:
            print(f"New jobs added to ready queue: {new_arrivals}")

    def print_results(self):
        total_TAT = 0.0
        total_TW = 0.0
        
        print("\n----- Job Results -----")
        # Sort jobs by ID to ensure they are printed in order
        sorted_jobs = sorted(self.jobs, key=lambda job: job.id)
        
        for job in sorted_jobs:
            tat = job.finish_time - job.arrival_time
            wt = tat - job.run_time
            
            print(f"Job {job.id:3d} -- TAT: {tat:3.2f} WT: {wt:3.2f}")
            
            total_TAT += tat
            total_TW += wt
        
        avg_turnaround_time = total_TAT / len(self.jobs)
        avg_wait_time = total_TW / len(self.jobs)
        
        print(f"Average TAT {avg_turnaround_time:3.2f} WT {avg_wait_time:3.2f}")


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: schedSim <job-file.txt> [-p <ALGORITHM>] [-q <QUANTUM>]")
        sys.exit(1)
    
    job_file = sys.argv[1]
    algorithm = ScheduleType.FIFO  # Default algorithm
    quantum = 1  # Default quantum
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '-p' and i + 1 < len(sys.argv):
            alg_str = sys.argv[i + 1]
            try:
                algorithm = ScheduleType(alg_str)
            except ValueError:
                # If invalid algorithm provided, use default FIFO
                algorithm = ScheduleType.FIFO
            i += 2
        elif sys.argv[i] == '-q' and i + 1 < len(sys.argv):
            try:
                quantum_val = int(sys.argv[i + 1])
                if quantum_val > 0:
                    quantum = quantum_val
            except ValueError:
                pass
            i += 2
        else:
            # Skip unknown arguments
            i += 1
    
    return job_file, algorithm, quantum


def main():
    job_file, algorithm, quantum = parse_arguments()
    
    simulator = SchedulerSimulator(job_file, algorithm, quantum)
    simulator.read_job_file()
    simulator.assign_job_ids()
    
    print(f"Job File: {job_file}")
    print(f"Algorithm: {algorithm.value}")
    if algorithm == ScheduleType.RR:
        print(f"Quantum: {quantum}")
    
    simulator.simulate()
    simulator.print_results()

if __name__ == "__main__":
    main()