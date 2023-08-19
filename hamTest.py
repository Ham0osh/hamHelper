# -*- coding: utf-8 -*-
"""
Created on Fri May 19 22:19:18 2023

@author: Hamish
"""
import numpy as np
import matplotlib.pyplot as plt
import hamHelp as hamHelp
from scipy.optimize import curve_fit
import os

wd = os.getcwd()

rcFile = "styles\\hamStyle.mplstyle"
rcName = rcFile.split('.')[0]

testOutPath = wd+"\\rc_test_plots\\"+rcName+'\\'
if not os.path.exists(testOutPath):
    os.makedirs(testOutPath)

def add_labels(ax = None, title = "Title", *args, **kwargs):
    if ax is None:
        ax = plt.gca()
    
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title, *args, **kwargs)

    return None

# make a series of default plots ##############################################


# Sine plot ###################################################################
title = "Sin Plot"
N = 4
x = np.linspace(0,np.pi*2,50)
amps  = np.linspace(2,6,N)
phase = np.linspace(0,np.pi/4,N)

for A, P in zip(amps,phase):
    plt.plot(x, A*np.sin(x - P), label = f"y={A:.1f}sin(x-{P:.1f})")

add_labels(title = title)
plt.legend()
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)
plt.show()

# Line plot ###################################################################
title = "Line Plot"
N = 4
x = np.linspace(0,np.pi*2,50)
amps  = np.linspace(2,6,N)
phase = np.linspace(0,np.pi/4,N)

for A, P in zip(amps,phase):
    plt.plot(x, A*(x - P), label = f"y={A:.1f}(x-{P:.1f})")

add_labels(title = title)
plt.legend()
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)
plt.show()


# Histogram  ###################################################################
title = "Histogram"
N = 420

dat = np.random.normal(size = N)

plt.hist(dat)

add_labels(title = title)
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)
plt.show()


# Scatter   ###################################################################
title = "Scatter"
N = 4
M = 15
dists = [np.random.uniform, np.random.standard_normal, np.random.laplace, 
         np.random.standard_exponential]

for i, func in enumerate(dists):
    x = func(size = M)
    y = func(size = M)
    plt.scatter(x, y, label = f'{i}th dist')

add_labels(title = title)
plt.legend()
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)
plt.show()


# Marginal plots ##############################################################
title = "Marginal Scatter"
# stolen from matplotlib
def scatter_hist(x, y, ax, ax_histx, ax_histy):
    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)

    # the scatter plot:
    ax.scatter(x, y, alpha = 0.5)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histx.hist(x, bins=bins)
    ax_histy.hist(y, bins=bins, orientation='horizontal')
# Create a Figure, which doesn't have to be square.
x = np.random.randn(1000)
y = np.random.randn(1000)
fig = plt.figure()
# Create the main axes, leaving 25% of the figure space at the top and on the
# right to position marginals.
ax = fig.add_gridspec(top=0.75, right=0.75).subplots()
# The main axes' aspect can be fixed.
ax.set(aspect=1)
# Create marginal axes, which have 25% of the size of the main axes.  Note that
# the inset axes are positioned *outside* (on the right and the top) of the
# main axes, by specifying axes coordinates greater than 1.  Axes coordinates
# less than 0 would likewise specify positions on the left and the bottom of
# the main axes.
ax_histx = ax.inset_axes([0, 1.05, 1, 0.25], sharex=ax)
ax_histy = ax.inset_axes([1.05, 0, 0.25, 1], sharey=ax)
# Draw the scatter plot and marginals.
scatter_hist(x, y, ax, ax_histx, ax_histy)

add_labels(title = '')
ax_histx.set_title(title)
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)
plt.show()


# Exponential Scale Fit #######################################################
title = "Exponential Scale Best Fit"
fig, (ax, ax_resid) = plt.subplots(2, 1, figsize=(6, 6), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]})
plt.subplots_adjust(hspace=0.1)
np.random.seed(444)
a = 1
b = 100

def func(x, A, B):
    return A*np.exp(x) + B*np.sin(x)/x

x = np.linspace(0.1,10,20)
y = func(x, a, b)*(1 + np.random.normal(scale = 0.1, size = 20)/x)
yerr = np.random.poisson(lam=7, size=20)*np.sqrt(func(x, a, b))**(2/3)
ax.errorbar(x, y, yerr = yerr, fmt='.', color='C0', label='Data')

pOpt, pCov = curve_fit(func, x, y, sigma=yerr, absolute_sigma=True, maxfev=6000)
errvec = np.sqrt(np.diag(pCov))
A, B = pOpt
Aerr, Berr = errvec 
modelx = np.linspace(0.95*np.min(x), 1.05*np.max(x), 100)
modely = func(modelx, A, B)
ax.plot(modelx, modely, '-', color='C1', label='Least Squares Fit')

resid = y - func(x, A, B)
normres = resid/yerr

ax_resid.plot(x, normres, '.', color='C0')

ax.set(ylabel='y', title=title)
ax_resid.set(xlabel='x')
ax.set_yscale('log')
ax.legend()
plt.savefig(f"{testOutPath}{title}.png", dpi = 300)

plt.show()



# Amplitude multiples
N = 6
offset = 1

amp = 0.7 + np.random.normal(scale = 0.15, size = N)



# colormap



# 3D contour




