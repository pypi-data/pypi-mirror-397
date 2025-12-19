from enum import Enum
from .lib.gtec_ble_wrapper import GtecBLEWrapper
import time

TIMEOUT = 6  # seconds


class Amplifier:

    class ChannelType(Enum):
        EXG = 1
        ACC = 2
        GYR = 3
        BAT = 4
        CNT = 5
        LINK = 6
        SATURATION = 7
        FLAG = 8
        VALID = 9
        OTHER = 10

    class Error(Enum):
        NONE = 0
        INVALID_HANDLE = 1
        BLUETOOTH_ADAPTER = 2
        BLUETOOTH_DEVICE = 3
        GENERAL = 4294967295

    _imp: GtecBLEWrapper
    _devices: list

    @staticmethod
    def get_api_version():
        return GtecBLEWrapper.get_api_version()

    @staticmethod
    def register(key: str):
        GtecBLEWrapper.register(key=key)

    @staticmethod
    def get_connected_devices():
        devices = []

        def on_devices_discovered(dev: list):
            nonlocal devices
            devices = dev

        GtecBLEWrapper.set_device_discovered_callback(on_devices_discovered)
        GtecBLEWrapper.start_scanning()
        t_start = time.time()
        while not devices and time.time() - t_start < TIMEOUT:
            time.sleep(0.2)
        GtecBLEWrapper.stop_scanning()
        return devices if devices else None

    def __init__(self, serial=None):
        cd = Amplifier.get_connected_devices()
        if cd is None:
            raise ValueError("No amplifiers connected.")
        if serial is None:
            serial = cd[0]
        if serial not in cd:
            raise ValueError(f"Device with serial number {serial} "
                             f"not connected.")
        self._imp = GtecBLEWrapper(serial)

    def set_data_callback(self, callback):
        self._imp.set_data_callback(callback)

    def start(self):
        self._imp.start()

    def stop(self):
        self._imp.stop()

    @property
    def model_number(self):
        return self._imp.model_number

    @property
    def serial_number(self):
        return self._imp.serial_number

    @property
    def firmware_version(self):
        return self._imp.firmware_version

    @property
    def hardware_version(self):
        return self._imp.hardware_version

    @property
    def manufacturer_name(self):
        return self._imp.manufacturer_name

    @property
    def channel_types(self):
        return self._imp.channel_types

    @property
    def no_of_acquired_channels(self):
        return self._imp.no_of_acquired_channels

    @property
    def sampling_rate(self):
        return self._imp.sampling_rate
