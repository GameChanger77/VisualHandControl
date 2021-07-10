import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeHandControl():
    def __init__(self, detector=htm.handDetector(detectorCon=0.75)):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]

        self.detector = detector

    def getVolumeControl(self, img, lmList, draw=True, maxLen=200, minLen=50):
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)
        length = np.interp(length, [minLen, maxLen], [0, 100])

        db = math.log10(1 + length)

        vol = np.interp(db, [0, 2.0043213737826426], [self.minVol, self.maxVol])

        disVol = np.interp(vol, [self.minVol, self.maxVol], [0, 100])
        # print(f'length{length}\tdb{db}\tvol{vol}\tdis{disVol}')
        self.volume.SetMasterVolumeLevel(vol, None)

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

            if length < minLen:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            elif length > maxLen:
                cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
            else:
                cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)

            cv2.putText(img, f'{int(length)}', (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 75, 0), 3)

        return img


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1080)
    cap.set(4, 720)

    pTime = 0

    detector = htm.handDetector(detectorCon=0.75)
    handControl = VolumeHandControl(detector)

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img, draw=True)

        if len(lmList) != 0:
            img = handControl.getVolumeControl(img, lmList, minLen=25, maxLen=300)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
