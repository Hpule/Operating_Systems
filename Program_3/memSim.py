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
                # print(f"DEBUG -- Removed evicted page from TLB: {removed}")
                return True
        return False

    def add_to_tlb(self, page_num, frame_num, reason=""):
        # print(f"DEBUG -- Adding to TLB {reason}: Page {page_num} -> Frame {frame_num}")
        self.tlb.append([page_num, frame_num])
        
        if len(self.tlb) > TLB_SIZE:
            removed = self.tlb.pop(0)
            # print(f"DEBUG -- Removed TLB entry (TLB full): {removed}")

    def replacement_policy(self):
        if self.algorithm == "FIFO":
            frame_num = self.fifo_counter
            self.fifo_counter = (self.fifo_counter + 1) % self.num_frames
            return frame_num
        
        elif self.algorithm == "LRU":  # Find Least Recently Used frame
            if (len(self.lru) < self.num_frames):
                for frame in range(self.num_frames):
                    if frame not in self.lru:
                        # print(f"DEBUG -- LRU: Selected unused frame {frame}")
                        return frame
                    
            victim_frame, _ = self.lru.popitem(last=False)
            return victim_frame
        
        elif self.algorithm == "OPT":
            # print(f"DEBUG -- OPT: Replacement needed at index {self.opt_add_index}")
            
            # First check if any frames are empty
            for frame in range(self.num_frames):
                if self.physical_memory[frame][2] is None:
                    print(f"DEBUG -- OPT: Selected unused frame {frame}")
                    return frame
            
            # All frames are full, find optimal victim
            farthest_use = -1
            victim_frame = 0
            
            # print(f"DEBUG -- OPT: All {self.num_frames} frames full, analyzing future usage:")
            
            for frame in range(self.num_frames):
                page_in_frame = self.physical_memory[frame][1]
                next_use = self.future_frames(page_in_frame, self.opt_add_index + 1)
                
                # print(f"DEBUG -- OPT: Frame {frame} has page {page_in_frame}, next use: {next_use}")
                
                # If this page is never used again, it's optimal to replace
                if next_use == float('inf'):
                    # print(f"DEBUG -- OPT: Selected frame {frame} (page {page_in_frame} never used again)")
                    return frame
                
                # Track the page that will be used farthest in the future
                if next_use > farthest_use:
                    farthest_use = next_use
                    victim_frame = frame
            
            # print(f"DEBUG -- OPT: Selected frame {victim_frame} (farthest future use at index {farthest_use})")
            return victim_frame
        
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
                self.opt_future_frames = addresses
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            sys.exit(1)
        
        for addr_idx, logical_address in enumerate(addresses):
            # print(f"\n=== ADDRESS {addr_idx + 1}: {logical_address} (Index {addr_idx}) ===")
            self.opt_add_index = addr_idx
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
                    # print(f"DEBUG -- PT HIT: Using frame {frame_num}")
                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    
                    # CRITICAL FIX: Add to TLB on page table hit too
                    # print(f"DEBUG -- Adding to TLB (PT hit): Page {page_num} -> Frame {frame_num}")
                    self.tlb.append([page_num, frame_num])
                    
                    if len(self.tlb) > TLB_SIZE:
                        removed = self.tlb.pop(0)
                        # print(f"DEBUG -- Removed TLB entry: {removed}")

                else:  # Page fault
                    # print(f"DEBUG -- PAGE FAULT: Loading page {page_num}")
                    # self.stats['page_faults'] += 1
                    
                    # Get frame to use
                    frame_num = self.replacement_policy()
                    # print(f"DEBUG -- Using frame {frame_num}")
                    
                    # If frame was in use, clean up
                    if self.physical_memory[frame_num][2] is not None:
                        old_page = self.physical_memory[frame_num][1]
                        # print(f"DEBUG -- Evicting page {old_page} from frame {frame_num}")
                        
                        # Clear page table entry
                        self.page_table[old_page][1] = 0
                        
                        # CRITICAL: Remove evicted page from TLB
                        self.remove_from_tlb(old_page)
                    
                    # Load new page
                    backing_store.seek(page_num * PAGE_SIZE)
                    data = backing_store.read(PAGE_SIZE)
                    
                    # Update physical memory and page table
                    self.physical_memory[frame_num] = [frame_num, page_num, data]
                    self.page_table[page_num] = [frame_num, 1]
                    # print(f"DEBUG -- Loaded page {page_num} into frame {frame_num}")
                    
                    if self.algorithm == "LRU":
                        self.update_lru_stack(frame_num)
                    
                    # Add to TLB
                    self.add_to_tlb(page_num, frame_num, "(page fault)")
            
            # self.print_tlb("CURRENT TLB")
                                
            # Convert physical value to readable value
            value_byte = self.physical_memory[frame_num][2][offset]
            if value_byte > 127:
                value_byte = value_byte - 256
            
            hex_data = self.physical_memory[frame_num][2].hex().upper()
            print(f"{logical_address}, {value_byte}, {frame_num}, {hex_data}")
            # Check Indivudal Results
            # print(f"{logical_address}, ") 
            # print(f"{value_byte}, ") 
            # print(f"{frame_num}, ") 
            # print(f"{hex_data}")            
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