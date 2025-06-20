# tinyfsTests.py
#!/usr/bin/env python3
"""
Extended TinyFS Test Suite
Tests for mount/unmount and file operations
"""
import os
import sys
from tinyfs import TinyFS
import constants

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_v.dsk", "test_i.dsk", "test_e.dsk", 
        "test_c.dsk", "test_fs1.dsk", "test_fs2.dsk",
        "test_fo.dsk", "test_w.dsk", "test_d.dsk", 
        "test_r.dsk", "test_s.dsk", "test_rs.dsk"
    ]
    
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

# ==================== MOUNT/UNMOUNT TESTS ====================

def test_mkfs():
    """Test filesystem creation"""
    print("=== Testing tfs_mkfs ===")
    
    fs = TinyFS()
    
    # Test 1: Create a filesystem
    result = fs.tfs_mkfs("test_v.dsk", constants.DEFAULT_DISK_SIZE)
    print(f"mkfs result: {result}")
    assert result == 0, f"mkfs should return 0 on success, got {result}"
    
    # Test 2: Verify file exists and has correct size
    assert os.path.exists("test_v.dsk"), "Disk file should exist"
    file_size = os.path.getsize("test_v.dsk")
    assert file_size == constants.DEFAULT_DISK_SIZE, f"File size should be {constants.DEFAULT_DISK_SIZE}, got {file_size}"
    
    print("✓ mkfs test passed!")

def test_mount_valid():
    """Test mounting a valid filesystem"""
    print("\n=== Testing tfs_mount with Valid Filesystem ===")
    
    fs = TinyFS()
    
    # Create filesystem first
    result = fs.tfs_mkfs("test_v.dsk", constants.DEFAULT_DISK_SIZE)
    assert result == 0, "Failed to create filesystem"
    
    # Test mounting
    result = fs.tfs_mount("test_v.dsk")
    print(f"Mount result: {result}")
    assert result == 1, f"Mount should succeed, got {result}"
    assert fs.is_mounted, "Filesystem should be marked as mounted"
    assert fs.mounted_filename == "test_v.dsk", "Mounted filename should match"
    
    # Clean unmount
    unmount_result = fs.tfs_unmount()
    assert unmount_result == 1, "Unmount should succeed"
    
    print("✓ Valid filesystem mount test passed!")

def test_mount_nonexistent():
    """Test mounting a file that doesn't exist"""
    print("\n=== Testing tfs_mount with Nonexistent File ===")
    
    fs = TinyFS()
    result = fs.tfs_mount("fake.dsk")
    print(f"Mount nonexistent file result: {result}")
    assert result == -1, "Mount should fail for nonexistent file"
    assert not fs.is_mounted, "Filesystem should not be marked as mounted"
    
    print("✓ Nonexistent file test passed!")

def test_unmount_not_mounted():
    """Test unmounting when not mounted"""
    print("\n=== Testing tfs_unmount When Not Mounted ===")
    
    fs = TinyFS()
    result = fs.tfs_unmount()
    print(f"Unmount when not mounted result: {result}")
    assert result == -1, "Unmount should fail when not mounted"
    
    print("✓ Unmount when not mounted test passed!")

# ==================== FILE OPERATION TESTS ====================

def test_open_basic():
    """Test basic file opening functionality"""
    print("\n=== Testing tfs_open Basic Functionality ===")
    
    fs = TinyFS()
    
    # Setup filesystem
    fs.tfs_mkfs("test_fo.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_fo.dsk")
    
    # Test 1: Open a new file
    fd1 = fs.tfs_open("test1.txt")
    print(f"Open test1.txt: fd={fd1}")
    assert fd1 >= 0, "File descriptor should be non-negative"
    
    # Test 2: Open another file
    fd2 = fs.tfs_open("test2.txt")
    print(f"Open test2.txt: fd={fd2}")
    assert fd2 >= 0, "File descriptor should be non-negative"
    assert fd2 != fd1, "Different files should have different file descriptors"
    
    # Test 3: Open same file again (should return same fd)
    fd1_again = fs.tfs_open("test1.txt")
    print(f"Reopen test1.txt: fd={fd1_again}")
    assert fd1_again == fd1, "Reopening same file should return same fd"
    
    fs.tfs_unmount()
    print("✓ Basic open test passed!")

