# Hand Gesture Car-Game Controller

This project uses a webcam to recognize hand gestures and send keyboard
commands to a car game running in another window. It does not include the car
game itself.

## Requirements

- Python 3.9 or newer
- A webcam
- A car game that accepts the keyboard controls listed below

## Setup

From the project folder, create and activate a virtual environment, then
install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On Windows, if PowerShell prevents virtual-environment activation, run the
program with the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Run

Start or focus the car game, then run:

```powershell
python main.py
```

Allow webcam access when prompted. The webcam preview is mirrored. Press
**Esc** while the preview window is focused to quit. The controller releases
any held key when it exits.

## Gestures

| Gesture | Keyboard input |
| --- | --- |
| Thumbs up | Up arrow |
| Closed fist | Down arrow |
| Index and middle fingers raised | Enter |
| Open palm | `S` |
| Hand on the left side of the preview | Left arrow |
| Hand on the right side of the preview | Right arrow |
| No hand or an unrecognized pose | Release the held key |

The game must be the active window for it to receive the keyboard inputs.
Keep the mouse away from the top-left screen corner while using the controller;
PyAutoGUI's corner fail-safe is enabled.

## Project files

- `main.py` — gesture recognition and keyboard controller
- `car.py` — compatibility launcher for the original filename
- `requirements.txt` — Python package dependencies
- `assets/` — optional location for project screenshots or images
