"""The load_image tool: adds a local PNG picture to the conversation."""
import base64
from tools.ls import is_path_safe


def load_image(chat, path):
    r"""Add the PNG at a relative path to chat.messages as an image message.

    >>> import os, tempfile
    >>> from types import SimpleNamespace
    >>> old_folder = os.getcwd()
    >>> os.chdir(tempfile.mkdtemp())
    >>> with open('dot.png', 'wb') as f:
    ...     _ = f.write(b'\x89PNG')
    >>> chat = SimpleNamespace(messages=[])
    >>> load_image(chat, 'dot.png')
    'Loaded dot.png'
    >>> chat.messages == [{'role': 'user', 'content': [{
    ...     'type': 'image_url',
    ...     'image_url': {'url': 'data:image/png;base64,iVBORw=='},
    ... }]}]
    True

    Bad paths leave the conversation unchanged:

    >>> load_image(chat, '/etc/dot.png')
    'Error: unsafe path'
    >>> load_image(chat, '../dot.png')
    'Error: unsafe path'
    >>> load_image(chat, 'missing.png')
    'Error: file not found'
    >>> load_image(chat, 'notes.txt')
    'Error: only PNG images are supported'
    >>> load_image(chat, '.')
    'Error: only PNG images are supported'
    >>> os.mkdir('folder.png')
    >>> load_image(chat, 'folder.png')
    'Error: could not read file'
    >>> len(chat.messages)
    1
    >>> os.chdir(old_folder)
    """
    if not is_path_safe(path):
        return 'Error: unsafe path'
    if not path.lower().endswith('.png'):
        return 'Error: only PNG images are supported'
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        return 'Error: file not found'
    except Exception:
        return 'Error: could not read file'
    encoded = base64.b64encode(data).decode('ascii')
    chat.messages.append({'role': 'user', 'content': [{
        'type': 'image_url',
        'image_url': {'url': 'data:image/png;base64,' + encoded},
    }]})
    return 'Loaded ' + path
