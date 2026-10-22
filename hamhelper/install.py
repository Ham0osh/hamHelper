"""Opt-in matplotlib look for hamhelper figures.

``import hamhelper`` never touches matplotlib's settings, and neither does importing this module. Nothing changes
until you call one of the setters below::

    import hamhelper.install as hi

    hi.style.hamstyle()           # the look: light, serif, one column, journal frame (or alightroom / adarkroom)
    hi.size.two_col()             # every figure from now on is 6.90 in wide
    with hi.size.one_col():       # ...except the ones made inside this block
        fig, ax = plt.subplots()

The look is built from independent axes. Each axis holds one choice at a time:

    =============  =============================================  =============
    axis           what it controls                               default
    =============  =============================================  =============
    style          the overall look (hamstyle, alightroom,        hamstyle
                   adarkroom)
    size           figure size and type size                      one_col
                   (one_col, one_col_tall, two_col, slide)
    variant        frame and tick geometry (journal, comms)       journal
    font           typeface (serif, sans)                         serif
    palette        colour cycle (default, tol, alight, adark)     default
    cmap           default colormap for images (sunset_warm,      sunset_warm
                   sunset_warm_w, grey, grey_dark, iridescent,
                   viridis, or any registered name)
    redundancy     line style / marker per colour                 off
                   (off, dash, marker, both)
    grid           faint dotted grid (off, on)                    off
    =============  =============================================  =============

The setters are stateful and order independent: ``hi.size.two_col(); hi.font.sans()`` and
``hi.font.sans(); hi.size.two_col()`` give identical rcParams, and the first call of any kind applies the whole look
with the defaults above for everything you have not chosen. A style may declare its own defaults for the other axes
(alightroom and adarkroom ask for their own grey palette and colormap and for a line style per series); your explicit choices
always win over those, whatever the call order.
The first call also registers hamhelper's colormaps with matplotlib, because the default image.cmap is one of them.

Every setter takes effect immediately and also returns a handle that undoes it when used in a ``with`` block::

    hi.palette.tol()              # stays in force
    with hi.variant.comms():      # only inside the block
        ...

``hi.apply(size="slide", variant="comms")`` sets several axes in one go, ``hi.current()`` reports what is in force,
and ``hi.reset()`` puts matplotlib's settings back as they were before the first call.

Each setter rewrites only the rcParams its own axis owns, so a hand edit of anything else
(``plt.rcParams["lines.linewidth"] = 2`` after choosing the palette) survives later calls. Choosing the style is the
exception: it rewrites the whole look. A ``with`` block undoes everything inside it, hand edits included.
"""
from pathlib import Path

import matplotlib as mpl

from hamhelper import colours as _colours

__all__ = ['style', 'size', 'variant', 'font', 'palette', 'cmap', 'redundancy', 'grid',
           'apply', 'reset', 'current', 'options']

_STYLE_DIR = Path(__file__).resolve().parent / 'styles'

# %------------------- What exists -------------------%

#: Every axis, in the order its layer is applied (a later axis overrides an earlier one where they overlap).
_AXES = ('style', 'size', 'variant', 'font', 'palette', 'cmap', 'redundancy', 'grid')

_CHOICES = {
    'style': ('hamstyle', 'alightroom', 'adarkroom'),
    'size': ('one_col', 'one_col_tall', 'two_col', 'slide'),
    'variant': ('journal', 'comms'),
    'font': ('serif', 'sans'),
    'palette': ('default', 'tol', 'alight', 'adark'),  # really whatever is in colours.PALETTES, see _choices()
    'cmap': ('ham_sunset_warm', 'ham_sunset_warm_w', 'ham_grey', 'ham_grey_dark', 'ptol_iridescent', 'viridis'),
    # any registered name works too
    'redundancy': ('off', 'dash', 'marker', 'both'),
    'grid': ('off', 'on'),
}

