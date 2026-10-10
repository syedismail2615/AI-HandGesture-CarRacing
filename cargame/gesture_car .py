import cv2
import mediapipe as mp
import pydirectinput
import math
import time

# --- Initialize MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7)

# --- Configuration ---
# Thresholds
LEAN_LEFT_THRESH = 0.4
LEAN_RIGHT_THRESH = 0.6
FIST_THRESH = 0 # 0 fingers
OPEN_PALM_THRESH = 4 # 4 or more fingers

# Keys
KEY_GAS = 'w'
KEY_BRAKE = 's'
KEY_LEFT = 'a'
KEY_RIGHT = 'd'

# State tracking to avoid repeated key presses
current_keys = set()

def press_key(key):
    if key not in current_keys:
        pydirectinput.keyDown(key)
        current_keys.add(key)

def release_key(key):
    if key in current_keys:
        pydirectinput.keyUp(key)
        current_keys.remove(key)

def get_finger_count(hand_landmarks):
    # Tip IDs for Thumb, Index, Middle, Ring, Pinky
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    
    # Thumb (Check horizontal movement for thumb - assuming right hand for simplicity or general open/close)
    # Note: This simple logic might vary based on hand orientation, but works for general open/close
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)
        
    # Other 4 fingers (Check vertical movement)
    for id in range(1, 5):
        if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

# --- Main Loop ---
cap = cv2.VideoCapture(0)

print("Starting Gesture Control... Press 'q' to quit.")
print("Controls: Open Hand = GAS (W), Fist = BRAKE (S), Head Left/Right = STEER (A/D)")

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Flip for mirror effect, easier for user coordination
        frame = cv2.flip(frame, 1) 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process Hand & Face
        hand_results = hands.process(rgb_frame)
        face_results = face_mesh.process(rgb_frame)
        
        status_text = []
        
        # --- Speed Control (Hand) ---
        gas_pressed = False
        brake_pressed = False
        
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                count = get_finger_count(hand_landmarks)
                
                # Draw hand landmarks for feedback
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if count >= OPEN_PALM_THRESH:
                    press_key(KEY_GAS)
                    release_key(KEY_BRAKE)
                    status_text.append("GAS")
                    gas_pressed = True
                elif count <= FIST_THRESH:
                    press_key(KEY_BRAKE)
                    release_key(KEY_GAS)
                    status_text.append("BRAKE")
                    brake_pressed = True
        
        # If no hand detected or neutral hand, release speed keys
        if not gas_pressed: release_key(KEY_GAS)
        if not brake_pressed: release_key(KEY_BRAKE)


        # --- Steering Control (Face) ---
        left_pressed = False
        right_pressed = False

        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                 # Draw partial face landmarks
                mp.solutions.drawing_utils.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION, 
                                                          landmark_drawing_spec=None, 
                                                          connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())

                nose = face_landmarks.landmark[1] # Nose tip
                
                if nose.x < LEAN_LEFT_THRESH:
                    press_key(KEY_LEFT)
                    release_key(KEY_RIGHT)
                    status_text.append("LEFT")
                    left_pressed = True
                elif nose.x > LEAN_RIGHT_THRESH:
                    press_key(KEY_RIGHT)
                    release_key(KEY_LEFT)
                    status_text.append("RIGHT")
                    right_pressed = True
        
        # If no face or neutral, release steering keys
        if not left_pressed: release_key(KEY_LEFT)
        if not right_pressed: release_key(KEY_RIGHT)

        # --- Visual Feedback ---
        cv2.putText(frame, " | ".join(status_text), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Driver Cam - Gesture Controller", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    # Release all keys on exit to prevent stuck keys
    for key in list(current_keys):
        release_key(key)
    cap.release()
    cv2.destroyAllWindows()
