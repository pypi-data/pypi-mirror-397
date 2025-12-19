from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted
import numpy as np
from .exceptions import InvalidModelError, NotFittedError, InvalidArrayError

def validate_sklearn_regressor(model):
    if not isinstance(model, BaseEstimator):
        raise InvalidModelError("Model must be a scikit-learn estimator.")
    if not isinstance(model, RegressorMixin):
        raise InvalidModelError("Model must be a scikit-learn regressor.")
    try:
        check_is_fitted(model)
    except Exception:
        raise NotFittedError("Model must be fitted before diagnostics.")

def validate_array(arr, name="array"):
    if not isinstance(arr, np.ndarray):
        raise InvalidArrayError(f"{name} must be a NumPy array.")
