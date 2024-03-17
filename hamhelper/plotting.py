"""
My custom plotting helpeer functions for day to day!
Created on Sat Aug 20 2023

@author: hamishj

Contributions 'borrowed' from:
 -
"""
import matplotlib.pyplot as plt
import numpy as np


# %----------------------------------------------------------------%
def despine(axis=None, trim: bool = False, drop: float = 0., noLine: bool = False, bottom: bool = True,
            left: bool = True, top: bool = False, right: bool = False):
    if type(axis) is type(None):
        axis = plt.gca()
    # Hide the specified spines
    axis.spines.right.set_visible(right)
    axis.spines.top.set_visible(top)
    axis.spines.bottom.set_visible(bottom)
    axis.spines.left.set_visible(left)

    # Stollen from seaborn git
    # https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py
    # line 375, accessed April 6, 2023
    if trim:
        # clip off the parts of the spines that extend past major ticks
        xticks = np.asarray(axis.get_xticks())
        if xticks.size:
            first_tick = np.compress(xticks >= min(axis.get_xlim()),
                                     xticks)[0]
            last_tick = np.compress(xticks <= max(axis.get_xlim()),
                                    xticks)[-1]
            axis.spines['bottom'].set_bounds(first_tick, last_tick)
            axis.spines['top'].set_bounds(first_tick, last_tick)
            new_ticks = xticks.compress(xticks <= last_tick)
            new_ticks = new_ticks.compress(new_ticks >= first_tick)
            axis.set_xticks(new_ticks)

        yticks = np.asarray(axis.get_yticks())
        if yticks.size:
            first_tick = np.compress(yticks >= min(axis.get_ylim()),
                                     yticks)[0]
            last_tick = np.compress(yticks <= max(axis.get_ylim()),
                                    yticks)[-1]
            axis.spines['left'].set_bounds(first_tick, last_tick)
            axis.spines['right'].set_bounds(first_tick, last_tick)
            new_ticks = yticks.compress(yticks <= last_tick)
            new_ticks = new_ticks.compress(new_ticks >= first_tick)
            axis.set_yticks(new_ticks)

    if drop:
        axis.spines.left.set_position(('outward', drop))
        axis.spines.bottom.set_position(('outward', drop))

    if noLine:
        for pos in ['bottom', 'left']:
            axis.spines[pos].set_visible(False)
    return None


def errorbands(x: np.ndarray, y: np.ndarray, yerr: np.ndarray, capsize: float = 0, ax=None, color=None, *args,
               **kwargs):
    """
    Wrapper of matplotlib fill_between which instead creates continuous colour bands that can be filled.

    TODO: Add interpolation types
    """
    if type(ax) is type(None):
        ax = plt.gca()
    low = y - yerr
    high = y + yerr
    poly = ax.fill_between(x, low, high, *args, facecolor=color, **kwargs)
    if capsize:
        ax.errorbar(x, y, yerr=yerr, capsize=capsize, color=color,
                    elinewidth=0, fmt='.')
    return poly
