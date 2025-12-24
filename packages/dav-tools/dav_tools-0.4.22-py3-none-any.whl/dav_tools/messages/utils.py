'''
Utility functions for messages.
'''

from .formatted_text import FormattedText

import sys as _sys
import os as _os
import getpass as _getpass

def read_input(*format_options: bytes, secret: bool = False, file=_sys.stderr) -> str:
    '''
    Ask input from a user using specified styling options.

    :param format_options: Text styling options.
    :param secret: Whether to hide the input.
    :param file: Stream to use for output.

    :returns: User input.
    '''

    result = None
    format = FormattedText('', *format_options)

    try:
        print(format.get_format(), file=file, end='')
        if secret:
            result = _getpass.getpass(prompt='')
        else:
            result = input()
        print(format.reset_format(), file=file, end='')
    except KeyboardInterrupt as e:
        print(format.reset_format(), file=file, end='')
        raise e

    return result

def clear_line(file=_sys.stdout, flush: bool = False) -> None:
    '''
    Clears the current line from any text of formatting.
    Not really suitable for files.

    :param file: Stream to clear.
    :param flush: Whether to flush the stream after printing.
    '''
    
    if file is None:
        return

    try:
        size = _os.get_terminal_size().columns
        print('\r', ' ' * size, '\r',
              sep='', end='', file=file, flush=flush)
    except OSError:
        pass    # Do nothing

