from typing import Dict, List, Optional
import time
import struct
import os
import libDisk
import constants
from fs_structures import SuperBlock, INode, FileExtent, BlockAttributes

class TinyFS:
    def __init__(self):
        self.disk = libDisk.libDisk()
        self.is_mounted = False
        self.mounted_filename = None

        # File tracking - always initialized, no hasattr needed!
        self.open_files: Dict[int, str] = {}  
        self.next_fd = 0  

        # File system structure
        self.memory_inode_table = []
        self.free_table = []
        
        # Constants
        self.MAGIC_NUMBER = constants.MAGIC_NUMBER
        self.ROOT_DIRECTORY_INODE = 2
        self.MAX_INODE_BLOCKS = 13
        self.MAX_DATA_BLOCKS = 25

    def tfs_mkfs(self, filename: str, size: int) -> int:
        print(f"Making file system: {filename}")

        try:
            if len(filename[:-4]) > int(constants.MAX_DISKNAME_LENGTH):
                print(f"mkfs erorr, filename too big! {len(filename)}")
                return -1
            else:
                    
                # openDisk returns file descriptor (≥0) on success, -1 on failure
                result = self.disk.openDisk(filename, size)
                if result < 0:  # Changed from != 0 to < 0
                    print("Failed to create disk")
                    return -1

                # Create simple superblock
                block_to_write = bytearray([constants.MAGIC_NUMBER])  # 0x5A
                block_to_write.append(self.ROOT_DIRECTORY_INODE)      # 0x02
                
                # Pad to full block size
                while len(block_to_write) < constants.BLOCK_SIZE:
                    block_to_write.append(0x00)
                
                # Write superblock to block 0
                result = self.disk.writeBlock(0, bytes(block_to_write))
                if result != 0:  # writeBlock returns 0 on success
                    print("Failed to write superblock")
                    self.disk.closeDisk()
                    return -1
                
                # Close disk
                self.disk.closeDisk()
                print(f"Filesystem {filename} created successfully")
                return 0
            
        except Exception as e:
            print(f"mkfs error: {e}")
            if self.disk.isOpen():
                self.disk.closeDisk()
            return -1

    def tfs_mount(self, filename: str) -> int:
        print("attempting to mount")
        try:
            if self.is_mounted:
                print("Already mounted")
                return -1
            
            # openDisk returns file descriptor (≥0) on success, -1 on failure
            result = self.disk.openDisk(filename, 0)  # 0 = open existing
            if result < 0:  # Changed from != 0 to < 0
                print("Failed to open disk")
                return -1
            
            # Read block 0 and check magic number
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(0, buffer)
            if result != 0:  # readBlock returns 0 on success
                print("Failed to read superblock")
                self.disk.closeDisk()
                return -1
            
            # Check magic number (first byte)
            if buffer[0] == constants.MAGIC_NUMBER:  # 0x5A
                self.is_mounted = True
                self.mounted_filename = filename
                print(f"Successfully mounted {filename}")
                return 1
            else:
                print(f"Bad magic number: expected {hex(constants.MAGIC_NUMBER)}, got {hex(buffer[0])}")
                self.disk.closeDisk()
                return -1
                
        except Exception as e:
            print(f"Mount error: {e}")
            return -1
    
    def tfs_unmount(self) -> int:
        print("unmounting")
        try:
            if not self.is_mounted:
                print("Not mounted")
                return -1
            
            # Close the disk
            result = self.disk.closeDisk()
            if result == 0:
                # Reset filesystem state
                self.is_mounted = False
                self.mounted_filename = None
                self.open_files.clear()
                self.next_fd = 0
                print("Successfully unmounted")
                return 1
            else:
                print("Failed to close disk")
                return -1
                
        except Exception as e:
            print(f"Unmount error: {e}")
            return -1

    # Stub implementations for the other methods to prevent errors
    def tfs_open(self, name: str) -> int:
        """Open a file for reading/writing"""
        print(f"Opening file: '{name}'")
        
        # Clean validation - no hasattr needed!
        if not self.is_mounted:
            print("Error: Filesystem not mounted")
            return -1
        
        if len(name[:-4]) > constants.MAX_FILENAME_LENGTH:
            print(f"Error: Filename too long (max {constants.MAX_FILENAME_LENGTH} chars)")
            return -1
        
        # Check if file is already open
        for fd, filename in self.open_files.items():
            if filename == name:
                print(f"File '{name}' already open with fd {fd}")
                return fd
        
        # Assign new file descriptor
        fd = self.next_fd
        self.open_files[fd] = name
        self.next_fd += 1
        
        print(f"File '{name}' opened with fd {fd}")
        return fd
    
    def tfs_close(self, fd: int) -> int:
        """Close an open file"""
        print(f"Closing file descriptor: {fd}")
        
        # Clean validation
        if not self.is_mounted:
            print("Error: Filesystem not mounted")
            return -1
        
        if fd not in self.open_files:
            print(f"Error: File descriptor {fd} not open")
            return -1
        
        # Remove from tracking
        filename = self.open_files[fd]
        del self.open_files[fd]
        
        print(f"Closed file '{filename}' (fd {fd})")
        return 0


    def tfs_write(self, fd: int, data: bytes) -> int:
        """Write data to a file"""
        print(f"Writing {len(data)} bytes to fd {fd}")
        
        # Clean validation
        if not self.is_mounted:
            print("Error: Filesystem not mounted")
            return -1
        
        if fd not in self.open_files:
            print(f"Error: File descriptor {fd} not open")
            return -1
        
        filename = self.open_files[fd]
        print(f"Writing to file: '{filename}'")
        
        # For now, just return success (stub implementation)
        # TODO: Implement actual disk writing
        return len(data)

    def tfs_delete(self, fd: int) -> int:
        """Delete a file"""
        print(f"Deleting file with fd: {fd}")
        
        # Clean validation
        if not self.is_mounted:
            print("Error: Filesystem not mounted")
            return -1
        
        if fd not in self.open_files:
            print(f"Error: File descriptor {fd} not open")
            return -1
        
        filename = self.open_files[fd]
        print(f"Deleting file: '{filename}'")
        
        # Remove from tracking
        del self.open_files[fd]
        
        # TODO: Implement actual disk deletion
        print(f"File '{filename}' deleted successfully")
        return 0

    def tfs_readByte(self, fd: int) -> int:
        if not hasattr(self, 'open_files') or fd not in self.open_files:
            return -1
        return -1  # No data

    def tfs_seek(self, fd: int, offset: int) -> int:
        if not hasattr(self, 'open_files') or fd not in self.open_files:
            return -1
        return 0

    # Helper methods you might need
    def _init_inode_table(self):
        """Initialize inode table - reference code style but as class method"""
        self.memory_inode_table = []
        for i in range(self.ROOT_DIRECTORY_INODE + 1, self.MAX_INODE_BLOCKS + self.ROOT_DIRECTORY_INODE + 1):
            self.memory_inode_table.append([
                i,                          # inode number
                -1,                         # filename (use -1 to check empty like reference)
                i - 1,                      # pointer to inode block
                0,                          # rw
                [-1, -1],                   # timestamps [create, update]
                0,                          # cursor
                0,                          # total blocks
                -1, -1, -1, -1, -1         # data extent pointers
            ])
        
        # Initialize free table for data blocks
        self.free_table = []
        for i in range(15, self.MAX_DATA_BLOCKS + 15):  # Data blocks start at 15
            self.free_table.append([i, -1, -1])  # [index, valid(-1=free), inode]

    def _get_timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def tfs_stat(self, filename: str) -> Optional[dict]:
        """Get file information"""
        if not self.is_mounted:
            return None
            
        inode_block = self._find_file_inode(filename)
        if inode_block == -1:
            return None
        
        buffer = bytearray(constants.BLOCK_SIZE)
        self.disk.readBlock(inode_block, buffer)
        inode = INode.unpack(bytes(buffer))
        
        return {
            'name': inode.file_name.rstrip('\x00'),
            'size': inode.file_size,
            'created': inode.time_created,
            'modified': inode.last_modified,
            'accessed': inode.last_accessed
        }

    def _find_file_inode(self, filename: str) -> int:
        """Helper method for finding file inodes"""
        # Placeholder implementation
        return -1

if __name__ == "__main__":
    print("TinyFS module loaded. Run tinyfsTest.py to test functions.")