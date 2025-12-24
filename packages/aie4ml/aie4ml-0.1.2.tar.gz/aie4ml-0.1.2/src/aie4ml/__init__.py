try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = '0.0.0'
    version_tuple = (0, 0, 0)

__all__ = ['__version__', 'version_tuple']
