# constants.py
BLOCK_SIZE = 256
MAGIC_NUMBER = 0x5A
BITMAP_SIZE = 248
DEFAULT_DISK_SIZE = 10240
MAX_DISKNAME_LENGTH = 20
MAX_FILENAME_LENGTH = 8
DATE_TIME_SIZE = 0

# Block types
SUPER_BLOCK = 1
INODE = 2
MAX_INODE_BLOCK = 13 # usable folders
FILE_EXTENT = 3
MAX_DATA_BLOCK = 24 # files
FREE = 4

# File system states
MOUNTED = 1
EXISTING_DISK = 0
DATE_AND_TIME_SIZE = 20

# Access modesS
READ = 1
WRITE = 0

DEFAULT_DISK_NAME = "tinyFSDisk"
MAX_FILES = 100
END_OF_DISK = 10
ROOT_INODE_BLOCK_NUM = 2