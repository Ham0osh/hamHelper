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

`hamhelper.install` does the stacking for you, remembers your choices and lets you change one at a time in any order:
```
import hamhelper.install as hi

hi.style.hamstyle()        # light, serif, one column, journal frame
hi.size.two_col()          # all later figures are 6.90 in wide
hi.palette.tol()           # Tol's Vibrant colour cycle instead of the default

with hi.size.one_col():    # a one-off: undone when the block ends
    fig, ax = plt.subplots()

hi.reset()                 # matplotlib as it was before the first call
```
| axis | choices | default |
|---|---|---|
| `hi.style` | `hamstyle` | `hamstyle` |
| `hi.size` | `one_col`, `one_col_tall`, `two_col`, `slide` | `one_col` |
| `hi.variant` | `journal`, `comms` | `journal` |
| `hi.font` | `serif`, `sans` | `serif` |
| `hi.palette` | `default`, `tol` | `default` |
| `hi.redundancy` | `off`, `dash`, `marker`, `both` | `off` |
| `hi.grid` | `off`, `on` | `off` |

`hi.apply(size='slide', variant='comms')` sets several at once, `hi.current()` shows what is in force. `redundancy` gives each colour in the cycle its own line style and/or marker, for greyscale prints and colour-blind readers.

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


**hamhelper.plotting.gtc()**  
COMING SOON: Generate a great triangle of confusion from a multi-dimensional pandas dataframe with one column correspponding to the dimension being evaluated (cost, error, counts, likelyhood...)
```
gtc( ... ):
```
> parameters

---
### colours
A suite of colour sets and colour maps I use with a custom `HamColor` class to easily import and play with the colours. Just stuff I like to use!
