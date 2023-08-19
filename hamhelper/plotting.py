"""
My custom plotting helpeer functions for day to day!
Created on Sat Aug 20 2023

@author: hamishj

Contributions 'borrowed' from:
 - 
"""
from hamhelper.errors import assert_error
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import numpy as np

# %----------------------------------------------------------------%
def despine(axis = None, trim = False, drop = 0, noLine = False,
            bottom = True, left = True, top = False, right = False):
    if axis == None:
        axis = plt.gca()
    # Hide the specified spines
    if not right:  axis.spines.right.set_visible(False)
    if not top:    axis.spines.top.set_visible(False)
    if not bottom: axis.spines.bottom.set_visible(False);
    if not left:   axis.spines.left.set_visible(False);
    
    # Stollen from seaborn git
    # https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py
    # line 375, accessed April 6, 2023
    if trim:
            # clip off the parts of the spines that extend past major ticks
            xticks = np.asarray(axis.get_xticks())
            if xticks.size:
                firsttick = np.compress(xticks >= min(axis.get_xlim()),
                                        xticks)[0]
                lasttick = np.compress(xticks <= max(axis.get_xlim()),
                                       xticks)[-1]
                axis.spines['bottom'].set_bounds(firsttick, lasttick)
                axis.spines['top'].set_bounds(firsttick, lasttick)
                newticks = xticks.compress(xticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                axis.set_xticks(newticks)

            yticks = np.asarray(axis.get_yticks())
            if yticks.size:
                firsttick = np.compress(yticks >= min(axis.get_ylim()),
                                        yticks)[0]
                lasttick = np.compress(yticks <= max(axis.get_ylim()),
                                       yticks)[-1]
                axis.spines['left'].set_bounds(firsttick, lasttick)
                axis.spines['right'].set_bounds(firsttick, lasttick)
                newticks = yticks.compress(yticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                axis.set_yticks(newticks)
    
    if drop:
        axis.spines.left.set_position(('outward', drop))
        axis.spines.bottom.set_position(('outward', drop))
        
    if noLine:
        for pos in ['bottom', 'left']:
                axis.spines[pos].set_visible(False)
   
def errorbands(x, y, yerr, capsize = 0, ax = None, color = None, *args, **kwargs):
    if ax == None:
        ax = plt.gca()
   
    low  = y - yerr
    high = y + yerr
    poly = ax.fill_between(x, low, high, *args, facecolor = color, **kwargs)
    if capsize:
        ax.errorbar(x,y, yerr = yerr, capsize = capsize, color = color,
                    elinewidth = 0, fmt = '.')
        
    return poly