#: What you get on an axis when neither you nor the style has said anything about it.
_DEFAULTS = {
    'style': 'hamstyle',
    'size': 'one_col',
    'variant': 'journal',
    'font': 'serif',
    'palette': 'default',
    'cmap': 'ham_sunset_warm',
    'redundancy': 'off',
    'grid': 'off',
}

#: style name -> style file in hamhelper/styles/ (without .mplstyle). A style file is a complete, standalone look.
_STYLE_FILES = {
    'hamstyle': 'hamStyle',
    'alightroom': 'alightroom',
    'adarkroom': 'adarkroom',
}

#: What each style asks for on the OTHER axes. An explicit choice from the user beats this; this beats _DEFAULTS.
_STYLE_DEFAULTS = {
    'hamstyle': {},
    # the two monochrome rooms: their own greys, a grey map for images, and a line style per series (greys this
    # close are not told apart by tone alone). Not markers: a marker cycle breaks ax.fill and hist(histtype='step'),
    # see redundancy.marker()
    'alightroom': {'palette': 'alight', 'cmap': 'ham_grey', 'redundancy': 'dash'},
    'adarkroom': {'palette': 'adark', 'cmap': 'ham_grey_dark', 'redundancy': 'dash'},
}

# size / variant / font choices are files named '<axis>_<choice>.mplstyle' in hamhelper/styles/.
_FILE_AXES = ('size', 'variant', 'font')

# %------------------- Typeface scaling -------------------%

#: Helvetica-class sans has a cap height of 0.72 em against Times' 0.66, so the same point size reads about 8% bigger.
#: Choosing the sans font scales the six text sizes of the size file by this.
_SANS_SCALE = 0.92
_TEXT_SCALE = {'serif': 1.0, 'sans': _SANS_SCALE}
_TEXT_SIZES = ('font.size', 'axes.titlesize', 'axes.labelsize', 'xtick.labelsize', 'ytick.labelsize',
               'legend.fontsize')

# %------------------- Choices -------------------%
def _choices(axis):
    """The names an axis accepts. Palettes are whatever colours.PALETTES holds, so adding one there adds it here."""
    if axis == 'palette':
        return tuple(_colours.PALETTES)
    return _CHOICES[axis]


def _ensure_cmap(name):
    """Make sure `name` is in matplotlib's colormap registry, registering hamhelper's maps if need be."""
    if name not in mpl.colormaps:
        _colours.register_cmaps()
    if name not in mpl.colormaps:
        raise ValueError('unknown colormap {!r}: not in matplotlib or hamhelper.colours'.format(name))


# %------------------- State -------------------%

#: explicit: only what has been chosen by a setter call (axis -> choice).
#: applied: the full set of choices in force after the last setter call, or None before the first.
#: baseline: matplotlib's settings before our first change, for reset().
_STATE = {'explicit': {}, 'applied': None, 'baseline': None}


def _raw_rc():
    """Copy of the current rcParams, bypassing validation and without resolving the backend."""
    return {k: v for k, v in dict.items(mpl.rcParams) if k != 'backend'}


def _restore_rc(snapshot):
    dict.update(mpl.rcParams, snapshot)


def _read(stem):
    """The settings in styles/<stem>.mplstyle. A bad value raises instead of being dropped with a log message."""
    path = _STYLE_DIR / (stem + '.mplstyle')
    return dict(mpl.rc_params_from_file(str(path), fail_on_error=True, use_default_template=False))


def _resolve(explicit):
    """Choice on every axis: what the user said, else what the style says, else the default."""
    style_name = explicit.get('style', _DEFAULTS['style'])
    declared = _STYLE_DEFAULTS[style_name]
    return {axis: explicit.get(axis) or declared.get(axis) or _DEFAULTS[axis] for axis in _AXES}


