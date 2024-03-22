"""Unit testing for colours module."""

# %------------------- Helper Tests -------------------%
# Test that all entries in colour lists contain valid hex values
import hamhelper.colours as hc
import numpy as np


@np.vectorize
def validateHex(hex_key: str):
    lengthVal = len(hex_key) == 7
    hashVal = hex_key[0] == '#'
    charVal = hex_key[1:].isalnum()
    return np.logical_and(np.logical_and(lengthVal, hashVal), charVal)


def test_named_hex_lists(capsys):
    """Test the lists of named colormap and named color lists"""

    for colours in [hc.colmaps, hc.colsets]:
        for name, hex_list in colours.items():
            # Check all hex keys are valid
            for _ in hex_list:
                hexValidation = validateHex(np.array(hex_list))
                assert np.all(hexValidation), f"Hex color values provided in {name} are invalid."

        # Check no duplicates
        names = list(colours.keys())
        assert len(names) == len(set(names)), 'There are duplicate named colour sets/maps in this library.'

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == '', 'Error encountered when testing named hex lists.'


def test_hex2rgb(capsys):
    """Test the proper hex to rgb conversion assuming Adobe colour space"""
    knownHex = ['#FFFFFF', '#000000', '#4C9900', '#9933FF', '#FFB266']
    knownRGB = [(255, 255, 255), (0, 0, 0), (76, 153, 0), (153, 51, 255), (255, 178, 102)]
    tolerance = 1e-8  # Because division can be silly

    for hex_value, rgb in zip(knownHex, knownRGB):
        errMessage = f'Hex value {hex_value} does not match RGB value {rgb}.'
        assert np.sum(np.array(rgb) - hc.hex_to_rgb(hex_value)) <= tolerance, errMessage

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == '', 'Error encountered when testing colours.hex_to_rgb().'


def test_rgb2dec(capsys):
    """Test for expected outputs for RGB /255 to dec /1 conversion"""
    knownRGB = [(255, 255, 255), (0, 0, 0), (123, 123, 123), (60, 120, 180)]
    knownDec = [[1, 1, 1], [0, 0, 0], [123/255, 123/255, 123/255], [60/255, 120/255, 180/255]]
    tolerance = 1e-8  # Because division can be silly

    for rgb, dec in zip(knownRGB, knownDec):
        errMessage = f'RGB value {rgb} does not match expected dec value within {tolerance:.2e}.'
        assert np.sum(np.array(dec) - np.array(hc.rgb_to_dec(list(rgb)))) <= tolerance, errMessage

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == '', 'Error encountered when testing colours.rgb_to_dec().'


def test_rgb2hexlist(capsys):
    knownHex = ['#FFFFFF', '#000000', '#4C9900', '#9933FF', '#FFB266']
    knownRGB = [(255, 255, 255), (0, 0, 0), (76, 153, 0), (153, 51, 255), (255, 178, 102)]

    testHex = hc.rgb_list_to_hex(knownRGB)
    for test, reference in zip(testHex, knownHex):
        assert test == reference, f'RGB values do not match expected hex values. Yields {test} instead of {reference}'

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == '', 'Error encountered when testing colours.rgb_to_hexlist().'


# %----------------------------------------------------%


# Test HamColour constructors:
# From custom name

# From mpl.Colormap names

# From hexlist

# From weighted hexlist


# Test HamColor actions
# Test reverse map

# test truncate

# Test adding

# test repr

# assert valid cmap returned


# Test HamColor Errors
# Empty colorlist

# Nonexistent name
