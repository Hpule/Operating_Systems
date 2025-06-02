from tinyfs import TinyFS
import constants

def test_basic_operations():
    """Test basic file system operations"""
    print("=== Testing Basic Operations ===")
    
    fs = TinyFS()
    
    # Test mkfs
    print("\n1. Creating filesystem...")
    result = fs.tfs_mkfs("test_comprehensive.dsk", constants.DEFAULT_DISK_SIZE)
    print(f"   mkfs: {'✓ Success' if result == 0 else '✗ Failed'}")
    
    # Test mount
    print("\n2. Mounting filesystem...")
    result = fs.tfs_mount("test_comprehensive.dsk")
    print(f"   mount: {'✓ Success' if result == 0 else '✗ Failed'}")
    
    if result != 0:
        print("Cannot proceed without successful mount")
        return
    
    # Test multiple file operations
    print("\n3. Testing file operations...")
    
    # Open multiple files
    fd1 = fs.tfs_open("file1.txt")
    fd2 = fs.tfs_open("document.dat")
    fd3 = fs.tfs_open("test")
    
    print(f"   Open file1.txt: {'✓ Success' if fd1 >= 0 else '✗ Failed'} (fd={fd1})")
    print(f"   Open document.dat: {'✓ Success' if fd2 >= 0 else '✗ Failed'} (fd={fd2})")
    print(f"   Open test: {'✓ Success' if fd3 >= 0 else '✗ Failed'} (fd={fd3})")
    
    # Test opening same file twice (should return same fd)
    fd1_again = fs.tfs_open("file1.txt")
    print(f"   Reopen file1.txt: {'✓ Same FD' if fd1_again == fd1 else '✗ Different FD'} (fd={fd1_again})")
    
    # Test write operations
    print("\n4. Testing write operations...")
    test_data = b"Hello, TinyFS! This is test data."
    
    if fd1 >= 0:
        bytes_written = fs.tfs_write(fd1, test_data)
        print(f"   Write to file1.txt: {'✓ Success' if bytes_written > 0 else '✗ Failed'} ({bytes_written} bytes)")
    
    if fd2 >= 0:
        large_data = b"X" * 1000  # Test larger write
        bytes_written = fs.tfs_write(fd2, large_data)
        print(f"   Write large data: {'✓ Success' if bytes_written > 0 else '✗ Failed'} ({bytes_written} bytes)")
    
    # Test read operations
    print("\n5. Testing read operations...")
    
    if fd1 >= 0:
        byte_value = fs.tfs_readByte(fd1)
        print(f"   Read byte from file1.txt: {'✓ Success' if byte_value >= 0 else '✗ Failed'} (value={byte_value})")
    
    # Test seek operations
    print("\n6. Testing seek operations...")
    
    if fd1 >= 0:
        seek_result = fs.tfs_seek(fd1, 5)
        print(f"   Seek in file1.txt: {'✓ Success' if seek_result == 0 else '✗ Failed'}")
    
    # Test close operations
    print("\n7. Testing close operations...")
    
    if fd1 >= 0:
        close_result = fs.tfs_close(fd1)
        print(f"   Close file1.txt: {'✓ Success' if close_result == 0 else '✗ Failed'}")
    
    if fd2 >= 0:
        close_result = fs.tfs_close(fd2)
        print(f"   Close document.dat: {'✓ Success' if close_result == 0 else '✗ Failed'}")
    
    # Test delete operations
    print("\n8. Testing delete operations...")
    
    if fd3 >= 0:
        delete_result = fs.tfs_delete(fd3)
        print(f"   Delete test file: {'✓ Success' if delete_result == 0 else '✗ Failed'}")
    
    # Test operations on closed files (should fail)
    print("\n9. Testing operations on closed files...")
    
    write_result = fs.tfs_write(fd1, b"test")  # fd1 was closed
    print(f"   Write to closed file: {'✓ Correctly failed' if write_result == -1 else '✗ Should have failed'}")
    
    read_result = fs.tfs_readByte(fd1)  # fd1 was closed
    print(f"   Read from closed file: {'✓ Correctly failed' if read_result == -1 else '✗ Should have failed'}")
    
    # Test unmount
    print("\n10. Unmounting filesystem...")
    result = fs.tfs_unmount()
    print(f"    unmount: {'✓ Success' if result == 0 else '✗ Failed'}")

def test_persistence():
    """Test that data persists across mount/unmount cycles"""
    print("\n=== Testing Persistence ===")
    
    fs1 = TinyFS()
    
    # Create and write to a file
    print("\n1. Creating file system and writing data...")
    fs1.tfs_mkfs("test_persist.dsk", constants.DEFAULT_DISK_SIZE)
    fs1.tfs_mount("test_persist.dsk")
    
    fd = fs1.tfs_open("persist.txt")
    if fd >= 0:
        fs1.tfs_write(fd, b"Persistent data test")
        fs1.tfs_close(fd)
    
    fs1.tfs_unmount()
    print("   Created file and unmounted")
    
    # Remount and try to read
    print("\n2. Remounting and checking data...")
    fs2 = TinyFS()
    result = fs2.tfs_mount("test_persist.dsk")
    
    if result == 0:
        fd = fs2.tfs_open("persist.txt")
        if fd >= 0:
            # Try to read the data back
            byte_val = fs2.tfs_readByte(fd)
            print(f"   Read from persistent file: {'✓ Success' if byte_val >= 0 else '✗ Failed'}")
            fs2.tfs_close(fd)
        else:
            print("   ✗ Failed to open persistent file")
    else:
        print("   ✗ Failed to remount filesystem")
    
    fs2.tfs_unmount()

def test_error_conditions():
    """Test error handling"""
    print("\n=== Testing Error Conditions ===")
    
    fs = TinyFS()
    
    # Test operations without mounting
    print("\n1. Operations without mounting...")
    fd = fs.tfs_open("test.txt")
    print(f"   Open without mount: {'✓ Correctly failed' if fd == -1 else '✗ Should have failed'}")
    
    # Test invalid file descriptors
    print("\n2. Invalid file descriptors...")
    fs.tfs_mkfs("test_error.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_error.dsk")
    
    write_result = fs.tfs_write(999, b"test")  # Invalid FD
    print(f"   Write with invalid FD: {'✓ Correctly failed' if write_result == -1 else '✗ Should have failed'}")
    
    read_result = fs.tfs_readByte(999)  # Invalid FD
    print(f"   Read with invalid FD: {'✓ Correctly failed' if read_result == -1 else '✗ Should have failed'}")
    
    fs.tfs_unmount()

def main():
    """Run all tests"""
    print("🚀 TinyFS Comprehensive Test Suite")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_persistence()
        test_error_conditions()
        
        print("\n" + "=" * 50)
        print("Test suite completed!")
        print("\nNote: Some operations may show as 'Failed' because")
        print("they are not fully implemented yet. This is expected.")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()