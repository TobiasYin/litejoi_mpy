import os

def S_IFMT(mode):
    """Return the portion of the file's mode that describes the
    file type.
    """
    return mode & 0o170000

S_IFDIR  = 0o040000  # directory
S_IFCHR  = 0o020000  # character device
S_IFBLK  = 0o060000  # block device
S_IFREG  = 0o100000  # regular file
S_IFIFO  = 0o010000  # fifo (named pipe)
S_IFLNK  = 0o120000  # symbolic link
S_IFSOCK = 0o140000  # socket file
# Fallbacks for uncommon platform-specific constants
S_IFDOOR = 0
S_IFPORT = 0
S_IFWHT = 0

# Functions to test for each file type

def S_ISDIR(mode):
    """Return True if mode is from a directory."""
    return S_IFMT(mode) == S_IFDIR

def isdir(path):
    st = os.stat(path)
    return S_ISDIR(st[0])

def size(path):
    st = os.stat(path)
    return st[6]

def exits(path):
    try:
        os.stat(path)
        return True
    except:
        return False


def clean(path):
    is_abs = path[0] == "/"
    p = "/".join([i for i in path.split('/') if i])
    if is_abs:
        p = "/" + p
    return p