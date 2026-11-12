"""The compact tool: replaces a long conversation with a short summary of it."""


def compact(chat):
    r"""Replace chat.messages with one entry holding a summary of at most five lines.

    >>> from types import SimpleNamespace
    >>> from unittest.mock import patch
    >>> chat = SimpleNamespace(messages=[
    ...     {'role': 'system', 'content': 'Be brief.'},
    ...     {'role': 'user', 'content': 'Hi'},
    ...     {'role': 'assistant', 'content': 'Hello!'},
    ... ])
    >>> reply = SimpleNamespace(content='We said hello.')
    >>> with patch('chat.llm', return_value=reply) as fake_llm:
    ...     compact(chat)
    'We said hello.'
    >>> chat.messages
    [{'role': 'system', 'content': 'We said hello.'}]
    >>> len(fake_llm.call_args.args[0])
    4

    A summary longer than five lines is cut to five, and a model that
    returns plain text instead of a message also works:

    >>> chat = SimpleNamespace(messages=[{'role': 'user', 'content': 'Hi'}])
    >>> with patch('chat.llm', return_value='1\n2\n3\n4\n5\n6\n7'):
    ...     compact(chat)
    '1\n2\n3\n4\n5'
    >>> chat.messages
    [{'role': 'system', 'content': '1\n2\n3\n4\n5'}]
    """
    import chat as chat_module  # imported here so tools never need chat.py to load
    ask = {'role': 'user',
           'content': 'Summarize our conversation so far in at most five lines.'}
    reply = chat_module.llm(chat.messages + [ask], temperature=0)
    summary = reply if isinstance(reply, str) else reply.content
    summary = '\n'.join(summary.strip().splitlines()[:5])
    chat.messages[:] = [{'role': 'system', 'content': summary}]
    return summary
