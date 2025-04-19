import pyautogui
import time
from Libresv3.config import ControlConfig

class ShortcutManager:
    def __init__(self):
        self.last_shortcut_time = 0
        self.space_pressed = False
        self.shift_pressed = False
        self.corner_hold_start = None
        self.active_corner = None

    def execute(self, state, current_time):
        # Handle corner navigation
        if state in ("TOP_LEFT_HOLD", "TOP_RIGHT_HOLD"):
            if self.active_corner != state:
                self.active_corner = state
                self.corner_hold_start = current_time
            elif current_time - self.corner_hold_start >= ControlConfig.NAV_HOLD_DURATION:
                if state == "TOP_LEFT_HOLD":
                    pyautogui.hotkey('alt', 'left')
                    return "PAGE BACK"
                else:
                    pyautogui.hotkey('alt', 'right')
                    return "PAGE FORWARD"
            else:
                return f"HOLD {state.split('_')[1]} CORNER"
        
        # Existing shortcuts
        elif state == "THUMB_OUT_LEFT":
            pyautogui.press('space')
            return "SPACE"
        
        elif state == "PINKY_OUT_LEFT":
            if not self.shift_pressed:
                pyautogui.keyDown('shift')
                self.shift_pressed = True
            else:
                pyautogui.keyUp('shift')
                self.shift_pressed = False
            return "SHIFT " + ("ON" if self.shift_pressed else "OFF")
        
        return None