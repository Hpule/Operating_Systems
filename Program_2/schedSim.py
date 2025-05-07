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

class SchedulerSimulator:
    def __init__(self, job_file, algorithm=ScheduleType.FIFO, quantum=1):
        self.job_file = job_file
        self.algorithm = algorithm
        self.quantum = quantum
        self.jobs = []

        self.current_time = 0
        self.completed_jobs = 0
        self.ready_queue = []
        
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
            
        if self.algorithm == ScheduleType.FIFO:
            self.simulate_fifo()
        elif self.algorithm == ScheduleType.SRTN:
            self.simulate_srtn()
        elif self.algorithm == ScheduleType.RR:
            self.simulate_rr()
        else:
            self.simulate_fifo()
    
    def run_job(self, job_index, run_time):
        job = self.jobs[job_index]
        
        if job.start_time == -1:
            job.start_time = self.current_time
        
        old_time = self.current_time
        self.current_time += run_time
        job.remaining_time -= run_time
        
        # Check if job completed
        if job.remaining_time == 0:
            job.finish_time = self.current_time
            self.completed_jobs += 1
            return True  # Job completed
        
        return False  # Job not completed
    
    def get_available_jobs(self):
        available_jobs = []
        for i, job in enumerate(self.jobs):
            if (job.arrival_time <= self.current_time and 
                job.finish_time == -1):
                available_jobs.append((i, job))
        return available_jobs
    
    def arriving_job(self):
        next_arrival = float('inf')
        next_job_index = -1
        
        for i, job in enumerate(self.jobs):
            if (job.arrival_time > self.current_time and 
                job.arrival_time < next_arrival and 
                job.finish_time == -1):
                next_arrival = job.arrival_time
                next_job_index = i
        
        return next_arrival
    
    def check_new_arrivals(self, old_time, current_job_index):
        new_arrivals = []
        
        for i, job in enumerate(self.jobs):
            if (job.arrival_time > old_time and 
                job.arrival_time <= self.current_time and 
                job.finish_time == -1 and 
                i not in self.ready_queue and
                i != current_job_index):
                
                self.ready_queue.append(i)
                new_arrivals.append((i, job.arrival_time))
        
        return new_arrivals
    
    def simulate_srtn(self):        
        while self.completed_jobs < len(self.jobs):
            available_jobs = self.get_available_jobs()
            
            if not available_jobs:
                if not self.advance_to_next_arrival():
                    break  # No more jobs will arrive
                continue
            
            available_jobs.sort(key=lambda x: x[1].remaining_time)
            job_index, job = available_jobs[0]
            next_arrival = self.arriving_job()
            
            if next_arrival == float('inf'):
                run_time = job.remaining_time  # Run until completion
            else:
                run_time = min(job.remaining_time, next_arrival - self.current_time)
            
            self.run_job(job_index, run_time)
    
    def simulate_rr(self):        
        while self.completed_jobs < len(self.jobs):
            self.update_ready_queue()
            
            if not self.ready_queue:  # No jobs ready
                if not self.advance_to_next_arrival():
                    break  # No more jobs
                continue
            
            job_index = self.ready_queue.pop(0)
            run_time = min(self.quantum, self.jobs[job_index].remaining_time)
            old_time = self.current_time
            job_completed = self.run_job(job_index, run_time)
            self.check_new_arrivals(old_time, job_index)
            
            if not job_completed:
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

    def print_results(self):
        total_tat = 0.0
        total_wt = 0.0
        sorted_jobs = sorted(self.jobs, key=lambda job: job.id)
        print("\n----- Job Results -----")
        for job in self.jobs:
            tat = job.finish_time - job.arrival_time
            wt = tat - job.run_time
            print(f"Job {job.id:3d} -- WT: {wt:3.1f} TAT: {tat:3.1f}")
            total_tat += tat
            total_wt += wt
        
        avg_tat = total_tat / len(self.jobs)
        avg_wt = total_wt / len(self.jobs) 
        print(f"Average WT:{avg_wt:3.1f} TAT:{avg_tat:3.1f} ")


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
                algorithm = ScheduleType.FIFO  #default FIFO
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
            i += 1  # Skip unknown arguments
    
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