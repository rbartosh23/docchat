"""The cat tool: reads a text file and returns what is inside it."""

from tools.ls import is_path_safe


def cat(path):
    r"""Return the contents of a text file, or an error message.

    >>> import os, tempfile
    >>> old_folder = os.getcwd()
    >>> os.chdir(tempfile.mkdtemp())
    >>> with open('hello.txt', 'w') as f:
    ...     _ = f.write('hi there\n')
    >>> cat('hello.txt')
    'hi there\n'
    >>> cat('missing.txt')
    'Error: file not found'
    >>> with open('bad.bin', 'wb') as f:
    ...     _ = f.write(b'\xff\xfe\xfa')
    >>> cat('bad.bin')
    'Error: not a text file'
    >>> cat('.')
    'Error: could not read file'
    >>> cat('/etc/passwd')
    'Error: unsafe path'
    >>> cat('../secret.txt')
    'Error: unsafe path'
    >>> os.chdir(old_folder)
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except UnicodeDecodeError:
        return 'Error: not a text file'
    except Exception:
        return 'Error: could not read file'
