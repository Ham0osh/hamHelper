# -*- coding: utf-8 -*-
"""
My custom colouring helper functions for day to day!
Created on Thu Jan 12 11:49:54 2023

@author: hamishj

Contributions 'borrowed' from:
 - wackywendell/mutedplots:
   https://github.com/wackywendell/mutedplots/blob/master/mutedcolors.py
"""
import os
import warnings
from typing import NamedTuple

from cycler import cycler as _cycler
from hamhelper import _geo
from hamhelper.errors import assert_error  # fixed import
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import numpy as np


# continuous
colmaps = {
        'ptol_sunset':      ['#364B9A', '#4A7BB7', '#6EA6CD', '#98CAE1', '#C2E4EF', '#EAECCC', '#FEDA8B', '#FDB366',
                             '#F67E4B', '#DD3D2D', '#A50026'],
        'ptol_nightfall':   ['#125A56', '#00767B', '#238F9D', '#42A7C6', '#60BCE9', '#9DCCEF', '#C6DBED', '#DEE6E7',
                             '#ECEADA', '#F0E6B2', '#F9D576', '#FFB954', '#FD9A44', '#F57634',  '#E94C1F', '#D11807',
                             '#A01813'],
        'ptol_ylorbr':      ['#FFFFE5', '#FFF7BC', '#FEE391', '#FEC44F', '#FB9A29', '#EC7014', '#CC4C02', '#993404',
                             '#662506'],
        'ptol_iridescent':  ['#FEFBE9', '#FCF7D5', '#F5F3C1', '#EAF0B5', '#DDECBF', '#D0E7CA', '#C2E3D2', '#B5DDD8',
                             '#A8D8DC', '#9BD2E1', '#8DCBE4', '#81C4E7', '#7BBCE7', '#7EB2E4', '#88A5DD', '#9398D2',
                             '#9B8AC4', '#9D7DB2', '#9A709E', '#906388', '#805770', '#684957', '#46353A'],
        'morlnd_ext_bb':    ['#000000', '#0018a8', '#6300e4', '#dc143c', '#ff7538', '#e6e635', '#ffffff'],
        }

# discrete
colsets = {
        'ptol_bright':          ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB',
                                 '#000000'],
        'ptol_vibrant':         ['#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB',
                                 '#000000'],
        'ptol_light':           ['#77AADD', '#EE8866', '#EEDD88', '#FFAABB', '#99DDFF', '#44BB99', '#BBCC33',
                                 '#AAAA00', '#DDDDDD', '#000000'],
        'ptol_muted':           ['#CC6677', '#332288', '#DDCC77', '#117733', '#88CCEE', '#882255', '#44AA99',
                                 '#999933', '#AA4499', '#DDDDDD', '#000000'],
        'ptol_high-contrast':   ['#004488', '#DDAA33', '#BB5566', '#000000'],
        'ptol_medium-contrast': ['#6699CC', '#004488', '#EECC66', '#994455', '#997700', '#EE99AA', '#000000'],
        'ham_simple':           ['#ff0000', '#000000', '#808080'],
        'pone_colorful':        ['#3399ff', '#31aeb4', '#d3eb36', '#fed32c', '#f4337d', '#cc3095'],
        'sfu_tones':            ['#CC0633', '#A6192E', '#e0e0df', '#54585A', '#000000']
        }

# create dict for all colours
all_col = {k: v for d in (colmaps, colsets) for k, v in d.items()}


def colours():
    """Prints list of all my custom colormaps."""
    output = ""
    for key in all_col.keys():
        output += key + ', '
    print(output)


# Colormaps ##################################################################################################
def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#")  # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v/255 for v in value]


def rgb_list_to_hex(rgb_list):
    """Convert list of RGB colours to hexidecimal strings.

    Args:
        rgb_list (list): List of RGB tuples.

    Returns:
        list: List of hexidecimal colour strings.
    """
    col_hex = [mcolors.to_hex(rgb_to_dec(_)) for _ in rgb_list]
    return col_hex


