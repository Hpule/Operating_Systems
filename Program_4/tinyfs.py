from type import Dict, List, Optional 
import time
import tin


class TinyFS:
    def __init__(self):
        self.disk = None
        self.open_files: Dict[int, str] = {}
        self.next_fd = 0
        self.superblock = None

    # ------ Main functions ------
    # Mandatory Functions - tfs (_mkfs, _mount, _unmount, _open, _close, _write, _delete, _readByte, _seek)

    def tfs_mkfs(self, filename: str, size: int) -> int:
        
        pass

    def tfs_mount(self, filename: str) -> int:
        pass

    def tfs_unmount(self) -> int:
        pass

    def tfs_open(self, name: str) -> int:
        pass

    def tfs_close(self, fd: int) -> int:
        pass

    def tfs_write(self, fd: int, data: bytes) -> int:
        pass

    def delete_file(self, fd: int) -> int:
        pass

    def seek(self, fd: int, offset: int) -> int:
        pass

    # ------ Other Functions ------

    def read_byte(self, fd: int) -> int:
        pass

    def rename(self, fd:int, new_name: str) -> int:
        pass

    def read_dir(self) -> List[str]:
        pass

    def _get_free_block(self) -> int:
        pass
    
    def _set_block_free(self, blocknum: int):
        pass

    def _find_file_index(self, filename: str) -> Optional[tuple]:
        pass