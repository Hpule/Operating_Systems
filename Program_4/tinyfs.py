from type import Dict, List, Optional 
import time
import tin


class TinyFS:
    def __init__(self):
        self.disk = None
        self.superblock = None
        self.open_files: Dict[int, str] = {}
        self.next_fd = 0

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

    def tfs_delete(self, fd: int) -> int:
        pass

    def tfs_readByte(self, fd: int) -> int:
        pass    

    def tfs_seek(self, fd: int, offset: int) -> int:
        pass

    # ------ Other Functions ------
    def tfs_rename(self, fd:int, new_name: str) -> int:
        pass

    def tfs_readdir() -> int:
        pass

    def tfs_stat(self) -> int:
        pass