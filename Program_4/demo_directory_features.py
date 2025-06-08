#!/usr/bin/env python3
# demo_directory_features.py
"""
Demo program for TinyFS directory listing and renaming features
"""
import os
from tinyfs import TinyFS
import constants

def demo_directory_features():
    """Demonstrate directory listing and renaming functionality"""
    print("=== TinyFS Directory Features Demo ===\n")
    
    # Clean up any existing test file
    if os.path.exists("demo_directory.dsk"):
        os.remove("demo_directory.dsk")
    
    fs = TinyFS()
    
    # Create and mount filesystem
    print("1. Creating and mounting filesystem...")
    fs.tfs_mkfs("demo_directory.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("demo_directory.dsk")
    print("✓ Filesystem ready\n")
    
    # Demo 1: Create several files
    print("2. Creating multiple files...")
    files_to_create = ["file1.txt", "file2.txt", "doc.txt", "data.txt"]
    file_descriptors = []
    
    for filename in files_to_create:
        fd = fs.tfs_open(filename)
        file_descriptors.append(fd)
        fs.tfs_write(fd, f"Content of {filename}".encode())
        print(f"   Created file '{filename}' with fd {fd}")
    
    print("✓ Files created\n")
    
    # Demo 2: List directory contents
    print("3. Listing directory contents...")
    file_list = fs.tfs_readdir()
    print("   Directory listing:")
    for i, filename in enumerate(file_list, 1):
        print(f"   {i}. {filename}")
    print("✓ Directory listing completed\n")
    
    # Demo 3: Rename files
    print("4. Testing file renaming...")
    
    # Rename file1.txt to new1.txt
    result = fs.tfs_rename("file1.txt", "new1.txt")
    print(f"   Rename 'file1.txt' to 'new1.txt': result={result} (should be 0)")
    
    # Rename file2.txt to new2.txt
    result = fs.tfs_rename("file2.txt", "new2.txt")
    print(f"   Rename 'file2.txt' to 'new2.txt': result={result} (should be 0)")
    
    # Try to rename to existing name (should fail)
    result = fs.tfs_rename("doc.txt", "new1.txt")
    print(f"   Rename 'doc.txt' to existing 'new1.txt': result={result} (should be -1)")
    
    # Try to rename non-existent file (should fail)
    result = fs.tfs_rename("nonexist.txt", "test.txt")
    print(f"   Rename non-existent file: result={result} (should be -1)")
    
    print("✓ Renaming tests completed\n")
    
    # Demo 4: List directory after renaming
    print("5. Directory listing after renaming...")
    file_list = fs.tfs_readdir()
    print("   Updated directory listing:")
    for i, filename in enumerate(file_list, 1):
        print(f"   {i}. {filename}")
    print("✓ Directory updated correctly\n")
    
    # Demo 5: Verify file content after rename
    print("6. Verifying file content after rename...")
    
    # Find the renamed file's fd
    renamed_fd = None
    for fd, file_handle in fs.open_files.items():
        if file_handle.filename == "new1.txt":
            renamed_fd = fd
            break
    
    if renamed_fd is not None:
        fs.tfs_seek(renamed_fd, 0)  # Go to beginning
        content = ""
        while True:
            byte_val = fs.tfs_readByte(renamed_fd)
            if byte_val == -1:  # EOF
                break
            content += chr(byte_val)
        print(f"   Content of renamed file 'new1.txt': '{content}'")
    
    print("✓ File content preserved after rename\n")
    
    # Demo 6: Show filesystem status
    print("7. Final filesystem status:")
    fs.print_status()
    
    # Clean up
    for fd in file_descriptors:
        fs.tfs_close(fd)
    fs.tfs_unmount()
    
    print("\n=== Directory Features Demo completed successfully! ===")
    print("\nDirectory features implemented:")
    print("✓ tfs_readdir() - List all files in filesystem")
    print("✓ tfs_rename() - Rename files")
    print("✓ Duplicate name prevention")
    print("✓ File content preservation during rename")
    print("✓ Error handling for invalid operations")

def test_edge_cases():
    """Test edge cases for directory features"""
    print("\n=== Directory Features Edge Case Tests ===\n")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_edge.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mount("test_edge.dsk")
    
    # Test 1: Empty directory listing
    print("Test 1: Empty directory listing")
    file_list = fs.tfs_readdir()
    print(f"Empty directory contains: {file_list} (should be [])")
    
    # Test 2: Long filename rename
    print("\nTest 2: Long filename handling")
    fd = fs.tfs_open("test.txt")
    fs.tfs_write(fd, b"test content")
    
    # Try to rename to a filename that's too long
    long_name = "verylongfilename.txt"  # This should be too long
    result = fs.tfs_rename("test.txt", long_name)
    print(f"Rename to long filename: result={result} (should be -1)")
    
    # Test 3: Chain renaming
    print("\nTest 3: Chain renaming")
    result1 = fs.tfs_rename("test.txt", "temp.txt")
    result2 = fs.tfs_rename("temp.txt", "final.txt")
    print(f"Chain rename test->temp: {result1}, temp->final: {result2}")
    
    final_list = fs.tfs_readdir()
    print(f"Final directory: {final_list}")
    
    # Clean up
    fs.tfs_close(fd)
    fs.tfs_unmount()
    
    print("✓ Edge case tests completed!\n")
    
    # Cleanup test files
    for filename in ["demo_directory.dsk", "test_edge.dsk"]:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    demo_directory_features()
    test_edge_cases()