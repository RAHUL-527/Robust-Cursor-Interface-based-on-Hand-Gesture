import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import pyautogui
import math
import pyvolume
import numpy as np
from math import hypot
import screen_brightness_control as sbc
import ctypes

# Disable the screen saver until the end of the execution
ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

# FRONT END DESIGN
class FrontendDesign:
    def __init__(self, root):
        self.root = root
        self.root.title("CURSOR INTERFACE")

        # Load background image
        background_image = Image.open("assets/hand.jpg")  # Replace with your image path
        background_photo = ImageTk.PhotoImage(background_image)

        # Create a label with the background image
        background_label = tk.Label(root, image=background_photo)
        background_label.image = background_photo
        background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Create buttons with metallic black color
        style = ttk.Style()
        style.configure("TButton", foreground="black", background="white", font=('Arial', 12, 'bold'))

        button1 = ttk.Button(root, text="START", command=self.button1_clicked)
        button2 = ttk.Button(root, text="HELP", command=self.button2_clicked)
        button3 = ttk.Button(root, text="EXIT", command=self.button3_clicked)

        # Place buttons in a 'V' shape alignment
        button1.place(relx=0.1, rely=0.7, relwidth=0.15, relheight=0.1)
        button2.place(relx=0.4, rely=0.8, relwidth=0.15, relheight=0.1)
        button3.place(relx=0.7, rely=0.7, relwidth=0.15, relheight=0.1)

    def button1_clicked(self):
        back(self)

    def button2_clicked(self):
        tk.messagebox.showinfo(title="HAND GESTURE INFORMATION", message="1. Middle Finger MCP for Cursor Movement\n2. Thumb Tip & Index Tip for Click\n3. Thumb Tip & Index Finger MCP for Scroll Down\n4. Thumb Tip & Pinky MCP for Scroll Up\n5. Thumb Tip & Ring Finger Tip for Volume Up 100%\n6. Thumb Tip & Pinky Pip for Volume Down 50%\n7. Thumb Tip & Pinky Tip for Volume Down 20%\n8. Thumb Tip & Index Finger Pip for Mouse Right Click\n9. Index Tip & Middle Finger Tip for Exit\n10. Two Thumb fingers distance Controls the Brightness")

    def button3_clicked(self):
        self.root.destroy()  # Close the window when Button 3 is clicked

# BACKEND PROCESS
def back(self):
    # Initialize Mediapipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands()

    # Initialize PyAutoGUI for mouse control
    screen_width, screen_height = pyautogui.size()
    mouse_speed = 20

    # Initialize volume control variables
    current_volume = 50
    pyautogui.press('shift')

    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe Hands
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Existing cursor movement, mouse actions, and gesture controls
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
                index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
                pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]

                index_x, index_y = int(index_tip.x * screen_width), int(index_tip.y * screen_height)
                thumb_x, thumb_y = int(thumb_tip.x * screen_width), int(thumb_tip.y * screen_height)

                # Cursor movement related to Index Tip
                pyautogui.moveTo(int(middle_finger_mcp.x * screen_width), int(middle_finger_mcp.y * screen_height))

                # Mouse click action if Index Tip and Thumb Tip touch together
                if math.dist((index_pip.x * screen_width, index_pip.y * screen_height), (thumb_x, thumb_y)) < 30:
                    pyautogui.click(button='right')

                if math.dist((index_x, index_y), (thumb_x, thumb_y)) < 30:
                    pyautogui.click()

                # Volume Down Control based on Pinky Tip and Thumb Tip touch
                if math.dist((pinky_tip.x * screen_width, pinky_tip.y * screen_height), (thumb_x, thumb_y)) < 20:
                    current_volume = 20
                    pyvolume.custom(current_volume)

                # Volume Control based on Pinky Pip and Thumb Tip touch
                if math.dist((pinky_pip.x * screen_width, pinky_pip.y * screen_height), (thumb_x, thumb_y)) < 20:
                    current_volume = 50
                    pyvolume.custom(current_volume)

                # Volume Up Control based on Ring Tip and Thumb Tip touch
                if math.dist((ring_tip.x * screen_width, ring_tip.y * screen_height), (thumb_x, thumb_y)) < 20:
                    current_volume = 100
                    pyvolume.custom(current_volume)

                # Scroll Down action based on Thumb Tip and Index MCP touch
                if math.dist((thumb_x, thumb_y), (index_finger_mcp.x * screen_width, index_finger_mcp.y * screen_height)) < 20:
                    pyautogui.scroll(-(mouse_speed))

                # Scroll Up action based on Thumb Tip and Middle Tip touch
                if math.dist((thumb_x, thumb_y), (pinky_mcp.x * screen_width, pinky_mcp.y * screen_height)) < 20:
                    pyautogui.scroll(mouse_speed)

                # Exit action based on Middle Finger Tip and Index Tip touch
                if math.dist((middle_tip.x * screen_width, middle_tip.y * screen_height), (index_x, index_y)) < 20:
                    cap.release()
                    cv2.destroyAllWindows()
                    # Re-enable the screen saver after program completion
                    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
                    exit()

        # Brightness Control using distance between both thumb tips
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            hand1, hand2 = results.multi_hand_landmarks[:2]
            thumb1 = hand1.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb2 = hand2.landmark[mp_hands.HandLandmark.THUMB_TIP]

            thumb1_x, thumb1_y = int(thumb1.x * screen_width), int(thumb1.y * screen_height)
            thumb2_x, thumb2_y = int(thumb2.x * screen_width), int(thumb2.y * screen_height)

            thumb_distance = math.dist((thumb1_x, thumb1_y), (thumb2_x, thumb2_y))

            if thumb_distance > 50:  # Condition to initiate brightness control
                brightness_level = np.interp(thumb_distance, [50, 300], [0, 100])
                sbc.set_brightness(int(brightness_level))

        cv2.imshow('CURSOR INTERFACE', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CURSOR INTERFACE")
    root.configure(bg="black")
    #root.geometry("960x500")
    root.geometry("537x259")
    app = FrontendDesign(root)
    root.mainloop()
