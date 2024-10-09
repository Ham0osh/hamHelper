# hamHelper [![PyPI version](https://badge.fury.io/py/hamhelper.svg)](https://badge.fury.io/py/hamhelper) ![Test Workflow](https://github.com/Ham0osh/hamHelper/actions/workflows/deploy.yml/badge.svg) ![Coverage](https://github.com/Ham0osh/hamHelper/blob/main/docs/coverage.svg)

### Description
This repository contains the HamHelper package written in Python3 for scientific plotting and analysis tools geared towards speeding up common workflows in my experience. This is mainly a wrapper of matplotlib with some script and numpy for common physics use cases.


## Usage

### Installing

In order to use this package you will need to have installed:  
 - Python3.XX,  
 - matplotlib,
 - scipy,
 - numpy.  
 
Install as you normally would with pip: `pip install hamhelper`

### Submodules

```
HamHelper.    # package root
|- plotting   # plotting helpers
|- colours    # colourmap definitions, helper functions, and custom colour class HamColour 
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
