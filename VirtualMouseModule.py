import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

wCam, hCam = 1280, 720

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

wScr, hScr = autopy.screen.size()


class VirtualMouse:  # This module doesn't work for some reason
    def __init__(self, detector, smoothening=7, frameR=150):
        self.detector = detector
        self.plocX, self.plocY = 0, 0
        self.smoothening = 7
        self.frameR = frameR
        self.clickToggle = True  # Keeps the program from clicking extremely fast

    def click_mode(self, img, draw=True):
        length, img, lineInfo = self.detector.findDistance(4, 8, img)

        if length <= 50 and self.clickToggle:
            if draw:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)

            self.clickToggle = False
            autopy.mouse.click()
        elif length > 50:
            self.clickToggle = True

    def movement_mode(self, img, lmList, draw=True):
        x1, y1 = lmList[8][1:]

        # User UI
        if draw:
            cv2.rectangle(img, (self.frameR, self.frameR), (wCam - self.frameR, hCam - self.frameR - 100), (255, 0, 255), 2)
            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)

        # Convert the coordinates to screen size
        x3 = np.interp(x1, (self.frameR, wCam - self.frameR), (0, wScr))
        y3 = np.interp(y1, (self.frameR, hCam - self.frameR - 100), (0, hScr))

        # Smoothen the movements
        clocX = self.plocX + (x3 - self.plocX) / self.smoothening
        clocY = self.plocY + (y3 - self.plocY) / self.smoothening
        # if cLocX > wScr or cLocX < 0:

        # Move the mouse
        autopy.mouse.move(wScr - clocX, clocY)

        self.plocX = clocX
        self.plocY = clocY


def main():
    pTime = 0
    detector = htm.handDetector(maxHands=1, detectorCon=0.75)
    mouse = VirtualMouse(detector)

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if len(lmList) != 0:
            fingers = detector.fingersUp()

            if fingers[1] == 1 and fingers[2] == 1:  # Clicking mode
                mouse.click_mode(img)
            elif fingers[1] == 1 and fingers[2] == 0:  # Moving mode
                mouse.movement_mode(img, lmList)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Virtual Mouse", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
