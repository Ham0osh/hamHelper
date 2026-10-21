"""Unit testing for colours module."""

# %------------------- Helper Tests -------------------%
# Test that all entries in colour lists contain valid hex values
import hamhelper.colours as hc
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest


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


# %------------------- get_continuous_cmap -------------------%
def test_continuous_cmap_float_list_and_single_colour():
    """A numpy float_list used to raise (ambiguous truth value) and a one colour list used to raise too."""
    cmap = hc.get_continuous_cmap(['#000000', '#ff0000', '#ffffff'], float_list=np.array([0., 0.25, 1.]))
    assert np.allclose(cmap(0.25)[:3], (1, 0, 0), atol=0.01)

    white = hc.get_continuous_cmap(['#FFFFFF'], name='just_white')
    assert white.name == 'just_white'
    assert np.allclose(white(0.0)[:3], (1, 1, 1)) and np.allclose(white(1.0)[:3], (1, 1, 1))


def test_display_my_maps_runs():
    hc.display_my_maps()
    assert len(plt.get_fignums()) == 1


def test_colours_lists_names(capsys):
    hc.colours()
    out = capsys.readouterr().out
    for name in hc.all_col:
        assert name in out


# %------------------- HamColour constructors -------------------%
def test_hamcolour_from_name_custom():
    col = hc.HamColour.from_name('ptol_sunset')
    assert col.name == 'ptol_sunset'
    assert len(col) == len(hc.colmaps['ptol_sunset'])
    assert col._created_from == 'named hexidecimal list'
    hexes = [h[:7].lower() for h in col.get_hexlist()]
    assert hexes[0] == hc.colmaps['ptol_sunset'][0].lower()
    assert hexes[-1] == hc.colmaps['ptol_sunset'][-1].lower()


def test_hamcolour_from_name_matplotlib():
    col = hc.HamColour.from_name('viridis', length=5)
    assert col.name == 'viridis' and len(col) == 5
    assert col._created_from == 'named mpl.Colormap'
    assert np.allclose(col(0.0), mpl.colormaps['viridis'](0.0))


def test_hamcolour_from_name_unknown_gives_white(capsys):
    """An unknown name prints a message and falls back to a one colour white map (this used to raise)."""
    col = hc.HamColour.from_name('definitely_not_a_colormap')
    assert 'Argument Error' in capsys.readouterr().out
    assert len(col) == 1
    assert np.allclose(col(0.5)[:3], (1, 1, 1))


def test_hamcolour_from_hex():
    col = hc.HamColour.from_hex('mine', ['#000000', '#ffffff'])
    assert col.name == 'mine' and len(col) == 2
    assert col._created_from == 'custom hexidecimal list'


@pytest.mark.parametrize('locations', [[0, 0.5, 1], [0, 50, 100]])
def test_hamcolour_from_hex_gradient(locations):
    """Locations above 1 are rescaled to [0, 1]. (The rescale used to be skipped, then crash on an array.)"""
    col = hc.HamColour.from_hex_gradient('grad', ['#000000', '#ff0000', '#ffffff'], locations)
    assert np.allclose(col(0.5)[:3], (1, 0, 0), atol=0.01)


# %------------------- HamColour actions -------------------%
def test_hamcolour_reverse():
    col = hc.HamColour.from_name('ptol_sunset')
    for rev in (-col, reversed(col)):
        assert rev.name == 'ptol_sunset_r'
        assert np.allclose(rev(0.0), col(1.0)) and np.allclose(rev(1.0), col(0.0))
    assert (+col) is col


def test_hamcolour_truncate():
    col = hc.HamColour.from_name('ptol_sunset')
    new = col.truncate(0.2, 0.8, update=False)
    assert new.name == 'ptol_sunset-truncated(0.20,0.80)'
    assert col.name == 'ptol_sunset', 'update=False must leave the original alone'
    assert np.allclose(new(0.0), col(0.2), atol=0.01) and np.allclose(new(1.0), col(0.8), atol=0.01)

    assert col.truncate(0.2, 0.8) is None
    assert col.name == new.name


def test_hamcolour_add():
    a, b = hc.HamColour.from_name('ptol_bright'), hc.HamColour.from_name('ptol_high-contrast')
    total = a
    total += b
    assert total.name == 'ptol_bright+ptol_high-contrast'
    assert len(total) == len(a) + len(b) == 12


def test_hamcolour_repr_eq_str():
    """repr used to raise AttributeError ('__name__'), and == is built on repr."""
    col = hc.HamColour.from_name('ptol_sunset')
    assert repr(col).startswith("HamColour(name='ptol_sunset'")
    assert col == hc.HamColour.from_name('ptol_sunset')
    assert col != hc.HamColour.from_name('ptol_bright')
    assert str(col).startswith('ptol_sunset from 11 colors')


def test_hamcolour_iter_and_length_setter():
    """iter() used to raise TypeError because __iter__ returned the Cycler rather than an iterator."""
    col = hc.HamColour.from_name('viridis', length=5)
    cycle = list(col)
    assert len(cycle) == 5 and 'color' in cycle[0]
    col.length = 3
    assert len(col) == 3 and len(list(col)) == 3
    assert col[0] == col.get_hexlist()[0]


def test_hamcolour_call_clamps(capsys):
    col = hc.HamColour.from_name('viridis')
    assert np.allclose(col(-1), col(0)) and 'Value Error' in capsys.readouterr().out
    assert np.allclose(col(2), col(1)) and 'Value Error' in capsys.readouterr().out


@pytest.mark.parametrize('N', [None, 1, 2, 3, 4, 9])
def test_hamcolour_test_figure(N):
    """HamColour.test passed `map=` to imshow, which matplotlib rejects."""
    hc.HamColour.from_name('ptol_sunset').test(N=N)
    assert len(plt.get_fignums()) == 1


def test_hamcolour_test_rejects_bad_n():
    with pytest.raises(ValueError):
        hc.HamColour.from_name('ptol_sunset').test(N=0)


def test_hamcolour_example_map_without_basemap(capsys):
    """Basemap is an optional extra; without it example_map reports and returns 0 rather than raising."""
    try:
        import mpl_toolkits.basemap  # noqa: F401
        pytest.skip('Basemap is installed.')
    except ImportError:
        pass
    assert hc.HamColour.from_name('ptol_sunset').example_map(plt.figure().gca()) == 0
    assert 'ImportError' in capsys.readouterr().out
