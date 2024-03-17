"""Test cases for main init"""
from hamhelper import hello_world


def test_hello_world(capsys):
    """Test hello world function"""
    hello_world()
    captured = capsys.readouterr()
    assert captured.out == 'This is my first pip package!\n'
    assert captured.err == ''
