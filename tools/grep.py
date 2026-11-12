"""The grep tool: finds the lines in files that match a regex."""

import glob
import re
from tools.ls import is_path_safe


def grep(regex, path):
    r"""Return every line in the files matching path that matches the regex.

    >>> import os, tempfile
    >>> old_folder = os.getcwd()
    >>> os.chdir(tempfile.mkdtemp())
    >>> with open('a.txt', 'w') as f:
    ...     _ = f.write('TODO: fix\nall good\n')
    >>> with open('b.txt', 'w') as f:
    ...     _ = f.write('nothing\nTODO later\n')
    >>> with open('bad.bin', 'wb') as f:
    ...     _ = f.write(b'\xff\xfe')
    >>> grep('TODO', 'a.txt')
    'TODO: fix'
    >>> grep('TODO', '*.txt')
    'TODO: fix\nTODO later'
    >>> grep('^all', 'a.txt')
    'all good'
    >>> grep('zzz', '*.txt')
    ''
    >>> grep('TODO', '*')
    'TODO: fix\nTODO later'
    >>> grep('[', 'a.txt')
    'Error: invalid regex'
    >>> grep('TODO', '/etc/*')
    'Error: unsafe path'
    >>> grep('TODO', '../*')
    'Error: unsafe path'
    >>> os.chdir(old_folder)
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    try:
        pattern = re.compile(regex)
    except re.error:
        return 'Error: invalid regex'
    matches = []
    for filename in sorted(glob.glob(path)):
        try:
            with open(filename, encoding='utf-8') as f:
                for line in f:
                    if pattern.search(line):
                        matches.append(line.rstrip('\n'))
        except Exception:
            continue
    return '\n'.join(matches)