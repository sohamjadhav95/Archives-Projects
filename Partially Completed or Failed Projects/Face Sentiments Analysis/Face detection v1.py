import cv2
import numpy as np
from deepface import DeepFace

# Initialize webcam
cap = cv2.VideoCapture(0)

# Store last few predictions for smoothing
emotion_history = []
max_history = 5  # Number of frames to average

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale for better face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Load OpenCV's face detector (Haar Cascade)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(60, 60))

    # Process only if face is detected
    if len(faces) > 0:
        x, y, w, h = faces[0]  # Take the first detected face
        face_roi = frame[y:y+h, x:x+w]  # Crop the detected face

        try:
            # Analyze face sentiment
            analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            
            if isinstance(analysis, list) and len(analysis) > 0:
                emotion = analysis[0]['dominant_emotion']
                emotion_history.append(emotion)
                
                # Keep history limited
                if len(emotion_history) > max_history:
                    emotion_history.pop(0)

                # Smooth output by taking the most frequent emotion in history
                smoothed_emotion = max(set(emotion_history), key=emotion_history.count)

                # Display result
                cv2.putText(frame, f"Emotion: {smoothed_emotion}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print(f"Error: {e}")

    # Display frame
    cv2.imshow("Face Sentiment Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
