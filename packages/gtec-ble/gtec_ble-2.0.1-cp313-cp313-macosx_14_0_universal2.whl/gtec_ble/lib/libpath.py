from enum import Enum

import platform
import sys
from pathlib import Path
import os

try:
    from importlib.resources import files  # Python 3.9+
except ImportError:
    from importlib_resources import files  # backport for Py <3.9


class System(Enum):
    Unknown = 1
    Windows = 2
    Linux = 3
    Mac = 4
    iOs = 5
    Android = 6


def get_system():
    systmp = System.Unknown
    system = platform.system()
    if system == 'Darwin':
        systmp = System.Mac
    elif system == 'Linux':
        systmp = System.Linux
        if hasattr(sys, 'getandroidapilevel'):
            systmp = System.Android
    elif system == 'Windows':
        systmp = System.Windows
    return systmp


system = get_system()
if system == System.Windows:
    platform_folder = 'windows'
    current_architecture = platform.architecture()[0]
    if current_architecture == '32bit':
        architecture_folder = 'Win32'
        library_name = 'libgtecble.dll'
    elif current_architecture == '64bit':
        architecture_folder = 'x64'
        library_name = 'libgtecble.dll'
    else:
        raise OSError('\'' + str(system) + '\' not supported')
elif system == System.Linux:
    raise OSError('\'' + str(system) + '\' not supported')
elif system == System.Mac:
    platform_folder = 'mac'
    architecture_folder = 'universal'
    library_name = 'libgtecble.dylib'
elif system == System.iOs:
    raise OSError('\'' + str(system) + '\' not supported')
elif system == System.Android:
    platform_folder = 'android'
    if platform.machine() == 'aarch64':
        architecture_folder = 'arm64-v8a'
        library_name = 'libgtecble.so'
    elif platform.machine() == 'armv7l':
        architecture_folder = 'armeabi-v7a'
        library_name = 'libgtecble.so'
    else:
        raise OSError('\'' + str(system) + '\' not supported')
else:
    raise OSError('\'' + str(system) + '\' not supported')


LIBPATH = str(
    files("gtec_ble").joinpath("lib", "native", platform_folder, architecture_folder, library_name)
)
