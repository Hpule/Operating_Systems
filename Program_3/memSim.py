#!/usr/bin/env python3
import sys
import argparse
from collections import deque
from enum import Enum

PAGE_NUM  = 0
VAL_BIT   = 1
MEM_FRAME = 1
PAGETABLE_SIZE = 256
FRAME_SIZE = 256 

tlb = []
page_table = []
disk = []
output_array = []
input_array = []
frames = -1
algorithm = "FIFO"

stats = {
    'tlb_hits': 0,
    'tlb_miss': 0,
    'page_faults': 0,
    'translated_addresses': 0
}

def tlb_check(target):
    for index, entry in enumerate(tlb):
        if entry[0] == target:
            return index
    return -1


def page_table_check(target):
    global page_table
    if page_table[target][1]:
        return page_table[target][0]
    return -1


def virtualMemory(file):    
    init()
    file_info = readFile(file)
    disk_bin = open('BACKING_STORE.bin', 'rb')

    frame_num = -1

    for address in file_info:
        page_num = int(address/FRAME_SIZE)
        tlb_hit = tlb_check(page_num)
        if tlb_hit > 0:
            print("TLB Hit")
            stats['tlb_hits'] += 1
            frame_num = tlb[tlb_hit][1]
            disk[frame_num][3] = 0
        else: 
            print("TLB Miss") # Look in Page Table
            stats['tlb_miss'] += 1
            page_table_hit = page_table_check(page_num)
            if page_table_hit >= 0:  # We do not care about TLB hits only misses
                print("Page Table Hit")
                frame_num = page_table[page_table_hit][1]
                disk[frame_num][3] = 0
            else: 
                print("Page Table Miss") # Look in disk
                stats['page_faults'] += 1

                disk_bin.seek(FRAME_SIZE*page_num)
                data = disk_bin.read(FRAME_SIZE)

                print(f"data: {data}") # a whole lot of ascii! (Looks ugly)--> convert!!!!
            


        stats['translated_addresses'] += 1
        print(f"{address}, 0, {frame_num}")
    return


def parse():
    parser = argparse.ArgumentParser(description='Virtual Memory Simulator (memSim)')
    parser.add_argument('filename'  , type=str, help='File name' )
    parser.add_argument('frames'    , type=int, help='Frame size'                ,default='1' )
    parser.add_argument('algorithm' , type=str, help='Algorithm - FIFO, LRU, OPT', default='FIFO')
    return parser.parse_args()


def main():
    terminal_info = parse()
    filename = terminal_info.filename 
    frames = terminal_info.frames
    algorithm = terminal_info.algorithm

    # Check all Parsed agruments 
    print(frames)
    if (frames <= 1) or (frames > FRAME_SIZE): 
        print("Frames must be greater than 0 and less than 256")
        exit(1)
    if algorithm != 'FIFO' and algorithm != 'LRU' and algorithm != 'OPT':
        print("Algorithm options: FIFO, LRU, OPT.")
        exit(1)

    virtualMemory(filename)
    print_stats()
    return 


def init():
    global page_table
    for page in range(PAGETABLE_SIZE):
        page_table.append([0,0])    
    for frames in range(FRAME_SIZE):
        disk.append([0,0,0,0]) #frame num, page num, data, age(LRU)
    for frames in range(FRAME_SIZE):
        output_array.append(0)
    

def readFile(filename):
    memory_addresses = []
    try:
        with open(filename, 'r') as file:
            for address in file:
                address = address.strip()
                if address:
                    address = int(address)
                    memory_addresses.append(address)
    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found")
        sys.exit(1)
    return memory_addresses


def readBin():
    try:
        with open('BACKING_STORE.bin', 'rb') as file:  # Fixed syntax
            return file
    except FileNotFoundError:
        print(f"Error: Backing store file 'BACKING_STORE.bin' not found")
        sys.exit(1)


def print_stats():
    print(f"Number of Translated Addresses = {stats['translated_addresses']}")
    print(f"Page Faults = {stats['page_faults']}")
    print(f"Page Fault Rate = {stats['page_faults'] / stats['translated_addresses']:.3f}")
    print(f"TLB Hits = {stats['tlb_hits']}")
    print(f"TLB Misses = {stats['translated_addresses'] - stats['tlb_hits']}")
    print(f"TLB Hit Rate = {stats['tlb_hits'] / stats['translated_addresses']:.3f}")


if __name__ == "__main__":
    main()