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
#   - example_map without Basemap installed prints and returns 0, no raise
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
#     install._PALETTES['default']
#   - plt.style.use('hamhelper.styles.hamStyle') gives the same rcParams as hi.style.hamstyle() from rcdefaults
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
