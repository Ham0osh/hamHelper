# hamHelper [![PyPI version](https://badge.fury.io/py/hamhelper.svg)](https://badge.fury.io/py/hamhelper) ![Test Workflow](https://github.com/Ham0osh/hamHelper/actions/workflows/deploy.yml/badge.svg) ![Coverage](https://github.com/Ham0osh/hamHelper/blob/main/docs/coverage.svg)

### Description
This repository contains the HamHelper package written in Python3 for scientific plotting and analysis tools geared towards speeding up common workflows in my experience. This is mainly a wrapper of matplotlib with some script and numpy for common physics use cases.


## Usage

### Installing

In order to use this package you will need to have installed:  
 - Python 3.8 or newer,  
 - matplotlib 3.5 or newer (tested up to 3.11),
 - numpy.  
 
Install as you normally would with pip: `pip install hamhelper`

The matplotlib style files ship with the package and can be used by name:
```
import matplotlib.pyplot as plt
plt.style.use('hamhelper.styles.hamStyle')
```
`import hamhelper` itself never changes any matplotlib setting; the style only applies when you ask for it.

### Styles

`hamStyle` is a minimal-ink style for physics figures: white substrate, black ink, serif type (Times-class, STIX maths), constrained layout, and a colour cycle built on Paul Tol's Sunset. On its own it gives a single-column (3.37 in) journal figure with a four-sided frame and inward ticks. Small overlay files change one thing at a time and can be stacked after it:
```
plt.style.use(['hamhelper.styles.hamStyle', 'hamhelper.styles.size_two_col'])
```
 - `size_one_col`, `size_one_col_tall`, `size_two_col`, `size_slide`: figure size, type size, line and tick weights  
 - `variant_journal` (boxed, ticks in), `variant_comms` (left and bottom spines only, ticks out)  
 - `font_serif`, `font_sans`

**Two monochrome styles, `alightroom` and `adarkroom`,** are hamStyle with every colour taken out, named for the text game *A Dark Room* and borrowing its restraint: one ink, one ground, grey for what recedes. They change colour and nothing else, so the same sizes, frame, type and overlays apply on top, and a figure laid out in one lands in the same place in the other.
 - `alightroom`: pure black on pure white (`plt.style.use('hamhelper.styles.alightroom')`).
 - `adarkroom`: white on an off-black ground, `#272727`. Pure black behind white type glows on a screen, so the ground is a neutral dark grey, and exported files are dark too (paste them on a dark slide).
 - Series are a ladder of eight greys (palettes `alight` and `adark`, from the full ink down to the dimmest grey that keeps 3.2:1 against the ground, equally spaced in CIEDE2000) and each also gets its own line style, because greys that close cannot be told apart by tone alone. Images use the matching grey maps `ham_grey` and `ham_grey_dark`, whose floor is the ground, so masked pixels and empty space melt into the page. Boxes, whiskers, patch outlines and the polar helpers' leader lines follow the ink; the pale band behind data (`plotting.band`) is a faint grey.
 - Each palette is made for its own ground: `hi.palette.tol()` on `adarkroom` is yours to ask for, but the contrast guarantee is gone.

`hamhelper.install` does the stacking for you, remembers your choices and lets you change one at a time in any order:
```
import hamhelper.install as hi

hi.style.hamstyle()        # light, serif, one column, journal frame
# hi.style.adarkroom()     # or white on off-black, in greys; hi.style.alightroom() for black on white, in greys
hi.size.two_col()          # all later figures are 6.90 in wide
hi.palette.tol()           # Tol's Vibrant colour cycle instead of the default

with hi.size.one_col():    # a one-off: undone when the block ends
    fig, ax = plt.subplots()

hi.reset()                 # matplotlib as it was before the first call
```
| axis | choices | default |
|---|---|---|
| `hi.style` | `hamstyle`, `alightroom`, `adarkroom` | `hamstyle` |
| `hi.size` | `one_col`, `one_col_tall`, `two_col`, `slide` | `one_col` |
| `hi.variant` | `journal`, `comms` | `journal` |
| `hi.font` | `serif`, `sans` | `serif` |
| `hi.palette` | `default`, `tol`, `alight`, `adark` (any palette in `hamhelper.colours.PALETTES`) | `default` |
| `hi.cmap` | `sunset_warm`, `sunset_warm_w`, `grey`, `grey_dark`, `iridescent`, `viridis`; `hi.cmap.set(name)` takes any colormap name | `sunset_warm` |
| `hi.redundancy` | `off`, `dash`, `marker`, `both` | `off` |
| `hi.grid` | `off`, `on` | `off` |

