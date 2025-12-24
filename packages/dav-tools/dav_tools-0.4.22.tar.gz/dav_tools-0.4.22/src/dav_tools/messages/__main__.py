from . import info, success, warning, error, critical_error, ask, ask_continue

if __name__ == '__main__':
    '''Allow basic printing from other programs'''
    from .. import argument_parser

    argument_parser.set_description('Display a message with style')
    argument_parser.set_developer_info('Davide Ponzini', 'davide.ponzini95@gmail.com')

    argument_parser.add_argument('message_type',
                                 choices=['info', 'success', 'warning', 'error', 'critical_error', 'ask', 'ask_continueN', 'ask_continueY'],
                                 help='Message type')
    argument_parser.add_argument('message', nargs='*')
    
    mess_type = argument_parser.args.message_type
    mess_text = argument_parser.args.message

    if mess_type == 'info':
        info(*mess_text)
    
    elif mess_type == 'success':
        success(*mess_text)
    
    elif mess_type == 'warning':
        warning(*mess_text)
    
    elif mess_type == 'error':
        error(*mess_text)

    elif mess_type == 'critical_error':
        critical_error(*mess_text)
    
    elif mess_type == 'ask':
        print(ask(mess_text[0]))
    
    elif mess_type == 'ask_continueN':
        ask_continue(mess_text[0] if len(mess_text) > 0 else None, default_yes=False)

    elif mess_type == 'ask_continueY':
        ask_continue(mess_text[0] if len(mess_text) > 0 else None, default_yes=True)