def get_continuous_cmap(hex_list, float_list=None, name: str = 'my_cmap', plot=False):
    '''
    creates and returns a color map that can be used in heat map figures.
    If float_list is not provided, colour map graduates linearly between each color in hex_list.
    If float_list is provided, each color in hex_list is mapped to the respective location in float_list.
    https://towardsdatascience.com/beautiful-custom-colormaps-with-matplotlib-5bab3d1f0e72

    Parameters
    ----------
    hex_list: list of hex code strings
    float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.

    Returns
    ----------
    colour map
    '''
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if len(rgb_list) == 1:
        # A single colour is a constant map. LinearSegmentedColormap needs points at both x=0 and x=1.
        rgb_list = rgb_list * 2
        float_list = [0., 1.]
    elif float_list is None or len(float_list) == 0:
        # (not `if float_list:`, which raises for a numpy array)
        float_list = list(np.linspace(0, 1, len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmp = mcolors.LinearSegmentedColormap(name, segmentdata=cdict, N=256)
    if plot:
        plt.figure(figsize=(6, 1))
        plt.imshow([list(np.arange(0, len(hex_list), 0.1))]*8 , interpolation='nearest', origin='lower', cmap=cmp)
        bounds = plt.gca().get_xlim()
        plt.xticks(bounds, [hex_list[0], hex_list[-1]])
        plt.yticks([])
    return cmp


def display_my_maps(continuous=colmaps, discrete=colsets):
    """Create a test plot for all gives colour maps and colour sets"""
    n = len(continuous)
    m = len(discrete)
    j = np.max([m, n])

    fig, axs = plt.subplots(j, 2, figsize=(6, j*2/3))
    fig.subplots_adjust(hspace=0.9)
    fig.patch.set_facecolor('whitesmoke')

    for i, hexlist in enumerate(list(continuous.values())):
        ax = axs[i, 0]
        ax.imshow([list(np.arange(0, 10 , 0.1))], interpolation='nearest', origin='lower',
                  cmap=get_continuous_cmap(hexlist), aspect='auto')
        ax.set(title=list(continuous.keys())[i])

    for i, hexlist in enumerate(list(discrete.values())):
        ax = axs[i, 1]
        ax.imshow([list(np.arange(0, 10, 10/len(hexlist)))], interpolation='nearest', origin='lower',
                  cmap=get_continuous_cmap(hexlist), aspect='auto')
        ax.set(title=list(discrete.keys())[i])

    for ax in axs.ravel():
        ax.axis('off')
    plt.show()


# Derived colormaps ##########################################################################################
# Maps built from Paul Tol's Sunset, so a sequential panel and a diverging panel in the same document share hues.
# They are plain matplotlib colormaps held in `derived_cmaps`; nothing is registered with matplotlib until you call
# register_cmaps().

#: The warm fraction of Sunset that ham_sunset_warm keeps (cream -> #A50026). Fitted against a printed poster
#: colourbar at RMS 1.21/255, i.e. exact to within rasterisation error.
WARM_FRACTION = 0.45

#: Nodes of ham_sunset_ordered, for series that ARE ordered (time, voltage, temperature): cool to warm.
ORDERED_NODES = ['#364B9A', '#60BCE9', '#CCBB44', '#F67E4B', '#DD3D2D']


def _build_derived_cmaps():
    sunset = get_continuous_cmap(colmaps['ptol_sunset'], name='ptol_sunset')
    warm = sunset(np.linspace(1.0 - WARM_FRACTION, 1.0, 256))

    # Same ramp with its floor pulled to white, for journal figures where empty space should stay page-white
    # rather than read as a filled cream field.
    n_floor = 56
    ramp = (np.linspace(0, 1, n_floor) ** 0.75)[:, None]
    warm_w = warm.copy()
    warm_w[:n_floor] = np.array([1.0, 1.0, 1.0, 1.0]) * (1 - ramp) + warm[:n_floor] * ramp

    maps = {
        'ham_sunset_warm': mcolors.ListedColormap(warm, name='ham_sunset_warm'),
        'ham_sunset_warm_w': mcolors.ListedColormap(warm_w, name='ham_sunset_warm_w'),
        'ham_sunset_ordered': get_continuous_cmap(ORDERED_NODES, name='ham_sunset_ordered'),
    }
    # masked / NaN pixels in an image panel come out page-white, not matplotlib's transparent black
    return {name: cmap.with_extremes(bad='#FFFFFF') for name, cmap in maps.items()}


#: name -> Colormap for the maps derived from Sunset: ham_sunset_warm (sequential, the warm 45% of Sunset),
#: ham_sunset_warm_w (same with the floor at white) and ham_sunset_ordered (cool to warm, five nodes).
derived_cmaps = _build_derived_cmaps()


def ordered(n: int) -> list:
    """n colours for series that ARE ordered (time, voltage, temperature), as hex strings.

    Cool to warm, so the reader can infer the sequence without reading the legend. Do not use for unordered
    categories: that implies an order the data does not have; use a Palette cycle instead. At n=5 this returns
    exactly ORDERED_NODES.
    """
    if n < 2:
        return [ORDERED_NODES[0]]
    nodes = np.array([mcolors.to_rgb(c) for c in ORDERED_NODES])
    at = np.linspace(0, 1, len(nodes))
    rgb = np.stack([np.interp(np.linspace(0, 1, n), at, nodes[:, k]) for k in range(3)], axis=1)
    return [mcolors.to_hex(c).upper() for c in rgb]


def tint(colour, keep: float = 0.25) -> str:
    """`colour` mixed toward white, keeping the fraction `keep` of it: the pale partner for a band or fill.
    keep=0.25 is about L* 88 for a mid-tone colour."""
    r, g, b = mcolors.to_rgb(colour)
    return mcolors.to_hex(tuple(1 - keep * (1 - x) for x in (r, g, b)))


def shade(colour, f: float = 0.85):
    """`colour` darkened to the fraction f of its value, as an RGB tuple: for TEXT that labels a line of that
    colour. A pale step (like #FDB366) makes a line but not legible type on a tinted fill; this keeps the hue and
    restores the contrast."""
    r, g, b = mcolors.to_rgb(colour)
    return (r * f, g * f, b * f)


# Palettes ###################################################################################################
#: Neutral for reference lines, requirement levels and guides to the eye.
GREY = '#777777'

#: Line style and marker per colour slot, used by Palette.cycler(redundancy=...) so slots that look alike in
#: greyscale or to a colour-blind reader still differ in stroke. Slot 1 solid, slot 2 dashed: the pair that is
#: identical in greyscale is also the pair that differs in stroke.
DASHES = ['-', (0, (5, 1.8)), (0, (1.2, 1.4)), (0, (5, 1.5, 1.2, 1.5)),
          '-', (0, (5, 1.8)), (0, (1.2, 1.4)), (0, (5, 1.5, 1.2, 1.5))]
MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', 'h']
_REDUNDANCY = ('off', 'dash', 'marker', 'both')


class Palette(NamedTuple):
    """A colour cycle with everything that goes with it, switched as one unit.

    name   key in PALETTES
    cycle  hex colours in slot order; the first five are the designed set, the other three are overflow so a
           six-series figure never wraps a colour (a wrapped colour is two series wearing one colour)
    names  a name for each colour
    bands  the pale partner of each colour, for +/- 1 sigma bands and fills
    parts  three warm colours for the COMPONENTS of a total drawn in slot 2 (a fit made of parts, a stack)
    """
    name: str
    cycle: tuple
    names: tuple
    bands: tuple
    parts: tuple = ()

    def cycler(self, redundancy: str = 'off'):
        """matplotlib cycler for this palette, for ax.set_prop_cycle() or axes.prop_cycle.

        redundancy  'off' (colour only), 'dash' (also a line style per slot), 'marker' (also a marker per slot,
                    drawn every 11% of the axes diagonal and offset per slot so two lines never put a marker in
                    the same place) or 'both'. For greyscale prints and colour-blind readers.
        """
        if redundancy in (None, False):
            redundancy = 'off'
        if redundancy not in _REDUNDANCY:
            raise ValueError("redundancy must be one of {}, not {!r}".format(', '.join(_REDUNDANCY), redundancy))
        n = len(self.cycle)
        cyc = _cycler(color=list(self.cycle))
        if redundancy in ('dash', 'both'):
            cyc = cyc + _cycler(linestyle=[DASHES[i % len(DASHES)] for i in range(n)])
        if redundancy in ('marker', 'both'):
            cyc = (cyc
                   + _cycler(marker=[MARKERS[i % len(MARKERS)] for i in range(n)])
                   + _cycler(markevery=[(0.012 + 0.023 * i, 0.11) for i in range(n)]))
        return cyc


#: The components of a total drawn in slot 2 (a fit made of parts, a stacked sum): a graded family of the total's red.
#: SUNSET_PARTS come from Sunset itself (11 nodes, counted from 1), so they share a cmap with everything else: nodes
#: 9 and 8 (#F67E4B, #FDB366) and the colour 60% of the way from node 9 to node 10 (#E65538), which is what keeps the
#: first part clear of the default palette's red (#C42E3C). Worst pair among data (slot 1), total (slot 2) and the
#: three parts, CIEDE2000: 10.8 normal / 11.6 protanopia / 7.7 deuteranopia / 8.3 tritanopia. (Sunset's own node 10,
#: #DD3D2D, would be only 9.8 / 9.7 / 8.3 / 6.1: too close to the nudged red.) They only work beside a red that sits
#: in Sunset.
#: TOL_PARTS are Tol's own magenta, orange and sand, for the red of Tol's Vibrant scheme (#CC3311):
#: 18.3 / 15.8 / 12.5 / 8.6 against Tol's blue and red.
SUNSET_PARTS = ('#E65538', '#F67E4B', '#FDB366')
TOL_PARTS = ('#EE3377', '#EE7733', '#DDCC77')

_DEFAULT_CYCLE = ('#29428F', '#C42E3C', '#238F9D', '#F67E4B', '#66CCEE', '#882255', '#BB5566', '#997700')
_DEFAULT_NAMES = ('indigo', 'red', 'teal', 'orange', 'cyan', 'wine', 'rose', 'ochre')
_TOL_CYCLE = ('#0077BB', '#CC3311', '#33BBEE', '#EE7733', '#009988', '#BB5566', '#882255', '#332288')
_TOL_NAMES = ('blue', 'red', 'cyan', 'orange', 'teal', 'rose', 'wine', 'indigo')

#: name -> Palette. "default" is built on Tol's Sunset: slots 1-2 are its two endpoints nudged in lightness (indigo
#: darker, red lighter) so a two-series figure stays apart in greyscale, slots 3-5 were chosen by max-min search over
#: the Tol pool for greyscale and dichromatic separation, 6-8 are overflow (wine, rose, ochre). "tol" is Tol's Vibrant
#: scheme reordered so neighbouring lines contrast as strongly as Vibrant allows (blue, red, cyan, orange, teal),
#: plus three Tol Muted colours as overflow. Add your own with PALETTES['mine'] = Palette(...).
PALETTES = {
    'default': Palette('default', _DEFAULT_CYCLE, _DEFAULT_NAMES,
                       ('#C2E4EF', '#E9B7B4', '#AFD9DF', '#FBD3BC', '#CCEEFF',
                        tint('#882255'), tint('#BB5566'), tint('#997700')),
                       SUNSET_PARTS),
    'tol': Palette('tol', _TOL_CYCLE, _TOL_NAMES, tuple(tint(c) for c in _TOL_CYCLE), TOL_PARTS),
}


def palette(name: str = 'default') -> Palette:
    """The palette called `name` from PALETTES ("default" or "tol")."""
    try:
        return PALETTES[name]
    except KeyError:
        raise KeyError("unknown palette {!r}; choose from {}".format(name, ', '.join(sorted(PALETTES)))) from None


# Accessibility ##############################################################################################
# Pure numpy, so the colour tools need nothing beyond matplotlib's own dependencies.

# Machado, Oliveira & Fernandes (2009), severity 1.0, applied to LINEAR sRGB.
_CVD = {
    'protanopia': np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
    'deuteranopia': np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    'tritanopia': np.array([[1.255528, -0.076749, -0.178779],
                            [-0.078411, 0.930809, 0.147602],
                            [0.004733, 0.691367, 0.303900]]),
}
VISION = ('normal',) + tuple(_CVD)

_SRGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                         [0.2126729, 0.7151522, 0.0721750],
                         [0.0193339, 0.1191920, 0.9503041]])
