import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute())
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

volume.SetMasterVolumeLevel(-5.0, None)

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectorCon=0.9)

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        if lmList[8][2] > lmList[4][2]:
            x1, y1 = lmList[0][1], lmList[0][2]
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
        else:
            # print(lmList[4], lmList[8])
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

            length = math.hypot(x2 - x1, y2 - y1)

            maxLen, minLen = 200, 50

            if length < minLen:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            elif length > maxLen:
                cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)

            # vol = np.interp(length, [minLen, maxLen], [minVol, maxVol])

            vol = np.interp(length, [minLen, maxLen], [minVol, maxVol])
            disVol = np.interp(vol, [minVol, maxVol], [0, 100])

            print(f'Volume: {vol}\tLength: {length}')
            volume.SetMasterVolumeLevel(vol, None)

            cv2.putText(img, f'{int(disVol)}', (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (30, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
