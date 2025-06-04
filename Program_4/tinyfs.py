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
            result = self.disk.openDisk(filename, size)
            if result != 0:
                return -1

            # Initialize bitmap - mark blocks 0, 1, 2 as used
            bitmap = bytearray(constants.BITMAP_SIZE)
            bitmap[0] = 0x07  # Blocks 0, 1, 2 used
            
            self.superblock = SuperBlock(
                attributes=BlockAttributes(constants.SUPER_BLOCK, constants.MAGIC_NUMBER),
                root_inode=constants.ROOT_INODE_BLOCK_NUM,
                free_block_bitmap=bitmap
            )
            
            # Write superblock
            sb_data = self.superblock.pack()
            result = self.disk.writeBlock(0, sb_data)
            if result != 0:
                return -1

            # Create root inode at block 2
            root_inode = INode(
                attributes=BlockAttributes(constants.INODE, constants.MAGIC_NUMBER),
                file_size=0,
                file_name="",  # Empty name for root
                time_created=time.strftime("%Y-%m-%d %H:%M:%S"),
                last_accessed=time.strftime("%Y-%m-%d %H:%M:%S"),
                last_modified=time.strftime("%Y-%m-%d %H:%M:%S"),
                data_block_start=0,
                next_inode_block=-1  # Important: -1, not 0
            )
            root_data = root_inode.pack()
            result = self.disk.writeBlock(constants.ROOT_INODE_BLOCK_NUM, root_data)
            
            self.disk.closeDisk()
            return 0 if result == 0 else -1
            
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
        
        try:
            # Find if file already exists
            inode_block_num = self._find_file_inode(filename)
            
            if inode_block_num == -1:
                # Create new file
                inode_block_num = self._create_new_file(filename, len(data))
                if inode_block_num == -1:
                    return -1
            else:
                # File exists, update it
                self._update_existing_file(inode_block_num, data)
            
            # Write the actual data
            data_start_block = self._get_data_start_block(inode_block_num)
            self._write_file_data(data, data_start_block)
            
            return len(data)
            
        except Exception as e:
            print(f"tfs_write error: {e}")
            return -1


    def tfs_delete(self, fd: int) -> int:
        if fd not in self.open_files:
            return -1
        
        filename = self.open_files[fd]
        del self.open_files[fd]
        return 0

    def tfs_readByte(self, fd: int) -> int:
        print(f"DEBUG: tfs_readByte called with fd={fd}")
        if fd not in self.open_files:
            return -1
        filename = self.open_files[fd]
        print(f"DEBUG: Reading from file '{filename}'")
        try:
            print(f"DEBUG: Looking for inode for file '{filename}'")
            # Find file inode
            inode_block = self._find_file_inode(filename)
            if inode_block == -1:
                print("DEBUG: File inode not found")
                return -1
            
            # Get current file position and read byte
            print(f"DEBUG: Getting current read position for inode block {inode_block}")
            current_block, position = self._get_current_read_position(inode_block)
            print(f"DEBUG: Current read position - block: {current_block}, position: {position}")
            if current_block == -1:
                return -1  # EOF or error
            
            # Read the block
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(current_block, buffer)
            if result != 0:
                return -1
            
            file_extent = FileExtent.unpack(bytes(buffer))
            
            # Check if we can read from current position
            if position < len(file_extent.data):
                byte_value = file_extent.data[position]
                
                # Update file pointer
                file_extent.file_pointer = position + 1
                updated_data = file_extent.pack()
                self.disk.writeBlock(current_block, updated_data)
                
                return byte_value
            
            return -1  # EOF
        except Exception as e:
            print(f"tfs_readByte error: {e}")
            return -1


    def tfs_seek(self, fd: int, offset: int) -> int:
        if fd not in self.open_files:
            return -1

        # filename = self.open_files[fd]

        # try:
        #     inode_block - self.find        

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


    def _find_file_inode(self, filename: str) -> int:
        print(f"DEBUG - _find_file_inode: searching for '{filename}'")
        current_inode_block = constants.ROOT_INODE_BLOCK_NUM
        print(f"DEBUG - _find_file_inode:S tarting search from root inode block {current_inode_block}")
        inode_count = 0

        while current_inode_block != -1:
            print(f"DEBUG - _find_file_inode: Checking inode block {current_inode_block}")
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(current_inode_block, buffer)
            print(f"DEBUG - _find_file_inode: Read inode block result: {result}")
            if result != 0:
                print(f"DEBUG - _find_file_inode: Failed to read inode block {current_inode_block}")
                return -1
            
            try:
                inode = INode.unpack(bytes(buffer))
                inode_filename = inode.file_name.rstrip('\x00')
                print(f"DEBUG - _find_file_inode: Inode {inode_count}: filename='{inode_filename}', next_block={inode.next_inode_block}")

                if inode_filename == filename:
                    print(f"DEBUG - _find_file_inode: Found matching filename at block {current_inode_block}")
                    return current_inode_block
                
                current_inode_block = inode.next_inode_block
                inode_count += 1

                if inode_count > 10:  # Safety check
                    print("DEBUG: Too many inodes, breaking to prevent infinite loop")
                    break
            
            except Exception as error:
                print(f"DEBUG: Error unpacking inode: {error}")
                return -1
            
        print(f"DEBUG - _find_file_inode: File '{filename}' not found in inode chain")
        return -1
    

    def _get_current_read_position(self, inode_block: int) -> tuple:
        # Get inode to find data start
        buffer = bytearray(constants.BLOCK_SIZE)
        self.disk.readBlock(inode_block, buffer)
        inode = INode.unpack(bytes(buffer))
        
        current_block = inode.data_block_start
        if current_block == 0:
            return -1, -1
        
        # Find current block with file pointer
        while current_block != 0:
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(current_block, buffer)
            if result != 0:
                return -1, -1
            
            file_extent = FileExtent.unpack(bytes(buffer))
            
            # Check if this block has the current position
            if file_extent.file_pointer < len(file_extent.data):
                return current_block, file_extent.file_pointer
            
            current_block = file_extent.next_data_block
        
        return -1, -1  # EOF
    
    def _create_new_file(self, filename: str, file_size: int) -> int:
        """Create a new file inode"""
        new_inode_block = self._get_free_block()
        if new_inode_block == -1:
            return -1
        
        data_start_block = self._get_free_block()
        if data_start_block == -1:
            self._free_block(new_inode_block)
            return -1
        
        # Create inode
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        new_inode = INode(
            attributes=BlockAttributes(constants.INODE, constants.MAGIC_NUMBER),
            file_size=file_size,
            file_name=filename,
            time_created=current_time,
            last_accessed=current_time,
            last_modified=current_time,
            data_block_start=data_start_block,
            next_inode_block=-1
        )
        
        # Link to previous inode chain
        self._link_inode_to_chain(new_inode_block)
        
        # Write new inode
        inode_data = new_inode.pack()
        result = self.disk.writeBlock(new_inode_block, inode_data)
        if result != 0:
            return -1
        
        return new_inode_block
    
    def _link_inode_to_chain(self, new_inode_block: int):
        current_block = constants.ROOT_INODE_BLOCK_NUM
        
        while True:
            buffer = bytearray(constants.BLOCK_SIZE)
            self.disk.readBlock(current_block, buffer)
            inode = INode.unpack(bytes(buffer))
            
            if inode.next_inode_block == -1:
                # Found end of chain
                inode.next_inode_block = new_inode_block
                updated_data = inode.pack()
                self.disk.writeBlock(current_block, updated_data)
                break
            
            current_block = inode.next_inode_block


    def _update_existing_file(self, inode_block: int, data: bytes):
        """Update an existing file's metadata"""
        buffer = bytearray(constants.BLOCK_SIZE)
        self.disk.readBlock(inode_block, buffer)
        inode = INode.unpack(bytes(buffer))
        
        # Update metadata
        inode.last_modified = time.strftime("%Y-%m-%d %H:%M:%S")
        inode.file_size = len(data)
        
        # Write back
        updated_data = inode.pack()
        self.disk.writeBlock(inode_block, updated_data)

    def _get_data_start_block(self, inode_block: int) -> int:
        """Get the starting data block for a file"""
        buffer = bytearray(constants.BLOCK_SIZE)
        self.disk.readBlock(inode_block, buffer)
        inode = INode.unpack(bytes(buffer))
        return inode.data_block_start

    def _write_file_data(self, data: bytes, start_block: int):
        """Write file data across multiple blocks if needed"""
        remaining_data = data
        current_block = start_block
        data_per_block = constants.BLOCK_SIZE - 8  # Account for headers
        
        while remaining_data:
            chunk_size = min(len(remaining_data), data_per_block)
            chunk = remaining_data[:chunk_size]
            remaining_data = remaining_data[chunk_size:]
            
            # Determine next block
            next_block = 0
            if remaining_data:
                next_block = self._get_free_block()
            
            # Create file extent
            file_extent = FileExtent(
                attributes=BlockAttributes(constants.FILE_EXTENT, constants.MAGIC_NUMBER),
                file_pointer=0,
                next_data_block=next_block,
                data=chunk.ljust(data_per_block, b'\x00')
            )
            
            # Write block
            extent_data = file_extent.pack()
            self.disk.writeBlock(current_block, extent_data)
            
            current_block = next_block

    def tfs_readdir(self) -> List[str]:
        """List all files in the filesystem"""
        files = []
        current_inode_block = constants.ROOT_INODE_BLOCK_NUM
        
        while current_inode_block != -1:
            buffer = bytearray(constants.BLOCK_SIZE)
            result = self.disk.readBlock(current_inode_block, buffer)
            if result != 0:
                break
            
            try:
                inode = INode.unpack(bytes(buffer))
                filename = inode.file_name.rstrip('\x00')
                if filename:  # Not empty (root has empty name)
                    files.append(filename)
                current_inode_block = inode.next_inode_block
            except:
                break
        
        return files

    def tfs_stat(self, filename: str) -> Optional[dict]:
        """Get file information"""
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
    