#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser

PAGE_NUM = 0
MEM_FRAM = 1
VALID_BIT = 1
FRAME_SIZE = 256
PAGETB_SIZE = 256

page_table = []  #frame, valid bit ,(index is page number)
tlb = [] #[memory page num, physical memory frame]. size 16
physical_mem = [] #index is frame number,
opt_array = []
input_file = []

frames_given = 256
algorithm = "FIFO"
num_translated_address = 0
frame_num = -1

def tlb_lookup(target):
    for index, entry in enumerate(tlb):
        if entry[0] == target:
            return index
    return -1

def table_init():
    global page_table
    for i in range(PAGETB_SIZE):
        page_table.append([0,0])
    for j in range(frames_given):
        physical_mem.append([0,0,0,0]) #frame num, page num, data, age(LRU)
    for k in range(frames_given):
        opt_array.append(0)

def pgtable_lookup(target):
    global page_table
    if (page_table[target][1]):
        return page_table[target][0]
    return -1

def update_lru(frame_num):
    #print("frame num " , frame_num)
    global physical_mem
    for entry in physical_mem:
        entry[3] += 1

def get_oldest_in_mem_lru():
    max_value = physical_mem[0][3]
    max_index = 0
    for i in range(1, len(physical_mem)):
        if physical_mem[i][3] > max_value:
            max_value = physical_mem[i][3]
            max_index = i
    return max_index


def get_youngest_in_mem_opt():
    global num_translated_address
    opt_array = [0] * frames_given
    frame_to_replace = 0
    result_array = [x // 256 for x in input_file]
    for i in range(frames_given):
        # Calculate the page number by dividing the logical address by the frame size (256)
        for j in range(num_translated_address, len(result_array)):
            if result_array[j] == physical_mem[i][1]:
                opt_array[i] += 1
    for i in range(len(opt_array)):
        if frame_to_replace < opt_array[i]:
            frame_to_replace = opt_array.index(i)
    return frame_to_replace


def page_replacement():
    global page_table
    global frame_num
    frame_num += 1

    if (num_translated_address > frames_given - 1):
        if (algorithm == 'FIFO'):
                ret_value = frame_num%frames_given
        elif (algorithm == 'LRU'):
            ret_value = get_oldest_in_mem_lru()
        elif algorithm == 'OPT':
            ret_value = get_youngest_in_mem_opt()
        #invalidate in page table
        page_table[physical_mem[ret_value][1]][1] = 0
    else:
        ret_value = frame_num
    return ret_value



def virtual_mem_sim (filename):
    global num_translated_address
    global frame_num
    page_faults = 0
    tlb_hit = 0
    tlb_miss = 0

    script_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(script_dir, filename)
    bin = open("BACKING_STORE.bin", "rb")
    table_init()

    try:
        with open(filepath, 'r') as file:
            for line in file:
                input_file.append(int(line.strip()))
        pass
    except FileNotFoundError:
        print("File:", filename, "doesn't exist")
        sys.exit()

    for logical_address in input_file:
        page_num = int(logical_address/FRAME_SIZE)
        tlb_index = tlb_lookup(page_num)
        if (tlb_index >= 0):
            tlb_hit += 1
            #print("tlb hit")
            frame_num = tlb[tlb_index][1]
            physical_mem[frame_num][3] = 0
        else:
            tlb_miss += 1
            #///add to tlb
            #print("tlb miss")
            pg_table_index = pgtable_lookup(page_num)
            if (pg_table_index >= 0):
                #page table hit!
                frame_num = page_table[pg_table_index][0]
                physical_mem[frame_num][3] = 0
                #print("page table hit")
            else:
                page_faults += 1
                #go to disk
                frame_num = page_replacement()
                #print("im going to replace", frame_num)
                bin.seek(FRAME_SIZE*page_num)
                data = bin.read(FRAME_SIZE)
                physical_mem[frame_num] = [frame_num, page_num, data, 0]
                page_table[page_num] = [frame_num, 1]

            tlb.append([page_num, frame_num])
            if (len(tlb) > 16) or (len(tlb) > frames_given):
                tlb.pop(0)

        update_lru(frame_num)

        #print(physical_mem)

        value = physical_mem[frame_num][2][(logical_address % 256)]
        int_value = ord(value)
        # try:
        #     int_value = int(value)
        # except ValueError:
        #     print("ChrispChrosp done goofied a lil")

        if (int_value > 127):
            int_value = int_value - 256

        print("{}, {}, {}, {}".format(logical_address, int_value, frame_num, physical_mem[frame_num][2].encode('hex').upper()))

        num_translated_address += 1


    print("Number of Translated Addresses = {}".format(num_translated_address))
    print("Page Faults = {}".format(page_faults))
    print("Page Fault Rate = {:.3f}".format(page_faults / num_translated_address))
    print("TLB Hits = {}".format(tlb_hit))
    print("TLB Misses = {}".format(tlb_miss))
    print("TLB Hit Rate = {:.3f}".format(tlb_hit / num_translated_address))



def main():
    # readd after doiong the do :)
    global algorithm
    global frames_given

    parser = ArgumentParser()
    parser.add_argument("filename", help="job filename")
    parser.add_argument( "pra", default="FIFO", help="memory algorithm", type=str)
    parser.add_argument("frames", default=1, help="frame size", type=int)
    args = parser.parse_args()

    job_file = args.filename
    frames_given = args.frames
    algorithm = args.pra

    if algorithm != "FIFO" and algorithm != "LRU" and algorithm != "OPT":
        print("Algorithm options: FIFO, LRU, OPT.")
        exit()

    if frames_given < 0:
        print("Frames must be an integer value greater than 0")
        exit()
    if frames_given > 256:
        print("Frames must be an integer value less than 256")
        exit()

    virtual_mem_sim (job_file)



if __name__ == "__main__":
    main()