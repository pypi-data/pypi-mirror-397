# hand_mouse

Control your computer with hand/eye tracking using MediaPipe and OpenCV.

Quick example (eye tracking):

```py
from hand_mouse import EyeTracker, move_cursor, click
import pyautogui

et = EyeTracker()
frame, results = et.get_frame()
# see examples/eye_control_demo.py for a runnable demo
```
