import platform
import ctypes
import os
from enum import Enum
import numpy as np
import struct
import sys
import uuid
import hashlib
from .libpath import LIBPATH


lib = ctypes.CDLL(LIBPATH)

GTECBLE_HANDLE = ctypes.c_uint64
GTECBLE_STRING_LENGTH_MAX = 255
GTECBLE_DEVICENAME_LENGTH_MAX = 15
GTECBLE_NUMBER_OF_CHANNELS_MAX = 64


class GTECBLE_DEVICE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("modelNumber", ctypes.c_char * GTECBLE_STRING_LENGTH_MAX),
        ("serialNumber", ctypes.c_char * GTECBLE_STRING_LENGTH_MAX),
        ("firmwareRevision", ctypes.c_char * GTECBLE_STRING_LENGTH_MAX),
        ("hardwareRevision", ctypes.c_char * GTECBLE_STRING_LENGTH_MAX),
        ("manufacturerName", ctypes.c_char * GTECBLE_STRING_LENGTH_MAX),
        ("channelTypes", ctypes.c_uint8 * GTECBLE_NUMBER_OF_CHANNELS_MAX),
        ("numberOfAcquiredChannels", ctypes.c_uint16),
        ("samplingRate", ctypes.c_uint16)
    ]


DeviceDiscoveredCallback = ctypes.CFUNCTYPE(None,
                                            ctypes.POINTER(ctypes.c_char * GTECBLE_DEVICENAME_LENGTH_MAX),  # noqa: E501
                                            ctypes.c_uint32)
DataAvailableCallback = ctypes.CFUNCTYPE(None,
                                         GTECBLE_HANDLE,
                                         ctypes.POINTER(ctypes.c_float),
                                         ctypes.c_uint32)

lib.GTECBLE_GetApiVersion.restype = ctypes.c_float
lib.GTECBLE_GetLastErrorText.restype = ctypes.c_char_p
lib.GTECBLE_StartScanning.restype = ctypes.c_uint32
lib.GTECBLE_StopScanning.restype = ctypes.c_uint32
lib.GTECBLE_RegisterDeviceDiscoveredCallback.argtypes = [DeviceDiscoveredCallback]  # noqa: E501
lib.GTECBLE_RegisterDeviceDiscoveredCallback.restype = ctypes.c_int
lib.GTECBLE_OpenDevice.argtypes = [ctypes.c_char_p, ctypes.POINTER(GTECBLE_HANDLE)]  # noqa: E501
lib.GTECBLE_OpenDevice.restype = ctypes.c_uint32
lib.GTECBLE_CloseDevice.argtypes = [ctypes.POINTER(GTECBLE_HANDLE)]
lib.GTECBLE_CloseDevice.restype = ctypes.c_uint32
lib.GTECBLE_RegisterDataAvailableCallback.argtypes = [GTECBLE_HANDLE, DataAvailableCallback]  # noqa: E501
lib.GTECBLE_RegisterDataAvailableCallback.restype = ctypes.c_int
lib.GTECBLE_GetDeviceInformation.argtypes = [GTECBLE_HANDLE, ctypes.POINTER(GTECBLE_DEVICE_INFORMATION)]  # noqa: E501
lib.GTECBLE_GetDeviceInformation.restype = ctypes.c_uint32


