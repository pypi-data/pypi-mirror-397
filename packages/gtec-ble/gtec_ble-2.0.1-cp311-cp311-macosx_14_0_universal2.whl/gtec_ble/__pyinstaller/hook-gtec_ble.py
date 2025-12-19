from PyInstaller.utils.hooks import collect_data_files
import os
import platform
import sys
from enum import Enum

# Get the gtec_ble package directory
import gtec_ble
gtec_ble_path = os.path.dirname(gtec_ble.__file__)


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


# Determine platform-specific library path
binaries = []
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
        architecture_folder = None
        library_name = None
elif system == System.Mac:
    platform_folder = 'mac'
    architecture_folder = 'universal'
    library_name = 'libgtecble.dylib'
elif system == System.Android:
    platform_folder = 'android'
    if platform.machine() == 'aarch64':
        architecture_folder = 'arm64-v8a'
        library_name = 'libgtecble.so'
    elif platform.machine() == 'armv7l':
        architecture_folder = 'armeabi-v7a'
        library_name = 'libgtecble.so'
    else:
        architecture_folder = None
        library_name = None
else:
    platform_folder = None
    architecture_folder = None
    library_name = None

# Add the native library as a binary if path is valid
if platform_folder and architecture_folder and library_name:
    lib_path = os.path.join(gtec_ble_path,
                            'lib',
                            'native',
                            platform_folder,
                            architecture_folder,
                            library_name)
    if os.path.exists(lib_path):
        binaries = [(lib_path, '.')]
