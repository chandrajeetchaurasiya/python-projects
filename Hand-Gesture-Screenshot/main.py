import os
import time
from datetime import datetime
import winsound

import cv2
import mediapipe as mp
import numpy as np
import pyautogui


# Configuration 
CAMERA_INDEX = 0
COUNTDOWN_SECONDS = 0
GESTURE_HOLD_SECONDS = 1.0
COOLDOWN_SECONDS = 3.0
PREVIEW_MAX_WIDTH = 1100
PREVIEW_MAX_HEIGHT = 750
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def finger_is_up(landmarks, tip_id, pip_id):
    """Return True when a finger tip is above its PIP joint."""
    return landmarks[tip_id].y < landmarks[pip_id].y


def detect_gesture(hand_landmarks):
    """
    Simple landmark-based gesture detection.
    Returns: 'OPEN_PALM', 'VICTORY', 'FIST', or 'UNKNOWN'.
    """
    lm = hand_landmarks.landmark

    index_up = finger_is_up(lm, 8, 6)
    middle_up = finger_is_up(lm, 12, 10)
    ring_up = finger_is_up(lm, 16, 14)
    pinky_up = finger_is_up(lm, 20, 18)

    fingers_up = [index_up, middle_up, ring_up, pinky_up]

    if all(fingers_up):
        return "OPEN_PALM"

    if index_up and middle_up and not ring_up and not pinky_up:
        return "VICTORY"

    if not any(fingers_up):
        return "FIST"

    return "UNKNOWN"


def play_capture_sound():
    """Play a short Windows notification sound."""
    try:
        winsound.Beep(1100, 180)
        winsound.Beep(1450, 220)
    except RuntimeError:
        winsound.MessageBeep()


def save_screenshot():
    """Capture the full desktop and save it as a PNG file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    image = pyautogui.screenshot()
    image.save(filepath)
    play_capture_sound()

    print(f"[SAVED] {os.path.abspath(filepath)}")
    return filepath, image


def show_preview(image):
    """Show a resized preview while keeping the saved image full resolution."""
    preview = np.array(image)
    preview = cv2.cvtColor(preview, cv2.COLOR_RGB2BGR)

    height, width = preview.shape[:2]
    scale = min(
        PREVIEW_MAX_WIDTH / width,
        PREVIEW_MAX_HEIGHT / height,
        1.0
    )
    new_size = (int(width * scale), int(height * scale))
    preview = cv2.resize(preview, new_size, interpolation=cv2.INTER_AREA)

    cv2.imshow("Screenshot Preview - Press any key to close", preview)
    print("[PREVIEW] Press any key in the preview window to close it.")
    cv2.waitKey(0)
    cv2.destroyWindow("Screenshot Preview - Press any key to close")


def draw_status(frame, gesture, status, countdown=None):
    """Draw readable instructions and current state on the camera window."""
    cv2.putText(
        frame, f"Gesture: {gesture}", (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2
    )
    cv2.putText(
        frame, status, (15, 70),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2
    )

    if countdown is not None:
        text = str(countdown)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 3
        thickness = 6
        size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (frame.shape[1] - size[0]) // 2
        y = (frame.shape[0] + size[1]) // 2
        cv2.putText(frame, text, (x, y), font, scale, (0, 0, 255), thickness)


def main():
    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("[ERROR] Could not open webcam. Check camera permissions or CAMERA_INDEX.")
        return

    print("\nHand Gesture Screenshot Application")
    print("-----------------------------------")
    print(" Open palm : Ready")
    print(" Victory sign: Start 3-second screenshot countdown")
    print(" Fist : Cancel countdown / reset")
    print("Q or ESC : Quit\n")

    victory_started_at = None
    last_capture_at = 0
    status = "Show an open palm, then a victory sign"
    countdown_active = False

    try:
        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.60
        ) as hands:

            while True:
                success, frame = camera.read()
                if not success:
                    print("[ERROR] Could not read a frame from webcam.")
                    break

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                gesture = "NO HAND"
                now = time.time()

                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    mp_drawing.draw_landmarks(
                        frame, hand, mp_hands.HAND_CONNECTIONS
                    )
                    gesture = detect_gesture(hand)

                # A fist cancels an active countdown.
                if countdown_active and gesture == "FIST":
                    countdown_active = False
                    victory_started_at = None
                    status = "Countdown cancelled"
                    print("[CANCELLED] Fist gesture detected.")

                # Victory sign must be held briefly to avoid accidental capture.
                if not countdown_active:
                    if gesture == "OPEN_PALM":
                        victory_started_at = None
                        status = "Ready - show victory sign to capture"
                    elif gesture == "VICTORY" and now - last_capture_at >= COOLDOWN_SECONDS:
                        if victory_started_at is None:
                            victory_started_at = now
                        held_for = now - victory_started_at
                        status = f"Hold victory sign: {max(0, GESTURE_HOLD_SECONDS - held_for):.1f}s"

                        if held_for >= GESTURE_HOLD_SECONDS:
                            countdown_active = True
                            countdown_started_at = time.time()
                            victory_started_at = None
                    elif gesture == "FIST":
                        victory_started_at = None
                        status = "Reset"
                    else:
                        victory_started_at = None
                        status = "Show open palm or victory sign"

                countdown_value = None

                if countdown_active:
                    elapsed = time.time() - countdown_started_at
                    remaining = COUNTDOWN_SECONDS - int(elapsed)

                    if remaining > 0:
                        countdown_value = remaining
                        status = "Screenshot capturing..."
                    else:
                        countdown_active = False
                        status = "Screenshot saved!"
                        filepath, screenshot_image = save_screenshot()
                        last_capture_at = time.time()
                        print(f"[INFO] Saved: {filepath}")
                        show_preview(screenshot_image)
                        status = "Ready - show victory sign to capture"

                draw_status(frame, gesture, status, countdown_value)
                cv2.imshow("Hand Gesture Screenshot - Q to quit", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break

    except KeyboardInterrupt:
        print("\n[INFO] Application stopped by user.")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("[INFO] Camera released. Application closed.")


if __name__ == "__main__":
    main()
