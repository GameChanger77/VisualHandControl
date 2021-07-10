import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

maxLen=100
minLen=0
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

for length in range(0, 101, 25):

    # length = np.interp(length, [minLen, maxLen], [0, 100])

    db = math.log10(1 + length)

    vol = np.interp(db, [0, 2.0043213737826426], [minVol, maxVol])

    disVol = np.interp(db, [0, 2.0043213737826426], [0, 100])
    print(f'length{length}\tdb{db}\tvol{vol}\tdis{disVol}')
    volume.SetMasterVolumeLevel(vol, None)
