from dav_tools import commands
import platform


def test_get_output_ok():
    assert commands.get_output('echo TEST123', on_success=lambda x: x.decode(), stdin=None) == 'TEST123\n'

def test_get_output_error():
    if platform.system() == 'Windows':
        assert commands.get_output('cmd /c exit 1', on_success=lambda x: x.decode(), on_error=lambda: b'ERROR', stdin=None) == 'ERROR'
    else:
        assert commands.get_output('false', on_success=lambda x: x.decode(), on_error=lambda: b'ERROR', stdin=None) == 'ERROR'

def test_is_installed_existing():
    if platform == 'Windows':
        assert commands.is_installed('cmd')
    elif platform == 'Linux':
        assert commands.is_installed('ls')

def test_is_installed_non_existing():
    assert not commands.is_installed('non_existing_command')

    