#!/usr/bin/env python3
import os
import sys
import argparse
from collections import deque, OrderedDict

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
        self.lru = OrderedDict()
        
        # Data structures
        self.tlb = []  # [page_num, frame_num]
        self.page_table = []  # [frame_num, valid_bit]
        self.physical_memory = []  # [frame_num, page_num, data]
        
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
        self.physical_memory = [[i, 0, None] for i in range(self.num_frames)]  # [frame_num, page_num, data, age]
        self.lru.clear()
    
    def tlb_lookup(self, page_num):
        for i, entry in enumerate(self.tlb):
            if entry[0] == page_num:
                return i
        return -1
    
    def page_table_lookup(self, page_num):
        if self.page_table[page_num][1] == 1:  # Valid bit is set
            return self.page_table[page_num][0]  # Return frame number
        return -1
    
    def update_lru_stack(self, frame_num):
        if frame_num in self.lru:
            del self.lru[frame_num]
        self.lru[frame_num] = None
        # print(f"DEBUG: Updated LRU - Frame {frame_num} moved to most recent")

    def print_tlb(self, prefix=""):
        if not self.tlb:
            print(f"DEBUG {prefix}: TLB is empty")
        else:
            print(f"DEBUG {prefix}: TLB contents ({len(self.tlb)}/{TLB_SIZE} entries):")
            for i, entry in enumerate(self.tlb):
                print(f"  TLB[{i}]: Page {entry[0]} Frame {entry[1]}")

    def replacement_policy(self):
        if self.algorithm == "FIFO":
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num
        
        elif self.algorithm == "LRU":  # Find Least Recently Used frame
            if (len(self.lru) < self.num_frames):
                for frame in range(self.num_frames):
                    if frame not in self.lru:
                        # print(f"DEBUG: LRU selected unused frame {frame}")
                        return frame
                    
            victim, _ = self.lru.popitem(last=False)
            return victim
        
        elif self.algorithm == "OPT":
            opt_frame = 0                    
            return 
        
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
            # print(f"\n=== PROCESSING ADDRESS: {logical_address} ===")
            page_num = logical_address // PAGE_SIZE
            offset = logical_address % PAGE_SIZE
            tlb_index = self.tlb_lookup(page_num)
            
            if tlb_index >= 0: # TLB hit
                frame_num = self.tlb[tlb_index][1]
                self.stats['tlb_hits'] += 1
                self.update_lru_stack(frame_num)
                # print(f"DEBUG -- TLB HIT: Frame {frame_num}")
                # self.print_tlb("AFTER TLB HIT\n")
            
            else: # TLB miss
                self.stats['tlb_misses'] += 1
                frame_num = self.page_table_lookup(page_num)
                # print(f"DEBUG -- TLB MISS: Frame {frame_num}")
                # self.print_tlb("AFTER TLB MISS\n")
                
                if frame_num >= 0:# Page table hit
                    self.update_lru_stack(frame_num)
                    # print(f"DEBUG -- PT HIT: Frame {frame_num}")
                    # self.print_tlb("AFTER PT HIT\n")

                else: # Page fault - page not in memory
                    # print(f"DEBUG -- PT MISS: Frame: {frame_num}")
                    self.stats['page_faults'] += 1
                    frame_num = self.replacement_policy()
                    
                    # If the frame was in use, invalidate its page table entry
                    old_page = self.physical_memory[frame_num][1]
                    if self.physical_memory[frame_num][2] is not None:
                        self.page_table[old_page][1] = 0  # Clear valid bit
                    
                    backing_store.seek(page_num * PAGE_SIZE)
                    data = backing_store.read(PAGE_SIZE)
                    
                    self.physical_memory[frame_num] = [frame_num, page_num, data, 0]
                    self.page_table[page_num] = [frame_num, 1]  # Set frame number and valid bit
                    # print(f"DEBUG -- UPDATE PT: Page {page_num} -> Frame {frame_num}, Valid = 1")
                    self.update_lru_stack(frame_num)

                # If we miss then add / update the TLB
                self.tlb.append([page_num, frame_num]) # Update TLB
                if (len(self.tlb) > TLB_SIZE) or (len(self.tlb) > self.num_frames):
                    self.tlb.pop(0)  # Remove oldest entry (FIFO for TLB)    

                # self.print_tlb("AFTER TLB UPDATE\n")
                                
            # Convert physical value to readable value
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
    
    if args.frames <= 0 or args.frames > 256:
        print("Error: Number of frames must be between 1 and 256")
        sys.exit(1)
    
    if args.algorithm not in ['FIFO', 'LRU', 'OPT']:
        print("Error: Algorithm must be one of FIFO, LRU, OPT")
        sys.exit(1)
    
    vm_sim = VirtualMemorySimulator(args.frames, args.algorithm)
    vm_sim.simulate(args.filename)

if __name__ == "__main__":
    main()