def _compose(choices, changed=None):
    """rcParams owned by the axes in `changed` (None = all of them), layer by layer. Reads files only.

    Changing the style rewrites everything, since a style file is the whole look and may declare defaults for the
    other axes. Any other axis rewrites only the keys it owns, so a hand edit elsewhere survives:
        size        every key of the size file (text sizes scaled for the current font)
        font        font.family, mathtext.fontset and the text sizes (rescaled)
        variant     the frame and tick keys
        palette, redundancy   axes.prop_cycle
        grid        axes.grid
    """
    todo = set(_AXES) if changed is None or 'style' in changed else set(changed)
    rc = {}
    if 'style' in todo:
        rc.update(_read(_STYLE_FILES[choices['style']]))
    if 'size' in todo or 'font' in todo:
        sizes = _read('size_' + choices['size'])
        if 'size' not in todo:
            sizes = {k: v for k, v in sizes.items() if k in _TEXT_SIZES}
        rc.update(sizes)
        scale = _TEXT_SCALE[choices['font']]
        if scale != 1.0:
            for key in _TEXT_SIZES:
                if isinstance(rc.get(key), (int, float)):
                    rc[key] = rc[key] * scale
    if 'font' in todo:
        rc.update(_read('font_' + choices['font']))
    if 'variant' in todo:
        rc.update(_read('variant_' + choices['variant']))
    if 'palette' in todo or 'redundancy' in todo:
        rc['axes.prop_cycle'] = _colours.palette(choices['palette']).cycler(choices['redundancy'])
    if 'cmap' in todo:
        _ensure_cmap(choices['cmap'])
        rc['image.cmap'] = choices['cmap']
    if 'grid' in todo:
        rc['axes.grid'] = choices['grid'] == 'on'
    return rc


class _Applied:
    """Returned by every setter. The change is already in force; used in a ``with`` block it is undone on exit."""

    def __init__(self, label, rc_before, explicit_before, applied_before):
        self._label = label
        self._rc = rc_before
        self._explicit = explicit_before
        self._applied = applied_before

    def undo(self):
        """Put matplotlib's settings and this module's choices back as they were before this change."""
        _restore_rc(self._rc)
        _STATE['explicit'] = dict(self._explicit)
        _STATE['applied'] = None if self._applied is None else dict(self._applied)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.undo()
        return False

    def __repr__(self):
        return '<hamhelper.install: {}>'.format(self._label)


def _commit(explicit, label, changed):
    """Make `explicit` the new set of choices and push the layers of the `changed` axes into rcParams.

    The first call of all applies every layer, whatever `changed` says."""
    if _STATE['applied'] is None:
        changed = None
    rc = _compose(_resolve(explicit), changed)  # may raise; nothing has been touched yet
    if _STATE['baseline'] is None:
        _STATE['baseline'] = _raw_rc()
    handle = _Applied(label, _raw_rc(), dict(_STATE['explicit']), _STATE['applied'])
    try:
        mpl.rcParams.update(rc)
    except Exception:
        handle.undo()
        raise
    _STATE['explicit'] = dict(explicit)
    _STATE['applied'] = _resolve(explicit)
    return handle


def _check_axis(axis):
    if axis not in _CHOICES:
        raise ValueError('unknown axis {!r}; choose from {}'.format(axis, ', '.join(_AXES)))


def _check(axis, choice):
    _check_axis(axis)
    if axis != 'cmap' and choice not in _choices(axis):  # any colormap name is accepted; _compose checks it exists
        raise ValueError('unknown {} {!r}; choose from {}'.format(axis, choice, ', '.join(_choices(axis))))


def _set(axis, choice):
    _check(axis, choice)
    explicit = dict(_STATE['explicit'])
    explicit[axis] = choice
    return _commit(explicit, '{}={}'.format(axis, choice), {axis})


