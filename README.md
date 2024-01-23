# hamHelper

*Coming soon*

### Installation**
`pip install hamhelper`

## Purpose

This package contains a set of helper functions and methods I use. Primarily geared towards physics, experimental analysis, and data visualization. The goal is to simplify common procedures around generating pretty plots Mitch minimal chart-junk as well as getting the values that matter (ie. curve fit routine that also computes common values of merit). In general, there are three parts:
> ### plotting
> despine(): Simple matplotlib wrapper to despine. Offers offset axis as well as trimmed axis like in Seaborn.
> errorbands(): Wrapper of matplotlib.pyplot.errorbar producing continuous bands instead of stems. You can additionaly enable the caps still.

> ### colours
> A suite of colour sets and colour maps I use with a custom `HamColor` class to easily import and play with the colours. Just stuff I like to use!
