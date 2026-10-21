"""Unit testing for plotting module."""
import hamhelper.plotting as hp
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def _axes_with_ticks():
    fig, ax = plt.subplots()
    ax.plot([0.5, 9.5], [0.5, 9.5])
    ax.set_xlim(0.5, 9.5)
    ax.set_ylim(0.5, 9.5)
    ax.set_xticks(range(0, 11, 2))
    ax.set_yticks(range(1, 12, 2))
    ax.set_xlim(0.5, 9.5)
    ax.set_ylim(0.5, 9.5)
    return ax


def test_despine_defaults_to_current_axes():
    fig, ax = plt.subplots()
    assert hp.despine() is None
    assert [ax.spines[s].get_visible() for s in ('top', 'right', 'bottom', 'left')] == [False, False, True, True]


def test_despine_flags():
    _, ax = plt.subplots()
    hp.despine(ax, bottom=False, left=False, top=True, right=True)
    assert [ax.spines[s].get_visible() for s in ('top', 'right', 'bottom', 'left')] == [True, True, False, False]


def test_despine_trim_clips_spines_to_outer_ticks():
    ax = _axes_with_ticks()
    hp.despine(ax, trim=True)
    assert ax.spines['bottom'].get_bounds() == (2, 8)
    assert ax.spines['left'].get_bounds() == (1, 9)
    assert list(ax.get_xticks()) == [2, 4, 6, 8]
    assert list(ax.get_yticks()) == [1, 3, 5, 7, 9]


def test_despine_drop_and_noline():
    _, ax = plt.subplots()
    hp.despine(ax, drop=5, noLine=True)
    assert ax.spines['left'].get_position() == ('outward', 5)
    assert ax.spines['bottom'].get_position() == ('outward', 5)
    assert not ax.spines['left'].get_visible() and not ax.spines['bottom'].get_visible()


def test_errorbands_fills_between_y_minus_and_plus_error():
    _, ax = plt.subplots()
    x = np.linspace(0, 1, 10)
    y = x ** 2
    yerr = np.full_like(x, 0.1)
    poly = hp.errorbands(x, y, yerr, ax=ax, color='C0', alpha=0.3)
    assert poly in ax.collections
    assert np.allclose(mcolors.to_rgb('C0'), poly.get_facecolor()[0][:3])
    assert np.isclose(ax.dataLim.y0, (y - yerr).min()) and np.isclose(ax.dataLim.y1, (y + yerr).max())
    assert not ax.containers, 'no caps were requested'


def test_errorbands_capsize_adds_caps_and_default_axes():
    fig, ax = plt.subplots()
    x = np.arange(5.)
    hp.errorbands(x, x, np.ones(5), capsize=3)
    assert len(ax.containers) == 1


def test_errorbands_without_colour():
    _, ax = plt.subplots()
    assert hp.errorbands(np.arange(3.), np.arange(3.), np.ones(3), ax=ax) in ax.collections
