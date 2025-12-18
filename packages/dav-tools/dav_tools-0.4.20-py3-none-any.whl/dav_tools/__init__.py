'''Python library to aid in software development.'''

# SUBMODULES
from . import commands, messages, devtools, files, requirements

# ARGUMENT PARSER
#   Hides package and only shows one instance of the class
from ._arg_parser import ArgumentAction, ArgumentParser as _ArgumentParser

argument_parser = _ArgumentParser()
'''Argument parser instance -- use this instead of importing the ``_arg_parser`` module.'''

# ...