`hi.apply(size='slide', variant='comms')` sets several at once, `hi.current()` shows what is in force, and `hi.palette.get()` returns the palette in force (cycle, names, pale bands, fit-component colours) so one script renders in any palette. The first setter call also registers hamhelper's colormaps with matplotlib (the default `image.cmap` is one of them); the standalone `hamStyle` file leaves `image.cmap` at matplotlib's default. `redundancy` gives each colour in the cycle its own line style and/or marker, for greyscale prints and colour-blind readers.

A style can declare its own defaults for the other axes: `alightroom` and `adarkroom` ask for their grey palette, their grey map and `redundancy='dash'`. Anything you choose yourself beats that, whatever the order of the calls, and `hi.reset('palette')` hands the axis back to the style.

*Markers and filled polygons.* Matplotlib gives the whole colour cycle to every artist that takes a cycle colour, and a filled polygon has no `markevery`, so with `redundancy='marker'` or `'both'` in force `ax.fill(...)` and `ax.hist(..., histtype='step')` raise `Polygon.set() got an unexpected keyword argument 'markevery'`. Lines, bars, error bars, scatter, `fill_between` and `ax.stairs` are fine. If you need step histograms, use `redundancy='dash'` (what the two monochrome styles do) or draw them with `ax.stairs(*np.histogram(x, bins))`.

### Submodules

```
HamHelper.    # package root
|- plotting   # plotting helpers
|- colours    # colourmap definitions, helper functions, and custom colour class HamColour 
|- install    # opt-in matplotlib styles: size, frame, font, colour cycle (see Styles above)
```

---
## Purpose

This package contains a set of helper functions and methods I use. Primarily geared towards physics, experimental analysis, and data visualization. The goal is to simplify common procedures around generating pretty plots with minimal chart-junk as well as getting the values that matter (ie. curve fit routine that also computes standard error and chi squared). In general, there are three parts:

### plotting
**hamhelper.plotting.despine()**  
Simple matplotlib wrapper to despine. Offers offset axis as well as trimmed axis like in Seaborn.  
```
despine(axis = None, trim = False, drop = 0, noLine = False, bottom = True, left = True, top = False, right = False):  
```
> **axis: None or mpl.axes object** (opt.)  
>     The axes object to act on, default plt.gca().  
> **trim: bool** (opt.)  
>     If true trims axes to the limiting ticks, default False.  
> **drop: float** (opt.)  
>     Distance to space spine from axes in pixels. Default 0.  
> **noLine: bool** (opt.)  
>     If true removes the spine but keeps the axis ticks, default False.  
> **bottom, left, top, right: bool** (opt.)  
>     Enable or disable the corresponding axes spine, default keeps bottom and left, removes top and right.  


**hamhelper.plotting.errorbands()**  
Wrapper of matplotlib.pyplot.errorbar producing continuous bands instead of stems. You can additionally enable the caps still.  
```
errorbands(x, y, yerr, capsize = 0, ax = None, color = None, *args, **kwargs):  
```
> **x: np.array like**  
>     The x dimension of pairwise data.  
> **y: np.array like**  
>     The y dimension of pairwise data.  
> **yerr: np.array like**  
>     The error in the y dimension of pairwise data.  
> **capsize: float** (opt.)  
>     The width of caps to be added above each data point at the same location as the error band.  
> **ax: None or plt.axes object** (opt.)  
>     Can specify to plot on another axis, defaults to plt.gca()  
> **color: tuple or string** (opt.)  
>     Facecolor of the error band. If tuple provided, expects a tuple of RGB or RGBA values. If string provided expects a hex '#RRGGBB' or matplotlib named color. Defaults None for no fill color.  
> <b>\*args & \*\*kwargs:</b> (opt.)  
>     Passed to plt.ax.fill\_between().  


**Figure helpers**

Tools for building a figure panel by panel. They read matplotlib's rcParams when called, never when imported, so they follow whatever style is in force (`hamhelper.install`, `plt.style.use`, or matplotlib's own defaults); the plates behind labels and the outlines take `axes.facecolor` and `axes.edgecolor`, so they suit a dark style too. The docstrings list every argument.

| function | what it does |
|---|---|
| `colorbar(mappable, ax)` | colourbar exactly as tall as its panel, with its thickness set in points so it is the same weight at every size; `cax=` draws into your own axes instead |
| `framed(ax)` | box an image panel: four spines, ticks inward and above the image (for the open comms variant) |
| `polar_frame(ax, ticks, labels, radial)` | dress a polar axes as a clean circular panel: rim ticks and labels, a radial spoke or a column of leader numerals |
| `disc(ax, artists)` | clip images and contours to a disc, with the circle as the frame and ordinary offset x and y spines |
| `fit_height(fig, ax)`, `square_figure(fig, ax)` | trim the figure height so an equal-aspect panel fills the width, or a panel comes out exactly square |
| `units(ax, 'y', name, unit)` | axis label in the house form `name [unit]` |
| `runs(ax, x, Y)` | thin translucent per-run traces under a bold mean or median; the traces never use up colour-cycle slots |
| `band`, `guide`, `spec_tick` | target band, dashed grey reference line, and a tick placed at a requirement value |
| `tag`, `panel_label` | corner label on a pale plate; bold panel letter such as `(a)` |
| `save(fig, name)` | write pdf and png at the figure's true size (never `bbox_inches='tight'`), named `name__size__variant` |

