"""
My custom plotting helper functions for day to day!
Created on Sat Aug 20 2023

@author: hamishj

Contributions 'borrowed' from:
 -
"""
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist
from matplotlib.collections import LineCollection
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle
from matplotlib.transforms import Bbox

from hamhelper import colours as _colours


# %----------------------------------------------------------------%
#  Figure helpers: panels, colourbars, circular axes, annotations, saving.
#
#  They read matplotlib's rcParams when called, never when imported, so they follow whatever style is in force
#  (hamhelper.install, plt.style.use(...) or matplotlib's own defaults). Plates behind labels take axes.facecolor
#  and outlines take axes.edgecolor, so they suit a dark style as well as a light one.

# Keyword aliases that matplotlib refuses to see together (ls= next to linestyle=).
_ALIASES = {'color': ('c',), 'linestyle': ('ls',), 'linewidth': ('lw',), 'fontsize': ('size',),
            'fontweight': ('weight',)}


def _setdefaults(kw: dict, **defaults) -> dict:
    """kw.setdefault for keywords with short aliases, so a caller's ls= is not rejected beside our linestyle=."""
    for name, value in defaults.items():
        if name not in kw and not any(alias in kw for alias in _ALIASES.get(name, ())):
            kw[name] = value
    return kw


def _tick_label_pt() -> float:
    """Size of the tick labels in points (rcParams may hold a name such as 'medium')."""
    return FontProperties(size=mpl.rcParams['xtick.labelsize']).get_size_in_points()


def _renderer(fig):
    """A renderer for measuring text before the first draw (the API moved between matplotlib releases)."""
    if hasattr(fig, '_get_renderer'):
        return fig._get_renderer()
    return fig.canvas.get_renderer()


class _BesideLocator:
    """Places an axes just right of `parent`, exactly as tall as `parent`, with a width and gap fixed in POINTS.

    Evaluated at draw time, so it follows the parent through aspect='equal' and constrained layout, and the bar
    stays the same physical thickness whether the panel is 2 in or 5 in wide."""

    def __init__(self, parent, gap_pt, width_pt):
        self.parent, self.gap, self.width = parent, gap_pt, width_pt

    def __call__(self, ax, renderer):
        fig = ax.get_figure()
        k = fig.dpi / 72.0
        bb = self.parent.bbox
        box = Bbox.from_bounds(bb.x1 + self.gap * k, bb.y0, self.width * k, bb.height)
        return box.transformed(fig.transFigure.inverted())


def colorbar(mappable, ax=None, label: str = None, width: float = None, pad: float = None, **kw):
    """Colourbar exactly as tall as the axes it belongs to.

    A stock fig.colorbar stays full slot height and overshoots a panel that aspect='equal' has shrunk. This one is
    an inset child of the panel, so its height IS the panel's height, and its thickness is set in points (default
    0.8 x the tick-label size) so it is the same weight at every figure size. Primary ticks only, pointing out:
    inward ticks vanish against the dark end of a sequential map, the one deliberate break from the journal
    variant's inward rule.

    Args:
        mappable: the image, contour set or collection the bar describes.
        ax (Axes or array of Axes, optional): panel to match; the first one if several. Defaults to the axes the
            mappable lives on.
        label (str, optional): label for the bar.
        width (float, optional): thickness in points. Defaults to 0.8 x the tick-label size.
        pad (float, optional): gap to the panel in points. Defaults to 0.8 x the tick-label size, plus whatever
            room polar_frame reserved for an east label.
        **kw: passed to fig.colorbar. Pass cax=<axes> to draw into your own axes (a gridspec cell, say) instead;
            width and pad are then ignored. Do that too in a tight multi-column figure, where the label of a bar
            can touch the next panel.

    Returns:
        matplotlib.colorbar.Colorbar
    """
    cax = kw.pop('cax', None)
    if cax is None:
        if ax is None:
            parent = getattr(mappable, 'axes', None) or plt.gca()
        else:
            parent = np.ravel(ax)[0] if np.iterable(ax) else ax
        unit = _tick_label_pt()
        width = 0.8 * unit if width is None else width
        pad = (0.8 * unit + getattr(parent, '_ham_rim', (0.0, 0.0))[0]) if pad is None else pad
        cax = parent.inset_axes([1.0, 0.0, 0.05, 1.0])  # placeholder bounds, the locator sets the real ones
        cax.set_axes_locator(_BesideLocator(parent, pad, width))
    cb = mappable.axes.figure.colorbar(mappable, cax=cax, **kw)
    lw = mpl.rcParams['axes.linewidth']
    cb.outline.set_linewidth(lw)
    cb.outline.set_edgecolor(mpl.rcParams['axes.edgecolor'])
    cb.ax.minorticks_off()
    cb.ax.tick_params(which='major', direction='out', width=lw, length=mpl.rcParams['xtick.major.size'] * 0.8)
    if label:
        cb.set_label(label)
    return cb


