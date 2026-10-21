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
