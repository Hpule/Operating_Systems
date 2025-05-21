#!/usr/bin/env python3
import os
import sys
import argparse

# Constants
PAGE_SIZE = 256
FRAME_SIZE = 256
TLB_SIZE = 16

class VirtualMemorySimulator:
    def __init__(self, num_frames=256, algorithm="FIFO"):
        # Configuration
        self.num_frames = num_frames
        self.algorithm = algorithm
        self.fifo_counter = 0
        
        # Data structures
        self.tlb = []  # [page_num, frame_num]
        self.page_table = []  # [frame_num, valid_bit]
        self.physical_memory = []  # [frame_num, page_num, data, age]
        
        # Statistics
        self.stats = {
            'translated_addresses': 0,
            'page_faults': 0,
            'tlb_hits': 0,
            'tlb_misses': 0
        }
        
        self.init_structures()
    
    def init_structures(self):
        self.page_table = [[0, 0] for _ in range(PAGE_SIZE)]  # [frame_num, valid_bit]
        self.physical_memory = [[i, 0, None, 0] for i in range(self.num_frames)]  # [frame_num, page_num, data, age]
    
    def tlb_lookup(self, page_num):
        for i, entry in enumerate(self.tlb):
            if entry[0] == page_num:
                return i
        return -1
    
    def page_table_lookup(self, page_num):
        if self.page_table[page_num][1] == 1:  # Valid bit is set
            return self.page_table[page_num][0]  # Return frame number
        return -1
    
    # def update_lru_ages(self):
    #     # Increment age for all frames
    #     for frame in self.physical_memory:
    #         if frame[2] is not None:  # Only update if frame has data
    #             frame[3] += 1
    
    def get_page_replacement_frame(self):
        if self.algorithm == "FIFO":
            # Simple FIFO: use the next frame in sequence
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num
        
        # elif self.algorithm == "LRU":
        #     # Find the least recently used frame
        #     max_age = -1
        #     lru_frame = 0
            
        #     for i in range(self.num_frames):
        #         if self.physical_memory[i][3] > max_age:
        #             max_age = self.physical_memory[i][3]
        #             lru_frame = i
            
        #     return lru_frame
        
        else:  # Default or OPT algorithm (not fully implemented)
            # Default to FIFO
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num
    
    def simulate(self, filename):
        try:
            backing_store = open('BACKING_STORE.bin', 'rb')
        except FileNotFoundError:
            print("Error: BACKING_STORE.bin not found")
            sys.exit(1)
        
        try:
            with open(filename, 'r') as file:
                addresses = [int(line.strip()) for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            sys.exit(1)
        
        for logical_address in addresses:
            page_num = logical_address // PAGE_SIZE
            offset = logical_address % PAGE_SIZE
            tlb_index = self.tlb_lookup(page_num)
            
            if tlb_index >= 0: # TLB hit
                frame_num = self.tlb[tlb_index][1]
                self.stats['tlb_hits'] += 1
                self.physical_memory[frame_num][3] = 0 # Reset age for LRU
            
            else: # TLB miss
                self.stats['tlb_misses'] += 1
                frame_num = self.page_table_lookup(page_num)
                
                if frame_num >= 0:# Page table hit
                    self.physical_memory[frame_num][3] = 0  # Reset age for LRU
                
                else: # Page fault - page not in memory

                    self.stats['page_faults'] += 1
                    frame_num = self.get_page_replacement_frame()
                    
                    # If the frame was in use, invalidate its page table entry
                    old_page = self.physical_memory[frame_num][1]
                    if self.physical_memory[frame_num][2] is not None:
                        self.page_table[old_page][1] = 0  # Clear valid bit
                    
                    backing_store.seek(page_num * PAGE_SIZE)
                    data = backing_store.read(PAGE_SIZE)
                    
                    self.physical_memory[frame_num] = [frame_num, page_num, data, 0]
                    self.page_table[page_num] = [frame_num, 1]  # Set frame number and valid bit
                
                self.tlb.append([page_num, frame_num]) # Update TLB
                if (len(self.tlb) > TLB_SIZE) or (len(self.tlb) > frame_num):
                    self.tlb.pop(0)  # Remove oldest entry (FIFO for TLB)          
            # self.update_lru_ages() # Update LRU ages
            
            value_byte = self.physical_memory[frame_num][2][offset]
            if value_byte > 127:
                value_byte = value_byte - 256
            
            hex_data = self.physical_memory[frame_num][2].hex().upper()
            # print(f"{logical_address}, {value_byte}, {frame_num}, {hex_data}")
            # Check Indivudal Results
            print(f"{logical_address}, ") 
            print(f"{value_byte}, ") 
            print(f"{frame_num}, ") 
            print(f"{hex_data}")            
            self.stats['translated_addresses'] += 1
        
        backing_store.close()
        self.print_stats()
    
    def print_stats(self):
        print(f"Number of Translated Addresses = {self.stats['translated_addresses']}")
        print(f"Page Faults = {self.stats['page_faults']}")
        print(f"Page Fault Rate = {self.stats['page_faults'] / self.stats['translated_addresses']:.3f}")
        print(f"TLB Hits = {self.stats['tlb_hits']}")
        print(f"TLB Misses = {self.stats['tlb_misses']}")
        print(f"TLB Hit Rate = {self.stats['tlb_hits'] / self.stats['translated_addresses']:.3f}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Virtual Memory Simulator (memSim)')
    parser.add_argument('filename',     type=str)
    parser.add_argument('frames',       type=int,   default=256)
    parser.add_argument('algorithm',    type=str,   default='FIFO', )
    
    args = parser.parse_args()
    
    # Validate inputs
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