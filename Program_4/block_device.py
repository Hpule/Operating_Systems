#!/usr/bin/env python3

import os
import math
from constants import BLOCK_SIZE

class BlockDevice:
    
    def __init__(self, filename=str, bytes_size= 0):
        self.filename = filename
        self.file_handle = None
        self.disk_size = 0
        
        if bytes_size < 0:
            raise ValueError("Size cannot be negative")
        
        if bytes_size == 0:
            self._open_existing_disk()
        else:
            self._create_new_disk(bytes_size)
    
    def _open_existing_disk(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Disk file {self.filename} does not exist")
        
        try:
            self.file_handle = open(self.filename, 'rb+')
            self.file_handle.seek(0, os.SEEK_END)
            self.disk_size = self.file_handle.tell()
            self.file_handle.seek(0)
        except IOError as e:
            raise IOError(f"Failed to open disk file {self.filename}: {e}")
    
    def _create_new_disk(self, bytes_size: int):
        if bytes_size < BLOCK_SIZE:
            raise ValueError(f"Disk size must be at least {BLOCK_SIZE} bytes")
        
        self.disk_size = math.ceil(bytes_size / BLOCK_SIZE) * BLOCK_SIZE
        
        try:
            self.file_handle = open(self.filename, 'wb+')
            self.file_handle.seek(self.disk_size - 1)
            self.file_handle.write(b'\x00')
            self.file_handle.seek(0)
        except IOError as e:
            raise IOError(f"Failed to create disk file {self.filename}: {e}")
    
    def read_block(self, block_num):
        if not self.file_handle:
            raise IOError("Disk is not open")
        
        if block_num < 0:
            raise ValueError("Block number cannot be negative")
        
        byte_offset = block_num * BLOCK_SIZE
        
        if byte_offset + BLOCK_SIZE > self.disk_size:
            raise ValueError(f"Block {block_num} is beyond disk size")
        
        try:
            self.file_handle.seek(byte_offset)
            data = self.file_handle.read(BLOCK_SIZE)
            
            if len(data) < BLOCK_SIZE:
                data += b'\x00' * (BLOCK_SIZE - len(data))
            
            return data
        except IOError as e:
            raise IOError(f"Failed to read block {block_num}: {e}")
    
    def write_block(self, block_num, data):
        if not self.file_handle:
            raise IOError("Disk is not open")
        
        if block_num < 0:
            raise ValueError("Block number cannot be negative")
        
        if len(data) != BLOCK_SIZE:
            raise ValueError(f"Data must be exactly {BLOCK_SIZE} bytes, got {len(data)}")
        
        byte_offset = block_num * BLOCK_SIZE
        
        if byte_offset + BLOCK_SIZE > self.disk_size:
            raise ValueError(f"Block {block_num} is beyond disk size")
        
        try:
            self.file_handle.seek(byte_offset)
            bytes_written = self.file_handle.write(data)
            self.file_handle.flush()
            
            if bytes_written != BLOCK_SIZE:
                raise IOError(f"Only wrote {bytes_written} of {BLOCK_SIZE} bytes")
                
        except IOError as e:
            raise IOError(f"Failed to write block {block_num}: {e}")
    
    def close(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def get_disk_size(self):
        return self.disk_size
    
    def get_total_blocks(self):
        return self.disk_size // BLOCK_SIZE
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        self.close()


def main():
    print("Testing BlockDevice...")
    
    try: 
        with BlockDevice("test_disk.bin", 1024) as disk:
            print(f"Created disk with {disk.get_total_blocks()} blocks")
            
            test_data = b"Hello TinyFS!" + b"\x00" * (256 - 13)
            disk.write_block(0, test_data)
            print("Wrote test data to block 0")
            
            read_data = disk.read_block(0)
            print(f"Read back: {read_data[:13].decode()}")
            
            try:
                disk.read_block(100)
            except ValueError as e:
                print(f"Expected error for invalid block: {e}")
        
        with BlockDevice("test_disk.bin", 0) as disk:
            print("Successfully opened existing disk")
            read_data = disk.read_block(0)
            print(f"Data still there: {read_data[:13].decode()}")
        
        os.remove("test_disk.bin")
        print("Test completed successfully!")
            
    except Exception as error:
        print(f"Test failed: {error}")
        if os.path.exists("test_disk.bin"):
            os.remove("test_disk.bin")


if __name__ == "__main__":
    main()