def framed(ax):
    """Box an image panel: all four spines, ticks inward AND on top of the image.

    A filled field (image, pcolormesh, filled contours) needs a boundary even when the line plots beside it are
    open. Call this on image panels in the comms variant; it changes nothing in the journal variant.
    """
    for spine in ax.spines.values():
        spine.set_visible(True)
    ax.tick_params(which='both', top=True, right=True, direction='in')
    ax.set_axisbelow(False)
    return ax


# %----------------------------------------------------------------%
#  Circular axes
def _polar_geometry(ax):
    """(rmax, to_display_angle, from_display_angle) for a polar axes, honouring theta offset and direction."""
    rmax = ax.get_ylim()[1]
    off, sgn = ax.get_theta_offset(), ax.get_theta_direction()
    return rmax, (lambda th: off + sgn * th), (lambda phi: (phi - off) / sgn)


def _ha_va(dx, dy, tol=0.35):
    ha = 'left' if dx > tol else 'right' if dx < -tol else 'center'
    va = 'bottom' if dy > tol else 'top' if dy < -tol else 'center'
    return ha, va


def _pt_annotate_line(ax, xy, off_pt, color, lw, xycoords='data', zorder=6):
    """A straight line of fixed LENGTH IN POINTS starting at `xy`, pointing `off_pt`.

    Tick marks must not scale with the axes, so they cannot be drawn in data units."""
    ax.annotate('', xy=xy, xycoords=xycoords, xytext=off_pt, textcoords='offset points',
                arrowprops=dict(arrowstyle='-', color=color, lw=lw, shrinkA=0, shrinkB=0, capstyle='butt'),
                annotation_clip=False, zorder=zorder)


