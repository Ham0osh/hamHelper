"""Unit testing for errors module."""
import hamhelper.errors as he
import numpy as np
import pytest


def test_assert_error_passes_on_true():
    assert he.assert_error(True, ValueError('unused')) is None
    assert he.assert_error(np.bool_(True), ValueError('unused')) is None


def test_assert_error_raises_the_given_error_on_false():
    with pytest.raises(KeyError, match='mine'):
        he.assert_error(False, KeyError('mine'))
    with pytest.raises(ValueError):
        he.assert_error(np.bool_(False), ValueError('numpy bools count as bools'))


@pytest.mark.parametrize('not_a_bool', [1, 0, 'yes', None, [True]])
def test_assert_error_requires_a_bool(not_a_bool):
    with pytest.raises(RuntimeError):
        he.assert_error(not_a_bool, ValueError('never reached'))
