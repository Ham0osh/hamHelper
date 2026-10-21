"""Unit testing for colours module."""

# %------------------- Helper Tests -------------------%
# Test that all entries in colour lists contain valid hex values
import hamhelper.colours as hc
import matplotlib as mpl
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
        errorMessage = f'RGB values do not match expected hex values. Yields {test} instead of {reference}'
        assert test.lower() == reference.lower(), errorMessage

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == '', 'Error encountered when testing colours.rgb_to_hexlist().'


def test_register_cmaps():
    """register_cmaps must work on current matplotlib (mpl.cm.register_cmap was removed in 3.9)."""
    names = hc.register_cmaps()
    assert names == set(hc.all_col.keys())
    for name in names:
        assert name in mpl.colormaps, f'{name} was not registered.'
        assert name + '_r' in mpl.colormaps, f'{name}_r was not registered.'

    # the reversed map really is reversed at the ends
    forward, backward = mpl.colormaps['ptol_sunset'], mpl.colormaps['ptol_sunset_r']
    assert np.allclose(forward(0.0), backward(1.0))
    assert np.allclose(forward(1.0), backward(0.0))

    # calling again is allowed, and a custom dictionary only registers its own entries
    assert hc.register_cmaps() == names
    assert hc.register_cmaps({'hh_test_map': ['#000000', '#ffffff']}) == {'hh_test_map'}
    assert np.allclose(mpl.colormaps['hh_test_map'](0.0)[:3], (0, 0, 0))
    assert np.allclose(mpl.colormaps['hh_test_map_r'](0.0)[:3], (1, 1, 1))


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
