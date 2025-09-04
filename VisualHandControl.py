import cv2
import numpy as np
import HandTrackingModule as htm
import VirtualMouseModule as vmouse
import VolumeHandControlModule as vcontrol
import time
import autopy
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

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

update_thread = None
stop_thread = False
selected_button_frame = None
volume_frame = None
mouse_frame = None
filler_frame1 = None
filler_frame2 = None
filler_frame3 = None
root = None
mode = 0


def select_button_frame(mode):
    global selected_button_frame

    # Map mode to button frame
    mode_to_frame = {
        1: filler_frame1,
        2: mouse_frame,
        3: volume_frame,  # Update this mapping as per your requirement
        # Add more mappings for other modes if needed
    }

    if mode == 0:
        if selected_button_frame:
            selected_button_frame.config(borderwidth=0)
        return

    # Get the corresponding button frame for the mode
    button_frame = mode_to_frame.get(mode)

    if button_frame:
        # Remove border from previously selected button (if any)
        if selected_button_frame:
            selected_button_frame.config(borderwidth=0)

        # Update selected button frame
        selected_button_frame = button_frame
        selected_button_frame.config(borderwidth=2, relief="solid")  # Add border to selected button frame
    else:
        print("Invalid mode")


def button_clicked(button_frame):
    global selected_button_frame

    # Remove border from previously selected button (if any)
    if selected_button_frame:
        selected_button_frame.config(borderwidth=0)

    # Update selected button
    selected_button_frame = button_frame
    selected_button_frame.config(borderwidth=2, relief="solid")  # Add border to selected button


def createWindow():
    def on_closing():
        root.quit()  # Quit the tkinter main loop
        global stop_thread
        stop_thread = True
        quit()

    # Create the main window
    global root
    root = tk.Tk()
    root.title("Visual Hand Control")
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Call on_closing when window is closed
    root.attributes('-topmost', True)  # Keep the window always on top

    global volume_frame, mouse_frame, filler_frame1, filler_frame2, filler_frame3

    # Load images
    volume_img = Image.open("images/volume_icon.png")
    volume_img = volume_img.resize((50, 50))
    volume_img = ImageTk.PhotoImage(volume_img)

    mouse_img = Image.open("images/mouse_icon.png")
    mouse_img = mouse_img.resize((50, 50))
    mouse_img = ImageTk.PhotoImage(mouse_img)

    filler_img = Image.open("images/filler_icon.png")
    filler_img = filler_img.resize((50, 50))
    filler_img = ImageTk.PhotoImage(filler_img)

    # Create buttons with images
    volume_frame = tk.Frame(root, borderwidth=0)  # Create a frame for the volume button
    volume_button = ttk.Button(volume_frame, image=volume_img, command=lambda: button_clicked(volume_frame))
    volume_button.pack()
    volume_frame.grid(row=0, column=0, padx=10, pady=10)

    mouse_frame = tk.Frame(root, borderwidth=0)  # Create a frame for the mouse button
    mouse_button = ttk.Button(mouse_frame, image=mouse_img, command=lambda: button_clicked(mouse_frame))
    mouse_button.pack()
    mouse_frame.grid(row=0, column=1, padx=10, pady=10)

    filler_frame1 = tk.Frame(root, borderwidth=0)  # Create a frame for the filler button
    filler_button1 = ttk.Button(filler_frame1, image=filler_img, command=lambda: button_clicked(filler_frame1))
    filler_button1.pack()
    filler_frame1.grid(row=0, column=2, padx=10, pady=10)

    filler_frame2 = tk.Frame(root, borderwidth=0)  # Create a frame for the filler button
    filler_button2 = ttk.Button(filler_frame2, image=filler_img, command=lambda: button_clicked(filler_frame2))
    filler_button2.pack()
    filler_frame2.grid(row=0, column=3, padx=10, pady=10)

    filler_frame3 = tk.Frame(root, borderwidth=0)  # Create a frame for the filler button
    filler_button3 = ttk.Button(filler_frame3, image=filler_img, command=lambda: button_clicked(filler_frame3))
    filler_button3.pack()
    filler_frame3.grid(row=0, column=4, padx=10, pady=10)

    global update_thread
    update_thread = threading.Thread(target=main)
    update_thread.start()

    # Run the tkinter event loop
    root.mainloop()


def main():
    def is_window_minimized(window):
        state = window.wm_state()
        return state == 'iconic'

    pTime = 0
    enabled = False
    toggle = False
    root.deiconify()

    global mode
    while not stop_thread:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if len(lmList) != 0:
            fingers = detector.fingersUp()

            if is_window_minimized(root):
                if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                    # root.wm_attributes("-topmost", True)
                    # root.after(0, lambda: root.wm_attributes("-topmost", False))
                    root.deiconify()
                    mode = 0
                    print("LIFTING ROOT")
            else:
                if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # Clicking mode
                    # if not toggle:
                    mode = 1
                    toggle = True
                    enabled = not enabled
                elif fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 0 and fingers[2] == 0 and fingers[3] == 0:  # Moving mode
                    # if not toggle:
                    mode = 2
                    toggle = True
                    enabled = not enabled
                elif fingers[1] == 1 and fingers[0] == 1 and fingers[4] == 1 and fingers[2] == 0 and fingers[3] == 0:  # Volume mode
                    # if not toggle:
                    mode = 3
                    toggle = True
                    enabled = not enabled
                # if fingers[3] == 1:  # Ring finger extended
                #
                # if fingers[0] == 1:  # Scroll Up
                #     autopy.key.tap(autopy.key.Code.UP_ARROW)
                # elif fingers[0] == 0:  # Scroll Down
                #     autopy.key.tap(autopy.key.Code.DOWN_ARROW)
                elif fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    print("HAND CLOSED")
                    root.iconify()
                else:
                    toggle = False
                    mode = 0

                # if enabled:  # TODO finish implementing the toggle feature
                select_button_frame(mode)
                if mode == 1:
                    mouse.click_mode(img)
                elif mode == 2:
                    mouse.movement_mode(img, lmList)
                elif mode == 3:
                    volControl.getVolumeControl(img, lmList, minLen=25, maxLen=300)

                print(f"Enable: {enabled} \tToggle: {toggle} \tMode: {mode} pinky: {fingers[4]}")

        else:
            enabled = False
            toggle = False

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Virtual Mouse", img)
        cv2.waitKey(1)

        # root.update()
        print(is_window_minimized(root))


createWindow()
