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
        self.opt_future_frames = [] # addresses when I read the file
        self.opt_add_index = 0
        
        # Data structures
        self.tlb = []  # [page_num, frame_num]
        self.page_table = []  # [frame_num, valid_bit]
        self.physical_memory = []  # [frame_num, page_num, data]
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

    def future_frames(self, page_num, start_index):
        for future in range(start_index, len(self.opt_future_frames)):
            future_page = self.opt_future_frames[future] // PAGE_SIZE
            if future_page == page_num:
                return future
        return float('inf')  # Never used again
    
    def remove_from_tlb(self, page_num):
        for i in range(len(self.tlb) - 1, -1, -1):
            if self.tlb[i][0] == page_num:
                removed = self.tlb.pop(i)
                return True
        return False

    def add_to_tlb(self, page_num, frame_num, reason=""):
        self.tlb.append([page_num, frame_num])
        if len(self.tlb) > TLB_SIZE:
            removed = self.tlb.pop(0)

    def replacement_policy(self):
        if self.algorithm == "FIFO":
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num
        
        elif self.algorithm == "LRU":  # Find Least Recently Used frame
            if (len(self.lru) < self.num_frames):
                for frame in range(self.num_frames):
                    if frame not in self.lru:
                        return frame
                    
            twink, _ = self.lru.popitem(last=False)
            return twink
        
        elif self.algorithm == "OPT":            
            for frame in range(self.num_frames): # Empty Frames?
                if self.physical_memory[frame][2] is None:
                    return frame
            
            power_bottom = -1 # Frames full, find twinks ;)
            twink = 0
            
            for frame in range(self.num_frames):
                page_in_frame = self.physical_memory[frame][1]
                next_use = self.future_frames(page_in_frame, self.opt_add_index + 1)
                if next_use == float('inf'):
                    return frame
                
                if next_use > power_bottom:
                    power_bottom = next_use
                    twink = frame
            
            return twink
        
        else:  # Default or OPT algorithm (not fully implemented)
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
                self.opt_future_frames = addresses
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            sys.exit(1)
        
        for addr_idx, logical_address in enumerate(addresses):
            self.opt_add_index = addr_idx
            page_num = logical_address // PAGE_SIZE
            offset = logical_address % PAGE_SIZE
            tlb_index = self.tlb_lookup(page_num)
            
            if tlb_index >= 0: # TLB hit
                frame_num = self.tlb[tlb_index][1]
                self.stats['tlb_hits'] += 1
                self.update_lru_stack(frame_num)
            
            else: # TLB miss
                self.stats['tlb_misses'] += 1
                frame_num = self.page_table_lookup(page_num)
                
                if frame_num >= 0:# Page table hit
                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    self.tlb.append([page_num, frame_num])
                    
                    if len(self.tlb) > TLB_SIZE:
                        _ = self.tlb.pop(0)

                else:  # Page fault
                    self.stats['page_faults'] += 1    
                    frame_num = self.replacement_policy()
                    
                    if self.physical_memory[frame_num][2] is not None:
                        old_page = self.physical_memory[frame_num][1]
                        self.page_table[old_page][1] = 0   # Clear page table entry
                        self.remove_from_tlb(old_page)     # Remove from TLB

                    backing_store.seek(page_num * PAGE_SIZE) # Load new page
                    data = backing_store.read(PAGE_SIZE)
                    self.physical_memory[frame_num] = [frame_num, page_num, data] # Update physical memory and page table
                    self.page_table[page_num] = [frame_num, 1]
                    
                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    
                    self.add_to_tlb(page_num, frame_num, "(page fault)")
                                            
            value_byte = self.physical_memory[frame_num][2][offset]
            if value_byte > 128:
                value_byte = value_byte - 256

            hex_data = self.physical_memory[frame_num][2].hex().upper()
            print(f"{logical_address}, {value_byte}, {frame_num}, {hex_data}")
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

    def print_tlb(self, prefix=""):
        if not self.tlb:
            print(f"DEBUG {prefix}: TLB is empty")
        else:
            print(f"DEBUG {prefix}: TLB contents ({len(self.tlb)}/{TLB_SIZE} entries):")
            for i, entry in enumerate(self.tlb):
                print(f"  TLB[{i}]: Page {entry[0]} Frame {entry[1]}")            

def main():
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