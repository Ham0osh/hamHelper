"""Shared pytest configuration for the hamhelper tests."""
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
