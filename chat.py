import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

def llm(messages, temperature=1):
    completion = client.chat.completions.create(
        messages=messages,
        model='openai/gpt-oss-20b',
        temperature=temperature,
    )
    return completion.choices[0].message.content


class Chat:
    def __init__(self, system="You're a helpful assistant."):
        self.messages = [{'role': 'system', 'content': system}]

    def send_message(self, message, temperature=0.8):
        """Send a message and retain the reply

        >>> from unittest.mock import MagicMock, patch
        >>> first = MagicMock()
        >>> first.choices[0].message.content = 'Hello!'
        >>> second = MagicMock()
        >>> second.choices[0].message.content = 'You said Hi.'
        >>> responses = [first, second]
        >>> sent = []
        >>> def fake_create(messages, **kwargs):
        ...     sent.append(list(messages))
        ...     return responses.pop(0)
        >>> with patch.object(client.chat.completions, 'create', side_effect=fake_create):
        ...     chat = Chat(system='Be brief.')
        ...     print(chat.send_message('Hi', temperature=0))
        ...     print(chat.send_message('What did I say?', temperature=0))
        Hello!
        You said Hi.
        >>> sent[1] == [
        ...     {'role': 'system', 'content': 'Be brief.'},
        ...     {'role': 'user', 'content': 'Hi'},
        ...     {'role': 'assistant', 'content': 'Hello!'},
        ...     {'role': 'user', 'content': 'What did I say?'},
        ... ]
        True
        >>> chat.messages[-1]
        {'role': 'assistant', 'content': 'You said Hi.'}
        """
        self.messages.append({'role': 'user', 'content': message})
        reply = llm(self.messages, temperature=temperature)
        self.messages.append({'role': 'assistant', 'content': reply})
        return reply


def repl(temperature=0.8):
    """Chat until the user exits.

    Two inputs, then end-of-input (EOFError):

    >>> from unittest.mock import MagicMock, patch
    >>> first = MagicMock()
    >>> first.choices[0].message.content = 'Hello!'
    >>> second = MagicMock()
    >>> second.choices[0].message.content = 'A helpful assistant.'
    >>> inputs = ['Hi', 'Who are you?', EOFError]
    >>> with patch('builtins.input', side_effect=inputs):
    ...     with patch.object(client.chat.completions, 'create', side_effect=[first, second]):
    ...         repl(temperature=0)
    Hello!
    A helpful assistant.
    <BLANKLINE>

    Ctrl-C (KeyboardInterrupt) also exits cleanly:

    >>> first = MagicMock()
    >>> first.choices[0].message.content = 'Hello!'
    >>> inputs = ['Hi', KeyboardInterrupt]
    >>> with patch('builtins.input', side_effect=inputs):
    ...     with patch.object(client.chat.completions, 'create', side_effect=[first]):
    ...         repl(temperature=0)
    Hello!
    <BLANKLINE>
    """
    chat = Chat(system= "You're a helpful assistant.")
    try:
        while True:
            user_input = input('chat> ')
            print(chat.send_message(user_input, temperature=temperature))
    except (KeyboardInterrupt, EOFError):
            print()

if __name__ == '__main__':
    repl()