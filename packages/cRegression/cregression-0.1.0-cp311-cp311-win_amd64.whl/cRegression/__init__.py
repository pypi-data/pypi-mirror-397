try:
    from .cRegression import LinearRegression
except ImportError as e:
    raise ImportError(
        "The compiled module 'cRegression.cRegression' is missing. "
        "Make sure you have built the package correctly with scikit-build."
    ) from e
