#!/usr/bin/env python3
"""
Simple TinyFS Test Suite
Tests for mount/unmount functionality
"""

import os
import sys
from tinyfs import TinyFS
import constants

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_valid.dsk", "test_invalid.dsk", "test_empty.dsk", 
        "test_corrupted.dsk", "test_fs1.dsk", "test_fs2.dsk"
    ]
    
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

def test_mkfs():
    """Test filesystem creation"""
    print("=== Testing tfs_mkfs ===")
    
    fs = TinyFS()
    
    # Test 1: Create a filesystem
    result = fs.tfs_mkfs("test_valid.dsk", constants.DEFAULT_DISK_SIZE)
    print(f"mkfs result: {result}")
    assert result == 0, f"mkfs should return 0 on success, got {result}"
    
    # Test 2: Verify file exists and has correct size
    assert os.path.exists("test_valid.dsk"), "Disk file should exist"
    file_size = os.path.getsize("test_valid.dsk")
    assert file_size == constants.DEFAULT_DISK_SIZE, f"File size should be {constants.DEFAULT_DISK_SIZE}, got {file_size}"
    
    print("✓ mkfs test passed!")

def test_mount_valid():
    """Test mounting a valid filesystem"""
    print("\n=== Testing tfs_mount with Valid Filesystem ===")
    
    fs = TinyFS()
    
    # Create filesystem first
    result = fs.tfs_mkfs("test_valid.dsk", constants.DEFAULT_DISK_SIZE)
    assert result == 0, "Failed to create filesystem"
    
    # Test mounting
    result = fs.tfs_mount("test_valid.dsk")
    print(f"Mount result: {result}")
    assert result == 1, f"Mount should succeed, got {result}"
    assert fs.is_mounted, "Filesystem should be marked as mounted"
    assert fs.mounted_filename == "test_valid.dsk", "Mounted filename should match"
    
    # Clean unmount
    unmount_result = fs.tfs_unmount()
    assert unmount_result == 1, "Unmount should succeed"
    
    print("✓ Valid filesystem mount test passed!")

def test_mount_nonexistent():
    """Test mounting a file that doesn't exist"""
    print("\n=== Testing tfs_mount with Nonexistent File ===")
    
    fs = TinyFS()
    result = fs.tfs_mount("nonexistent.dsk")
    print(f"Mount nonexistent file result: {result}")
    assert result == -1, "Mount should fail for nonexistent file"
    assert not fs.is_mounted, "Filesystem should not be marked as mounted"
    
    print("✓ Nonexistent file test passed!")

def test_mount_invalid_magic():
    """Test mounting a file with invalid magic number"""
    print("\n=== Testing tfs_mount with Invalid Magic Number ===")
    
    # Create file with wrong magic number
    with open("test_invalid.dsk", 'wb') as f:
        f.write(b'\x99\x02')  # Wrong magic, correct root pointer
        f.write(b'\x00' * (constants.DEFAULT_DISK_SIZE - 2))
    
    fs = TinyFS()
    result = fs.tfs_mount("test_invalid.dsk")
    print(f"Mount invalid magic result: {result}")
    assert result == -1, "Mount should fail for invalid magic number"
    assert not fs.is_mounted, "Filesystem should not be marked as mounted"
    
    print("✓ Invalid magic number test passed!")

def test_mount_already_mounted():
    """Test mounting when already mounted"""
    print("\n=== Testing tfs_mount When Already Mounted ===")
    
    fs = TinyFS()
    
    # Create two filesystems
    fs.tfs_mkfs("test_fs1.dsk", constants.DEFAULT_DISK_SIZE)
    fs.tfs_mkfs("test_fs2.dsk", constants.DEFAULT_DISK_SIZE)
    
    # Mount first filesystem
    result1 = fs.tfs_mount("test_fs1.dsk")
    assert result1 == 1, "First mount should succeed"
    
    # Try to mount second (should fail)
    result2 = fs.tfs_mount("test_fs2.dsk")
    print(f"Second mount result: {result2}")
    assert result2 == -1, "Second mount should fail when already mounted"
    assert fs.mounted_filename == "test_fs1.dsk", "Should still be mounted to first filesystem"
    
    # Clean unmount
    fs.tfs_unmount()
    
    print("✓ Already mounted test passed!")

