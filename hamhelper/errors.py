"""Functions to help with error catching and handling."""

def assert_error(expression, error):
    """Assert function which raises a specified error when the expression evaluates False."""
    if not isinstance(expression, (np.bool_, bool)):
        raise RuntimeError('"expression" has to be of type bool')
    if not expression:
        raise error
    return