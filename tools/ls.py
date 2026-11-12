"""The ls tool: lists files in a folder, and checks that paths are safe."""

import glob
import os


def is_path_safe(path):
    """Return True if the path is relative and does not contain '..'.

    >>> is_path_safe('notes.txt')
    True
    >>> is_path_safe('docs/notes.txt')
    True
    >>> is_path_safe('/etc/passwd')
    False
    >>> is_path_safe('../secret.txt')
    False
    >>> is_path_safe('docs/../../secret.txt')
    False
    """
    if os.path.isabs(path) or path.startswith('/'):
        return False
    if '..' in path:
        return False
    return True


def ls(path='.'):
    """List the files in a folder, sorted, separated by two spaces.

    >>> import os, tempfile
    >>> old_folder = os.getcwd()
    >>> os.chdir(tempfile.mkdtemp())
    >>> open('b.txt', 'w').close()
    >>> open('a.txt', 'w').close()
    >>> ls()
    'a.txt  b.txt'
    >>> ls('.')
    'a.txt  b.txt'
    >>> ls('/etc')
    'Error: unsafe path'
    >>> os.chdir(old_folder)
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    files = glob.glob(os.path.join(path, '*'))
    names = sorted(os.path.basename(f) for f in files)
    return '  '.join(names)