def polar_frame(ax, ticks='cardinal', labels=None, radial: str = 'spoke', rticks=(0.5, 1.0), rlabels=None,
                rlabel: str = None, rangle: float = 315.0, crosshair: bool = True, rings: bool = True,
                direction: str = 'in', color=None, leader: dict = None):
    """Dress a polar axes as a clean circular panel.

    Args:
        ax (Axes): a polar axes. Call this AFTER plotting and after set_ylim(0, rmax).
        ticks: angular ticks on the rim. 'cardinal' = 4 majors; '30' = 30 deg majors + 10 deg minors; '45' = 45 deg
            majors + 22.5 deg minors; or a (major, minor) tuple in degrees, e.g. (90, 30); None for none.
        labels: rim labels at the majors: None, 'deg', 'compass' (E N W S), or a dict {angle_deg: text}.
        radial: how the radius is annotated.
            'spoke'  a radial axis line at `rangle` with perpendicular ticks and numerals beside them (on a pale
                     plate, so they stay legible over colour);
            'leader' the radial axis runs from the centre to the 6 o'clock rim; each major tick sends a thin grey
                     line left to the circle's extreme x, where the numeral sits in a column, like a y axis;
            None     no radial annotation.
        rticks: radii (data units) that get ticks.
        rlabels: text for each of rticks. Defaults to '%g' of the radius.
        rlabel (str, optional): axis title for the radius ('leader': rotated, beside the numerals).
        rangle (float): angle of the spoke in degrees.
        crosshair (bool): dashed centre cross.
        rings (bool): dotted rings at the interior radii in rticks.
        direction ('in' or 'out'): which way the rim ticks point.
        color: colour of the frame, ticks and guides. Defaults to rcParams['axes.edgecolor'].
        leader (dict, optional): style overrides for the leader layout, e.g. dict(color='#888', alpha=1, lw=0.8,
            pad=5): lw is a multiple of axes.linewidth, pad the gap in points between line end and numeral.

    Everything is drawn in points or axes fractions, so it looks the same at every figure size. The room the rim
    labels need on the east side is remembered on the axes so that colorbar() clears it.

    Returns:
        ax
    """
    presets = {'cardinal': (90, None), '30': (30, 10), '45': (45, 22.5)}
    if isinstance(ticks, str) and ticks not in presets:
        raise ValueError("ticks must be one of {}, a (major, minor) tuple or None, not {!r}"
                         .format(sorted(presets), ticks))
    if radial not in ('spoke', 'leader', None):
        raise ValueError("radial must be 'spoke', 'leader' or None, not {!r}".format(radial))
    if direction not in ('in', 'out'):
        raise ValueError("direction must be 'in' or 'out', not {!r}".format(direction))
    if color is None:
        color = mpl.rcParams['axes.edgecolor']
    names = list(rlabels) if rlabels is not None else ['{:g}'.format(r) for r in rticks]
    if len(names) != len(rticks):
        raise ValueError('rlabels has {} entries but rticks has {}'.format(len(names), len(rticks)))

    rmax, phi, theta_of = _polar_geometry(ax)
    lw = mpl.rcParams['axes.linewidth']
    fs = _tick_label_pt()
    Lmaj = mpl.rcParams['xtick.major.size']
    Lrim, Lrim_min, Lrad = Lmaj, max(mpl.rcParams['xtick.minor.size'], 0.6 * Lmaj), Lmaj
    lead = dict(color='#555555', alpha=0.75, lw=0.55, pad=3.5)
    lead.update(leader or {})
    sgn_in = -1.0 if direction == 'in' else 1.0

    ax._ham_rim = (0.0, 0.0)  # points the rim labels need beside (east) and above/below (north/south) the circle
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.spines['polar'].set_linewidth(lw)
    ax.spines['polar'].set_edgecolor(color)
    ax.set_axisbelow(False)

    # --- rim ticks ----------------------------------------------------------------------------------------
    major, minor = presets[ticks] if isinstance(ticks, str) else (ticks or (None, None))
    marks = {}
    if major:
        for a in np.arange(0, 360, major):
            marks[round(a % 360, 6)] = Lrim
    if minor:
        for a in np.arange(0, 360, minor):
            marks.setdefault(round(a % 360, 6), Lrim_min)
    for a, length in marks.items():
        p = phi(np.deg2rad(a))
        _pt_annotate_line(ax, (np.deg2rad(a), rmax), (sgn_in * length * np.cos(p), sgn_in * length * np.sin(p)),
                          color, mpl.rcParams['xtick.major.width'])
    if labels:
        if labels == 'deg':
            lab = {a: '{:g}°'.format(a) for a in (np.arange(0, 360, major) if major else [])}
        elif labels == 'compass':
            lab = {0: 'E', 90: 'N', 180: 'W', 270: 'S'}
        else:
            lab = dict(labels)
        off = Lmaj * 0.6 + 2
        try:
            rend = _renderer(ax.figure)
            k = 72.0 / ax.figure.dpi
        except Exception:
            rend = None
        rim_x = rim_y = 0.0
        for a, t in lab.items():
            p = phi(np.deg2rad(a))
            dx, dy = np.cos(p), np.sin(p)
            if radial == 'leader' and dx < -0.05 and dy < -0.05:
                continue  # the lower-left quadrant belongs to the leader lines and numerals
            ha, va = _ha_va(dx, dy)
            ann = ax.annotate(t, xy=(np.deg2rad(a), rmax), xycoords='data', xytext=(dx * off, dy * off),
                              textcoords='offset points', ha=ha, va=va, fontsize=fs * 0.92, annotation_clip=False)
            if rend is not None:
                ext = ann.get_window_extent(rend)
                w_pt, h_pt = ext.width * k, ext.height * k
            else:
                w_pt, h_pt = 0.6 * fs * len(t), 1.2 * fs
            if dx > 0.9:  # east label: pushes the colourbar out
                rim_x = max(rim_x, off + w_pt)
            if abs(dy) > 0.9:  # north / south label: pushes the title / xlabel out
                rim_y = max(rim_y, off + h_pt)
        ax._ham_rim = (rim_x, rim_y)

    # --- guides: dotted rings at interior radii, dashed centre cross -----------------------------------------
    th = np.linspace(0, 2 * np.pi, 361)
    if rings:
        for r in rticks:
            if 0 < r < rmax:
                ax.plot(th, np.full_like(th, r), color=color, alpha=0.28, lw=lw * 0.6, ls=(0, (1, 2.5)), zorder=3)
    spoke_phi = np.deg2rad(270.0) if radial == 'leader' else phi(np.deg2rad(rangle))
    if crosshair:
        for a in (0, 90, 180, 270):
            p = phi(np.deg2rad(a))
            if radial and abs(np.cos(p - spoke_phi) - 1) < 1e-6:
                continue  # the spoke owns this half-axis
            ax.plot([theta_of(p)] * 2, [0, rmax], color=color, alpha=0.4, lw=lw * 0.7, ls=(0, (4, 3)), zorder=3)

    # --- radial axis ------------------------------------------------------------------------------------------
    if not radial:
        return ax
    th_s = theta_of(spoke_phi)
    ax.plot([th_s, th_s], [0, rmax], color=color, lw=lw, solid_capstyle='butt', zorder=5)
    px, py = -np.sin(spoke_phi), np.cos(spoke_phi)  # perpendicular to the spoke
    texts = []
    for r, name in zip(rticks, names):
        for sgn in (+1, -1):  # symmetric tick across the spoke
            _pt_annotate_line(ax, (th_s, r), (sgn * px * Lrad / 2, sgn * py * Lrad / 2), color,
                              mpl.rcParams['xtick.major.width'])
        if radial == 'spoke':
            off = Lrad / 2 + 2.5
            ha, va = _ha_va(px, py)
            texts.append(ax.annotate(name, xy=(th_s, r), xycoords='data', xytext=(px * off, py * off),
                                     textcoords='offset points', ha=ha, va=va, fontsize=fs, annotation_clip=False,
                                     bbox=dict(fc=mpl.rcParams['axes.facecolor'], ec='none', alpha=0.85, pad=1.2),
                                     zorder=7))
        else:  # 'leader'
            y = 0.5 - 0.5 * r / rmax  # axes-fraction height of the tick
            ax.plot([0.5, 0.0], [y, y], transform=ax.transAxes, clip_on=False, color=lead['color'],
                    alpha=lead['alpha'], lw=lw * lead['lw'], zorder=4)
            texts.append(ax.annotate(name, xy=(0.0, y), xycoords='axes fraction', xytext=(-lead['pad'], 0),
                                     textcoords='offset points', ha='right', va='center', fontsize=fs,
                                     annotation_clip=False))
    if rlabel and radial == 'leader':
        try:  # measure the column of numerals
            rend = _renderer(ax.figure)
            wpt = max(t.get_window_extent(rend).width for t in texts) * 72 / ax.figure.dpi
        except Exception:
            wpt = 0.56 * fs * max(len(n) for n in names)
        ax.annotate(rlabel, xy=(0.0, 0.25), xycoords='axes fraction', xytext=(-(lead['pad'] + wpt + 4), 0),
                    textcoords='offset points', ha='right', va='center', rotation=90,
                    fontsize=mpl.rcParams['axes.labelsize'], annotation_clip=False)
    elif rlabel:
        ax.annotate(rlabel, xy=(0.5, 0.0), xycoords='axes fraction', xytext=(0, -Lmaj - 4 - ax._ham_rim[1]),
                    textcoords='offset points', ha='center', va='top', fontsize=mpl.rcParams['axes.labelsize'],
                    annotation_clip=False)
    return ax


