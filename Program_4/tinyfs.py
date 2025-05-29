from type import Dict, List, Optional 
import time

class TinyFS:
    def __init__(self):
        self.disk = None
        self.open_files: Dict[int, str] = {}
        self.next_fd = 0
        self.superblock = None

    def mkfs(self, filename: str, size: int) -> int:
        pass

    def mount(self, filename: str) -> int:
        pass

    def unmount(self) -> int:
        pass

    def open_file(self, name: str) -> int:
        pass

    def close_file(self, fd: int) -> int:
        pass

    def write_file(self, fd: int, data: bytes) -> int:
        pass

    def read_byte(self, fd: int) -> int:
        pass

    def delete_file(self, fd: int) -> int:
        pass

    def seek(self, fd: int, offset: int) -> int:
        pass

    def rename(self, fd:int, new_name: str) -> int:
        pass

    def read_dir(self) -> List[str]:
        pass

    # Helper Functions 
    def _get_free_block(self) -> int:
        pass
    
    def _set_block_free(self, blocknum: int):
        pass

    def _find_file_index(self, filename: str) -> Optional[tuple]:
        pass