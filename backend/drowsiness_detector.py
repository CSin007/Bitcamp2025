import dlib
import cv2
import numpy as np
from imutils import face_utils
import os

# Load model from file
model_path = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# EAR = Eye Aspect Ratio helper
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# Main function: returns a drowsiness score from 0 (alert) to 10 (very drowsy)
def get_drowsiness_score(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        left_eye = shape[42:48]
        right_eye = shape[36:42]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        ear = (left_ear + right_ear) / 2.0

        # Convert EAR into score: lower EAR = more fatigue
        if ear >= 0.3:
            return 0  # Eyes open
        elif ear <= 0.15:
            return 10  # Drowsy
        else:
            # Linearly scale between 0.3 and 0.15 → score 0 to 10
            score = int((0.3 - ear) / (0.3 - 0.15) * 10)
            return min(score, 10)

    return -1  # No face detected