def disc(ax, artists, r: float = 1.0, offset_pt: float = 4.0, color=None):
    """Cartesian axes on a circular frame.

    Clips `artists` to a disc of radius r and draws the circle as the panel frame, keeping ordinary x and y ticks on
    offset left and bottom spines, so the numerals read like any other plot and the circle just *is* the boundary
    of the data.

    Args:
        ax (Axes): ordinary axes, centred on the origin.
        artists: the artist or list of artists to clip: images, collections and contour sets all work.
        r (float): radius of the disc in data units.
        offset_pt (float): how far the left and bottom spines sit outside the axes, in points.
        color: colour of the circle. Defaults to rcParams['axes.edgecolor'].

    Returns:
        ax
    """
    if color is None:
        color = mpl.rcParams['axes.edgecolor']
    lw = mpl.rcParams['axes.linewidth']
    clip = Circle((0, 0), r, transform=ax.transData)
    for a in (list(artists) if isinstance(artists, (list, tuple)) else [artists]):
        # matplotlib >= 3.8: a ContourSet is an Artist. Before that it is a bag of collections.
        for piece in ([a] if isinstance(a, Artist) else a.collections):
            piece.set_clip_path(clip)
    ax.add_patch(Circle((0, 0), r, fill=False, ec=color, lw=lw, zorder=6))
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_position(('outward', offset_pt))
        ax.spines[side].set_bounds(-r, r)
        ax.spines[side].set_linewidth(lw)
    ax.tick_params(which='both', top=False, right=False, direction='out')
    ax.set_aspect('equal')
    return ax