# %------------------- One namespace per axis -------------------%
class _Axis:
    """One independent setting. Call one of its methods to choose; ``.options()`` lists them."""

    _axis = ''

    def set(self, choice):
        """Choose by name, for when the choice is in a variable: ``hi.size.set("two_col")``."""
        return _set(self._axis, choice)

    def options(self):
        """The names this axis accepts."""
        return _choices(self._axis)

    def current(self):
        """The choice in force on this axis, or None before anything has been applied."""
        applied = _STATE['applied']
        return None if applied is None else applied[self._axis]

    def __repr__(self):
        return '<hamhelper.install.{}: {} (options: {})>'.format(self._axis, self.current(),
                                                                   ', '.join(self.options()))


class _Style(_Axis):
    _axis = 'style'

    def hamstyle(self):
        """Light substrate, black ink, minimal frame; the look developed for physics papers and posters."""
        return _set('style', 'hamstyle')

    def alightroom(self):
        """hamstyle with every colour taken out: black ink on white, a ladder of greys for the series, and a
        different line style on each (defaults for palette, cmap and redundancy; your own choices still win)."""
        return _set('style', 'alightroom')

    def adarkroom(self):
        """The same, turned over: white ink on an off-black ground (#272727), exported dark too."""
        return _set('style', 'adarkroom')


class _Size(_Axis):
    _axis = 'size'

    def one_col(self):
        """3.37 x 2.40 in, one column of a two-column page. Type 9 / 10 pt."""
        return _set('size', 'one_col')

    def one_col_tall(self):
        """3.37 x 3.70 in: one column wide, taller for stacked panels. Type 9 / 10 pt."""
        return _set('size', 'one_col_tall')

    def two_col(self):
        """6.90 x 3.20 in, both columns of a two-column page. Type 10 / 11 pt."""
        return _set('size', 'two_col')

    def slide(self):
        """10.0 x 5.63 in, the body of a 16:9 slide (posters too). Type 20 / 22 pt."""
        return _set('size', 'slide')


class _Variant(_Axis):
    _axis = 'variant'

    def journal(self):
        """Four-sided box, ticks inward, minor ticks on every side."""
        return _set('variant', 'journal')

    def comms(self):
        """Left and bottom spines only, ticks outward: minimal ink for slides and posters."""
        return _set('variant', 'comms')


class _Font(_Axis):
    _axis = 'font'

    def serif(self):
        """Times-class serif with STIX maths."""
        return _set('font', 'serif')

    def sans(self):
        """Helvetica-class sans with STIX sans maths; text sizes scaled by 0.92 to match the serif's visual size."""
        return _set('font', 'sans')


class _Palette(_Axis):
    _axis = 'palette'

    def default(self):
        """Eight-colour cycle built from Tol's Sunset (indigo, red, teal, orange, cyan, then overflow)."""
        return _set('palette', 'default')

    def tol(self):
        """Eight-colour cycle from Tol's Vibrant (blue, red, cyan, orange, teal) plus three of his Muted."""
        return _set('palette', 'tol')

    def alight(self):
        """Eight greys for the white page of alightroom: ink to the dimmest that keeps 3.2:1 against white."""
        return _set('palette', 'alight')

    def adark(self):
        """Eight greys for the dark ground of adarkroom: white down to the dimmest that keeps 3.2:1 on #272727."""
        return _set('palette', 'adark')

    def get(self):
        """The Palette in force (the default one before anything has been applied): its cycle, names, pale bands
        and fit-component colours. Read colours from here and one script renders in any palette."""
        applied = _STATE['applied']
        return _colours.palette(_DEFAULTS['palette'] if applied is None else applied['palette'])


class _Cmap(_Axis):
    _axis = 'cmap'

    def sunset_warm(self):
        """The warm 45% of Tol's Sunset, cream to dark red: sequential, and a slice of the diverging map."""
        return _set('cmap', 'ham_sunset_warm')

    def sunset_warm_w(self):
        """Same ramp with its floor pulled to white, so empty space stays page-white."""
        return _set('cmap', 'ham_sunset_warm_w')

    def grey(self):
        """White to black in equal steps of lightness: the map of alightroom."""
        return _set('cmap', 'ham_grey')

    def grey_dark(self):
        """The dark ground (#272727) to white in equal steps of lightness: the map of adarkroom."""
        return _set('cmap', 'ham_grey_dark')

    def iridescent(self):
        """Tol's Iridescent."""
        return _set('cmap', 'ptol_iridescent')

    def viridis(self):
        """matplotlib's own default."""
        return _set('cmap', 'viridis')


