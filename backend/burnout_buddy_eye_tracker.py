import cv2
import json
import os
import mediapipe as mp
from collections import deque
from drowsiness_detector import get_drowsiness_score


def main():
    score_history = deque(maxlen=10)  # Smooth over last 10 scores
    total_score = 0
    frame_count = 0

    # === Init MediaPipe ===
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    cap = cv2.VideoCapture(0)

    # === Tracking Variables ===
    blink_start_time = None
    long_blinks = 0
    blink_timestamps = []
    no_movement_counter = 0

    prev_iris_x = None
    prev_iris_y = None
    movement_threshold = 0.001  # Adjust based on stability

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Camera not working")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        raw_score = get_drowsiness_score(frame)

        if raw_score != -1:
            score_history.append(raw_score)
            drowsiness_score = int(sum(score_history) / len(score_history))

            total_score += raw_score
            frame_count += 1

            average_drowsiness = total_score / frame_count
        else:
            drowsiness_score = -1
            average_drowsiness = -1

        if drowsiness_score == -1:
            status = "No Face"
            color = (255, 255, 255)
        elif drowsiness_score >= 7:
            status = f"High Fatigue (Score: {drowsiness_score})"
            color = (0, 0, 255)
        elif drowsiness_score >= 4:
            status = f"Moderate Fatigue (Score: {drowsiness_score})"
            color = (0, 165, 255)
        else:
            status = f"Low Fatigue (Score: {drowsiness_score})"
            color = (0, 255, 0)

        cv2.putText(frame, status, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_spec,
                )

                left_iris = face_landmarks.landmark[473]
                iris_x = left_iris.x
                iris_y = left_iris.y

                if prev_iris_x is not None and prev_iris_y is not None:
                    dx = abs(iris_x - prev_iris_x)
                    dy = abs(iris_y - prev_iris_y)
                    if dx + dy < movement_threshold:
                        no_movement_counter += 1
                    else:
                        no_movement_counter = 0

                prev_iris_x = iris_x
                prev_iris_y = iris_y

        cv2.imshow("BurnoutBuddy - Fatigue Detector", frame)
        if cv2.waitKey(5) & 0xFF == 27:  # Esc to close
            break

        # Only update if we have enough data
        if (
            frame_count % 10 == 0
        ):  # every 10 frames (or remove this line for every frame)
            with open("latest_score.json", "w") as f:
                json.dump({"average_drowsiness": average_drowsiness}, f)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
