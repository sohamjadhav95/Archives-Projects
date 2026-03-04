import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_w, screen_h = pyautogui.size()

# Initialize Webcam
cap = cv2.VideoCapture(0)

def get_finger_positions(hand_landmarks, frame_w, frame_h):
    """Extracts the x, y positions of key fingers."""
    finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    positions = {}
    
    for tip in finger_tips:
        x = int(hand_landmarks.landmark[tip].x * frame_w)
        y = int(hand_landmarks.landmark[tip].y * frame_h)
        positions[tip] = (x, y)

    return positions

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_h, frame_w, _ = frame.shape  # Get frame dimensions
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger positions
            finger_pos = get_finger_positions(hand_landmarks, frame_w, frame_h)

            # Extract key finger coordinates
            index_finger = finger_pos.get(8, None)
            middle_finger = finger_pos.get(12, None)
            thumb = finger_pos.get(4, None)

            if index_finger:
                # Convert frame coordinates to screen coordinates
                screen_x = np.interp(index_finger[0], (0, frame_w), (0, screen_w))
                screen_y = np.interp(index_finger[1], (0, frame_h), (0, screen_h))

                # Move the mouse
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)

            # Gesture Controls
            if index_finger and middle_finger:
                # Left Click (Index & Middle Up)
                if abs(index_finger[1] - middle_finger[1]) < 20:  # Fingers close together
                    pyautogui.click()
                    cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if index_finger and not middle_finger:
                # Right Click (Fist)
                if abs(index_finger[1] - thumb[1]) < 20:  # Thumb & index close
                    pyautogui.rightClick()
                    cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if index_finger and thumb:
                # Scrolling (Pinch Gesture)
                distance = abs(index_finger[0] - thumb[0])  # Horizontal distance
                if distance < 30:
                    pyautogui.scroll(5)  # Scroll Up
                    cv2.putText(frame, "Scroll Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                elif distance > 80:
                    pyautogui.scroll(-5)  # Scroll Down
                    cv2.putText(frame, "Scroll Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the output
    cv2.imshow("Hand Gesture Mouse Control", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
