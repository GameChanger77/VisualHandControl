import cv2
import numpy as np
import HandTrackingModule as htm
import VirtualMouseModule as vmouse
import VolumeHandControlModule as vcontrol
import time
import autopy

##########################################
wCam, hCam = 1280, 720
frameR = 100
smoothening = 7
##########################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1, detectorCon=0.75, trackingCon=0.85)
mouse = vmouse.VirtualMouse(detector, frameR=frameR, smoothening=smoothening)
volControl = vcontrol.VolumeHandControl(detector)

wScr, hScr = autopy.screen.size()

pTime = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        fingers = detector.fingersUp()

        if fingers[1] == 1:  # First/pointer finger extended
            if fingers[2] == 1 and fingers[4] == 0:  # Clicking mode
                mouse.click_mode(img)
            elif fingers[2] == 0 and fingers[4] == 0:  # Moving mode
                mouse.movement_mode(img, lmList)
            elif fingers[0] == 1 and fingers[4] == 1:  # Volume mode
                volControl.getVolumeControl(img, lmList, minLen=25, maxLen=300)

            if fingers[3] == 1:  # Ring finger extended

                if fingers[0] == 1:  # Scroll Up
                    autopy.key.tap(autopy.key.Code.UP_ARROW)
                elif fingers[0] == 0:  # Scroll Down
                    autopy.key.tap(autopy.key.Code.DOWN_ARROW)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)
