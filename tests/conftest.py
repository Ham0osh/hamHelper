"""Shared pytest configuration for the hamhelper tests."""
# ----------------------------------------------------------------------------------------------------------
# TODO(me): tests to write for the matplotlib compatibility fixes (branch compat/modern-matplotlib)
#
# colours.register_cmaps
#   - works on matplotlib >= 3.9 (mpl.cm.register_cmap is gone): every name in all_col, plus '<name>_r',
#     ends up in mpl.colormaps; the _r map has its ends swapped
#   - calling it twice is fine
# colours.get_continuous_cmap
#   - float_list passed as a numpy array (used to raise "ambiguous truth value")
#   - a one colour hex list gives a constant map (LinearSegmentedColormap needs points at 0 and 1)
# colours.HamColour
#   - repr() and == work (old code used self.__name__)
#   - iter(col) works (a Cycler is iterable, not an iterator)
#   - .test(N=...) draws (imshow was given map= instead of cmap=): try N = None, 1, 2, 3, 4, 9; N=0 raises ValueError
#   - from_hex_gradient with locations above 1 rescales them to [0, 1] (the walrus bound a bool, not the max)
#   - from_name('nonsense') prints a message and returns a one colour white map
#   - truncate(update=True / False), reversed / -col, += stacking
#   - example_map draws one collection of 13 paths, returns a Mercator and leaves the limits at (0, xmax), (0, ymax);
#     a missing shapefile raises FileNotFoundError; test(mapBool=True) draws (no Basemap needed any more)
# _geo (hamhelper/_geo.py: numpy-only shapefile reader and Mercator)
#   - read_shapefile on map_files/lpr_000b16a_e: 13 shapes in PRUID order; each record's header bbox equals the bbox
#     of its points; ring and point counts match the .shx index (27132 rings, 3390960 points in all); every ring is
#     closed; attributes (PRENAME, PRFNAME 'Québec' with its accent) come from the .dbf
#   - spherical areas of the provinces are within 1% of Statistics Canada's totals except Ontario and Quebec (Great
#     Lakes and James Bay water is clipped): a guard against reading the coordinates wrong
#   - bad input: a file that is not a shapefile (file code != 9994) and a point-type shapefile raise ValueError; a
#     missing .dbf is fine
#   - read_dbf: text, integer, float, logical and blank numeric fields (build a tiny .dbf in tmp_path with struct)
#   - Mercator: the lower-left corner maps to (0, 0); xmax = R * radians(longitude span); y equals
#     R * (asinh(tan(lat)) - asinh(tan(lat0))); inverse(m(lon, lat)) round-trips; poles and reversed corners raise
#     ValueError
#   - polygon_path: one MOVETO per ring and no CLOSEPOLY; a clockwise outer ring with an anticlockwise hole renders
#     the hole empty, the same orientation fills it (draw a PathPatch with Agg and read a pixel: Path.contains_point
#     does not follow the fill rule)
#   - do NOT ax.add_patch the big paths in a test: matplotlib >= 3.8 takes ~25 s for Nunavut alone
# colours._resolve_dir, savePath, makeAllTests
#   - relative paths land in the package folder, absolute paths are used as given, legacy '\\colour_demos' still works
#   - test(savePath=tmp_path) writes hamMap_<name>.png (it used to write one file with backslashes in its name on
#     Linux/macOS)
# styles/hamStyle.mplstyle
#   - loads with warnings as errors and no "Bad value" log lines (matplotlib drops bad keys silently)
#   - axes.prop_cycle is really applied (a quoted '#hex' in a style file is cut off as a comment)
#   - plt.style.use('hamhelper.styles.hamStyle') works
# plotting
#   - despine: defaults, trim (spine bounds = outer ticks), drop, noLine
#   - errorbands: fill spans y -/+ yerr, colour is applied, capsize adds an errorbar container
#
# TODO(me): tests to write for the new style system (branch dev-hamstyle: styles/*.mplstyle, install.py)
#
# import hygiene
#   - import hamhelper, hamhelper.plotting, hamhelper.colours, hamhelper.install leaves matplotlib.rcParams unchanged
#     (compare dict.items(mpl.rcParams) without the 'backend' key, before and after, in a fresh subprocess)
# style files
#   - every file in styles/ loads with mpl.rc_params_from_file(path, fail_on_error=True, use_default_template=False)
#     and logs nothing (caplog) and warns nothing (-W error)
#   - within each axis the layer files hold the SAME keys (size_*: 25, variant_*: 16, font_*: 2); that is what makes
#     switching safe, because a stale key from the previous choice can never be left behind
#   - hamStyle.mplstyle repeats size_one_col, variant_journal and font_serif exactly, and its cycle equals
#     colours.PALETTES['default'].cycler('off')
#   - plt.style.use('hamhelper.styles.hamStyle') gives the same rcParams as hi.style.hamstyle() from rcdefaults,
#     except image.cmap (hi sets it, the style file leaves it at matplotlib's default)
# install
#   - order independence: same final choices in any call order (with junk choices made first) -> identical rcParams
#   - with-block: restores rcParams and hi.current() on exit, on an exception, and when nested
#   - setters only rewrite the keys their own axis owns (hand edit lines.linewidth, call hi.font.sans(): survives;
#     call hi.size.slide(): replaced); hi.style.hamstyle() rewrites everything
#   - font.sans scales font.size, axes.titlesize, axes.labelsize, tick labels and legend.fontsize by 0.92 once
#     (sans twice == sans once; sans then serif == never sans), whichever of size / font was set last
#   - redundancy: off -> cycle has only 'color'; dash adds 'linestyle'; marker adds 'marker' and 'markevery'; both
#     adds all of them
#   - style-declared defaults (monkeypatch _CHOICES / _STYLE_FILES / _STYLE_DEFAULTS with a fake style): explicit
#     choices beat them in either call order; switching back to hamstyle drops them
#   - errors: unknown name / axis raises ValueError and leaves rcParams and hi.current() untouched; a file that fails
#     to load part-way leaves them untouched too
#   - hi.reset() restores rcParams exactly as before the first call; hi.reset('size') forgets one choice only
#   - a figure draws at every size (plt.subplots, legend, savefig to a buffer)
#   - cmap axis: first call sets image.cmap to ham_sunset_warm and registers it; hi.cmap.set('no_such_map') raises
#     ValueError and changes nothing; hi.cmap.set('magma') works; reset() restores image.cmap
#   - palette axis: hi.palette.get() is colours.palette(<name in force>); a palette added to colours.PALETTES shows
#     up in hi.palette.options() and can be set (remember to delete it again)
#
# TODO(me): tests to write for the colour work (branch dev-hamstyle: colours.py)
#
# palettes
#   - 'default' and 'tol': 8 colours, 8 names, 8 bands, 3 parts; every colour a valid #RRGGBB
#   - Palette.cycler: 'off' -> only 'color'; 'dash' adds 'linestyle'; 'marker' adds 'marker' + 'markevery'; 'both'
#     all four; None / False mean 'off'; anything else raises ValueError. palette('nope') raises KeyError
#   - worst-pair separation of the first five colours stays above 17 (hc.cvd_scores('default', n=5)): a guard
#     against someone nudging a colour and breaking colour-blind safety; parts beside slots 1-2 above 7.5
# derived maps
#   - nothing is registered on import; register_cmaps() registers every name and its '_r', twice in a row is fine,
#     and register_cmaps({'x': [hex, hex]}) still takes plain lists; the _r map is the reverse
#   - ham_sunset_warm is monotone in lightness; ham_sunset_warm_w starts at white; NaN / masked pixels are white
#   - ordered(5) returns ORDERED_NODES exactly, ordered(2) the two ends, ordered(1) the first
# CVD tools
#   - delta_e matches Sharma et al.'s published CIEDE2000 pairs (e.g. (50, 2.6772, -79.7751) vs
#     (50, 0, -82.7485) = 2.0425; (50, 2.5, 0) vs (73, 25, -18) = 27.1492); delta_e(x, x) = 0; symmetric
#   - lab_lightness: white 100, black 0; to_greyscale gives equal channels; simulate_cvd on a grey changes nothing
#     much; audit() returns a string naming all four vision types
# HamColour
#   - from_name('ham_sunset_warm') works; from_palette('tol') returns exactly the eight colours in order
#
# TODO(me): tests to write for the plotting helpers (branch dev-hamstyle: plotting.py, section "Figure helpers")
#
# colorbar
#   - same height as its panel after aspect='equal' or a squashed aspect (draw, compare window extents); thickness is
#     0.8 x the tick-label size in points at every figure size; gap is 0.8 x that plus the east-label room polar_frame
#     left on the axes (ax._ham_rim); outline takes axes.edgecolor; label set; width= and pad= are honoured
#   - ax=None uses the mappable's own axes, not plt.gca(); a list or a 2-D array of axes uses the first; cax= is used
#     as given and width / pad are ignored
# framed / disc
#   - framed: four spines visible, ticks inward on all sides, axisbelow False
#   - disc: images, collections, a list of them and a ContourSet are clipped; a legacy ContourSet (an object with a
#     .collections list that is not an Artist, as before matplotlib 3.8) is clipped piece by piece; left and bottom
#     spines are offset and bounded to (-r, r); aspect equal; no warning with a real ContourSet (-W error)
# polar_frame
#   - bad ticks preset, radial, direction, or an rlabels list of the wrong length raises ValueError
#   - labels='deg' / 'compass' / dict create the annotations; the lower-left quadrant is skipped for radial='leader'
#   - ax._ham_rim records room for the east and north/south labels, and colorbar clears it
#   - every helper runs under plain matplotlib defaults (string label sizes, no constrained layout), and under a dark
#     rcParams context the tag plate takes axes.facecolor and the colorbar outline and polar frame axes.edgecolor
# fit_height / square_figure
#   - the figure height settles (two calls give the same height); grow=False never makes it taller; the panel ends up
#     square to 0.003 in
# runs
#   - one LineCollection of n traces in the aggregate's colour at alpha 0.35, below the aggregate; the aggregate takes
#     the next cycle colour and the traces use NO cycle slots (with hi.redundancy.both(), an ordinary line plotted
#     after runs() is slot 2, not slot 8); mean vs median; a 1-D Y is one run; limits include every trace
# label helpers
#   - guide / panel_label / tag accept ls= or linestyle=, lw= or linewidth=, c= or color=, size= or fontsize=, weight=
#     or fontweight= (matplotlib rejects both spellings together); defaults applied otherwise; bad which / loc / axis
#     raise ValueError
#   - spec_tick adds a tick, keeps the automatic ones, adds no duplicate, works on an inverted axis
#   - units returns 'name [unit]' (or just name) and sets the label on the right axis
# save
#   - writes name__size__variant__suffix.ext with whichever parts are given, creates outdir; a png at 3.37 x 2.40 in
#     and dpi=600 is 2022 x 1440 px
# import hygiene
#   - importing hamhelper.plotting leaves matplotlib.rcParams unchanged
#
# Tips: run `python -m pytest -W error` so any deprecation warning fails the test.
#       "Bad value in file" from an rc/style file is a log message, not a warning: use the caplog fixture.
#       Test against the old code too (git stash the fix) to check a test really fails without it.
# ----------------------------------------------------------------------------------------------------------

import matplotlib

# Never open a GUI window or block on plt.show() while testing (the Windows CI runner has Tk available).
matplotlib.use('Agg')

import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _close_figures():
    """Close every figure after each test so they do not pile up."""
    yield
    plt.close('all')
