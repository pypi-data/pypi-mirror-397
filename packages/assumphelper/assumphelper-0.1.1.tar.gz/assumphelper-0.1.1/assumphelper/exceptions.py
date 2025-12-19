class InvalidModelError(TypeError):
    """Raised when the model is not a scikit-learn estimator."""
    pass

class NotFittedError(RuntimeError):
    """Raised when the model has not been fitted yet."""
    pass

class InvalidArrayError(TypeError):
    """Raised when an input is not a valid NumPy array."""
    pass
