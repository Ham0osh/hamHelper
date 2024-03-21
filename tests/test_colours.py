"""Unit testing for colours module."""

# %------------------- Helper Tests -------------------%
# Test that all entries in colorlists contain valid hex values
import hamhelper.colours as hc
import numpy as np

@np.vectorize
def validateHex(hexkey: str):
    lengthVal = len(hexkey) == 7
    hashVal = hexkey[0] == '#'
    charVal = hexkey[1:].asalnum()
    return np.conditional_and(lengVal, hashVal, charVal)
    

def test_named_hex_lists(capsys):
    """Test the lists of named colormap and named color lists"""
    
    for colours in [hc.colmaps, hc.colsets]:
        for name, hex_list in colours:  
            # Check all hex keys are valid
            for _ in hex_list:
                hexValidation = validateHex(np.array(hex_list))
                assert np.all(hexValidation), f"Hex color values provided in {name} are invalid."
            
        # Check no duplicates
        names = list(colours.keys())
        assert len(names) == len(set(names)), f'There are duplicate named colour sets/maps in this library.'
        
    assert captured.out == ''
    assert captured.err == '', f'Error encountered when testing named hexlists.'
    

def test_hex2rgb(capsys):
    """Test the propper hex to rgb conversion assuming Adobe colorspace"""
    knownHex = ['#FFFFFF', '#000000', '#4C9900', '#9933FF', '#FFB266']
    knownRGB = [(255, 255, 255), (0, 0, 0), (76, 153, 0), (153, 51, 255), (255, 178, 102)]
    
    for hexi, rgb in zip(knownHex, knownRGB):
        assert list(rgb) == hc.hex_to_rgb(hexi), f'Hex value {hexi} does not match RGB value {rgb}.'
  
    assert captured.out == ''
    assert captured.err == '', f'Error encountered when testing colours.hex_to_rgb().'


def test_rgb2dec(capsys):
    """Test for expected outputs for RGB /255 to dec /1 conversion"""
    knownRGB = [(255, 255, 255), (0, 0, 0), (123, 123, 123), (60, 120, 180)]
    knownDec = [[1, 1, 1], [0, 0, 0], [123/255, 123/255, 123/255], [60/255, 120/255, 180/255]]
    tolerance = 1e-8  # Because devision can be silly
    
    for rgb, dec in zip(knownRGB, knownDec):
        assert np.sum(np.array(dec) - np.array(hc.rgb_to_dec(list(rgb)))) <= tolerance, f'RGB value {rgb} does not match expected dec value witin {tolerance:.2e}.' 
    
    assert captured.out == ''
    assert captured.err == '', f'Error encountered when testing colours.rgb_to_dec().'
 

def test_rgb2hexlist(capsys):
    knownHex = ['#FFFFFF', '#000000', '#4C9900', '#9933FF', '#FFB266']
    knownRGB = [(255, 255, 255), (0, 0, 0), (76, 153, 0), (153, 51, 255), (255, 178, 102)]
    
    assert knownHex == hc.rgb_to_hexlist(knownRGB), f'RGB values do not match expected hex values.'
   
    assert captured.out == ''
    assert captured.err == '', f'Error encountered when testing colours.rgb_to_hexlist().'


# %----------------------------------------------------%


# Test HamColour constructors:
# From custom name

# From mpl.Colormap names

# From hexlist

# From eighted hexlist


# Test Hamcolor actions
# Test revrse map

# test truncate

# Test adding

# test repr

# assert valid cmap returned


# Test HamColor Errors
# Empty colorlist

# Nonexistent name