class _Redundancy(_Axis):
    _axis = 'redundancy'

    def off(self):
        """Colour alone tells the series apart."""
        return _set('redundancy', 'off')

    def dash(self):
        """Each colour slot also gets its own line style."""
        return _set('redundancy', 'dash')

    def marker(self):
        """Each colour slot also gets its own marker (spaced along the line, not at every point).

        Matplotlib hands the whole cycle to every artist that takes a cycle colour, and a filled polygon has no
        `markevery`: with a marker cycle in force ``ax.fill(...)`` and ``ax.hist(..., histtype="step")`` raise
        "Polygon.set() got an unexpected keyword argument 'markevery'". Lines, bars, errorbars, scatter,
        fill_between and ax.stairs are fine; use dash() if you need the step histograms."""
        return _set('redundancy', 'marker')

    def both(self):
        """Colour, line style and marker: survives a greyscale photocopy. Same limit as marker(): no ax.fill or
        step histograms."""
        return _set('redundancy', 'both')


class _Grid(_Axis):
    _axis = 'grid'

    def off(self):
        """No grid."""
        return _set('grid', 'off')

    def on(self):
        """Faint dotted grid."""
        return _set('grid', 'on')


style = _Style()
size = _Size()
variant = _Variant()
font = _Font()
palette = _Palette()
cmap = _Cmap()
redundancy = _Redundancy()
grid = _Grid()


# %------------------- Whole-look functions -------------------%
def apply(style=None, size=None, variant=None, font=None, palette=None, cmap=None, redundancy=None, grid=None):
    """Set several axes at once; an axis left as None keeps its current choice.

    Same as calling each setter in turn, but rcParams are rebuilt once, and the returned handle undoes all of it
    together when used in a ``with`` block::

        with hi.apply(size="slide", variant="comms"):
            ...
    """
    given = {'style': style, 'size': size, 'variant': variant, 'font': font, 'palette': palette, 'cmap': cmap,
             'redundancy': redundancy, 'grid': grid}
    explicit = dict(_STATE['explicit'])
    labels = []
    for axis in _AXES:
        if given[axis] is not None:
            _check(axis, given[axis])
            explicit[axis] = given[axis]
            labels.append('{}={}'.format(axis, given[axis]))
    return _commit(explicit, ', '.join(labels) or 'no change', {a for a in _AXES if given[a] is not None})


def reset(*axes):
    """Undo hamhelper.install.

    With no arguments, matplotlib's settings go back to what they were before the first setter call (hand edits made
    since are lost too) and every choice is forgotten. With axis names, ``hi.reset("size", "font")``, only those
    choices are forgotten and the axes fall back to the style's default or the global one; the rest stays as chosen.
    """
    if not axes:
        baseline = _STATE['baseline']
        if baseline is not None:
            _restore_rc(baseline)
        _STATE['explicit'] = {}
        _STATE['applied'] = None
        _STATE['baseline'] = None
        return None
    for axis in axes:
        _check_axis(axis)
    if _STATE['applied'] is None:
        return None
    explicit = {k: v for k, v in _STATE['explicit'].items() if k not in axes}
    return _commit(explicit, 'reset ' + ', '.join(axes), set(axes))


def current():
    """The choice on every axis as currently in force; an empty dict before anything has been applied."""
    applied = _STATE['applied']
    return {} if applied is None else dict(applied)


def options():
    """Every axis and the names it accepts."""
    return {axis: _choices(axis) for axis in _AXES}