def fit_height(fig, ax, grow: bool = False, iterations: int = 6):
    """Trim the figure HEIGHT so an equal-aspect panel (circle, square image) fills the figure WIDTH exactly.

    Constrained layout cannot shrink a panel whose aspect is fixed: if the labels, leader numerals and colourbar
    need more width than the fixed figure width leaves, they spill past the page edge instead. The panel's
    diameter is D = width - 2*pad - (everything beside the panel); this sets the height to match.

    Args:
        fig (Figure): figure to resize (its width is kept).
        ax (Axes): the equal-aspect panel.
        grow (bool): False never makes the figure taller than you asked for.
        iterations (int): refinement passes; it stops early once the height settles to 0.003 in.

    Returns:
        fig
    """
    wp = mpl.rcParams['figure.constrained_layout.w_pad']
    hp = mpl.rcParams['figure.constrained_layout.h_pad']
    W, H = fig.get_size_inches()
    for _ in range(iterations):
        fig.canvas.draw()
        rend = _renderer(fig)
        ab, tb = ax.get_window_extent(rend), ax.get_tightbbox(rend)
        k = 1.0 / fig.dpi
        extras_w = (tb.width - ab.width) * k
        extras_h = (tb.height - ab.height) * k
        D = W - 2 * wp - extras_w
        new_h = D + extras_h + 2 * hp
        if not grow:
            new_h = min(new_h, H)
        if abs(new_h - fig.get_size_inches()[1]) < 0.003:
            break
        fig.set_size_inches(W, new_h)
    return fig


