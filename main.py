"""
MIT License

Copyright (c) 2025 Chase Rainey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import cv2
import mediapipe as mp
import time
from Libresv3.config import VisualConfig, ControlConfig
from Libresv3.controls.mouse import MouseController
from Libresv3.controls.shortcuts import ShortcutManager
from Libresv3.controls.tracker import HandTracker

# Configure logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

def Libres():
    tracker = None
    cap = None
    try:
        tracker = HandTracker()
        mouse = MouseController()
        shortcuts = ShortcutManager()
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError("Could not open video capture")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands

        quit_start_time = None
        last_frame_time = time.time()

        while cap.isOpened():
            try:
                success, image = cap.read()
                if not success:
                    continue

                fps = 1 / (time.time() - last_frame_time)
                last_frame_time = time.time()
                
                image = cv2.flip(image, 1)
                height, width = image.shape[:2]
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Draw UI elements
                corner_size = int(width * ControlConfig.NAV_CORNER_SIZE)
                cv2.rectangle(image, (0, 0), (corner_size, corner_size), 
                            VisualConfig.NAV_COLOR, -1)
                cv2.rectangle(image, (width-corner_size, 0), (width, corner_size), 
                            VisualConfig.NAV_COLOR, -1)

                results = tracker.hands.process(rgb_image)
                action = None
                quit_program = False

                if results.multi_hand_landmarks:
                    overlay = image.copy()
                    for hand_landmarks, handedness in zip(
                            results.multi_hand_landmarks,
                            results.multi_handedness
                    ):
                        handedness = handedness.classification[0].label
                        state = tracker.get_hand_state(hand_landmarks, handedness)

                        if handedness == "Right":
                            if state in ["MOVE", "DRAG"]:
                                mouse.move_cursor(hand_landmarks.landmark[8], state)
                            action = mouse.handle_click(state)
                            
                            # Visual feedback
                            if state == "DRAG":
                                cv2.putText(image, "DRAGGING", (width//2-50, 30),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, VisualConfig.DRAG_COLOR, 2)
                                x, y = int(hand_landmarks.landmark[8].x * width), int(hand_landmarks.landmark[8].y * height)
                                cv2.circle(image, (x, y), 20, VisualConfig.DRAG_COLOR, 2)
                        
                        else:  # Left hand
                            mouse.left_hand_active = True
                            
                            if state == "PEACE":
                                if quit_start_time is None:
                                    quit_start_time = time.time()
                                elif time.time() - quit_start_time >= ControlConfig.QUIT_GESTURE_TIME:
                                    quit_program = True
                                    action = "QUITTING..."
                                else:
                                    action = f"QUIT IN {2-int(time.time()-quit_start_time)}s"
                            else:
                                quit_start_time = None
                                if state.startswith("SCROLL"):
                                    action = mouse.handle_scroll(state)
                                else:
                                    action = shortcuts.execute(state, time.time())

                            # Draw corner progress
                            if shortcuts.active_corner:
                                elapsed = time.time() - shortcuts.corner_hold_start
                                progress = min(1.0, elapsed/ControlConfig.NAV_HOLD_DURATION)
                                center = (corner_size//2, corner_size//2) if shortcuts.active_corner == "TOP_LEFT_HOLD" else (width-corner_size//2, corner_size//2)
                                cv2.circle(image, center, int(progress*(corner_size//2)), (255,255,255), 2)

                        # Draw landmarks
                        mp_drawing.draw_landmarks(
                            overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_utils.DrawingSpec(
                                color=VisualConfig.LANDMARK_COLOR,
                                thickness=VisualConfig.LANDMARK_RADIUS),
                            mp.solutions.drawing_utils.DrawingSpec(
                                color=VisualConfig.CONNECTION_COLOR,
                                thickness=VisualConfig.CONNECTION_THICKNESS))

                    cv2.addWeighted(overlay, VisualConfig.LANDMARK_OPACITY,
                                  image, 1-VisualConfig.LANDMARK_OPACITY, 0, image)

                    # Quit progress
                    if quit_start_time is not None:
                        progress = min(1.0, (time.time()-quit_start_time)/ControlConfig.QUIT_GESTURE_TIME)
                        cv2.rectangle(image, (10, height-30), 
                                    (10 + int(150*progress), height-10), 
                                    VisualConfig.QUIT_COLOR, -1)

                else:
                    mouse.left_hand_active = False
                    quit_start_time = None

                # Display info
                if action:
                    text_color = (VisualConfig.QUIT_COLOR if "QUIT" in action 
                                else VisualConfig.TEXT_COLOR)
                    cv2.putText(image, action, (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
                
                cv2.putText(image, f"FPS: {int(fps)}", (width-100, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, VisualConfig.TEXT_COLOR, 2)

                cv2.imshow('LibrasV3: Hand-Controlled Mouse with Browser Control', image)
                if (cv2.waitKey(1) & 0xFF == ord(ControlConfig.QUIT_KEY)) or quit_program:
                    break

            except Exception as e:
                print(f"Frame processing error: {e}")
                continue

    except Exception as e:
        print(f"Initialization error: {e}")
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        if tracker is not None:
            del tracker  # Ensures proper cleanup

if __name__ == "__main__":
    Libres()