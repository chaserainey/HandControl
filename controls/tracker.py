from Libresv3.config import ControlConfig
import mediapipe as mp
import math

class HandTracker:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        self.prev_index_pos = None

    def is_hand_open(self, landmarks):
        """Check if all fingers are extended"""
        return all(landmarks.landmark[tip].y < landmarks.landmark[tip-2].y 
                 for tip in [8, 12, 16, 20])

    def is_palm_down(self, landmarks):
        """Check if palm is facing downward"""
        return landmarks.landmark[0].y > landmarks.landmark[9].y

    def get_hand_state(self, landmarks, handedness):
        try:
            wrist = landmarks.landmark[0]
            index_tip = landmarks.landmark[8]
            
            # Right hand controls
            if handedness == "Right":
                current_pos = (index_tip.x, index_tip.y)
                
                # Click detection
                if self.prev_index_pos:
                    movement = math.sqrt((current_pos[0]-self.prev_index_pos[0])**2 + 
                                       (current_pos[1]-self.prev_index_pos[1])**2)
                    
                    # Left click
                    if (movement > ControlConfig.CLICK_MOVEMENT_THRESHOLD and
                        current_pos[0] > self.prev_index_pos[0]):
                        self.prev_index_pos = None
                        return "LEFT_CLICK"
                    
                    # Right click
                    if (landmarks.landmark[12].y < landmarks.landmark[10].y and  # Middle extended
                        movement > ControlConfig.CLICK_MOVEMENT_THRESHOLD and
                        current_pos[0] > self.prev_index_pos[0]):
                        self.prev_index_pos = None
                        return "RIGHT_CLICK"
                
                self.prev_index_pos = current_pos
                
                # Drag (OK gesture)
                thumb_tip = landmarks.landmark[4]
                pinch_dist = math.sqrt((thumb_tip.x-index_tip.x)**2 + (thumb_tip.y-index_tip.y)**2)
                if (pinch_dist < ControlConfig.PINCH_THRESHOLD and
                    landmarks.landmark[12].y > landmarks.landmark[10].y and  # Middle not extended
                    landmarks.landmark[16].y > landmarks.landmark[14].y and  # Ring not extended
                    landmarks.landmark[20].y > landmarks.landmark[18].y):    # Pinky not extended
                    return "DRAG"
                
                return "MOVE" if self.is_hand_open(landmarks) else "CLOSED"
            
            # Left hand controls
            else:
                # Scroll detection
                if self.is_palm_down(landmarks):
                    angle = math.degrees(math.atan2(
                        wrist.y - landmarks.landmark[9].y,
                        wrist.x - landmarks.landmark[9].x
                    ))
                    if abs(angle) > ControlConfig.SCROLL_ACTIVATION_ANGLE:
                        return "SCROLL_DOWN" if angle > 0 else "SCROLL_UP"
                
                # Navigation corners
                if all(landmarks.landmark[tip].y > landmarks.landmark[tip-2].y + 0.05
                      for tip in [8, 12, 16, 20]):  # Closed fist
                    if wrist.x < ControlConfig.NAV_CORNER_SIZE and wrist.y < ControlConfig.NAV_CORNER_SIZE:
                        return "TOP_LEFT_HOLD"
                    elif wrist.x > 1 - ControlConfig.NAV_CORNER_SIZE and wrist.y < ControlConfig.NAV_CORNER_SIZE:
                        return "TOP_RIGHT_HOLD"
                
                # Shortcuts
                if (landmarks.landmark[4].x < landmarks.landmark[3].x and  # Thumb out
                    landmarks.landmark[8].y > landmarks.landmark[6].y):    # Index not extended
                    return "THUMB_OUT_LEFT"
                
                if (landmarks.landmark[20].y < landmarks.landmark[18].y and  # Pinky extended
                    landmarks.landmark[8].y > landmarks.landmark[6].y):      # Index not extended
                    return "PINKY_OUT_LEFT"
                
                # Peace gesture
                if (landmarks.landmark[8].y < landmarks.landmark[6].y and  # Index extended
                    landmarks.landmark[12].y < landmarks.landmark[10].y and  # Middle extended
                    landmarks.landmark[16].y > landmarks.landmark[14].y and  # Ring not extended
                    landmarks.landmark[20].y > landmarks.landmark[18].y):    # Pinky not extended
                    return "PEACE"
                
                return "OTHER_LEFT"
        
        except Exception as e:
            print(f"Tracking error: {e}")
            return "ERROR"

    def __del__(self):
        if hasattr(self, 'hands'):
            self.hands.close()