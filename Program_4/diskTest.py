#!/usr/bin/env python3
# simple_test.py

import libDisk
from constants import BLOCK_SIZE

# Test 1: Create a new disk
disk = libDisk.libDisk()
result = disk.openDisk("test.dsk", BLOCK_SIZE * 10)  # 10 blocks
print(f"Create disk: {'Success' if result >= 0 else 'Failed'} (fd={result})")

# Test 2: Write some data
data = b"Hello, TinyFS!" + b'\x00' * (BLOCK_SIZE - 14)
result = disk.writeBlock(0, data)
print(f"Write block 0: {'Success' if result == 0 else 'Failed'}")

# Test 3: Read it back
buffer = [0] * BLOCK_SIZE  # Changed from bytearray to list
result = disk.readBlock(0, buffer)
print(f"Read block 0: {'Success' if result == 0 else 'Failed'}")
print(f"Data: {bytes(buffer[:14]).decode('utf-8')}")

# Test 4: Close disk
result = disk.closeDisk()
print(f"Close disk: {'Success' if result == 0 else 'Failed'}")

# Test 5: Reopen and verify data persists
disk2 = libDisk.libDisk()
result = disk2.openDisk("test.dsk", 0)  # 0 = open existing
print(f"Reopen disk: {'Success' if result >= 0 else 'Failed'} (fd={result})")

buffer2 = [0] * BLOCK_SIZE  # Changed from bytearray to list
result = disk2.readBlock(0, buffer2)
print(f"Read persistent data: {'Success' if result == 0 else 'Failed'}")
print(f"Persistent data: {bytes(buffer2[:14]).decode('utf-8')}")

result = disk2.closeDisk()
print(f"Close disk2: {'Success' if result == 0 else 'Failed'}")

print("\nTest completed!")