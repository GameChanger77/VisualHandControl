# VisualHandControl

This project is an attempt at creating a complete computer gesture control system based on computer vision.
It uses openCV and mediaPipe to detect the hands and get the position of 21 different landmarks on the hand.
By tracking each landmark individually this project is able to link certain hand gestures with certain controls on the computer.
This project is still in early development so the functionality is very limited.

Currenty the user can:
~ Move the cursor around the screen
~ "Click" on the screen
~ "Double click" on the screen
~ Adjust the computer volume

More functionallity like scrolling and on-screen keyboard activation will be added eventually.


Disclamer:
There is no guarante that this will actually work with your system. You will also need a decent quality webcam to detect your hands.
The quality of the detection is based off the clarity of the image that the program receives and the ability of openCV and mediaPipe to perform hand tracking.
