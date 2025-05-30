import struct
from dataclasses import dataclass
from typing import Optional
from constants import *

@dataclass
class BlockAttributes:
    block_type: int
    magic_number: int

@dataclass
class SuperBlock:
    attributes: BlockAttributes
    root_inode: int
    free_block_bitmap: bytearray

    def pack() -> bytes:
        pass

    @classmethod
    def unpack(cls, data: bytes):
        pass

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
        pass
    @classmethod
    def unpack(cls, data:bytes):
        pass

@dataclass
class FileExtent:
    attributes: BlockAttributes
    file_pointer: int
    next_data_block: int
    data: bytes
    
    def pack(self) -> bytes:
        pass
    @classmethod
    def unpack(cls, data:bytes):
        pass