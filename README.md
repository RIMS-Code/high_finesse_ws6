# High Finesse WS6

Control class
to query and set the HighFinesse WS6 wavemeter.
Heavily influenced by
https://github.com/stepansnigirev/py-ws7
and therefore,
this class should also be able to communicate 
with the WS7.
Only tested with the WS6.

## Preparation

Make sure you have the wavelength software installed and running.
You should also ensure that you know where the `wlmData.dll` file lives.
For a standard installation it should be in
`"C:\Windows\System32\wlmData.dll"`.

## Usage

For detailed usage,
see the docstring in the `high_finesse.py` file.
Generally,
the usage of the wavemeter class should
be similar to usage of any instrument 
that is used in 
[InstrumentKit](https://github.com/Galvant/InstrumentKit).
A simple example with comments is given below:

```python
from high_finesse import WavelengthMeter
path_to_dll = "C:\Windows\System32\wlmData.dll"

# initialize the wavelength meter
wlm = WavlengthMeter(dllpath="C:\Windows\System32\wlmData.dll")  # this is also the default
print(wlm.wavelengths)  # reads all wavelengths in a list
```

If you want to interact with channels in switcher mode,
e.g., to turn the third channel on,
set it to auto_exposure,
and read its frequency,
continue as following:

```python
ch3 = wlm.channel[2]  # count pythonic!
ch3.use_channel = True
ch3.auto_exposure = True
print(ch3.frequency)
```

## Powered by

All original code is licensed under 
[MIT](LICENSE).
Specific code fragments and routines
were taken and adopted from the following 
packages:

Code        |       Package         |   License     |   URL 
------------|-----------------------|---------------|---------
ProxyList   | InstrumentKit         | AGPL-v3       | https://github.com/Galvant/InstrumentKit
wlmConst    | High Finesse          | Unknown       | http://www.highfinesse.com/
wlmData     | High Finesse          | Unknown       | http://www.highfinesse.com/

Furthermore,
part of this class was inspired by
https://github.com/stepansnigirev/py-ws7.