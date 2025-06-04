from tinyfs import TinyFS
from constants import DEFAULT_DISK_SIZE
import os
import sys

def test_basic_operations():
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

def test_file_write_read():
    print("\n" + "=" * 50)
    print("TEST 2: File Write/Read Operations")
    print("=" * 50)
    
    fs = TinyFS()
    
    # Setup filesystem
    fs.tfs_mkfs("test_write_read.dsk", DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_write_read.dsk")
    
    # Test file creation and writing
    fd = fs.tfs_open("hello.txt")
    test_data = b"Hello, TinyFS World!"
    
    if fd >= 0:
        bytes_written = fs.tfs_write(fd, test_data)
        print(f"  write file: {'Success' if bytes_written > 0 else 'Failed'} ({bytes_written} bytes)")
        
        # Test reading back
        fs.tfs_seek(fd, 0)  # Reset to beginning
        read_data = b""
        
        # Read byte by byte
        for i in range(len(test_data)):
            byte_val = fs.tfs_readByte(fd)
            if byte_val >= 0:
                read_data += bytes([byte_val])
            else:
                break
        
        print(f"  read file: {'Success' if read_data == test_data else 'Failed'}")
        print(f"  Written: {test_data}")
        print(f"  Read:    {read_data}")
        
        fs.tfs_close(fd)
    else:
        print("  Failed to open file for writing")
    
    fs.tfs_unmount()
    return True

def test_multiple_files():
    print("\n" + "=" * 50)
    print("TEST 3: Multiple Files")
    print("=" * 50)
    
    fs = TinyFS()
    fs.tfs_mkfs("test_multi.dsk", DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_multi.dsk")
    
    files_data = {
        "file1.txt": b"This is the first file content.",
        "file2.txt": b"Second file with different content!",
        "file3.txt": b"Third file for testing multiple files."
    }
    
    file_descriptors = {}
    
    # Create and write multiple files
    for filename, data in files_data.items():
        fd = fs.tfs_open(filename)
        if fd >= 0:
            bytes_written = fs.tfs_write(fd, data)
            file_descriptors[filename] = fd
            print(f"  Created {filename}: {bytes_written} bytes written")
        else:
            print(f"  Failed to create {filename}")
    
    # Test directory listing
    try:
        file_list = fs.tfs_readdir()
        print(f"  Directory listing: {file_list}")
        
        # Check if all files are listed
        for filename in files_data.keys():
            if filename in file_list:
                print(f"  {filename} found in directory")
            else:
                print(f"  {filename} missing from directory")
    except:
        print("  Directory listing failed")
    
    # Close all files
    for filename, fd in file_descriptors.items():
        result = fs.tfs_close(fd)
        print(f"  Closed {filename}: {'Success' if result == 0 else 'Failed'}")
    
    fs.tfs_unmount()
    return True

def test_file_deletion():
    print("\n" + "=" * 50)
    print("TEST 5: File Deletion")
    print("=" * 50)
    
    fs = TinyFS()
    fs.tfs_mkfs("test_delete.dsk", DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_delete.dsk")
    
    # Create test files
    test_files = ["delete1.txt", "delete2.txt", "keep.txt"]
    
    for filename in test_files:
        fd = fs.tfs_open(filename)
        if fd >= 0:
            test_data = f"Content of {filename}".encode()
            fs.tfs_write(fd, test_data)
            print(f"  Created {filename}")
        else:
            print(f"  Failed to create {filename}")
    
    # List files before deletion
    try:
        files_before = fs.tfs_readdir()
        print(f"  Files before deletion: {files_before}")
    except:
        print("  Could not list files before deletion")
    
    # Delete some files
    fd_to_delete = fs.tfs_open("delete1.txt")
    if fd_to_delete >= 0:
        delete_result = fs.tfs_delete(fd_to_delete)
        print(f"  Delete delete1.txt: {'Success' if delete_result == 0 else 'Failed'}")
    
    fd_to_delete2 = fs.tfs_open("delete2.txt")
    if fd_to_delete2 >= 0:
        delete_result = fs.tfs_delete(fd_to_delete2)
        print(f"  Delete delete2.txt: {'Success' if delete_result == 0 else 'Failed'}")
    
    # List files after deletion
    try:
        files_after = fs.tfs_readdir()
        print(f"  Files after deletion: {files_after}")
        
        # Verify deletions
        if "delete1.txt" not in files_after and "delete2.txt" not in files_after:
            print("  Deleted files successfully removed from directory")
        else:
            print("  Deleted files still appear in directory")
        
        if "keep.txt" in files_after:
            print("  Non-deleted file still exists")
        else:
            print("  Non-deleted file was accidentally removed")
            
    except:
        print("  Could not list files after deletion")
    
    fs.tfs_unmount()
    return True

def cleanup_test_files():
    print("\nCleaning up test files...")

    test_files = [
        "test_fs.dsk", "test_write_read.dsk", "test_multi.dsk",
        "test_delete.dsk"
    ]
    
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

if __name__ == "__main__":
    test_basic_operations()
    test_file_write_read()
    # test_multiple_files()
    # test_file_deletion()

    cleanup_test_files()