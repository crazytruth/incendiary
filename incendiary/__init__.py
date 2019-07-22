import pkg_resources

__version__ = pkg_resources.get_distribution('incendiary').version
__author__ = 'Kwang Jin Kim'
__email__ = 'david@mymusictaste.com'

from incendiary.xray.app import Incendiary

__all__ = ['Incendiary', 'OpenTracing']
