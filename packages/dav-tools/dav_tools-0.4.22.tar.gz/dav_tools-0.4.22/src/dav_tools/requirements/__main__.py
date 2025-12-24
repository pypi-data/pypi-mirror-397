from .. import argument_parser, ArgumentAction
from . import _require_root, _require_os

if __name__ == '__main__':
    '''Allow requirements from other programs'''

    argument_parser.set_description('Set script requirements')
    argument_parser.set_developer_info('Davide Ponzini', 'davide.ponzini95@gmail.com')

    argument_parser.add_argument('--root', action=ArgumentAction.STORE_TRUE, help='script needs to be run with admin privileges')
    argument_parser.add_argument('--os', nargs='+', help='script can only be run on these OSes')

    if argument_parser.args.root:
        _require_root(auto_elevate=False)

    if argument_parser.args.os:
        _require_os(*argument_parser.args.os)