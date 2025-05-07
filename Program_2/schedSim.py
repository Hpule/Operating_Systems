#!/usr/bin/env python3
"""
schedSim - Process Scheduler Simulator
Supports FIFO, SRTN, and RR scheduling algorithms
"""

import sys
from enum import Enum

# Enum for scheduling algorithms
class ScheduleType(Enum):
    FIFO = "FIFO"  # First In First Out
    SRTN = "SRTN"  # Shortest Remaining Time Next
    RR = "RR"      # Round Robin

# Job class to store job information
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

# Main scheduler simulator class
class SchedulerSimulator:
    def __init__(self, job_file, algorithm=ScheduleType.FIFO, quantum=1):
        self.job_file = job_file
        self.algorithm = algorithm
        self.quantum = quantum
        self.jobs = []

    def read_job_file(self):
        """Read jobs from the specified file."""
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
        """Sort jobs by arrival time and assign IDs."""
        # Sort jobs by arrival time
        self.jobs.sort(key=lambda job: job.arrival_time)
        
        # Assign IDs based on sorted order
        for i, job in enumerate(self.jobs):
            job.id = i

    def simulate(self):
        """Run the selected scheduling algorithm simulation."""
        if not self.jobs:
            print("No jobs to simulate.")
            return

        if self.algorithm == ScheduleType.FIFO:
            self.simulate_fifo()
        elif self.algorithm == ScheduleType.SRTN:
            self.simulate_srtn()
        elif self.algorithm == ScheduleType.RR:
            self.simulate_rr()
        else:
            # Default to FIFO
            self.simulate_fifo()

    def simulate_fifo(self):
        """Simulate First In First Out scheduling."""
        print("FIFO scheduling to be implemented")
        # Placeholder for FIFO implementation
        pass

    def simulate_srtn(self):
        """Simulate Shortest Remaining Time Next scheduling."""
        print("SRTN scheduling to be implemented")
        # Placeholder for SRTN implementation
        pass

    def simulate_rr(self):
        """Simulate Round Robin scheduling."""
        print("RR scheduling to be implemented")
        # Placeholder for RR implementation
        pass

    def print_results(self):
        """Calculate and print turnaround and wait times for all jobs."""
        # For now, just print out job details for debugging
        print("Job details:")
        for job in sorted(self.jobs, key=lambda j: j.id):
            print(f"Job {job.id}: Run Time={job.run_time}, Arrival Time={job.arrival_time}")
        
        print("\nScheduling results to be implemented")


def parse_arguments():
    """Parse command-line arguments in the format specified by the assignment."""
    if len(sys.argv) < 2:
        print("Usage: schedSim <job-file.txt> [-p <ALGORITHM>] [-q <QUANTUM>]")
        sys.exit(1)
    
    job_file = sys.argv[1]
    algorithm = ScheduleType.FIFO  # Default algorithm
    quantum = 1  # Default quantum
    
    # Process -p and -q options in any order
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
                # If invalid quantum, use default
                pass
            i += 2
        else:
            # Skip unknown arguments
            i += 1
    
    return job_file, algorithm, quantum


def main():
    """Main function to run the scheduler simulator."""
    # Parse command-line arguments
    job_file, algorithm, quantum = parse_arguments()
    
    # Create simulator instance
    simulator = SchedulerSimulator(job_file, algorithm, quantum)
    
    # Read jobs from file
    simulator.read_job_file()
    
    # Assign job IDs based on arrival time
    simulator.assign_job_ids()
    
    # Print information about the simulation setup
    print(f"Job File: {job_file}")
    print(f"Algorithm: {algorithm.value}")
    if algorithm == ScheduleType.RR:
        print(f"Quantum: {quantum}")
    print()
    
    # For debugging: Skip simulation for now
    # simulator.simulate()
    
    # Print job details without scheduling results
    simulator.print_results()


if __name__ == "__main__":
    main()