```python
import matplotlib.pyplot as plt
import hamhelper.install as hi
import hamhelper.plotting as hp

hi.apply(size='one_col', variant='comms')
fig, ax = plt.subplots()
im = ax.imshow(img)
hp.framed(ax)                                          # an image panel gets a box even in the open variant
hp.colorbar(im, ax, label=r'Irradiance, $I/I_0$')
hp.save(fig, 'beam', size='one_col', variant='comms')  # figures/beam__one_col__comms.pdf and .png
```


**hamhelper.plotting.gtc()**  
COMING SOON: Generate a great triangle of confusion from a multi-dimensional pandas dataframe with one column correspponding to the dimension being evaluated (cost, error, counts, likelyhood...)
```
gtc( ... ):
```
> parameters

---
### colours
A suite of colour sets and colour maps I use with a custom `HamColour` class to easily import and play with the colours. Just stuff I like to use!
Importing it registers nothing with matplotlib; call `hamhelper.colours.register_cmaps()` when you want the names (`'ptol_sunset'`, `'ham_sunset_warm'`, each also as `'<name>_r'`) available to `cmap=`.

**Palettes.** `hc.palette('default')` and `hc.palette('tol')` return a `Palette`: eight colours in slot order (the first five are the designed set, three more are overflow so a six-series figure never wraps a colour), a name and a pale band for each, `parts`, three colours for the components of a total drawn in slot 2 (a fit made of peaks), a `highlight` (the fill of `plotting.band`), a `lead` (the leader lines of `polar_frame`) and, optionally, its own `dashes`. `hc.current_palette()` finds the palette whose colours are the cycle matplotlib is using, which is how the plotting helpers pick colours that suit the room. `pal.cycler('both')` gives a matplotlib cycler (also `'off'`, `'dash'`, `'marker'`) that adds a line style and/or marker per colour for greyscale prints and colour-blind readers. `default` is built on Paul Tol's Sunset with its two endpoints nudged in lightness so a two-series figure stays apart in greyscale; `tol` is Tol's Vibrant scheme reordered; `alight` and `adark` are the grey ladders of the two monochrome styles. Add your own with `hc.PALETTES['mine'] = hc.Palette(...)`.

**Sequential maps from Sunset.** `ham_sunset_warm` is the warm 45% of Sunset, so a sequential panel and a diverging `ptol_sunset` panel in one document share hues; `ham_sunset_warm_w` pulls its floor to white; `ham_sunset_ordered` and `hc.ordered(n)` give cool-to-warm colours for series that are ordered (time, voltage). `ham_grey` (white to black) and `ham_grey_dark` (the dark ground to white) step evenly in lightness and belong to the monochrome styles. `hc.tint(colour)` and `hc.shade(colour)` make a pale partner or a text-legible dark one; `hc.tint(colour, ground=hc.GROUND_DARK)` gives the dim partner on a dark ground.

**Checking a palette.** Pure numpy: `hc.audit('default', n=5)` prints each colour's L* and the worst pair under normal vision, protanopia, deuteranopia and tritanopia (CIEDE2000; about 10 is comfortable for thin lines); `hc.cvd_scores`, `hc.simulate_cvd`, `hc.to_greyscale`, `hc.lab_lightness`, `hc.rgb_to_lab` and `hc.delta_e` are the pieces.

**Trying a colour map.** `HamColour.test()` draws a colour bar, lines, markers and a scatter in the map; `test(mapBool=True)` adds a map of Canada's provinces and territories, drawn with numpy and matplotlib only (no Basemap). `HamColour.example_map(ax)` draws just the map and returns its Mercator projection, so `m(lon, lat)` gives the position of a point on it. The map files are in the repository but not in the pip package.

---
### Licence and credits
hamhelper is released under the MIT licence (see `LICENSE`).

The example map in `hamhelper/map_files` is Statistics Canada's *Provinces/Territories, Cartographic Boundary File, 2016 Census*, adapted: this copy has its coordinates as longitude and latitude. Contains information licensed under the [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada). Details in `hamhelper/map_files/NOTICE.md`.
