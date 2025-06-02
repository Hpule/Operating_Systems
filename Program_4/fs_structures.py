import struct
import constants 
from dataclasses import dataclass
from typing import Optional

@dataclass
class BlockAttributes:
    block_type: int
    magic_number: int
    
    def pack(self) -> bytes:
        return struct.pack('BB', self.block_type, self.magic_number)
    
    @classmethod
    def unpack(cls, data: bytes):
        block_type, magic_number = struct.unpack('BB', data[:2])
        return cls(block_type, magic_number)

@dataclass
class SuperBlock:
    attributes: BlockAttributes
    root_inode: int
    free_block_bitmap: bytearray

    def pack(self) -> bytes:
        # Pack: attributes(2) + padding(2) + root_inode(2) + bitmap(248)
        result = bytearray(constants.BLOCK_SIZE)
        
        # Pack attributes
        attr_data = self.attributes.pack()
        result[0:2] = attr_data
        
        # Pack root inode (with padding)
        struct.pack_into('xxH', result, 2, self.root_inode)
        
        # Pack bitmap
        result[6:6+constants.BITMAP_SIZE] = self.free_block_bitmap[:constants.BITMAP_SIZE]
        
        return bytes(result)

    @classmethod
    def unpack(cls, data: bytes):
        attributes = BlockAttributes.unpack(data[0:2])
        root_inode = struct.unpack('H', data[4:6])[0]
        bitmap = bytearray(data[6:6+constants.BITMAP_SIZE])
        
        return cls(attributes, root_inode, bitmap)

@dataclass
class INode:
    attributes: BlockAttributes
    file_size: int
    file_name: str
    time_created: str
    last_accessed: str
    last_modified: str
    data_block_start: int
    next_inode_block: int
    
    def pack(self) -> bytes:
        result = bytearray(constants.BLOCK_SIZE)
        offset = 0
        
        # Pack attributes
        attr_data = self.attributes.pack()
        result[offset:offset+2] = attr_data
        offset += 4  # Include padding
        
        # Pack file size
        struct.pack_into('H', result, offset, self.file_size)
        offset += 2
        
        # Pack filename (9 bytes including null terminator)
        name_bytes = self.file_name.encode('utf-8')[:8] + b'\x00'
        result[offset:offset+9] = name_bytes
        offset += 9
        
        # Pack timestamps (simplified - just use first 20 chars)
        for timestamp in [self.time_created, self.last_accessed, self.last_modified]:
            ts_bytes = timestamp.encode('utf-8')[:20].ljust(20, b'\x00')
            result[offset:offset+20] = ts_bytes
            offset += 20
        
        # Pack data block start and next inode
        struct.pack_into('II', result, offset, self.data_block_start, self.next_inode_block)
        
        return bytes(result)
    
    @classmethod
    def unpack(cls, data: bytes):
        offset = 0
        attributes = BlockAttributes.unpack(data[offset:offset+2])
        offset += 4
        
        file_size = struct.unpack('H', data[offset:offset+2])[0]
        offset += 2
        
        file_name = data[offset:offset+9].rstrip(b'\x00').decode('utf-8')
        offset += 9
        
        # Unpack timestamps
        timestamps = []
        for _ in range(3):
            ts = data[offset:offset+20].rstrip(b'\x00').decode('utf-8')
            timestamps.append(ts)
            offset += 20
        
        data_block_start, next_inode_block = struct.unpack('II', data[offset:offset+8])
        
        return cls(attributes, file_size, file_name, timestamps[0], 
                  timestamps[1], timestamps[2], data_block_start, next_inode_block)

@dataclass
class FileExtent:
    attributes: BlockAttributes
    file_pointer: int
    next_data_block: int
    data: bytes
    
    def pack(self) -> bytes:
        result = bytearray(constants.BLOCK_SIZE)
        
        # Pack attributes
        attr_data = self.attributes.pack()
        result[0:2] = attr_data
        
        # Pack file pointer and next block
        struct.pack_into('BxI', result, 2, self.file_pointer, self.next_data_block)
        
        # Pack data
        data_size = constants.BLOCK_SIZE - 8  # Remaining space after headers
        data_to_pack = self.data[:data_size].ljust(data_size, b'\x00')
        result[8:] = data_to_pack
        
        return bytes(result)
    
    @classmethod
    def unpack(cls, data: bytes):
        attributes = BlockAttributes.unpack(data[0:2])
        file_pointer, next_data_block = struct.unpack('BxI', data[2:8])
        file_data = data[8:]
        
        return cls(attributes, file_pointer, next_data_block, file_data)