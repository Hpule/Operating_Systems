from tinyfs import TinyFS
from constants import DEFAULT_DISK_SIZE

def test_basic_operations():
    """Test basic TinyFS operations"""
    fs = TinyFS()
    
    print("Testing TinyFS...")
    
    # Test mkfs
    result = fs.tfs_mkfs("test_fs.dsk", DEFAULT_DISK_SIZE)
    print(f"mkfs: {'Success' if result == 0 else 'Failed'}")
    
    # Test mount
    result = fs.tfs_mount("test_fs.dsk")
    print(f"mount: {'Success' if result == 0 else 'Failed'}")
    
    # Test open file
    fd = fs.tfs_open("testfile.txt")
    print(f"open file: {'Success' if fd >= 0 else 'Failed'} (fd={fd})")
    
    # Test close file
    if fd >= 0:
        result = fs.tfs_close(fd)
        print(f"close file: {'Success' if result == 0 else 'Failed'}")
    
    # Test unmount
    result = fs.tfs_unmount()
    print(f"unmount: {'Success' if result == 0 else 'Failed'}")

if __name__ == "__main__":
    test_basic_operations()