def square_figure(fig, ax, iterations: int = 4):
    """Resize the figure's HEIGHT until `ax` is exactly square on the page.

    Constrained layout fixes margins in inches, so once those are known the height that makes a given axes square
    is a simple correction. Use it for joint plots, where aspect='equal' cannot be asked of axes tied to their
    marginals.
    """
    for _ in range(iterations):
        fig.canvas.draw()
        w, h = fig.get_size_inches()
        bb = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        if abs(bb.width - bb.height) < 0.003:
            break
        fig.set_size_inches(w, h + (bb.width - bb.height))
    return fig


# %----------------------------------------------------------------%
#  Labels, guides and annotations
def units(ax, axis: str, name: str, unit: str = None) -> str:
    """Axis label in the house convention: units(ax, 'y', 'Radial jitter', 'urad') -> 'Radial jitter [urad]'.

    Returns the text it set."""
    if axis not in ('x', 'y'):
        raise ValueError("axis must be 'x' or 'y', not {!r}".format(axis))
    text = '{} [{}]'.format(name, unit) if unit else name
    (ax.set_xlabel if axis == 'x' else ax.set_ylabel)(text)
    return text


def runs(ax, x, Y, color=None, label: str = None, summary: str = 'mean', alpha: float = 0.35):
    """Thin translucent per-run traces beneath a bold aggregate.

    Y is (n_runs, n_points). Shows the spread and the summary at once, which a mean with error bars hides and a
    spaghetti plot buries. The aggregate is an ordinary ax.plot line, so it takes the next colour of the cycle (and
    its dash or marker under a redundancy cycle) unless `color` is given; the traces are ONE LineCollection in that
    colour, so they never use up cycle slots.

    Args:
        ax (Axes): axes to draw on.
        x: the shared x values, (n_points,).
        Y: one row per run, (n_runs, n_points).
        color (optional): colour for the aggregate and the traces.
        label (str, optional): legend label (given to the aggregate only).
        summary ('mean' or 'median'): which aggregate to draw.
        alpha (float): opacity of the traces.

    Returns:
        list of Line2D: the aggregate line, as ax.plot returns.
    """
    if summary not in ('mean', 'median'):
        raise ValueError("summary must be 'mean' or 'median', not {!r}".format(summary))
    Y = np.atleast_2d(np.asarray(Y, float))
    x = np.asarray(x, float)
    lw = mpl.rcParams['lines.linewidth']
    agg = Y.mean(0) if summary == 'mean' else np.median(Y, axis=0)
    kw = {} if color is None else {'color': color}
    lines = ax.plot(x, agg, lw=lw * 1.25, label=label, zorder=2.5, **kw)
    traces = LineCollection([np.column_stack((x, row)) for row in Y], colors=[lines[0].get_color()],
                            linewidths=lw * 0.45, alpha=alpha, zorder=1.5,
                            capstyle=mpl.rcParams['lines.solid_capstyle'],
                            joinstyle=mpl.rcParams['lines.solid_joinstyle'])
    ax.add_collection(traces)
    ax.autoscale_view()
    return lines


def spec_tick(ax, value: float, axis: str = 'y') -> float:
    """Add a tick at a requirement value, keeping the automatic ones.

    Puts the specification on the axis itself rather than in the caption. Call it after the limits are final.
    """
    if axis not in ('x', 'y'):
        raise ValueError("axis must be 'x' or 'y', not {!r}".format(axis))
    get, put = (ax.get_yticks, ax.set_yticks) if axis == 'y' else (ax.get_xticks, ax.set_xticks)
    lo, hi = ax.get_ylim() if axis == 'y' else ax.get_xlim()
    lo, hi = min(lo, hi), max(lo, hi)
    keep = [t for t in get() if lo <= t <= hi and abs(t - value) > 1e-9]
    put(sorted(keep + [value]))
    return value


