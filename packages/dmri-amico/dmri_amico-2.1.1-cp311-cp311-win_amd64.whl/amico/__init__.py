"""""" # start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'dmri_amico.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from amico.core import Evaluation, setup
from amico.util import set_verbose, get_verbose
# from amico import core
# from amico import scheme
# from amico import lut
# from amico import models
# from amico import util

__all__ = ['Evaluation', 'setup', 'set_verbose', 'get_verbose']

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
__version__ = version('dmri-amico')
