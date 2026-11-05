# Hand Gesture Screenshot

A Windows Python application that captures the full desktop using hand gestures detected through a webcam.

## Features
- Detects one hand using MediaPipe and OpenCV.
- Open palm indicates readiness.
- Victory sign starts a 3-second countdown.
- Fist cancels an active countdown.
- Saves full-resolution screenshots in `screenshots/`.
- Shows a screenshot preview and plays a Windows capture sound.

## Requirements
- Windows 10/11
- Python 3.12 (64-bit)
- A working webcam

## Setup (PowerShell)

```powershell
cd "path\to\hand_gesture_screenshot"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, run this in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## Run

```powershell
python main.py
```

## Gestures
| Gesture | Action |
|---|---|
| Open palm | Ready |
| Victory sign (index + middle fingers up) | Start screenshot countdown |
| Fist | Cancel countdown / reset |

Hold the victory sign for about one second. After the three-second countdown, the full desktop screenshot is saved automatically.

Press `Q` or `Esc` in the camera window to exit.

## Notes
- The screenshot is saved at the desktop's original resolution; only the preview is resized.
- Close or minimize private windows before capturing.
- If the webcam does not open, check Windows camera permissions or change `CAMERA_INDEX` in `main.py`.

## requirment for this project 
 - opencv-python==4.10.0.84
 - mediapipe==0.10.21
 - numpy==1.26.4
 - PyAutoGUI==0.9.54
 - Pillow==11.1.0
  
