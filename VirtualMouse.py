import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy


wCam, hCam = 640, 480
frameR = 100
smoothening = 7

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1, detectorCon=0.75)
wScr, hScr = autopy.screen.size()
print(f"Screen Width: {wScr}, Screen Height: {hScr}")

pTime = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)

    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        print(x1, y1, x2, y2)

        fingers = detector.fingersUp()

        if fingers[1] == 1 and fingers[2] == 1:  # Clicking mode
            length, img, lineInfo = detector.findDistance(8, 12, img)

            if length <= 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

        elif fingers[1] == 1 and fingers[2] == 0:  # Moving mode
            # User UI
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR - 100), (255, 0, 255), 2)
            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)

            # Convert the coordinates to screen size
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR - 100), (0, hScr))

            # Smoothen the movements
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            #if cLocX > wScr or cLocX < 0:


            # Move the mouse
            autopy.mouse.move(wScr - clocX, clocY)

    plocX = clocX
    plocY = clocY

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)

