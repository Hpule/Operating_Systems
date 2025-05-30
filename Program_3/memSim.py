#!/usr/bin/env python3
import os
import sys
import argparse
from collections import OrderedDict

# Constants
PAGE_SIZE = 256           # Each page is 256 bytes
FRAME_SIZE = 256          # Each frame is 256 bytes
TLB_SIZE = 16             # TLB can store up to 16 entries

class VirtualMemorySimulator:
    def __init__(self, num_frames=256, algorithm="FIFO"):
        # Simulator configuration
        self.num_frames = num_frames            # Total number of frames in physical memory
        self.algorithm = algorithm              # Replacement algorithm to use (FIFO, LRU, OPT)
        self.fifo_counter = 0                   # Counter for FIFO replacement
        self.lru = OrderedDict()                # OrderedDict to track LRU order
        self.opt_future_frames = []             # List of future memory accesses for OPT
        self.opt_add_index = 0                  # Index tracker for OPT algorithm

        # Data structures
        self.tlb = []                           # Translation Lookaside Buffer: stores [page_num, frame_num] entries
        self.page_table = []                    # Page Table: stores [frame_num, valid_bit] entries for each page
        self.physical_memory = []               # Physical Memory: stores [frame_num, page_num, data, age] entries

        # Statistics tracking
        self.stats = {
            'translated_addresses': 0,          # Number of addresses translated
            'page_faults': 0,                   # Number of page faults
            'tlb_hits': 0,                      # Number of TLB hits
            'tlb_misses': 0                     # Number of TLB misses
        }

        self.init_structures()

    def init_structures(self):
        # Initialize page table and physical memory with default values
        self.page_table = [[0, 0] for _ in range(PAGE_SIZE)]  # Frame number and valid bit
        self.physical_memory = [[i, 0, None, 0] for i in range(self.num_frames)]  # Frame ID, Page #, Data, Age
        self.lru.clear()

    def tlb_lookup(self, page_num):
        # Search for page number in the TLB
        for i, entry in enumerate(self.tlb):
            if entry[0] == page_num:
                return i
        return -1

    def page_table_lookup(self, page_num):
        # Look up page number in the page table and check if valid bit is set
        if self.page_table[page_num][1] == 1:
            return self.page_table[page_num][0]  # Return frame number
        return -1

    def future_frames(self, page_num, start_index):
        # Used by OPT algorithm: returns the next future access index of a page
        for future in range(start_index, len(self.opt_future_frames)):
            future_page = self.opt_future_frames[future] // PAGE_SIZE
            if future_page == page_num:
                return future
        return float('inf')  # If never used again

    def remove_from_tlb(self, page_num):
        # Remove an entry from TLB if the given page number exists
        for i in range(len(self.tlb) - 1, -1, -1):
            if self.tlb[i][0] == page_num:
                self.tlb.pop(i)
                return True
        return False

    def add_to_tlb(self, page_num, frame_num):
        # Add a new page-frame mapping to the TLB and remove oldest if TLB is full
        self.tlb.append([page_num, frame_num])
        if len(self.tlb) > TLB_SIZE:
            self.tlb.pop(0)

    def get_page_replacement_frame(self):
        # Determine which frame to replace based on selected algorithm
        if self.algorithm == "FIFO":
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num

        elif self.algorithm == "LRU":
            # If space available, find unused frame
            if len(self.lru) < self.num_frames:
                for frame in range(self.num_frames):
                    if frame not in self.lru:
                        return frame
            # If all used, evict least recently used
            victim_frame, _ = self.lru.popitem(last=False)
            return victim_frame

        elif self.algorithm == "OPT":
            # Check for unused frame first
            for frame in range(self.num_frames):
                if self.physical_memory[frame][2] is None:
                    return frame
            # All frames are full, find the one with farthest future use
            farthest_use = -1
            victim_frame = 0
            for frame in range(self.num_frames):
                page_in_frame = self.physical_memory[frame][1]
                next_use = self.future_frames(page_in_frame, self.opt_add_index + 1)
                if next_use == float('inf'):
                    return frame
                if next_use > farthest_use:
                    farthest_use = next_use
                    victim_frame = frame
            return victim_frame

        else:
            # Default to FIFO if invalid algorithm
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num

    def update_lru_stack(self, frame_num):
        # Update the order of LRU access tracking
        if frame_num in self.lru:
            del self.lru[frame_num]
        self.lru[frame_num] = None

    def simulate(self, filename):
        # Load the backing store file and address file
        try:
            backing_store = open('BACKING_STORE.bin', 'rb')
        except FileNotFoundError:
            print("Error: BACKING_STORE.bin not found")
            sys.exit(1)

        try:
            with open(filename, 'r') as file:
                addresses = [int(line.strip()) for line in file if line.strip()]
                self.opt_future_frames = addresses
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            sys.exit(1)

        for addr_idx, logical_address in enumerate(addresses):
            # For each logical address, determine the physical address and data
            self.opt_add_index = addr_idx
            page_num = logical_address // PAGE_SIZE
            offset = logical_address % PAGE_SIZE
            tlb_index = self.tlb_lookup(page_num)

            if tlb_index >= 0:
                # TLB hit
                frame_num = self.tlb[tlb_index][1]
                self.stats['tlb_hits'] += 1
                self.update_lru_stack(frame_num)
            else:
                # TLB miss
                self.stats['tlb_misses'] += 1
                frame_num = self.page_table_lookup(page_num)

                if frame_num >= 0:
                    # Page table hit
                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    self.add_to_tlb(page_num, frame_num)
                else:
                    # Page fault: page not in physical memory
                    self.stats['page_faults'] += 1
                    frame_num = self.get_page_replacement_frame()

                    if self.physical_memory[frame_num][2] is not None:
                        old_page = self.physical_memory[frame_num][1]
                        self.page_table[old_page][1] = 0
                        self.remove_from_tlb(old_page)

                    backing_store.seek(page_num * PAGE_SIZE)
                    data = backing_store.read(PAGE_SIZE)
                    self.physical_memory[frame_num] = [frame_num, page_num, data, 0]
                    self.page_table[page_num] = [frame_num, 1]

                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    self.add_to_tlb(page_num, frame_num)

            # Retrieve the value at the calculated physical memory location
            value_byte = self.physical_memory[frame_num][2][offset]
            if value_byte > 127:
                value_byte = value_byte - 256

            hex_data = self.physical_memory[frame_num][2].hex().upper()
            print(f"{logical_address}, {value_byte}, {frame_num}, {hex_data}")
            self.stats['translated_addresses'] += 1

        backing_store.close()
        self.print_stats()

    def print_stats(self):
        # Print out final statistics after simulation completes
        print(f"Number of Translated Addresses = {self.stats['translated_addresses']}")
        print(f"Page Faults = {self.stats['page_faults']}")
        print(f"Page Fault Rate = {self.stats['page_faults'] / self.stats['translated_addresses']:.3f}")
        print(f"TLB Hits = {self.stats['tlb_hits']}")
        print(f"TLB Misses = {self.stats['tlb_misses']}")
        print(f"TLB Hit Rate = {self.stats['tlb_hits'] / self.stats['translated_addresses']:.3f}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Virtual Memory Simulator (memSim)')
    parser.add_argument('filename', type=str)         # Address input file
    parser.add_argument('frames', type=int, default=256)  # Number of frames
    parser.add_argument('algorithm', type=str, default='FIFO')  # Page replacement algorithm
    args = parser.parse_args()

    # Validate command line arguments
    if args.frames <= 0 or args.frames > 256:
        print("Error: Number of frames must be between 1 and 256")
        sys.exit(1)
    if args.algorithm not in ['FIFO', 'LRU', 'OPT']:
        print("Error: Algorithm must be one of FIFO, LRU, OPT")
        sys.exit(1)

    # Create and run the simulator
    vm_sim = VirtualMemorySimulator(args.frames, args.algorithm)
    vm_sim.simulate(args.filename)

if __name__ == "__main__":
    main()