_WHITE_D65 = np.array([0.95047, 1.0, 1.08883])


def _as_rgb(colours):
    """(N, 3) float RGB from one colour or a sequence of anything matplotlib understands, or an (N, 3) array."""
    if isinstance(colours, np.ndarray) and colours.ndim >= 2 and colours.shape[-1] in (3, 4):
        return np.asarray(colours, float)[..., :3].reshape(-1, 3)
    if isinstance(colours, (str, tuple)) and mcolors.is_color_like(colours):
        return np.array([mcolors.to_rgb(colours)])
    return np.array([mcolors.to_rgb(c) for c in colours])


def _srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(c):
    c = np.clip(np.asarray(c, float), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def simulate_cvd(colours, kind: str = 'deuteranopia'):
    """How `colours` look to a viewer with `kind` of colour blindness: 'protanopia', 'deuteranopia' or 'tritanopia'.

    Returns an (N, 3) array of sRGB values in [0, 1]."""
    if kind not in _CVD:
        raise ValueError("kind must be one of {}, not {!r}".format(', '.join(_CVD), kind))
    return _linear_to_srgb(_srgb_to_linear(_as_rgb(colours)) @ _CVD[kind].T)


def to_greyscale(colours):
    """`colours` as a greyscale print shows them (luminance), as an (N, 3) array of equal-channel sRGB values."""
    y = _srgb_to_linear(_as_rgb(colours)) @ _SRGB_TO_XYZ[1]
    g = _linear_to_srgb(y)
    return np.stack([g, g, g], axis=-1)


def rgb_to_lab(rgb):
    """CIE L*a*b* (D65) of sRGB values in [0, 1], shape (..., 3)."""
    xyz = (_srgb_to_linear(rgb) @ _SRGB_TO_XYZ.T) / _WHITE_D65
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def lab_lightness(colours):
    """CIE L* (0 black, 100 white) of each colour: what survives a greyscale print."""
    return rgb_to_lab(_as_rgb(colours))[:, 0]


def delta_e(lab1, lab2):
    """CIEDE2000 colour difference between L*a*b* values (broadcasting, shape (..., 3)).

    About 2 is the smallest difference a trained eye sees side by side; about 10 is comfortable for two thin
    lines on white."""
    lab1, lab2 = np.broadcast_arrays(np.asarray(lab1, float), np.asarray(lab2, float))
    l1, a1, b1 = lab1[..., 0], lab1[..., 1], lab1[..., 2]
    l2, a2, b2 = lab2[..., 0], lab2[..., 1], lab2[..., 2]
    c_bar = (np.hypot(a1, b1) + np.hypot(a2, b2)) / 2
    g = 0.5 * (1 - np.sqrt(c_bar ** 7 / (c_bar ** 7 + 25.0 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360

    d_l, d_c = l2 - l1, c2p - c1p
    zero_c = c1p * c2p == 0
    dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dh = np.where(zero_c, 0.0, dh)
    d_h = 2 * np.sqrt(c1p * c2p) * np.sin(np.radians(dh) / 2)

    l_bar, c_bar_p = (l1 + l2) / 2, (c1p + c2p) / 2
    h_sum = h1p + h2p
    h_bar = np.where(np.abs(h1p - h2p) <= 180, h_sum / 2, np.where(h_sum < 360, (h_sum + 360) / 2, (h_sum - 360) / 2))
    h_bar = np.where(zero_c, h_sum, h_bar)
    t = (1 - 0.17 * np.cos(np.radians(h_bar - 30)) + 0.24 * np.cos(np.radians(2 * h_bar))
         + 0.32 * np.cos(np.radians(3 * h_bar + 6)) - 0.20 * np.cos(np.radians(4 * h_bar - 63)))
    d_theta = 30 * np.exp(-(((h_bar - 275) / 25) ** 2))
    r_c = 2 * np.sqrt(c_bar_p ** 7 / (c_bar_p ** 7 + 25.0 ** 7))
    s_l = 1 + 0.015 * (l_bar - 50) ** 2 / np.sqrt(20 + (l_bar - 50) ** 2)
    s_c = 1 + 0.045 * c_bar_p
    s_h = 1 + 0.015 * c_bar_p * t
    r_t = -np.sin(np.radians(2 * d_theta)) * r_c
    term_c, term_h = d_c / s_c, d_h / s_h
    return np.sqrt((d_l / s_l) ** 2 + term_c ** 2 + term_h ** 2 + r_t * term_c * term_h)


def _pairwise_de(rgb):
    lab = rgb_to_lab(rgb)
    return delta_e(lab[:, None, :], lab[None, :, :])


def _resolve_colours(colours, names, n):
    """(hex list, name list) for a Palette, a palette name, a list of colours or None (the default palette)."""
    if colours is None:
        colours = 'default'
    if isinstance(colours, str) and colours in PALETTES:
        colours = PALETTES[colours]
    if isinstance(colours, Palette):
        names = names or list(colours.names)
        colours = list(colours.cycle)
    colours = [mcolors.to_hex(c) for c in colours]
    names = list(names) if names is not None else ['c{}'.format(i + 1) for i in range(len(colours))]
    if n is not None:
        colours, names = colours[:n], names[:n]
    return colours, names


def cvd_scores(colours=None, n: int = None) -> dict:
    """Worst-pair CIEDE2000 separation of a set of colours, for each way of seeing them.

    colours  a Palette, a palette name, or a list of colours (default: the default palette)
    n        use only the first n colours (the designed set is the first five)

    Returns {vision: (worst delta E, index of one colour of the pair, index of the other)} with vision one of
    'normal', 'protanopia', 'deuteranopia', 'tritanopia'. The larger the number the safer; about 10 is comfortable
    for thin lines."""
    cols, _ = _resolve_colours(colours, None, n)
    rgb = _as_rgb(cols)
    out = {}
    for kind in VISION:
        sim = rgb if kind == 'normal' else np.clip(simulate_cvd(rgb, kind), 0, 1)
        m = _pairwise_de(sim)
        iu = np.triu_indices(len(cols), k=1)
        k = int(np.argmin(m[iu]))
        out[kind] = (float(m[iu][k]), int(iu[0][k]), int(iu[1][k]))
    return out


def audit(colours=None, names=None, n: int = None) -> str:
    """A text report on a set of colours: each one's L* and how far its nearest neighbour is in greyscale, then the
    worst pair (CIEDE2000) under normal vision and the three dichromacies. Print it.

    colours  a Palette, a palette name, or a list of colours (default: the default palette)
    names    names for a list of colours
    n        use only the first n colours (the designed set is the first five)"""
    cols, nms = _resolve_colours(colours, names, n)
    lightness = lab_lightness(cols)
    width = max(len(x) for x in nms)
    out = ['{:>{w}}  {:>7}  {:>5}   nearest in greyscale'.format('name', 'hex', 'L*', w=width)]
    for i, (name, c) in enumerate(zip(nms, cols)):
        gap = min(abs(lightness[i] - lightness[j]) for j in range(len(cols)) if j != i) if len(cols) > 1 else 0.0
        out.append('{:>{w}}  {:>7}  {:5.1f}   dL* = {:4.1f}'.format(name, c, lightness[i], gap, w=width))
    out.append('')
    for kind, (de, i, j) in cvd_scores(cols).items():
        out.append('{:>12}: worst pair {}/{}  CIEDE2000 {:.1f}'.format(kind, nms[i], nms[j], de))
    return '\n'.join(out)


def register_cmaps(cmap_dict: dict = None):
    """
    Defines a set of new colormaps for matplotlib, and registers them (each also as '<name>_r', reversed).
    Nothing is registered until you call this.

    Borrowed from wackywendell on Github:
    https://github.com/wackywendell/mutedplots/blob/master/mutedcolors.py

    arguments:
        cmap_dict (dict): {name: color list} pairs defining colormaps. Default 'None'
                           loads all of my maps: the named colour lists, plus the maps derived from Sunset
                           (ham_sunset_warm, ham_sunset_warm_w, ham_sunset_ordered).
    returns:
        set of cmap keys registered.
    """
    if cmap_dict is None:
        # load all colors
        cmap_dict = dict(all_col)
        cmap_dict.update(derived_cmaps)

    # matplotlib.cm.register_cmap was removed in matplotlib 3.9; the registry API below exists from 3.5.
    # force=True keeps repeated calls idempotent, as the old function was. Re-registering our own maps is
    # expected here, so the "Overwriting the cmap" warning is silenced for this call only.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Overwriting the cmap')
        for name, colors in cmap_dict.items():
            if isinstance(colors, mcolors.Colormap):
                # a ready-made map: register a copy under its key, and its reverse
                cmap = colors.copy()
                cmap.name = name
                rcmap = colors.reversed(name=name + '_r')
            else:
                cmap = mcolors.LinearSegmentedColormap.from_list(name, colors)
                rcmap = mcolors.LinearSegmentedColormap.from_list(name + '_r', list(reversed(colors)))
            mpl.colormaps.register(cmap, name=name, force=True)
            mpl.colormaps.register(rcmap, name=name + '_r', force=True)
    return set(cmap_dict.keys())


def _resolve_dir(path: str) -> str:
    """Resolve an output directory given as a string, on any operating system.

    Relative paths are taken relative to the installed hamhelper package directory, as they always were.
    The historical Windows spelling with a leading backslash (r'\\colour_demos') still means 'inside the package'.
    Absolute paths are used as they are, and backslashes in a relative path are accepted on every platform.
    """
    path = path.lstrip('\\') if path.startswith('\\') else path
    if os.sep != '\\':
        path = path.replace('\\', os.sep)
    if os.path.isabs(path):
        return path
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


class HamColour:
    __slots__ = {'_name', '_cmap', '_length', '_cycler', '_created_from'}

    def __init__(self, cmap, length: int = 8):
        self._name = cmap.name
        self._cmap = cmap
        self._length = length
        if length > 1:
            self._cycler = mpl.cycler(color=cmap(np.linspace(0, 1, length)))
        else:
            # error here TODO
            self._cycler = mpl.cycler(color=cmap([0., 1]))
        self._created_from = 'mpl.Colormap'

    def __str__(self):
        return f"{self._name} from {self._length} colors: {', '.join(self.get_hexlist())}"

    def __repr__(self):
        return (f"{type(self).__name__}"
                f"(name='{self._name}', "
                f"length={self._length}, "
                f"created_from='{self._created_from}', "
                f"colours={self.get_hexlist()})"
                )

    def __call__(self, number):
        if number < 0:
            number = 0
            print("Value Error: Please chose float between [0, 1], set to 0.")
        elif number > 1:
            number = 1
            print("Value Error: Please chose float between [0, 1], set to 1.")
        return self._cmap(number)

    def __next__(self):
        return self._cycler

    def __iter__(self):
        # iter() must return an iterator; a Cycler is iterable but is not one itself.
        return iter(self._cycler)

    def __len__(self):
        return self._length

    def __getitem__(self, key):
        return self.get_hexlist()[key]

    def __eq__(self, other):
        a = type(self) is type(other)
        b = repr(self) == repr(other)
        return a & b

    def __neg__(self):
        # reverse the order!
        reversedMap = HamColour(self._cmap.reversed(), self._length)
        reversedMap._name = self._name + '_r'
        return reversedMap

    def __pos__(self):
        return self

    def __reversed__(self):
        return -self

    def __iadd__(self, other):
        # will stack colormaps
        name_tot = self._name + '+' + other._name
        hexlist_tot = self.get_hexlist() + other.get_hexlist()
        # bad practice, creates a new class instance
        return HamColour.from_hex(name_tot, hexlist_tot)

    @classmethod
    def from_name(cls, name, length: int = 8):
        # Check custom defined
        if name in list(all_col.keys()):
            hexlist = all_col[name]
            cmap = get_continuous_cmap(hexlist, name=name)
            tmp_cls = cls(cmap, length=len(hexlist))
            tmp_cls._created_from = 'named hexidecimal list'
            return tmp_cls
        elif name in derived_cmaps:
            tmp_cls = cls(derived_cmaps[name], length=length)
            tmp_cls._created_from = 'derived Sunset colormap'
            return tmp_cls
        elif name in list(mpl.colormaps):
            cmap = mpl.colormaps[name]
            tmp_cls = cls(cmap, length=length)
            tmp_cls._created_from = 'named mpl.Colormap'
            return tmp_cls
        else:
            # This name does not exist in my definitions or matplotlib's!
            print("Argument Error: Chosen name does not exist in the custom set of colormaps or matplotlib.")
            hexlist = ['#FFFFFF']
            cmap = get_continuous_cmap(hexlist, name=name)
            return cls(cmap, 1)

    @classmethod
    def from_hex(cls, name: str, hexlist: list):
        cmap = get_continuous_cmap(hexlist, name=name)
        tmp_cls = cls(cmap, len(hexlist))
        tmp_cls._created_from = 'custom hexidecimal list'
        return tmp_cls

    @classmethod
    def from_palette(cls, name: str = 'default'):
        """The cycle of a Palette (see PALETTES) as a discrete HamColour, one colour per slot."""
        pal = palette(name)
        # a ListedColormap, so each slot is exactly its colour rather than a point on a smooth gradient
        tmp_cls = cls(mcolors.ListedColormap(list(pal.cycle), name=pal.name), length=len(pal.cycle))
        tmp_cls._created_from = 'palette'
        return tmp_cls

    @classmethod
    def from_hex_gradient(cls, name: str, hexlist: list, locations: list):
        # (the original `if max_scale := max(locations) > 1` bound max_scale to the comparison's bool, so
        # locations were divided by True, i.e. never rescaled)
        max_scale = max(locations)
        if max_scale > 1:
            locations = np.array(locations) / max_scale
        cmap = get_continuous_cmap(hexlist, name=name, float_list=locations)
        tmp_cls = cls(cmap, length=len(hexlist))
        tmp_cls._created_from = 'custom hexidecimal list'
        return tmp_cls

    @property
    def name(self):
        return self._name

    @property
    def cmap(self):
        return self._cmap

    @property
    def length(self):
        return self._length

    @property
    def cycler(self):
        return self._cycler

    @length.setter
    def length(self, N):
        self._length = N
        self._cycler = mpl.cycler(color=self._cmap(np.linspace(0, 1, N)))

    def _color_list(self, N: int = None):
        if type(N) is type(None):
            N = self._length
        return self._cmap(np.linspace(0, 1, N, endpoint=True))

    def get_rgbalist(self, N: int = None):
        return self._color_list(N)

    def get_hexlist(self, N: int = None):
        rgba = self._color_list(N)
        hexList = [mcolors.rgb2hex(_, keep_alpha=True) for _ in rgba]
        return hexList

    def test(self, N=None, mapBool=False, savePath=None):
        """Test function to generate a serries of common plots in one figure.

        Args:
            N (int, optional): _description_. Defaults to initialize length.
            mapBool (bool, optional): Adds a map of Canada to the plot, coloured with the map (see example_map).
                Defaults to False.
            savePath (str, optional): Directory to save the figure in (as hamMap_<name>.png), relative to the
                package directory unless absolute. Defaults to None meaning do not save.
        """
        if N is None:
            N = self._length
            N_bar = 256
        else:
            N_bar = N
        assert_error(N > 0, ValueError("Argument 'N' must be a positive integer or 'None' type."))  # noqa: F631

        # x, y for line plot
        t = 10
        f = 0.5
        spacing = 1

        ax_map = None  # leave empty if we dont want to plot
        if mapBool:
            # with a map the figure is wider
            fig = plt.figure(tight_layout=True, figsize=(11, 4))
            gs = gridspec.GridSpec(2, 3, height_ratios=[1, 5], width_ratios=[3, 5, 3])
            pp = 1
        else:
            fig = plt.figure(tight_layout=True, figsize=(8, 4))
            gs = gridspec.GridSpec(2, 2, height_ratios=[1, 5], width_ratios=[5, 3])
            pp = 0
        # generate axis for each plot using gridspec
        ax_bar = fig.add_subplot(gs[0, pp])
        ax_plot = fig.add_subplot(gs[1, pp])
        ax_mkr = fig.add_subplot(gs[0, pp + 1])
        ax_sct = fig.add_subplot(gs[1, pp + 1])

        # make background off white
        fig.patch.set_facecolor('whitesmoke')

        # PLOT BAR %-------------------------------------------------------------------%
        ax_bar.imshow([list(np.arange(0, 1 , 1/N_bar))]*5, interpolation='nearest', origin='lower',
                      cmap=self.cmap, aspect='auto')
        ax_bar.set_title(self.name, size=17, pad=8)

        # PLOT LINES & COLORS %--------------------------------------------------------%
        c = [self.cmap(_)[:-1] for _ in np.linspace(0, 1, N)]
        x = np.linspace(0, t, 100)
        widths = [2, 3, 4, 5, 6, 7, 8, 9]  # increasing thickness
        markers = ['.', 'o', 's', '^', '*', 'D', '$f$', 'p', 'o']  # markers to show
        flstl = ['full']*(len(markers)-1) + ['none']  # repeat markers for each color
        widths.reverse()

        for i in range(N):
            # For each color in the cmap we want to plot
            for _, thicc in enumerate(widths):  # do increasing thickness
                xtmp = x[0+_*2:_*2+3]
                ax_plot.plot(xtmp, np.sin(xtmp/f) + i*spacing, color=c[i], lw=thicc)

            # show different linestyles
            ax_plot.plot(x[len(widths)*2:61], np.sin(x[len(widths)*2:61]/f) + i*spacing, color=c[i], ls='solid')
            ax_plot.plot(x[60:71], np.sin(x[60:71]/f) + i*spacing , color=c[i], ls='solid')
            ax_plot.plot(x[70:81], np.sin(x[70:81]/f) + i*spacing , color=c[i], ls='dashed')
            ax_plot.plot(x[80:93], np.sin(x[80:93]/f) + i*spacing , color=c[i], ls='dashdot')
            ax_plot.plot(x[92:100], np.sin(x[92:100]/f) + i*spacing , color=c[i], ls='dotted')

            # do scatter plot
            x_sct = np.random.random(size=5)
            y_sct = np.random.random(size=5)
            ax_sct.scatter(x_sct, y_sct, color=c[i])

        # PLOT MARKERS %---------------------------------------------------------------%
        for _, mkr in enumerate(markers):
            if N >= 8:
                # to messy if many colors, so stick to first and last few
                ax_mkr.plot(_, -0.15, marker=mkr, color=c[0], fillstyle=flstl[_])
                ax_mkr.plot(_, -0.05, marker=mkr, color=c[3], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.05, marker=mkr, color=c[-4], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.15, marker=mkr, color=c[-1], fillstyle=flstl[_])
            elif N >= 4:
                # 4-8 colors, plot four with less spacing
                ax_mkr.plot(_, -0.15, marker=mkr, color=c[0], fillstyle=flstl[_])
                ax_mkr.plot(_, -0.05, marker=mkr, color=c[1], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.05, marker=mkr, color=c[-2], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.15, marker=mkr, color=c[-1], fillstyle=flstl[_])
            elif N == 3:
                # only plot three
                ax_mkr.plot(_, -0.15, marker=mkr, color=c[0], fillstyle=flstl[_])
                ax_mkr.plot(_, 0, marker=mkr, color=c[1], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.15, marker=mkr, color=c[-1], fillstyle=flstl[_])
            elif N == 2:
                # plot two
                ax_mkr.plot(_, -0.1, marker=mkr, color=c[0], fillstyle=flstl[_])
                ax_mkr.plot(_, 0.1, marker=mkr, color=c[-1], fillstyle=flstl[_])
            else:
                # plot one
                ax_mkr.plot(_, 0, marker=mkr, color=c[0], fillstyle=flstl[_])

        if mapBool:
            # PLOT MAP %---------------------------------------------------------------%
            ax_map = fig.add_subplot(gs[:, 0])
            self.example_map(ax_map, N)
            ax_map.axis('off')

        # format axis to make it pretty!
        ax_mkr.set(ylim=(-0.2, 0.2))
        ax_bar.axis('off')
        ax_mkr.axis('off')
        ax_sct.set(xticks=[], yticks=[])
        ax_sct.patch.set_alpha(0)
        ax_sct.spines['top'].set_visible(False)
        ax_sct.spines['right'].set_visible(False)
        ax_plot.set(frame_on=False)
        ax_plot.yaxis.labelpad = -10
        ax_plot.set(ylabel="N = {}".format(N), xticks=[], yticks=[])

        if savePath is None:
            plt.show()
        else:
            out_dir = _resolve_dir(savePath)
            os.makedirs(out_dir, exist_ok=True)
            plt.savefig(os.path.join(out_dir, 'hamMap_' + self.name + '.png'), dpi=300)
            plt.show()
        return None

    def truncate(self, start: float = 0, stop: float = 1, subsample: int = 256, update: bool = True):
        """Create a new colormap from a reduced range of an existing map.

        Args:
            start (float, optional): Starting fraction from 0 to 1. Defaults to 0.
            stop (float, optional): Ending fraction from 0 to 1. Defaults to 1.
            subsample (int, optional): Sample resolution, reduce to create linear discrete map. Defaults to 256.
            update (bool, optional): Update existing object to this new one, otherwise returns a new
                                     HamMap object. Defaults to True.

        Returns:
            HamMap: Custom colormap object.
        """
        new_name = f'{self._name}-truncated({start:.2f},{stop:.2f})'
        new_cmap = mcolors.LinearSegmentedColormap.from_list(new_name, self.cmap(np.linspace(start, stop, subsample)))
        if update:
            self._name = new_name
            self._cmap = new_cmap
        else:
            return HamColour(new_cmap, length=self._length)

    def example_map(self, ax, N: int = None, shape_file: str = 'lpr_000b16a_e'):
        r"""Draw an example map of Canada on a given matplotlib axis, each province or territory in one of N colours.

        Needs only numpy and matplotlib: hamhelper._geo reads the shapefile and does the Mercator projection that
        Basemap used to do.

        Map data: Statistics Canada, Provinces/Territories, Cartographic Boundary File, 2016 Census (adapted
        from the original, see map_files/NOTICE.md). Contains information licensed under the Open Government
        Licence - Canada.

        Args:
            ax (plt.Axes): Axes to plot map on.
            N (int, optional): Number of colors, defaults to initialized length.
            shape_file (str, optional): Shape file name (no extension) in the 'map_files' subfolder to define
                                        map. Defaults to 'lpr_000b16a_e'.

        Returns:
            hamhelper._geo.Mercator: the projection of the map drawn. m(lon, lat) gives the (x, y) position
            on the axes, so points can be added to the map; m.xmax and m.ymax are its far corner.

        Raises:
            FileNotFoundError: the shapefile is not there (map_files is in the repository but not in the pip
                               package).
        """
        from matplotlib.collections import PathCollection

        if N is None:
            N = self._length
        colors = self.cmap(np.linspace(0, 1, N))

        shape_file = os.path.join(_resolve_dir('map_files'), shape_file.lstrip('\\/'))
        shapes = _geo.read_shapefile(shape_file)  # raises FileNotFoundError when missing

        m = _geo.Mercator(llcrnrlon=-144, llcrnrlat=41, urcrnrlon=-51, urcrnrlat=83.7)  # centred on Canada

        # One path per province in a single collection, colours dealt out at random. A collection and not
        # ax.add_patch: since matplotlib 3.8 add_patch walks every segment of the path in Python to find its
        # limits, which takes about 25 s for Nunavut alone (3.4 million vertices in the file). The limits are set below.
        np.random.shuffle(colors)
        paths = [_geo.polygon_path(shape.parts, m) for shape in shapes]
        ax.add_collection(PathCollection(paths, facecolors=[colors[k % len(colors)] for k in range(len(paths))],
                                         edgecolors='k', linewidths=0.1, zorder=2), autolim=False)
        ax.set(xlim=(m.xmin, m.xmax), ylim=(m.ymin, m.ymax), aspect='equal')
        return m


def makeAllTests(continuousMaps: list = colmaps, discreteMaps: list = colsets, fileOutPath: str = 'colour_demos',
                 mapBool: bool = False):
    for key in continuousMaps:
        colo = HamColour.from_hex(key, continuousMaps[key])
        colo.test(mapBool=mapBool, savePath=fileOutPath)
    for key in discreteMaps:
        colo = HamColour.from_hex(key, discreteMaps[key])
        colo.test(N=colo.length, mapBool=mapBool, savePath=fileOutPath)
