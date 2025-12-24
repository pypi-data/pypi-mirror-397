
import os
import sys

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

if (sys.version_info[0] < 3) or ((sys.version_info[0] == 3) and (sys.version_info[1] < 8)):
    os.environ["Path"] += os.pathsep + MODULE_DIR
else:
    os.add_dll_directory(MODULE_DIR)
    # Workaround for Conda Python 3.8 environments under Windows.PATHSEP_STRING
    # Although Python changed the DLL search mechanism in Python 3.8,
    # Windows Conda Python 3.8 environments still use the old mechanism...
    os.environ["Path"] += os.pathsep + MODULE_DIR


from .ids_peak_ipl import *
from .exceptions import *
