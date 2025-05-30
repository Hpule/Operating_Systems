#!/usr/bin/env python3
"""
libDisk.py - Low-level disk emulation library for TinyFS

This module provides a block-based disk interface that emulates
a physical disk using a regular file. All disk operations work
with fixed-size blocks.
"""

import os
import math
from typing import Optional
from constants import BLOCK_SIZE, END_OF_DISK

class DiskError(Exception):
    """Custom exception for disk operations"""
    pass

class libDisk:
    def __init__(self):
        self.filename: Optional[str] = None
        self.file_handle = None
        self.disk_size: int = 0
        self.is_open: bool = False
    
    # ------ Main functions ------
    # Mandatory Functions - openDisk, readBlock, writeBlock, closeDisk
    
    def openDisk(self, filename: str, nBytes: int) -> int:
        try:
            if nBytes < 0:
                return -1
            
            if 0 < nBytes < BLOCK_SIZE:
                return -1  # Disk must be at least one block
            
            self.filename = filename
            
            if nBytes == 0:
                if not os.path.exists(filename):
                    return -1
                
                self.file_handle = open(filename, 'rb+')
                self.file_handle.seek(0, os.SEEK_END)
                self.disk_size = self.file_handle.tell()
                self.file_handle.seek(0)
                
            else:
                self.disk_size = math.ceil(nBytes / BLOCK_SIZE) * BLOCK_SIZE
                self.file_handle = open(filename, 'wb+')
                
                self.file_handle.seek(self.disk_size - 1)
                self.file_handle.write(b'\x00')
                self.file_handle.seek(0)
                self.file_handle.flush()
            
            self.is_open = True
            return 0
            
        except Exception as e:
            print(f"openDisk error: {e}")
            if self.file_handle:
                self.file_handle.close()
                self.file_handle = None
            return -1
    
    def readBlock(self, bNum: int, block: bytearray) -> int:
        if not self.is_open or not self.file_handle:
            return -1
        
        if bNum < 0:
            return -1
        
        byte_offset = bNum * BLOCK_SIZE
        if byte_offset + BLOCK_SIZE > self.disk_size:
            return END_OF_DISK
        
        try:
            self.file_handle.seek(byte_offset)
            data = self.file_handle.read(BLOCK_SIZE)
            
            if len(data) != BLOCK_SIZE:
                return -1
            
            block[:] = data
            self.file_handle.seek(0)
            return 0
            
        except Exception as e:
            print(f"readBlock error: {e}")
            return -1
    
    def writeBlock(self, bNum: int, block: bytes) -> int:
        if not self.is_open or not self.file_handle:
            return -1
        
        if bNum < 0:
            return -1
        
        if len(block) != BLOCK_SIZE:
            return -1
        
        byte_offset = bNum * BLOCK_SIZE
        if byte_offset + BLOCK_SIZE > self.disk_size:
            return END_OF_DISK
        
        try:
            self.file_handle.seek(byte_offset)
            bytes_written = self.file_handle.write(block)
            
            if bytes_written != BLOCK_SIZE:
                return -1
            
            self.file_handle.flush()
            self.file_handle.seek(0)
            return 0
            
        except Exception as e:
            print(f"writeBlock error: {e}")
            return -1
    
    def closeDisk(self) -> int:
        if not self.is_open or not self.file_handle:
            return -1
        
        try:
            self.file_handle.close()
            self.file_handle = None
            self.is_open = False
            self.disk_size = 0
            self.filename = None
            return 0
            
        except Exception as e:
            print(f"closeDisk error: {e}")
            return -1
    
    # ------ Other Functions ------
    def getDiskSize(self) -> int:
        return self.disk_size if self.is_open else 0
    
    def getTotalBlocks(self) -> int:
        return self.disk_size // BLOCK_SIZE if self.is_open else 0
    
    def isOpen(self) -> bool:
        return self.is_open


_disk_instance = libDisk()

def openDisk(filename: str, nBytes: int) -> int:
    return _disk_instance.openDisk(filename, nBytes)

def readBlock(bNum: int, block: bytearray) -> int:
    return _disk_instance.readBlock(bNum, block)

def writeBlock(bNum: int, block: bytes) -> int:
    return _disk_instance.writeBlock(bNum, block)

def closeDisk() -> int:
    return _disk_instance.closeDisk()