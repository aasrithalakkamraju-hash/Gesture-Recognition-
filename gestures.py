import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for idx, hand in enumerate(result.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            hand_label = result.multi_handedness[idx].classification[0].label
            lm = hand.landmark

            fingers = []

            # Thumb logic differs for left and right hands
            if hand_label == "Right":
                fingers.append(lm[4].x < lm[3].x)
            else:
                fingers.append(lm[4].x > lm[3].x)

            # Other four fingers
            fingers.append(lm[8].y < lm[6].y)
            fingers.append(lm[12].y < lm[10].y)
            fingers.append(lm[16].y < lm[14].y)
            fingers.append(lm[20].y < lm[18].y)

            finger_count = fingers.count(True)

            if finger_count == 0:
                gesture = "Fist"
            elif finger_count == 1:
                gesture = "One Finger"
            elif finger_count == 2:
                gesture = "Two Fingers"
            elif finger_count == 3:
                gesture = "Three Fingers"
            elif finger_count == 4:
                gesture = "Four Fingers"
            elif finger_count == 5:
                gesture = "Five Fingers"
            else:
                gesture = "Unknown"

            # Display text near wrist
            wrist = lm[0]
            h, w, _ = frame.shape
            x, y = int(wrist.x * w), int(wrist.y * h)

            cv2.putText(
                frame,
                f"{hand_label}: {gesture}",
                (x - 40, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Two Hand Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
