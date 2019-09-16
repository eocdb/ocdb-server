import functools
import warnings


def deprecated(func):
    """
    This is a decorator which can be used to mark classes, methods, and functions
    as deprecated. It will result in a warning of category ``DeprecationWarning`` being emitted
    when the decorated class, method, or function is used.
    """

    @functools.wraps(func)
    def decorator_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated element {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return decorator_func
