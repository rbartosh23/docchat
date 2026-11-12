"""A command-line chat program that answers questions about files using tools."""
import argparse
import json
import os
from dotenv import load_dotenv
from groq import Groq

from tools.calculate import calculate
from tools.cat import cat
from tools.grep import grep
from tools.ls import ls

load_dotenv()

SYSTEM = ("You're a helpful assistant that answers questions about the "
          "files in the current folder. Use your tools to look at them.")

FUNCTIONS = {'calculate': calculate, 'ls': ls, 'cat': cat, 'grep': grep}

TOOLS = [
    {'type': 'function', 'function': {
        'name': 'calculate',
        'description': 'Evaluate an arithmetic expression like 2 + 3 * 4.',
        'parameters': {
            'type': 'object',
            'properties': {'expression': {'type': 'string'}},
            'required': ['expression'],
        },
    }},
    {'type': 'function', 'function': {
        'name': 'ls',
        'description': 'List the files in a folder. Defaults to the current folder.',
        'parameters': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': [],
        },
    }},
    {'type': 'function', 'function': {
        'name': 'cat',
        'description': 'Read the contents of a text file.',
        'parameters': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    }},
    {'type': 'function', 'function': {
        'name': 'grep',
        'description': 'Find lines matching a regex in files. The path may use globs like *.py.',
        'parameters': {
            'type': 'object',
            'properties': {
                'regex': {'type': 'string'},
                'path': {'type': 'string'},
            },
            'required': ['regex', 'path'],
        },
    }},
]


def llm(messages, temperature=1, tools=None):
    """Send the conversation to the model and return its whole reply message."""
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    options = {}
    if tools:
        options['tools'] = tools
    completion = client.chat.completions.create(
        messages=messages,
        model='openai/gpt-oss-20b',
        temperature=temperature,
        timeout=30,
        **options,
    )
    return completion.choices[0].message


class Chat:
    r"""A conversation with a model that can run tools two ways.

    Tools run automatically when the model asks for them (send_message), or
    manually when the user types a /command (run_manual_command). With
    debug=True, every automatic tool call is printed as it runs.

    >>> chat = Chat()
    >>> chat.run_tool('calculate', {'expression': '2 + 3'})
    '5'
    >>> chat.run_tool('nope', {})
    'Error: unknown tool'
    >>> chat.run_tool('cat', {'wrong_name': 'x'})
    'Error: bad arguments'
    >>> chat.run_manual_command('/calculate 2 * 4')
    '8'
    >>> chat.messages[-1]['content']
    '/calculate 2 * 4\n8'
    >>> chat.run_manual_command('/nope')
    'Error: unknown command'
    >>> chat.run_manual_command('/ls /etc')
    'Error: unsafe path'
    >>> chat.run_manual_command('/ls a b c')
    'Error: wrong number of arguments'

    Debug mode prints the tool name and its arguments, then still runs it:

    >>> chat = Chat(debug=True)
    >>> chat.run_tool('calculate', {'expression': '1 + 1'})
    [tool] calculate {'expression': '1 + 1'}
    '2'
    """

    def __init__(self, system="You're a helpful assistant.", debug=False):
        self.messages = [{'role': 'system', 'content': system}]
        self.debug = debug

    def run_tool(self, name, arguments):
        """Run the named tool using a dictionary of arguments."""
        if self.debug:
            print(f'[tool] {name} {arguments}')
        if name not in FUNCTIONS:
            return 'Error: unknown tool'
        try:
            return str(FUNCTIONS[name](**arguments))
        except TypeError:
            return 'Error: bad arguments'

    def run_manual_command(self, line):
        """Run a typed /command and add its output to the conversation."""
        parts = line[1:].split()
        if not parts or parts[0] not in FUNCTIONS:
            return 'Error: unknown command'
        name = parts[0]
        args = parts[1:]
        if name == 'calculate':
            args = [' '.join(args)]
        try:
            output = str(FUNCTIONS[name](*args))
        except TypeError:
            return 'Error: wrong number of arguments'
        self.messages.append({'role': 'user', 'content': line + '\n' + output})
        return output

    def send_message(self, message, temperature=0.8):
        """Send a message, run any tools the model asks for, and return the answer.

        >>> from types import SimpleNamespace
        >>> from unittest.mock import patch
        >>> def fake_reply(content=None, calls=None):
        ...     reply = SimpleNamespace(content=content, tool_calls=calls)
        ...     dump = {'role': 'assistant', 'content': content}
        ...     reply.model_dump = lambda exclude_none=True: dump
        ...     return reply
        >>> with patch('chat.llm', side_effect=[fake_reply('Hello!')]):
        ...     chat = Chat(system='Be brief.')
        ...     print(chat.send_message('Hi', temperature=0))
        Hello!
        >>> chat.messages[-1]
        {'role': 'assistant', 'content': 'Hello!'}

        Now the model asks for a tool, and we answer it with the result:

        >>> function = SimpleNamespace(
        ...     name='calculate', arguments='{"expression": "2 + 3"}')
        >>> call = SimpleNamespace(id='call-1', function=function)
        >>> replies = [fake_reply(calls=[call]), fake_reply('The answer is 5.')]
        >>> with patch('chat.llm', side_effect=replies):
        ...     chat = Chat()
        ...     print(chat.send_message('What is 2 + 3?', temperature=0))
        The answer is 5.
        >>> chat.messages[-2]
        {'role': 'tool', 'tool_call_id': 'call-1', 'content': '5'}
        """
        self.messages.append({'role': 'user', 'content': message})
        while True:
            reply = llm(self.messages, temperature=temperature, tools=TOOLS)
            self.messages.append(reply.model_dump(exclude_none=True))
            if not reply.tool_calls:
                return reply.content
            for call in reply.tool_calls:
                arguments = json.loads(call.function.arguments)
                result = self.run_tool(call.function.name, arguments)
                self.messages.append({
                    'role': 'tool',
                    'tool_call_id': call.id,
                    'content': result,
                })