def test_mount_empty_file():
    """Test mounting an empty file"""
    print("\n=== Testing tfs_mount with Empty File ===")
    
    # Create empty file
    with open("test_empty.dsk", 'wb') as f:
        pass  # Empty file
    
    fs = TinyFS()
    result = fs.tfs_mount("test_empty.dsk")
    print(f"Mount empty file result: {result}")
    assert result == -1, "Mount should fail for empty file"
    assert not fs.is_mounted, "Filesystem should not be marked as mounted"
    
    print("✓ Empty file test passed!")

def test_unmount_not_mounted():
    """Test unmounting when not mounted"""
    print("\n=== Testing tfs_unmount When Not Mounted ===")
    
    fs = TinyFS()
    result = fs.tfs_unmount()
    print(f"Unmount when not mounted result: {result}")
    assert result == -1, "Unmount should fail when not mounted"
    
    print("✓ Unmount when not mounted test passed!")

def test_unmount_after_mount():
    """Test proper unmount after mount"""
    print("\n=== Testing tfs_unmount After Mount ===")
    
    fs = TinyFS()
    
    # Create and mount filesystem
    fs.tfs_mkfs("test_valid.dsk", constants.DEFAULT_DISK_SIZE)
    mount_result = fs.tfs_mount("test_valid.dsk")
    assert mount_result == 1, "Mount should succeed"
    
    # Unmount
    unmount_result = fs.tfs_unmount()
    print(f"Unmount result: {unmount_result}")
    assert unmount_result == 1, "Unmount should succeed"
    assert not fs.is_mounted, "Should not be mounted after unmount"
    assert fs.mounted_filename is None, "Mounted filename should be None after unmount"
    
    print("✓ Unmount after mount test passed!")

def test_multiple_mount_unmount_cycles():
    """Test multiple mount/unmount cycles"""
    print("\n=== Testing Multiple Mount/Unmount Cycles ===")
    
    fs = TinyFS()
    fs.tfs_mkfs("test_valid.dsk", constants.DEFAULT_DISK_SIZE)
    
    # Test 3 cycles
    for i in range(3):
        print(f"  Cycle {i+1}:")
        
        # Mount
        mount_result = fs.tfs_mount("test_valid.dsk")
        assert mount_result == 1, f"Mount should succeed in cycle {i+1}"
        assert fs.is_mounted, f"Should be mounted in cycle {i+1}"
        
        # Unmount
        unmount_result = fs.tfs_unmount()
        assert unmount_result == 1, f"Unmount should succeed in cycle {i+1}"
        assert not fs.is_mounted, f"Should not be mounted after unmount in cycle {i+1}"
    
    print("✓ Multiple mount/unmount cycles test passed!")

def test_mount_corrupted():
    """Test mounting corrupted filesystem"""
    print("\n=== Testing tfs_mount with Corrupted Filesystem ===")
    
    fs = TinyFS()
    
    # Create valid filesystem first
    fs.tfs_mkfs("test_corrupted.dsk", constants.DEFAULT_DISK_SIZE)
    
    # Corrupt the magic number
    with open("test_corrupted.dsk", 'r+b') as f:
        f.seek(0)
        f.write(b'\x00')  # Wrong magic number
    
    result = fs.tfs_mount("test_corrupted.dsk")
    print(f"Mount corrupted filesystem result: {result}")
    assert result == -1, "Mount should fail for corrupted filesystem"
    assert not fs.is_mounted, "Filesystem should not be marked as mounted"
    
    print("✓ Corrupted filesystem test passed!")

def run_all_tests():
    """Run all tests"""
    print("TinyFS Simple Test Suite")
    print("=" * 50)
    
    # Clean up before starting
    cleanup_test_files()
    
    tests = [
        test_mkfs,
        test_mount_valid,
        test_mount_nonexistent,
        test_mount_invalid_magic,
        test_mount_already_mounted,
        test_mount_empty_file,
        test_unmount_not_mounted,
        test_unmount_after_mount,
        test_multiple_mount_unmount_cycles,
        test_mount_corrupted
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Clean up after tests
    cleanup_test_files()
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("Your mount/unmount implementation is working correctly!")
    else:
        print(f"❌ {failed} test(s) failed. Check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)