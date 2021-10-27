"""Class to communicate with the HighFinesse WS6 (WS7).

This class is heavily influenced / copied from:
https://github.com/stepansnigirev/py-ws7
"""


import ctypes
from typing import List

from utils import ProxyList


class WavelengthMeter:
    def __init__(self, dllpath: str = "C:\Windows\System32\wlmData.dll"):
        """Initialize the Wavelength meter.

        :param dllpath: Path to the DLL.
        """
        self.dll = ctypes.WinDLL(dllpath)

        # set up variable types
        self.dll.GetExposureModeNum.restype = ctypes.c_long
        self.dll.GetWavelengthNum.restype = ctypes.c_double
        self.dll.GetFrequencyNum.restype = ctypes.c_double
        self.dll.GetSwitcherMode.restype = ctypes.c_long

    class Channel:
        """Wavelengthmeter channel class."""

        def __init__(self, parent, idx: int):
            """Initialize the channel.

            :param parent: Parent class that is calling this one.
            :param idx: Channel number of wavelength meter, pythonic starting at 0.
            """
            self._parent = parent
            self._idx = idx + 1

            self._dll = self._parent.dll

        @property
        def auto_exposure(self) -> bool:
            """Get / set auto exposure mode of channel.

            :return: Status if auto exposure mode is activated.
            """
            return bool(
                self._dll.GetExposureModeNum(
                    ctypes.c_long(self._idx), ctypes.c_bool(True)
                )
            )

        @auto_exposure.setter
        def auto_exposure(self, value: bool):
            self._dll.SetExposureModeNum(ctypes.c_long(self._idx), ctypes.c_bool(value))

        @property
        def exposure(self) -> List[int]:
            """Get / set exposure time.

            Depending on the wavemeter, one or two CCD arrays will be available. If no
            second CCD array is present, the return will likely contain a negative
            number (see wavelength meter documentation for details).

            If only one value is given to set, only CCD array 1 will be set.

            :return: Exposure values in ms for the CCD arrays.

            :raise ValueError: Exposure not set with one or two values.
            """
            exp_arr1 = int(
                self._dll.GetExposureNum(
                    ctypes.c_long(self._idx), ctypes.c_long(1), ctypes.c_long(0)
                )
            )

            exp_arr2 = int(
                self._dll.GetExposureNum(
                    ctypes.c_long(self._idx), ctypes.c_long(2), ctypes.c_long(0)
                )
            )

            return [exp_arr1, exp_arr2]

        @exposure.setter
        def exposure(self, value: List[int]):
            if not isinstance(value, list):
                value = [value]

            if not 1 <= len(value) <= 2:
                raise ValueError(
                    "You must set one or two values (as list) for "
                    "the CCD array exposure times."
                )

            self._dll.SetExposureNum(
                ctypes.c_long(self._idx), ctypes.c_long(1), ctypes.c_long(value[0])
            )
            if len(value) == 2:
                self._dll.SetExposureNum(
                    ctypes.c_long(self._idx), ctypes.c_long(2), ctypes.c_long(value[1])
                )

        @property
        def frequency(self) -> float:
            """Get frequency of channel in THz.

            :return: Frequency in THz
            """
            return self._dll.GetFrequencyNum(
                ctypes.c_long(self._idx), ctypes.c_double(0)
            )

        @property
        def wavelength(self) -> float:
            """Get wavelength of given channel in nm.

            :return: Wavelength in nm
            """
            return self._dll.GetWavelengthNum(
                ctypes.c_long(self._idx), ctypes.c_double(0)
            )

    @property
    def channel(self):
        """Return a channel object."""
        return ProxyList(self, self.Channel, range(8))

    @property
    def frequencies(self) -> List[float]:
        """Get frequencies of all 8 channels."""
        return [self.channel[it].frequency for it in range(8)]

    @property
    def switcher_mode(self) -> bool:
        """Get / set switcher mode.

        :return: Status if switcher mode is turned on.
        """
        return bool(self.dll.GetSwitcherMode(ctypes.c_long(0)))

    @switcher_mode.setter
    def switcher_mode(self, value: bool):
        self.dll.SetSwitcherMode(ctypes.c_long(int(value)))

    @property
    def wavelengths(self) -> List[float]:
        """Get wavelengths of all 8 channels."""
        return [self.channel[it].wavelength for it in range(8)]
