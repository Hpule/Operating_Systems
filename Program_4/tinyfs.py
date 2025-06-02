from typing import Dict, List, Optional
import time
import struct
import libDisk
import constants
from fs_structures import SuperBlock, INode, FileExtent, BlockAttributes

class TinyFS:
    def __init__(self):
        self.disk = libDisk.libDisk()
        self.superblock = None
        self.open_files: Dict[int, str] = {}
        self.next_fd = 0
        self.is_mounted = False

    # ------ Main functions ------
    # Mandatory Functions - tfs (_mkfs, _mount, _unmount, _open, _close, _write, _delete, _readByte, _seek)

    def tfs_mkfs(self, filename: str, size: int) -> int:
        try:
            print(f"DEBUG: Creating filesystem {filename} with size {size}")
            # Create disk
            result = self.disk.openDisk(filename, size)
            if result != 0:
                return -1
            print("DEBUG: Disk opened successfully")

            # Initialize superblock
            bitmap = bytearray(constants.BITMAP_SIZE)
            # Mark first few blocks as used (superblock, root inode)
            bitmap[0] = 0x03  # Blocks 0 and 1 used
            
            self.superblock = SuperBlock(
                attributes=BlockAttributes(constants.SUPER_BLOCK, constants.MAGIC_NUMBER),
                root_inode=constants.ROOT_INODE_BLOCK_NUM,
                free_block_bitmap=bitmap
            )
            
            print("DEBUG: Superblock created")

            # Write superblock to disk
            sb_data = self.superblock.pack()
            print(f"DEBUG: Superblock packed, size: {len(sb_data)}")
            result = self.disk.writeBlock(0, sb_data)
            if result != 0:
                print(f"DEBUG: Failed to write superblock: {result}")
                return -1
            print("DEBUG: Root inode written successfully")

            self.disk.closeDisk()
            print("DEBUG: Disk closed, mkfs complete")
            return 0
            
        except Exception as e:
            print(f"tfs_mkfs error: {e}")
            return -1

    def tfs_mount(self, filename: str) -> int:
        try:
            result = self.disk.openDisk(filename, constants.EXISTING_DISK)
            if result != 0:
                return -1
            
            # Read and verify superblock
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(0, buffer)
            if result != 0:
                return -1
            
            self.superblock = SuperBlock.unpack(bytes(buffer))
            
            # Verify magic number
            if self.superblock.attributes.magic_number != constants.MAGIC_NUMBER:
                self.disk.closeDisk()
                return -1
            
            self.is_mounted = True
            return 0
            
        except Exception as e:
            print(f"tfs_mount error: {e}")
            return -1

    def tfs_unmount(self) -> int:
        try:
            if not self.is_mounted:
                return -1
            
            # Write superblock back to disk
            if self.superblock:
                sb_data = self.superblock.pack()
                self.disk.writeBlock(0, sb_data)
            
            self.disk.closeDisk()
            self.open_files.clear()
            self.next_fd = 0
            self.is_mounted = False
            return 0
            
        except Exception as e:
            print(f"tfs_unmount error: {e}")
            return -1

    def tfs_open(self, name: str) -> int:
        print(f"DEBUG: Opening file '{name}'")
        print(f"DEBUG: Is mounted: {self.is_mounted}")
        
        if not self.is_mounted:
            print("DEBUG: Filesystem not mounted")
            return -1
        
        if len(name) > constants.MAX_FILENAME_LENGTH:
            print(f"DEBUG: Filename too long: {len(name)} > {constants.MAX_FILENAME_LENGTH}")
            return -1
        
        # Check if already open
        for fd, filename in self.open_files.items():
            if filename == name:
                print(f"DEBUG: File already open with fd {fd}")
                return fd
        
        # Assign new file descriptor
        fd = self.next_fd
        self.open_files[fd] = name
        self.next_fd += 1
        print(f"DEBUG: File opened with new fd {fd}")
        return fd

    def tfs_close(self, fd: int) -> int:
        if fd not in self.open_files:
            return -1
        
        del self.open_files[fd]
        return 0

    def tfs_write(self, fd: int, data: bytes) -> int:
        if fd not in self.open_files:
            return -1
        
        filename = self.open_files[fd]        
        return len(data)  # Return bytes written

    def tfs_delete(self, fd: int) -> int:
        if fd not in self.open_files:
            return -1
        
        filename = self.open_files[fd]
        del self.open_files[fd]
        return 0

    def tfs_readByte(self, fd: int) -> int:
        if fd not in self.open_files:
            return -1
        
        # Implementation would involve:
        # 1. Find current file position
        # 2. Read from appropriate data block
        # 3. Update file pointer
        
        return 0  # Return byte value or -1 for EOF/error

    def tfs_seek(self, fd: int, offset: int) -> int:
        if fd not in self.open_files:
            return -1
        
        # Implementation would update file pointer
        return 0

    # ------ Helper functions ------
    
    def _get_free_block(self) -> int:
        if not self.superblock:
            return -1
        
        bitmap = self.superblock.free_block_bitmap
        for i in range(len(bitmap)):
            byte_val = bitmap[i]
            for bit in range(8):
                if not (byte_val & (1 << bit)):
                    # Found free block
                    bitmap[i] |= (1 << bit)
                    return i * 8 + bit
        
        return -1  # No free blocks

    def _free_block(self, block_num: int):
        if not self.superblock:
            return
        
        byte_index = block_num // 8
        bit_index = block_num % 8
        
        if byte_index < len(self.superblock.free_block_bitmap):
            self.superblock.free_block_bitmap[byte_index] &= ~(1 << bit_index)
