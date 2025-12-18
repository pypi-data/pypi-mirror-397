"""
Multi-Expert Chain for Audio Tasks (MECAT)
"""

import sys
try:
    from importlib.metadata import version
    __version__ = version("mecat")
except Exception:
    __version__ = "0.0.0+dev"

# Use lazy imports to avoid early import conflicts
def __getattr__(name):
    module_dict = sys.modules[__name__].__dict__
    """Lazy import mechanism to avoid early imports"""
    if name == "evaluate":
        from .evaluate import evaluate
        module_dict[name] = evaluate
        return evaluate
    elif name == "load_data_with_config":
        from .evaluate import load_data_with_config
        module_dict[name] = load_data_with_config
        return load_data_with_config
    elif name == "load_prediction_file":
        from .evaluate import load_prediction_file
        module_dict[name] = load_prediction_file
        return load_prediction_file
    elif name == "results_to_dataframe":
        from .evaluate import results_to_dataframe
        module_dict[name] = results_to_dataframe
        return results_to_dataframe
    elif name == "BaseScorer":
        from .scorer import BaseScorer
        module_dict[name] = BaseScorer
        return BaseScorer
    elif name == "DATE":
        from .DATE import DATE
        module_dict[name] = DATE
        return DATE
    elif name == "DATEEvaluator":
        from .DATE import DATEEvaluator
        module_dict[name] = DATEEvaluator
        return DATEEvaluator
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "evaluate",
    "load_data_with_config",
    "load_prediction_file",
    "results_to_dataframe",
    "BaseScorer",
    "DATE",
    "DATEEvaluator",
]
