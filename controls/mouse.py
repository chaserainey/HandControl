import pyautogui
import time
import numpy as np
from Libresv3.config import ControlConfig

class MouseController:
    def __init__(self):
        self.prev_x, self.prev_y = pyautogui.position()
        self.screen_width, self.screen_height = pyautogui.size()
        self.last_click_time = 0
        self.is_dragging = False
        self.drag_start_time = 0
        self.left_hand_active = False
        self.last_scroll_time = 0

    def move_cursor(self, index_tip, state):
        try:
            x = np.interp(index_tip.x,
                         [ControlConfig.SCREEN_PADDING, 1-ControlConfig.SCREEN_PADDING],
                         [0, self.screen_width])
            y = np.interp(index_tip.y,
                         [ControlConfig.SCREEN_PADDING, 1-ControlConfig.SCREEN_PADDING],
                         [0, self.screen_height])

            if state == "MOVE":
                x = self.prev_x + (x - self.prev_x) * ControlConfig.SMOOTHING_FACTOR
                y = self.prev_y + (y - self.prev_y) * ControlConfig.SMOOTHING_FACTOR
                pyautogui.moveTo(x, y)
            
            elif state == "DRAG":
                if not self.is_dragging:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    self.drag_start_time = time.time()
                pyautogui.dragTo(x, y, button='left', duration=0)
            
            self.prev_x, self.prev_y = x, y
        
        except Exception as e:
            print(f"Movement error: {e}")

    def handle_click(self, state):
        try:
            current_time = time.time()
            
            if state == "LEFT_CLICK" and current_time - self.last_click_time > ControlConfig.CLICK_COOLDOWN:
                pyautogui.click()
                self.last_click_time = current_time
                return "LEFT CLICK"
            
            elif state == "RIGHT_CLICK" and current_time - self.last_click_time > ControlConfig.CLICK_COOLDOWN:
                pyautogui.rightClick()
                self.last_click_time = current_time
                return "RIGHT CLICK"
            
            elif self.is_dragging and state != "DRAG":
                if current_time - self.drag_start_time > ControlConfig.DRAG_RELEASE_TIME:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    return "DRAG END"
            
            return None
        
        except Exception as e:
            print(f"Click error: {e}")
            return None

    def handle_scroll(self, direction):
        try:
            current_time = time.time()
            if current_time - self.last_scroll_time > ControlConfig.SCROLL_COOLDOWN:
                scroll_amount = -ControlConfig.SCROLL_SENSITIVITY if direction == "SCROLL_DOWN" else ControlConfig.SCROLL_SENSITIVITY
                pyautogui.scroll(scroll_amount)
                self.last_scroll_time = current_time
                return f"SCROLL {direction.split('_')[1]}"
            return None
        
        except Exception as e:
            print(f"Scroll error: {e}")
            return None