def band(ax, lo: float, hi: float, axis: str = 'y', color: str = '#FCDB8E', label: str = None, alpha: float = 1.0):
    """Target or acceptance band as a filled span, behind the data, with a legend patch if `label` is given."""
    if axis not in ('x', 'y'):
        raise ValueError("axis must be 'x' or 'y', not {!r}".format(axis))
    span = ax.axhspan if axis == 'y' else ax.axvspan
    return span(lo, hi, color=color, lw=0, alpha=alpha, zorder=0.3, label=label)


def tag(ax, text: str, loc: str = 'lower left', pad: float = 0.03, **kw):
    """Corner label on a pale plate, legible on top of a filled field.

    Args:
        ax (Axes): axes to label.
        text (str): the label.
        loc (str): 'lower left', 'lower right', 'upper left' or 'upper right'.
        pad (float): distance from the corner, as a fraction of the axes.
        **kw: passed to ax.text (fontsize defaults to axes.labelsize; a bbox= replaces the plate).
    """
    if loc not in ('lower left', 'lower right', 'upper left', 'upper right'):
        raise ValueError("loc must be 'lower|upper left|right', not {!r}".format(loc))
    ha, va = 'left', 'bottom'
    x, y = pad, pad
    if 'right' in loc:
        ha, x = 'right', 1 - pad
    if 'upper' in loc:
        va, y = 'top', 1 - pad
    _setdefaults(kw, fontsize=mpl.rcParams['axes.labelsize'])
    kw.setdefault('bbox', dict(facecolor=mpl.rcParams['axes.facecolor'], alpha=0.78, edgecolor='none', pad=1.8))
    return ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, **kw)


def panel_label(ax, text: str, loc=(0.03, 0.97), **kw):
    """Bold panel letter, e.g. '(a)', inside the top-left corner of the axes.

    loc is in axes fractions; **kw go to ax.text (weight and fontsize can be overridden)."""
    _setdefaults(kw, fontweight='bold', fontsize=mpl.rcParams['axes.labelsize'])
    return ax.text(*loc, text, transform=ax.transAxes, ha='left', va='top', **kw)


def guide(ax, which: str = 'y', value: float = 0.0, label: str = None, **kw):
    """Dashed grey reference line (zero, a requirement level, a guide to the eye), behind the data.

    which is 'y' for a horizontal line at y=value and 'x' for a vertical line at x=value; **kw go to
    axhline / axvline (color, linewidth and linestyle can be overridden, with or without the short names)."""
    if which not in ('x', 'y'):
        raise ValueError("which must be 'x' or 'y', not {!r}".format(which))
    _setdefaults(kw, color=_colours.GREY, linewidth=mpl.rcParams['axes.linewidth'] * 1.2, linestyle=(0, (4, 2)))
    kw.setdefault('zorder', 0.5)
    line = (ax.axhline if which == 'y' else ax.axvline)(value, **kw)
    if label:
        line.set_label(label)
    return line


# %----------------------------------------------------------------%
def save(fig, name: str, outdir: str = 'figures', size: str = None, variant: str = None,
         formats=('pdf', 'png'), suffix: str = None, dpi: int = 600) -> dict:
    """Write fig at its true physical size, once per format.

    Files are named name__size__variant__suffix.ext with whichever parts are given, so one script can write every
    size and variant side by side. It never uses bbox_inches='tight'; a figure comes out the size it was made, as
    long as rcParams['savefig.bbox'] is 'standard' (hamstyle sets that).

    Args:
        fig (Figure): the figure.
        name (str): file stem.
        outdir (str): folder, made if missing.
        size, variant, suffix (str, optional): parts to add to the file name.
        formats: file extensions to write.
        dpi (int): resolution of 'png'; other formats follow rcParams['savefig.dpi'].

    Returns:
        dict: {extension: pathlib.Path} of the files written.
    """
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = '__'.join(part for part in (name, size, variant, suffix) if part)
    paths = {}
    for ext in formats:
        path = outdir / '{}.{}'.format(stem, ext)
        fig.savefig(path, format=ext, dpi=dpi if ext == 'png' else None)
        paths[ext] = path
    return paths


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