class GtecBLEWrapper():

    _key = None
    _dd_callback = None
    _dd_callback_internal = None

    _data_callback: callable
    _data_callback_internal: callable

    @staticmethod
    def __handle_error__(errorCode):
        from ..amplifier import Amplifier
        if errorCode != Amplifier.Error.NONE.value:
            error_text = lib.GTECBLE_GetLastErrorText()
            error_text_str = error_text.decode('utf-8')
            raise ValueError(error_text_str)

    @staticmethod
    def _check_key():
        mac = uuid.getnode()
        mac_str = f"{mac:012x}"
        key_ref = hashlib.sha256(mac_str.encode()).hexdigest()
        if GtecBLEWrapper._key != key_ref:
            raise KeyError("Invalid usage.")

    @staticmethod
    def get_api_version():
        return np.frombuffer(struct.pack('f', lib.GTECBLE_GetApiVersion()),
                             dtype=np.float32)[0]

    @staticmethod
    def register(key: str):
        GtecBLEWrapper._key = key
        GtecBLEWrapper._check_key()

    @staticmethod
    def start_scanning():
        GtecBLEWrapper._check_key()
        if GtecBLEWrapper._dd_callback is None:
            raise ValueError("No device discovered callback set.")
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_RegisterDeviceDiscoveredCallback(GtecBLEWrapper._dd_callback_internal))  # noqa: E501
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_StartScanning())

    @staticmethod
    def stop_scanning():
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_StopScanning())
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_RegisterDeviceDiscoveredCallback(ctypes.cast(None, DeviceDiscoveredCallback)))  # noqa: E501

    @staticmethod
    def _dd_callback_wrapper(devices, num_dev):
        device_list = [devices[i].value.decode("utf-8")
                       for i in range(num_dev)]
        if GtecBLEWrapper._dd_callback is not None:
            GtecBLEWrapper._dd_callback(device_list)

    @staticmethod
    def set_device_discovered_callback(callback):
        GtecBLEWrapper._dd_callback = callback
        if GtecBLEWrapper._dd_callback_internal is None:
            GtecBLEWrapper._dd_callback_internal = DeviceDiscoveredCallback(GtecBLEWrapper._dd_callback_wrapper)  # noqa: E501

    def _data_callback_wrapper(self, hDevice, sample, sample_size):
        sample_array = np.fromiter(sample, dtype=np.float32, count=sample_size)
        if self._data_callback is not None:
            self._data_callback(data=sample_array)

    def set_data_callback(self, callback):
        self._data_callback = callback

    def __init__(self, serial):
        GtecBLEWrapper._check_key()
        self._data_callback = None
        self.__hDevice = GTECBLE_HANDLE()
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_OpenDevice(serial.encode('utf-8'), ctypes.byref(self.__hDevice)))  # noqa: E501
        self.__device_info = GTECBLE_DEVICE_INFORMATION()
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_GetDeviceInformation(self.__hDevice, ctypes.byref(self.__device_info)))  # noqa: E501
        self._data_callback_internal = DataAvailableCallback(self._data_callback_wrapper)  # noqa: E501

    def start(self):
        if self._data_callback is None:
            raise ValueError("No data callback set.")
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_RegisterDataAvailableCallback(self.__hDevice, self._data_callback_internal))  # noqa: E501

    def stop(self):
        GtecBLEWrapper.__handle_error__(lib.GTECBLE_RegisterDataAvailableCallback(self.__hDevice, ctypes.cast(None, DataAvailableCallback)))  # noqa: E501

    def __del__(self):
        try:
            lib.GTECBLE_CloseDevice(ctypes.byref(self.__hDevice))
        except Exception:
            pass  # do nothing; destructor must not fail

    @property
    def model_number(self):
        return self.__device_info.modelNumber.decode('utf-8')

    @property
    def serial_number(self):
        return self.__device_info.serialNumber.decode('utf-8')

    @property
    def firmware_version(self):
        return self.__device_info.firmwareRevision.decode('utf-8')

    @property
    def hardware_version(self):
        return self.__device_info.hardwareRevision.decode('utf-8')

    @property
    def manufacturer_name(self):
        return self.__device_info.manufacturerName.decode('utf-8')

    @property
    def channel_types(self):
        return [num for num in self.__device_info.channelTypes if num != 0]

    @property
    def no_of_acquired_channels(self):
        return self.__device_info.numberOfAcquiredChannels

    @property
    def sampling_rate(self):
        return self.__device_info.samplingRate

    @property
    def handle(self):
        return self.__hDevice.value
