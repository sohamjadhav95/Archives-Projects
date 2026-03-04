import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# Initialize Webcam
cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    """Counts the number of extended fingers"""
    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    count = 0

    # Compare finger tips with their respective lower joints to determine openness
    if hand_landmarks.landmark[tips[0]].x > hand_landmarks.landmark[tips[0] - 1].x:  # Thumb condition
        count += 1
    for tip in tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1

    return count

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB (MediaPipe requires RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands
    results = hands.process(rgb_frame)

    action = "No gesture detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Count extended fingers
            fingers_up = count_fingers(hand_landmarks)

            # Gesture-based actions
            if fingers_up == 1 and hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:
                action = "Thumbs Up - Volume Up"
                pyautogui.press("volumeup")  # Increase volume
            elif fingers_up == 1 and hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y:
                action = "Thumbs Down - Volume Down"
                pyautogui.press("volumedown")  # Decrease volume
            elif fingers_up == 5:
                action = "Open Palm - Mute/Unmute"
                pyautogui.press("volumemute")  # Toggle mute
            elif fingers_up == 2:
                action = "Peace Sign - Taking Screenshot"
                pyautogui.screenshot("screenshot.png")  # Take a screenshot
            elif fingers_up == 0:
                action = "Fist - Locking Screen"
                pyautogui.hotkey("win", "l")  # Lock screen

            # Display the detected action
            cv2.putText(frame, action, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show camera feed
    cv2.imshow("Hand Gesture Control", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
