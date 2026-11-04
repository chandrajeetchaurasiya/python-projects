
import cv2 as cv
import mediapipe.python.solutions.hands as mpHands
import mediapipe.python.solutions.drawing_utils as drawing
import numpy as np
import math

#  HAND DETECTION 

hand = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# CAMERA SETUP 

cam = cv.VideoCapture(0)

if not cam.isOpened():
    print("Camera could not be opened!")
    exit()

canvas = None
prev_x, prev_y = 0, 0

# COLORS 

colors = [
    (255, 0, 0),       # Blue
    (0, 255, 0),       # Green
    (0, 0, 255),       # Red
    (0, 255, 255),     # Yellow
    (255, 255, 0),     # Cyan
    (255, 0, 255),     # Magenta
    (0, 165, 255),     # Orange
    (255, 255, 255),   # White
    (0, 0, 0)          # Black
]

color = colors[2]
brush_thickness = 5

# COLOR PALETTE 

palette = [
    (1, 50),
    (100, 150),
    (200, 250),
    (300, 350),
    (400, 450),
    (500, 550),
    (600, 650),
    (700, 750),
    (800, 850)
]


def draw_palette(frame):
    for i, (start, end) in enumerate(palette):
        cv.rectangle(
            frame,
            (start, 10),
            (end, 50),
            colors[i],
            -1
        )

    cv.putText(
        frame,
        "COLOR PALETTE",
        (10, 75),
        cv.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


# MAIN LOOP 

cv.namedWindow("Canvas", cv.WINDOW_NORMAL)

while True:

    success, frame = cam.read()

    if not success:
        print("Video capture failed!")
        break

    frame = cv.flip(frame, 1)

    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)

    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    hand_detected = hand.process(frame_rgb)

    draw_palette(frame)

    #HAND TRACKING 

    if hand_detected.multi_hand_landmarks:

        for handlmk in hand_detected.multi_hand_landmarks:

            drawing.draw_landmarks(
                frame,
                handlmk,
                mpHands.HAND_CONNECTIONS
            )

            index_tip = handlmk.landmark[8]
            thumb_tip = handlmk.landmark[4]
            small_tip = handlmk.landmark[20]

            cx = int(index_tip.x * w)
            cy = int(index_tip.y * h)

            tx = int(thumb_tip.x * w)
            ty = int(thumb_tip.y * h)

            sx = int(small_tip.x * w)
            sy = int(small_tip.y * h)

            cv.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
            cv.circle(frame, (tx, ty), 8, (255, 105, 0), -1)
            cv.circle(frame, (sx, sy), 8, (255, 105, 0), -1)

            # GESTURE DETECTION 

            distance1 = math.hypot(tx - cx, ty - cy)
            distance2 = math.hypot(sx - tx, sy - ty)

            # Clear canvas: Thumb + Little finger
            if distance2 < 50:
                canvas = np.zeros_like(frame)
                prev_x, prev_y = 0, 0

            # Stop drawing: Thumb + Index finger
            elif distance1 < 50:
                prev_x, prev_y = 0, 0

            else:

                # COLOR SELECTION 

                selected_color = False

                if 0 <= cy <= 60:
                    for i, (start, end) in enumerate(palette):

                        if start <= cx <= end:
                            color = colors[i]
                            selected_color = True
                            prev_x, prev_y = 0, 0
                            break

                # DRAWING 

                if not selected_color:

                    if prev_x != 0 and prev_y != 0:

                        cv.line(
                            canvas,
                            (prev_x, prev_y),
                            (cx, cy),
                            color,
                            brush_thickness
                        )

                    prev_x, prev_y = cx, cy

    else:
        # Reset when hand disappears
        prev_x, prev_y = 0, 0

    #  DISPLAY INSTRUCTIONS 

    cv.putText(
        frame,
        "Thumb + Index: Stop Drawing",
        (20, 100),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
    )

    cv.putText(
        frame,
        "Thumb + Little Finger: Clear Canvas",
        (20, 130),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
    )

    cv.putText(
        frame,
        "Press Q to Quit",
        (20, 160),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    #  COMBINE CANVAS AND CAMERA 

    combined = cv.addWeighted(canvas, 1, frame, 1, 0)

    display_frame = cv.resize(frame, (700, 400))
    display_canvas = cv.resize(combined, (700, 400))

    window = np.hstack((display_canvas, display_frame))

    cv.imshow("Canvas", window)

    key = cv.waitKey(1) & 0xFF

    if key == ord('q'):
        break

#  RELEASE RESOURCES

cam.release()
hand.close()
cv.destroyAllWindows()
