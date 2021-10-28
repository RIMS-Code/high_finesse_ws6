"""Class to communicate with the HighFinesse WS6 (WS7).

This class is heavily influenced / copied from:
https://github.com/stepansnigirev/py-ws7
"""

from enum import Enum
import ctypes
from typing import List
import warnings

from headers import load_wlm_data_dll
from headers import wlmConst
from utils import ProxyList


class WavelengthMeter:
    """Communicate with a HighFinesse wavelenght meter.

    Note: This only works on Windows. The wavelength meter software must have been
    started by the user.

    Example:
        >>> wlm = WavelengthMeter()
        >>> ch = wlm.channel[5]  # choose the sixth channel
        >>> a = ch.wavelength  # stores wavelength of channel in variable a
        >>> b = wlm.wavelengths  # stores all wavelengths as list in variable b
    """

    def __init__(self, dllpath: str = "C:\Windows\System32\wlmData.dll"):
        """Initialize the Wavelength meter.

        :param dllpath: Path to the DLL.
        """
        self._dll = load_wlm_data_dll(dllpath)

        if self._dll.GetWLMCount(0) == 0:
            raise IOError("There is no running wavelength meter server instance.")

    class OperationState(Enum):
        """Enum class with the available operation states."""

        adjustment = wlmConst.cAdjustment
        measurement = wlmConst.cMeasurement
        stop = wlmConst.cStop

    class Channel:
        """Wavelengthmeter channel class."""

        def __init__(self, parent, idx: int):
            """Initialize the channel.

            :param parent: Parent class that is calling this one.
            :param idx: Channel number of wavelength meter, pythonic starting at 0.

            :raise TypeError: Not initialized from wavelength meter channel.
            """
            if not isinstance(parent, WavelengthMeter):
                raise TypeError("Must initialize channel from `WavelengthMeter` class.")

            self._parent = parent
            self._idx = idx + 1

            self._dll = self._parent._dll

        @property
        def auto_exposure(self) -> bool:
            """Get / set auto exposure mode of channel.

            :return: Status if auto exposure mode is activated.

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.auto_exposure = False
                >>> ch.auto_exposure
                False
            """
            return bool(self._dll.GetExposureModeNum(self._idx, True))

        @auto_exposure.setter
        def auto_exposure(self, value: bool):
            self._dll.SetExposureModeNum(self._idx, value)

        @property
        def exposure(self) -> List[int]:
            """Get / set exposure time.

            Depending on the wavemeter, one or two CCD arrays will be available. If no
            second CCD array is present, the return will likely contain a negative
            number (see wavelength meter documentation for details).

            If only one value is given to set, only CCD array 1 will be set.

            :return: Exposure values in ms for the CCD arrays.

            :raise ValueError: Exposure not set with one or two values.

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.exposure = [100, 100]  # set both CCD arrays to 100ms exposure
                >>> ch.exposure
                [100, 100]
            """
            exp_arr1 = int(self._dll.GetExposureNum(self._idx, 1, 0))
            exp_arr2 = int(self._dll.GetExposureNum(self._idx, 2, 0))
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

            self._dll.SetExposureNum(self._idx, 1, value[0])
            if len(value) == 2:
                self._dll.SetExposureNum(self._idx, 2, value[1])

        @property
        def frequency(self) -> float:
            """Get frequency of channel in THz.

            :return: Frequency in THz

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.frequency
                337.212
            """
            return self._dll.GetFrequencyNum(self._idx, 0)

        @property
        def show_channel(self) -> bool:
            """Turn channel displaying on or off.

            Only works when the wavelength meter is in switcher mode, otherwise it warns
            the user that it cannot do anything.
            Displaying of the curve remaines untouched.
            Note, if the channel is unused, it will automatically enable usage.

            :return: Status if the specific channel is turned on.

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.show_channel = True
                >>> ch.show_channel
                True
            """
            use_flag = ctypes.c_long(0)
            show_flag = ctypes.c_long(0)
            self._dll.GetSwitcherSignalStates(
                self._idx, ctypes.byref(use_flag), ctypes.byref(show_flag)
            )
            return bool(show_flag)

        @show_channel.setter
        def show_channel(self, value: bool):
            if self._parent.switcher_mode:
                self._dll.SetSwitcherSignalStates(self._idx, 1, int(value))
            else:
                warnings.warn(
                    "Switcher mode not active, therefore cannot use this" "function."
                )

        @property
        def use_channel(self) -> bool:
            """Turn channel usage on or off.

            Only works when the wavelength meter is in switcher mode, otherwise it warns
            the user that it cannot do anything.
            Displaying of the curve remaines untouched.

            :return: Status if the specific channel is turned on.

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.use_channel = True
                >>> ch.use_channel
                True
            """
            use_flag = ctypes.c_long(0)
            show_flag = ctypes.c_long(0)
            self._dll.GetSwitcherSignalStates(
                self._idx, ctypes.byref(use_flag), ctypes.byref(show_flag)
            )
            return bool(use_flag)

        @use_channel.setter
        def use_channel(self, value: bool):
            if self._parent.switcher_mode:
                self._dll.SetSwitcherSignalStates(
                    self._idx, int(value), int(self.show_channel)
                )
            else:
                warnings.warn(
                    "Switcher mode not active, therefore cannot use this" "function."
                )

        @property
        def wavelength(self) -> float:
            """Get wavelength of given channel in nm.

            :return: Wavelength in nm

            Example:
                >>> wlm = WavelengthMeter()
                >>> ch = wlm.channel[2]  # third channel
                >>> ch.wavelength
                837.212
            """
            return self._dll.GetWavelengthNum(self._idx, 0)

    @property
    def channel(self):
        """Return a channel object.

        Note: The first channel is number 0 (think pythonic!).

        Example:
            >>> wlm = WavelengthMeter()
            >>> ch = wlm.channel[2]  # third channel
        """
        return ProxyList(self, self.Channel, range(8))

    @property
    def frequencies(self) -> List[float]:
        """Get frequencies of all 8 channels.

        Example:
            >>> wlm = WavelengthMeter()
            >>> wlm.frequencies
            [223.232, 337.121, 339.888, 321.231, 339.981, 398.121, 420.121, 333.212]
        """
        return [self.channel[it].frequency for it in range(8)]

    @property
    def operation(self) -> OperationState:
        """Get / Set operation state.

        See the `OperationState` enum class for options.

        :return: Operation state of the wavelength meter.

        :raise TypeError: Set variable is not an `OperationState` enum.

        Example:
            >>> wlm = WavelengthMeter()
            >>> wlm.operation = wlm.OperationState.measurement
            >>> print(wlm.operation)
            OperationState.measurement
        """
        return self.OperationState(self._dll.GetOperationState(0))

    @operation.setter
    def operation(self, value: OperationState):
        if not isinstance(value, self.OperationState):
            raise TypeError("Your chosen value is not of type `OperationState`.")
        self._dll.Operation(value.value)

    @property
    def switcher_mode(self) -> bool:
        """Get / set switcher mode.

        :return: Status if switcher mode is turned on.

        Example:
            >>> wlm = WavelengthMeter()
            >>> wlm.switcher_mode = True
            >>> wlm.switcher_mode
            True
        """
        return bool(self._dll.GetSwitcherMode(0))

    @switcher_mode.setter
    def switcher_mode(self, value: bool):
        self._dll.SetSwitcherMode(int(value))

    @property
    def wavelengths(self) -> List[float]:
        """Get wavelengths of all 8 channels.

        Example:
            >>> wlm = WavelengthMeter()
            >>> wlm.wavelengths
            [823.232, 822.121, 888.888, 888.231, 898.981, 888.121, 764.121, 921.212]
        """
        return [self.channel[it].wavelength for it in range(8)]
