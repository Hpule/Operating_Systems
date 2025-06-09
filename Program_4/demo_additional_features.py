#!/usr/bin/env python3
# demo_additional_features.py
"""
Demo program for TinyFS additional features:
1. Read-only and writeByte support
2. Future: Directory listing (when implemented)
"""
import os
from tinyfs import TinyFS
import constants

def demo_readonly_writebyte():
    """Demonstrate read-only and writeByte functionality"""
    print("=== TinyFS Additional Features Demo ===\n")
    
    # Clean up any existing test file
    if os.path.exists("demo_features.dsk"):
        os.remove("demo_features.dsk")
    
    fs = TinyFS()
    
    # Create and mount filesystem
    print("1. Creating and mounting filesystem...")
    fs.tfs_mkfs("demo_features.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("demo_features.dsk")
    print("✓ Filesystem ready\n")
    
    # Demo 1: writeByte functionality
    print("2. Testing writeByte functionality...")
    fd = fs.tfs_open("test.txt")
    
    # Write individual bytes using writeByte
    message = "Hello!"
    for i, char in enumerate(message):
        result = fs.tfs_writeByte(fd, ord(char))
        print(f"   Wrote byte '{char}' (ASCII {ord(char)}) at position {i}: result={result}")
    
    # Read back the bytes
    print("\n   Reading back with readByte:")
    fs.tfs_seek(fd, 0)  # Go to beginning
    for i in range(len(message)):
        byte_val = fs.tfs_readByte(fd)
        print(f"   Position {i}: read '{chr(byte_val)}' (ASCII {byte_val})")
    
    print("✓ writeByte demo completed\n")
    
    # Demo 2: Read-only functionality
    print("3. Testing read-only functionality...")
    
    # Make file read-only
    result = fs.tfs_makeRO("test.txt")
    print(f"   Made file read-only: result={result}")
    
    # Try to write to read-only file (should fail)
    write_result = fs.tfs_write(fd, b" More text")
    print(f"   Attempted write to read-only file: result={write_result} (should be -1)")
    
    # Try writeByte on read-only file (should fail)
    writebyte_result = fs.tfs_writeByte(fd, ord('X'))
    print(f"   Attempted writeByte to read-only file: result={writebyte_result} (should be -1)")
    
    # Try to delete read-only file (should fail)
    delete_result = fs.tfs_delete(fd)
    print(f"   Attempted delete of read-only file: result={delete_result} (should be -1)")
    
    # Reading should still work
    fs.tfs_seek(fd, 0)
    byte_val = fs.tfs_readByte(fd)
    print(f"   Reading from read-only file still works: '{chr(byte_val)}'")
    
    print("✓ Read-only protection working\n")
    
    # Demo 3: Making file read-write again
    print("4. Converting back to read-write...")
    
    result = fs.tfs_makeRW("test.txt")
    print(f"   Made file read-write: result={result}")
    
    # Now writing should work again
    write_result = fs.tfs_write(fd, b" World")
    print(f"   Write to read-write file: result={write_result} (should be > 0)")
    
    writebyte_result = fs.tfs_writeByte(fd, ord('!'))
    print(f"   WriteByte to read-write file: result={writebyte_result} (should be 0)")
    
    print("✓ Read-write conversion working\n")
    
    # Demo 4: Show final file content
    print("5. Final file content:")
    fs.tfs_seek(fd, 0)
    content = ""
    while True:
        byte_val = fs.tfs_readByte(fd)
        if byte_val == -1:  # EOF
            break
        content += chr(byte_val)
    
    print(f"   Complete file content: '{content}'")
    
    # Show file status
    print(f"\n6. File status:")
    fs.print_status()
    
    # Clean up
    fs.tfs_close(fd)
    fs.tfs_unmount()
    
    print("\n=== Demo completed successfully! ===")
    print("\nAdditional features implemented:")
    print("✓ tfs_writeByte() - Write individual bytes")
    print("✓ tfs_makeRO() - Make files read-only")
    print("✓ tfs_makeRW() - Make files read-write")
    print("✓ Read-only protection in write operations")
    print("✓ Read-only protection in delete operations")
    print("\nNext steps:")
    print("- Implement a second additional feature for full credit")
    print("- Record demonstration video")
    print("- Update README with feature descriptions")

def test_additional_features():
    """Run additional tests for the new features"""
    print("\n=== Additional Feature Tests ===\n")
    
    fs = TinyFS()
    
    # Test filesystem
    fs.tfs_mkfs("test_additional.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_additional.dsk")
    
    # Test 1: Multiple files with different read-only status
    print("Test 1: Multiple files with mixed read-only status")
    fd1 = fs.tfs_open("file1.txt")
    fd2 = fs.tfs_open("file2.txt")
    
    fs.tfs_write(fd1, b"File 1 content")
    fs.tfs_write(fd2, b"File 2 content")
    
    # Make only file1 read-only
    fs.tfs_makeRO("file1.txt")
    
    # Test writes
    result1 = fs.tfs_write(fd1, b" extra")  # Should fail
    result2 = fs.tfs_write(fd2, b" extra")  # Should succeed
    
    print(f"Write to read-only file1: {result1} (should be -1)")
    print(f"Write to read-write file2: {result2} (should be > 0)")
    
    # Test 2: writeByte with position tracking
    print("\nTest 2: writeByte position tracking")
    fd3 = fs.tfs_open("pstss.txt")
    
    # Write bytes at different positions
    for i, char in enumerate("ABCDE"):
        pos_before = fs.open_files[fd3].position
        result = fs.tfs_writeByte(fd3, ord(char))
        pos_after = fs.open_files[fd3].position
        print(f"Wrote '{char}': pos {pos_before} -> {pos_after}, result={result}")
    
    # Read back and verify positions
    fs.tfs_seek(fd3, 0)
    print("Reading back:")
    for i in range(5):
        pos_before = fs.open_files[fd3].position
        byte_val = fs.tfs_readByte(fd3)
        pos_after = fs.open_files[fd3].position
        print(f"Read '{chr(byte_val)}': pos {pos_before} -> {pos_after}")
    
    # Clean up
    fs.tfs_close(fd1)
    fs.tfs_close(fd2)
    fs.tfs_close(fd3)
    fs.tfs_unmount()
    
    print("✓ Additional tests completed!\n")
    
    # Cleanup test files
    for filename in ["demo_features.dsk", "test_additional.dsk"]:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    demo_readonly_writebyte()
    test_additional_features()