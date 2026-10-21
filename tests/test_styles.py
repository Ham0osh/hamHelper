"""Unit testing for the .mplstyle files shipped with hamhelper."""
import logging
import pathlib
import warnings

import hamhelper.colours as hc
import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

STYLE_DIR = pathlib.Path(hc.__file__).parent / 'styles'
STYLES = sorted(STYLE_DIR.glob('*.mplstyle'))


def test_styles_are_found():
    assert {p.name for p in STYLES} >= {'hamStyle.mplstyle', 'default.mplstyle'}


@pytest.mark.parametrize('style', STYLES, ids=lambda p: p.name)
def test_style_loads_cleanly(style, caplog, tmp_path):
    """A style must parse with no warnings and no 'Bad value' log lines (matplotlib drops bad keys quietly)."""
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with caplog.at_level(logging.WARNING):
            mpl.rc_params_from_file(style, use_default_template=False)
            with plt.style.context(str(style)):
                fig, ax = plt.subplots()
                ax.plot([0, 1], [0, 1], label='line')
                ax.legend()
                fig.savefig(tmp_path / 'smoke.png')
    assert not caplog.records, [r.getMessage() for r in caplog.records]


def test_hamstyle_cycle_is_applied():
    """The colour cycle used to be dropped: a quoted '#hex' inside a style file is cut off as a comment."""
    rc = mpl.rc_params_from_file(STYLE_DIR / 'hamStyle.mplstyle', use_default_template=False)
    colours = rc['axes.prop_cycle'].by_key()['color']
    assert [c.lower().lstrip('#') for c in colours] == [c.lower().lstrip('#') for c in hc.colsets['ptol_light'][:8]]


def test_style_is_available_by_package_name():
    """plt.style.use accepts '<package>.<subpackage>.<file>', which is how an installed copy is used."""
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with plt.style.context('hamhelper.styles.hamStyle'):
            assert mpl.rcParams['figure.dpi'] == 200
            assert not mpl.rcParams['axes.spines.top']
