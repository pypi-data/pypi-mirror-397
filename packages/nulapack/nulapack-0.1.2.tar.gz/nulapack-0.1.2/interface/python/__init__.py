from importlib.metadata import PackageNotFoundError, version

from .gauss_seidel import gauss_seidel


try:
    __version__ = version("nulapack")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ["__version__", "gauss_seidel"]
