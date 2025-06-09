#!/usr/bin/env python3
# llibDisk.py
import os
import errno
import constants
from typing import Optional

class DiskError(Exception):
    """Custom exception for disk operations"""
    pass


INODE_TABLE = []

class libDisk:
    def __init__(self):
        self.fd: Optional[int] = None
        self.filename: Optional[str] = None
        self.is_open: bool = False
        self.file_handle = None
        self.disk_size: int = 0
    
    # ------ Main functions ------
    # Mandatory Functions - openDisk, readBlock, writeBlock, closeDisk
    
    def openDisk(self, filename: str, nBytes: int) -> int:
        try:
            if os.path.exists(filename):
                if nBytes > 0:
                    # Open existing file for resize/overwrite
                    self.fd = os.open(filename, os.O_RDWR)
                    with open(filename, 'r+b') as file:
                        zero_bytes = bytearray([0x00] * nBytes)
                        file.write(zero_bytes)
                    self.disk_size = nBytes
                else:
                    # Open existing file without modification
                    self.fd = os.open(filename, os.O_RDWR)
                    file_stats = os.fstat(self.fd)
                    self.disk_size = file_stats.st_size
                    print("Disk opened, nothing overwritten")
            else:
                # Create new file
                if nBytes == 0:
                    print("Cannot open non-existent file with nBytes=0")
                    return -1
                
                self.fd = os.open(filename, os.O_RDWR | os.O_CREAT, 0o644)
                with open(filename, 'w+b') as file:
                    zero_bytes = bytearray([0x00] * nBytes)
                    file.write(zero_bytes)
                self.disk_size = nBytes
            
            self.is_open = True
            return self.fd
            
        except Exception as e:
            print(f"Error opening disk: {e}")
            if self.fd is not None:
                try:
                    os.close(self.fd)
                except:
                    pass
                self.fd = None
            return -1
    
    def readBlock(self, bNum: int, block: bytearray) -> int:
        if not self.is_open or self.fd is None:
            print("Disk not open")
            return -1
        if bNum < 0:
            print("Invalid block number")
            return -1
        
        try:
            byte_offset = bNum * constants.BLOCK_SIZE
            if byte_offset + constants.BLOCK_SIZE > self.disk_size:
                print(f"Read beyond disk: offset {byte_offset}, disk size {self.disk_size}")
                return -1
            
            os.lseek(self.fd, byte_offset, os.SEEK_SET)
            data = os.read(self.fd, constants.BLOCK_SIZE)

            if len(data) != constants.BLOCK_SIZE:
                print(f"Read {len(data)} bytes, expected {constants.BLOCK_SIZE}")
                return -1
                        
            block[:] = data
            return 0

        except Exception as e:
            if e.errno == errno.EBADF:
                print("Bad file descriptor")
            else:
                print(f"Error reading disk: {e}")
            return -1
    
    def writeBlock(self, bNum: int, block: bytes) -> int:
        if not self.is_open or self.fd is None:
            print("Disk not open")
            return -1
        
        if bNum < 0:
            print("Invalid block number")
            return -1
        
        try:
            # Check bounds
            byte_offset = bNum * constants.BLOCK_SIZE
            if byte_offset + constants.BLOCK_SIZE > self.disk_size:
                print(f"Write beyond disk: offset {byte_offset}, disk size {self.disk_size}")
                return -1
            
            # Prepare data - take exactly BLOCK_SIZE bytes
            if isinstance(block, (bytes, bytearray)):
                write_data = block[:constants.BLOCK_SIZE]
            elif isinstance(block, list):
                write_data = bytes(block[:constants.BLOCK_SIZE])
            else:
                write_data = str(block)[:constants.BLOCK_SIZE].encode()
            
            # Pad if necessary
            if len(write_data) < constants.BLOCK_SIZE:
                write_data += b'\x00' * (constants.BLOCK_SIZE - len(write_data))
            
            # Seek and write
            os.lseek(self.fd, byte_offset, os.SEEK_SET)
            bytes_written = os.write(self.fd, write_data)
            
            if bytes_written != constants.BLOCK_SIZE:
                print(f"Wrote {bytes_written} bytes, expected {constants.BLOCK_SIZE}")
                return -1
            
            return 0
            
        except OSError as e:
            if e.errno == errno.EBADF:
                print("Bad file descriptor")
            else:
                print(f"Error writing disk: {e}")
            return -1
    
    def closeDisk(self) -> int:
        if not self.is_open or self.fd is None:
            return -1
        
        try:
            os.close(self.fd)
            self.fd = None
            self.is_open = False
            self.disk_size = 0
            self.filename = None
            return 0
            
        except OSError as e:
            print(f"Error closing disk: {e}")
            return -1
    
    # ------ Other Functions ------
    def getDiskSize(self) -> int:
        return self.disk_size if self.is_open else 0
    
    def getTotalBlocks(self) -> int:
        return self.disk_size // constants.BLOCK_SIZE if self.is_open else 0
    
    def isOpen(self) -> bool:
        return self.is_open
    
    def getFilename(self) -> Optional[str]:
        return self.filename if self.is_open else None

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close disk"""
        if self.is_open:
            self.closeDisk()


_disk_instance = libDisk()

def openDisk(filename: str, nBytes: int) -> int:
    return _disk_instance.openDisk(filename, nBytes)

def readBlock(bNum: int, block: bytearray) -> int:
    return _disk_instance.readBlock(bNum, block)

def writeBlock(bNum: int, block: bytes) -> int:
    return _disk_instance.writeBlock(bNum, block)

def closeDisk() -> int:
    return _disk_instance.closeDisk()