def repl(temperature=0.8, debug=False):
    """Chat until the user exits.

    Two inputs, then end-of-input (EOFError):

    >>> from unittest.mock import patch
    >>> inputs = ['Hi', 'Who are you?', EOFError]
    >>> replies = ['Hello!', 'A helpful assistant.']
    >>> with patch('builtins.input', side_effect=inputs):
    ...     with patch.object(Chat, 'send_message', side_effect=replies):
    ...         repl(temperature=0)
    Hello!
    A helpful assistant.
    <BLANKLINE>

    Ctrl-C (KeyboardInterrupt) also exits cleanly:

    >>> with patch('builtins.input', side_effect=['Hi', KeyboardInterrupt]):
    ...     with patch.object(Chat, 'send_message', side_effect=['Hello!']):
    ...         repl(temperature=0)
    Hello!
    <BLANKLINE>

    A /command runs a tool directly, with no model request:

    >>> with patch('builtins.input', side_effect=['/calculate 1 + 2', EOFError]):
    ...     repl()
    3
    <BLANKLINE>
    """
    chat = Chat(system=SYSTEM, debug=debug)
    try:
        while True:
            user_input = input('chat> ')
            if not user_input.strip():
                continue
            if user_input.startswith('/'):
                print(chat.run_manual_command(user_input))
            else:
                try:
                    print(chat.send_message(user_input, temperature=temperature))
                except Exception as error:
                    print('Error:', error)
    except (KeyboardInterrupt, EOFError):
        print()


def main(argv=None):
    """Run the command line: chat, chat "message", or chat --debug.

    With a message, send just that message and print the reply. Without one,
    start the interactive chat.

    >>> from unittest.mock import patch
    >>> with patch.object(Chat, 'send_message', return_value='Hello!'):
    ...     main(['Hi'])
    Hello!
    >>> with patch.object(Chat, 'send_message', side_effect=OSError('down')):
    ...     main(['Hi'])
    Error: down
    >>> with patch('builtins.input', side_effect=[EOFError]):
    ...     main(['--debug'])
    <BLANKLINE>
    """
    parser = argparse.ArgumentParser(
        description='Chat about the files in the current folder.')
    parser.add_argument('message', nargs='?',
                        help='send this one message, print the reply, and exit')
    parser.add_argument('--debug', action='store_true',
                        help='print each tool call (name and arguments)')
    args = parser.parse_args(argv)
    if args.message is None:
        repl(debug=args.debug)
        return
    chat = Chat(system=SYSTEM, debug=args.debug)
    try:
        print(chat.send_message(args.message))
    except Exception as error:
        print('Error:', error)


if __name__ == '__main__':
    main()
