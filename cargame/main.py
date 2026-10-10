import sys

import cv2
import mediapipe as mp
import pyautogui


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
current_key = None


def press(key):
    global current_key
    if current_key != key:
        release()
        pyautogui.keyDown(key)
        current_key = key


def release():
    global current_key
    if current_key is not None:
        pyautogui.keyUp(current_key)
        current_key = None


def fingers_up(landmarks):
    tips = (4, 8, 12, 16, 20)
    fingers = [landmarks[4].x < landmarks[3].x]
    fingers.extend(
        landmarks[tip].y < landmarks[tip - 2].y for tip in tips[1:]
    )
    return fingers


def run():
    camera = cv2.VideoCapture(0)
    hand_tracker = None

    try:
        if not camera.isOpened():
            raise RuntimeError(
                "Could not open the webcam. Connect a camera and check that "
                "another application is not using it."
            )

        hand_tracker = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        print("Hand gesture controller started. Press Esc in the preview to quit.")

        while True:
            received_frame, frame = camera.read()
            if not received_frame:
                raise RuntimeError("Could not read a frame from the webcam.")

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand_tracker.process(rgb_frame)
            height, width = frame.shape[:2]

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                landmarks = hand_landmarks.landmark
                mp_draw.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                fingers = fingers_up(landmarks)
                wrist_x = landmarks[0].x * width

                if fingers == [True, False, False, False, False]:
                    press("up")
                elif fingers == [False, False, False, False, False]:
                    press("down")
                elif (
                    fingers[1]
                    and fingers[2]
                    and not fingers[3]
                    and not fingers[4]
                ):
                    press("enter")
                elif all(fingers):
                    press("s")
                elif wrist_x < width * 0.35:
                    press("left")
                elif wrist_x > width * 0.65:
                    press("right")
                else:
                    release()
            else:
                release()

            cv2.imshow("Gesture Game Controller", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        release()
        camera.release()
        if hand_tracker is not None:
            hand_tracker.close()
        cv2.destroyAllWindows()


def main():
    try:
        run()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