def test_open_not_mounted():
    """Test opening file when filesystem not mounted"""
    print("\n=== Testing tfs_open When Not Mounted ===")
    
    fs = TinyFS()
    
    # Try to open file without mounting
    fd = fs.tfs_open("test.txt")
    print(f"Open without mount: fd={fd}")
    assert fd == -1, "Open should fail when not mounted"
    
    print("✓ Open when not mounted test passed!")

def test_open_filename_too_long():
    """Test opening file with name too long"""
    print("\n=== Testing tfs_open with Long Filename ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("000001111.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("000001111.dsk")
    
    # Try to open file with very long name
    long_name = "a" * (constants.MAX_FILENAME_LENGTH + 5)
    fd = fs.tfs_open(long_name)
    print(f"Open long filename: fd={fd}")
    assert fd == -1, "Open should fail for filename too long"
    
    fs.tfs_unmount()
    print("✓ Long filename test passed!")

def test_open_multiple_files():
    """Test opening multiple files"""
    print("\n=== Testing tfs_open Multiple Files ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_fo.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_fo.dsk")
    
    # Open several files
    filenames = ["file1.txt", "file2.dat", "file3.log", "file4.tmp"]
    file_descriptors = []
    
    for filename in filenames:
        fd = fs.tfs_open(filename)
        print(f"Opened {filename}: fd={fd}")
        assert fd >= 0, f"Should successfully open {filename}"
        file_descriptors.append(fd)
    
    # Verify all fds are unique
    assert len(set(file_descriptors)) == len(file_descriptors), "All file descriptors should be unique"
    
    fs.tfs_unmount()
    print("✓ Multiple files open test passed!")

def test_close_basic():
    """Test basic file closing functionality"""
    print("\n=== Testing tfs_close Basic Functionality ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_fo.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_fo.dsk")
    
    # Open and close a file
    fd = fs.tfs_open("test.txt")
    assert fd >= 0, "File should open successfully"
    
    result = fs.tfs_close(fd)
    print(f"Close fd {fd}: result={result}")
    assert result == 0, "Close should succeed"
    
    # Try to close the same fd again (should fail)
    result2 = fs.tfs_close(fd)
    print(f"Close fd {fd} again: result={result2}")
    assert result2 == -1, "Closing already closed fd should fail"
    
    fs.tfs_unmount()
    print("✓ Basic close test passed!")

def test_close_invalid_fd():
    """Test closing invalid file descriptors"""
    print("\n=== Testing tfs_close with Invalid FDs ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_fo.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_fo.dsk")
    
    # Test invalid file descriptors
    invalid_fds = [-1, 999, 100]
    
    for fd in invalid_fds:
        result = fs.tfs_close(fd)
        print(f"Close invalid fd {fd}: result={result}")
        assert result == -1, f"Closing invalid fd {fd} should fail"
    
    fs.tfs_unmount()
    print("✓ Invalid fd close test passed!")

def test_close_multiple_files():
    """Test closing multiple files"""
    print("\n=== Testing tfs_close Multiple Files ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_fo.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_fo.dsk")
    
    # Open multiple files
    filenames = ["file1.txt", "file2.txt", "file3.txt"]
    fds = []
    
    for filename in filenames:
        fd = fs.tfs_open(filename)
        fds.append(fd)
    
    # Close all files
    for i, fd in enumerate(fds):
        result = fs.tfs_close(fd)
        print(f"Close {filenames[i]} (fd {fd}): result={result}")
        assert result == 0, f"Should successfully close {filenames[i]}"
    
    fs.tfs_unmount()
    print("✓ Multiple files close test passed!")

def test_write_basic():
    """Test basic write functionality"""
    print("\n=== Testing tfs_write Basic Functionality ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    # Open file and write data
    fd = fs.tfs_open("test.txt")
    assert fd >= 0, "File should open successfully"
    
    test_data = b"Hello, TinyFS World!"
    bytes_written = fs.tfs_write(fd, test_data)
    print(f"Write {len(test_data)} bytes: result={bytes_written}")
    assert bytes_written == len(test_data), "Should write all bytes"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Basic write test passed!")

def test_write_invalid_fd():
    """Test writing to invalid file descriptors"""
    print("\n=== Testing tfs_write with Invalid FDs ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    test_data = b"Test data"
    invalid_fds = [-1, 999, 100]
    
    for fd in invalid_fds:
        result = fs.tfs_write(fd, test_data)
        print(f"Write to invalid fd {fd}: result={result}")
        assert result == -1, f"Writing to invalid fd {fd} should fail"
    
    fs.tfs_unmount()
    print("✓ Invalid fd write test passed!")

def test_write_closed_file():
    """Test writing to closed file"""
    print("\n=== Testing tfs_write to Closed File ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    # Open file, close it, then try to write
    fd = fs.tfs_open("test.txt")
    fs.tfs_close(fd)
    
    test_data = b"Should fail"
    result = fs.tfs_write(fd, test_data)
    print(f"Write to closed file: result={result}")
    assert result == -1, "Writing to closed file should fail"
    
    fs.tfs_unmount()
    print("✓ Write to closed file test passed!")

def test_write_multiple_files():
    """Test writing to multiple files"""
    print("\n=== Testing tfs_write Multiple Files ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    # Open multiple files and write different data
    files_data = {
        "file1.txt": b"First file content",
        "file2.txt": b"Second file content",
        "file3.txt": b"Third file content"
    }
    
    for filename, data in files_data.items():
        fd = fs.tfs_open(filename)
        assert fd >= 0, f"Should open {filename}"
        
        bytes_written = fs.tfs_write(fd, data)
        print(f"Write to {filename}: {bytes_written} bytes")
        assert bytes_written == len(data), f"Should write all bytes to {filename}"
        
        fs.tfs_close(fd)
    
    fs.tfs_unmount()
    print("✓ Multiple files write test passed!")

def test_write_large_data():
    """Test writing large data"""
    print("\n=== Testing tfs_write Large Data ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    fd = fs.tfs_open("large.txt")
    assert fd >= 0, "File should open successfully"
    
    # Create large data (1KB)
    large_data = b"A" * 1024
    bytes_written = fs.tfs_write(fd, large_data)
    print(f"Write large data: {bytes_written} bytes")
    assert bytes_written == len(large_data), "Should write all bytes"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Large data write test passed!")

def test_write_empty_data():
    """Test writing empty data"""
    print("\n=== Testing tfs_write Empty Data ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_w.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_w.dsk")
    
    fd = fs.tfs_open("empty.txt")
    assert fd >= 0, "File should open successfully"
    
    empty_data = b""
    bytes_written = fs.tfs_write(fd, empty_data)
    print(f"Write empty data: result={bytes_written}")
    assert bytes_written == 0, "Should write 0 bytes for empty data"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Empty data write test passed!")

def test_delete_basic():
    """Test basic delete functionality"""
    print("\n=== Testing tfs_delete Basic Functionality ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_d.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_d.dsk")
    
    # Open file, write data, then delete
    fd = fs.tfs_open("del_me.txt")
    assert fd >= 0, "File should open successfully"
    
    fs.tfs_write(fd, b"This file will be deleted")
    
    result = fs.tfs_delete(fd)
    print(f"Delete file: result={result}")
    assert result == 0, "Delete should succeed"
    
    # Try to write to deleted file (should fail)
    write_result = fs.tfs_write(fd, b"Should fail")
    print(f"Write to deleted file: result={write_result}")
    assert write_result == -1, "Writing to deleted file should fail"
    
    fs.tfs_unmount()
    print("✓ Basic delete test passed!")

def test_delete_invalid_fd():
    """Test deleting with invalid file descriptors"""
    print("\n=== Testing tfs_delete with Invalid FDs ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_d.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_d.dsk")
    
    invalid_fds = [-1, 999, 100]
    
    for fd in invalid_fds:
        result = fs.tfs_delete(fd)
        print(f"Delete invalid fd {fd}: result={result}")
        assert result == -1, f"Deleting invalid fd {fd} should fail"
    
    fs.tfs_unmount()
    print("✓ Invalid fd delete test passed!")

def test_delete_closed_file():
    """Test deleting closed file"""
    print("\n=== Testing tfs_delete Closed File ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_d.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_d.dsk")
    
    # Open file, close it, then try to delete
    fd = fs.tfs_open("test.txt")
    fs.tfs_close(fd)
    
    result = fs.tfs_delete(fd)
    print(f"Delete closed file: result={result}")
    assert result == -1, "Deleting closed file should fail"
    
    fs.tfs_unmount()
    print("✓ Delete closed file test passed!")

def test_delete_multiple_files():
    """Test deleting multiple files"""
    print("\n=== Testing tfs_delete Multiple Files ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_d.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_d.dsk")
    
    # Create multiple files
    filenames = ["delete1.txt", "delete2.txt", "delete3.txt"]
    fds = []
    
    for filename in filenames:
        fd = fs.tfs_open(filename)
        fs.tfs_write(fd, f"Content of {filename}".encode())
        fds.append(fd)
    
    # Delete all files
    for i, fd in enumerate(fds):
        result = fs.tfs_delete(fd)
        print(f"Delete {filenames[i]}: result={result}")
        assert result == 0, f"Should successfully delete {filenames[i]}"
    
    fs.tfs_unmount()
    print("✓ Multiple files delete test passed!")

def test_delete_and_recreate():
    """Test deleting file and recreating with same name"""
    print("\n=== Testing tfs_delete and Recreate ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_d.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_d.dsk")
    
    filename = "recreate.txt"
    
    # Create and delete file
    fd1 = fs.tfs_open(filename)
    fs.tfs_write(fd1, b"Original content")
    fs.tfs_delete(fd1)
    
    # Recreate file with same name
    fd2 = fs.tfs_open(filename)
    print(f"Recreate file: fd={fd2}")
    assert fd2 >= 0, "Should be able to recreate file"
    
    # Write new content
    bytes_written = fs.tfs_write(fd2, b"New content")
    assert bytes_written > 0, "Should be able to write to recreated file"
    
    fs.tfs_close(fd2)
    fs.tfs_unmount()
    print("✓ Delete and recreate test passed!")

# ==================== INTEGRATION TESTS ====================

def test_file_operations_integration():
    """Test integration of all file operations"""
    print("\n=== Testing File Operations Integration ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_i.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_i.dsk")
    
    # Test sequence: open -> write -> close -> reopen -> delete
    filename = "int.txt"
    test_data = b"Integration test data"
    
    # Step 1: Open and write
    fd = fs.tfs_open(filename)
    assert fd >= 0, "Should open file"
    
    bytes_written = fs.tfs_write(fd, test_data)
    assert bytes_written == len(test_data), "Should write all data"
    
    # Step 2: Close file
    close_result = fs.tfs_close(fd)
    assert close_result == 0, "Should close file"
    
    # Step 3: Reopen same file
    fd2 = fs.tfs_open(filename)
    assert fd2 >= 0, "Should reopen file"
    
    # Step 4: Write more data
    more_data = b" - Additional data"
    bytes_written2 = fs.tfs_write(fd2, more_data)
    assert bytes_written2 == len(more_data), "Should write additional data"
    
    # Step 5: Delete file
    delete_result = fs.tfs_delete(fd2)
    assert delete_result == 0, "Should delete file"
    
    fs.tfs_unmount()
    print("✓ File operations integration test passed!")

def test_persistence_across_mount_unmount():
    """Test that file operations work across mount/unmount cycles"""
    print("\n=== Testing Persistence Across Mount/Unmount ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_p.dsk", constants.DEFAULT_DISK_SIZE)
    
    # First session: create and write file
    fs.tfs_mount("test_p.dsk")
    fd = fs.tfs_open("pers.txt")
    fs.tfs_write(fd, b"Persistent data")
    fs.tfs_close(fd)
    fs.tfs_unmount()
    
    # Second session: try to access file
    fs2 = TinyFS()
    mount_result = fs2.tfs_mount("test_p.dsk")
    assert mount_result == 1, "Should remount successfully"
    
    # Try to open the file (basic test - full persistence requires disk implementation)
    fd2 = fs2.tfs_open("pers.txt")
    print(f"Reopen persistent file: fd={fd2}")
    assert fd2 >= 0, "Should be able to open file after remount"
    
    fs2.tfs_close(fd2)
    fs2.tfs_unmount()
    print("✓ Basic persistence test passed!")

# ==================== tfs_readByte TESTS ====================

def test_readbyte_basic():
    """Test basic readByte functionality"""
    print("\n=== Testing tfs_readByte Basic Functionality ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_r.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_r.dsk")
    
    # Open file and write some data
    fd = fs.tfs_open("test.txt")
    test_data = b"Hello"
    fs.tfs_write(fd, test_data)
    
    # Try to read bytes back
    for i, expected_byte in enumerate(test_data):
        byte_value = fs.tfs_readByte(fd)
        print(f"Read byte {i}: got {byte_value}, expected {expected_byte}")
        assert byte_value == expected_byte, f"Byte {i}: expected {expected_byte}, got {byte_value}"
    
    # Reading past end should return -1
    eof_byte = fs.tfs_readByte(fd)
    print(f"Read past EOF: {eof_byte}")
    assert eof_byte == -1, "Reading past EOF should return -1"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Basic readByte test passed!")

def test_readbyte_invalid_fd():
    """Test readByte with invalid file descriptors"""
    print("\n=== Testing tfs_readByte with Invalid FDs ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_r.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_r.dsk")
    
    # Test invalid file descriptors
    invalid_fds = [-1, 999, 100]
    
    for fd in invalid_fds:
        result = fs.tfs_readByte(fd)
        print(f"ReadByte invalid fd {fd}: result={result}")
        assert result == -1, f"ReadByte invalid fd {fd} should fail"
    
    fs.tfs_unmount()
    print("✓ Invalid fd readByte test passed!")

def test_readbyte_not_mounted():
    """Test readByte when filesystem not mounted"""
    print("\n=== Testing tfs_readByte When Not Mounted ===")
    
    fs = TinyFS()
    
    # Try to read without mounting
    result = fs.tfs_readByte(0)
    print(f"ReadByte without mount: result={result}")
    assert result == -1, "ReadByte should fail when not mounted"
    
    print("✓ ReadByte when not mounted test passed!")

def test_readbyte_closed_file():
    """Test readByte on closed file"""
    print("\n=== Testing tfs_readByte on Closed File ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_r.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_r.dsk")
    
    # Open file, write data, close it, then try to read
    fd = fs.tfs_open("test.txt")
    fs.tfs_write(fd, b"test")
    fs.tfs_close(fd)
    
    result = fs.tfs_readByte(fd)
    print(f"ReadByte closed file: result={result}")
    assert result == -1, "ReadByte should fail on closed file"
    
    fs.tfs_unmount()
    print("✓ ReadByte closed file test passed!")

def test_readbyte_empty_file():
    """Test readByte on empty file"""
    print("\n=== Testing tfs_readByte on Empty File ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_r.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_r.dsk")
    
    # Open file but don't write anything
    fd = fs.tfs_open("empty.txt")
    
    result = fs.tfs_readByte(fd)
    print(f"ReadByte empty file: result={result}")
    assert result == -1, "ReadByte should return -1 for empty file"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ ReadByte empty file test passed!")

def test_readbyte_large_file():
    """Test readByte on file larger than one block"""
    print("\n=== Testing tfs_readByte on Large File ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_r.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_r.dsk")
    
    # Create data larger than one block
    large_data = b"A" * (constants.BLOCK_SIZE + 100)  # Spans multiple blocks
    
    fd = fs.tfs_open("large.txt")
    fs.tfs_write(fd, large_data)
    
    # Read first few bytes
    for i in range(10):
        byte_value = fs.tfs_readByte(fd)
        print(f"Large file byte {i}: {byte_value}")
        assert byte_value == ord('A'), f"Byte {i}: expected {ord('A')}, got {byte_value}"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ ReadByte large file test passed!")

# ==================== tfs_seek TESTS ====================

def test_seek_basic():
    """Test basic seek functionality"""
    print("\n=== Testing tfs_seek Basic Functionality ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_s.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_s.dsk")
    
    # Open file and write data
    fd = fs.tfs_open("test.txt")
    test_data = b"0123456789"
    fs.tfs_write(fd, test_data)
    
    # Seek to position 5 and read
    seek_result = fs.tfs_seek(fd, 5)
    print(f"Seek to position 5: result={seek_result}")
    assert seek_result == 0, "Seek should succeed"
    
    byte_value = fs.tfs_readByte(fd)
    print(f"Read after seek: got {byte_value}, expected {ord('5')}")
    assert byte_value == ord('5'), f"After seek to 5: expected {ord('5')}, got {byte_value}"
    
    # Seek to beginning and read
    seek_result = fs.tfs_seek(fd, 0)
    assert seek_result == 0, "Seek to beginning should succeed"
    
    byte_value = fs.tfs_readByte(fd)
    assert byte_value == ord('0'), f"After seek to 0: expected {ord('0')}, got {byte_value}"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Basic seek test passed!")

def test_seek_invalid_fd():
    """Test seek with invalid file descriptors"""
    print("\n=== Testing tfs_seek with Invalid FDs ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_s.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_s.dsk")
    
    invalid_fds = [-1, 999, 100]
    
    for fd in invalid_fds:
        result = fs.tfs_seek(fd, 10)
        print(f"Seek invalid fd {fd}: result={result}")
        assert result == -1, f"Seek invalid fd {fd} should fail"
    
    fs.tfs_unmount()
    print("✓ Invalid fd seek test passed!")

def test_seek_not_mounted():
    """Test seek when filesystem not mounted"""
    print("\n=== Testing tfs_seek When Not Mounted ===")
    
    fs = TinyFS()
    
    result = fs.tfs_seek(0, 10)
    print(f"Seek without mount: result={result}")
    assert result == -1, "Seek should fail when not mounted"
    
    print("✓ Seek when not mounted test passed!")

def test_seek_beyond_file():
    """Test seeking beyond file end"""
    print("\n=== Testing tfs_seek Beyond File End ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_s.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_s.dsk")
    
    # Create small file
    fd = fs.tfs_open("small.txt")
    fs.tfs_write(fd, b"test")  # 4 bytes
    
    # Try to seek beyond end
    seek_result = fs.tfs_seek(fd, 100)
    print(f"Seek beyond end: result={seek_result}")
    assert seek_result == -1, "Seek beyond file end should fail"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Seek beyond file test passed!")

def test_seek_negative_offset():
    """Test seeking with negative offset"""
    print("\n=== Testing tfs_seek with Negative Offset ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_s.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_s.dsk")
    
    fd = fs.tfs_open("test.txt")
    fs.tfs_write(fd, b"hello")
    
    # Try negative seek
    seek_result = fs.tfs_seek(fd, -1)
    print(f"Seek negative offset: result={seek_result}")
    assert seek_result == -1, "Seek with negative offset should fail"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Seek negative offset test passed!")

# ==================== INTEGRATION TESTS ====================

def test_read_seek_integration():
    """Test readByte and seek working together"""
    print("\n=== Testing ReadByte and Seek Integration ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_rs.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_rs.dsk")
    
    # Write alphabet
    fd = fs.tfs_open("alphabet.txt")
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fs.tfs_write(fd, alphabet)
    
    # Test random access reading
    test_positions = [0, 5, 10, 25, 0, 15]
    expected_chars = [b'A', b'F', b'K', b'Z', b'A', b'P']
    
    for pos, expected in zip(test_positions, expected_chars):
        # Seek to position
        seek_result = fs.tfs_seek(fd, pos)
        assert seek_result == 0, f"Seek to {pos} should succeed"
        
        # Read byte
        byte_value = fs.tfs_readByte(fd)
        print(f"Position {pos}: read {chr(byte_value)}, expected {chr(expected[0])}")
        assert byte_value == expected[0], f"Position {pos}: expected {expected[0]}, got {byte_value}"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ ReadByte and Seek integration test passed!")

def test_sequential_vs_random_reading():
    """Test sequential reading vs random access"""
    print("\n=== Testing Sequential vs Random Reading ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_rs.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_rs.dsk")
    
    # Write test data
    fd = fs.tfs_open("sequence.txt")
    test_data = b"0123456789"
    fs.tfs_write(fd, test_data)
    
    # Sequential reading from start
    print("Sequential reading:")
    fs.tfs_seek(fd, 0)  # Start from beginning
    for i in range(len(test_data)):
        byte_value = fs.tfs_readByte(fd)
        expected = ord(str(i))
        print(f"  Sequential byte {i}: {byte_value} (expected {expected})")
        assert byte_value == expected, f"Sequential read failed at position {i}"
    
    # Random access reading
    print("Random access reading:")
    random_positions = [7, 2, 9, 0, 5]
    for pos in random_positions:
        fs.tfs_seek(fd, pos)
        byte_value = fs.tfs_readByte(fd)
        expected = ord(str(pos))
        print(f"  Random access pos {pos}: {byte_value} (expected {expected})")
        assert byte_value == expected, f"Random access failed at position {pos}"
    
    fs.tfs_close(fd)
    fs.tfs_unmount()
    print("✓ Sequential vs Random reading test passed!")

def test_multiple_files_seek_read():
    """Test seek and read operations on multiple files"""
    print("\n=== Testing Multiple Files Seek and Read ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_rs.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_rs.dsk")
    
    # Create multiple files with different content
    files_data = {
        "numbers.txt": b"0123456789",
        "letters.txt": b"ABCDEFGHIJ",
        "symbols.txt": b"!@#$%^&*()"
    }
    
    fds = {}
    for filename, data in files_data.items():
        fd = fs.tfs_open(filename)
        fs.tfs_write(fd, data)
        fds[filename] = fd
    
    # Test reading from different positions in different files
    test_cases = [
        ("numbers.txt", 5, ord('5')),
        ("letters.txt", 2, ord('C')),
        ("symbols.txt", 0, ord('!')),
        ("numbers.txt", 0, ord('0')),
        ("letters.txt", 9, ord('J'))
    ]
    
    for filename, pos, expected in test_cases:
        fd = fds[filename]
        fs.tfs_seek(fd, pos)
        byte_value = fs.tfs_readByte(fd)
        print(f"{filename} pos {pos}: got {byte_value}, expected {expected}")
        assert byte_value == expected, f"{filename} pos {pos}: expected {expected}, got {byte_value}"
    
    # Close all files
    for fd in fds.values():
        fs.tfs_close(fd)
    
    fs.tfs_unmount()
    print("✓ Multiple files seek and read test passed!")


def run_all_tests():
    """Run all tests"""
    print("Extended TinyFS Test Suite")
    print("=" * 60)
    
    # Clean up before starting
    cleanup_test_files()
    
    tests = [
        # Mount/Unmount tests
        test_mkfs,
        test_mount_valid,
        test_mount_nonexistent,
        test_unmount_not_mounted,
        
        # File open tests
        test_open_basic,
        test_open_not_mounted,
        test_open_filename_too_long,
        test_open_multiple_files,
        
        # File close tests
        test_close_basic,
        test_close_invalid_fd,
        test_close_multiple_files,
        
        # File write tests
        test_write_basic,
        test_write_invalid_fd,
        test_write_closed_file,
        test_write_multiple_files,
        test_write_large_data,
        test_write_empty_data,
        
        # File delete tests
        test_delete_basic,
        test_delete_invalid_fd,
        test_delete_closed_file,
        test_delete_multiple_files,
        test_delete_and_recreate,
        
        # Integration tests
        test_file_operations_integration,
        test_persistence_across_mount_unmount,

        # ReadByte tests
        test_readbyte_basic,
        test_readbyte_invalid_fd,
        test_readbyte_not_mounted,
        test_readbyte_closed_file,
        test_readbyte_empty_file,
        test_readbyte_large_file,
        
        # Seek tests
        test_seek_basic,
        test_seek_invalid_fd,
        test_seek_not_mounted,
        test_seek_beyond_file,
        test_seek_negative_offset,
        
        # Integration tests
        test_read_seek_integration,
        test_sequential_vs_random_reading,
        test_multiple_files_seek_read,

    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Clean up after tests
    cleanup_test_files()
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("ALL TESTS PASSED!")
        print("Your TinyFS implementation is working correctly!")
    else:
        print(f" {failed} test(s) failed. Check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)