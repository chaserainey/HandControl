class VisualConfig:
    """Visual configuration settings"""
    LANDMARK_COLOR = (0, 255, 0)  # Green
    LANDMARK_RADIUS = 2
    CONNECTION_COLOR = (255, 255, 255)  # White
    CONNECTION_THICKNESS = 1
    LANDMARK_OPACITY = 0.5
    
    # UI Colors
    TEXT_COLOR = (255, 255, 255)
    QUIT_COLOR = (0, 0, 255)
    LEFT_CLICK_COLOR = (0, 255, 0)  # Green
    RIGHT_CLICK_COLOR = (0, 0, 255)  # Red
    DRAG_COLOR = (0, 255, 255)      # Yellow
    SCROLL_COLOR = (255, 0, 255)    # Purple
    NAV_COLOR = (200, 200, 0)       # Yellow for navigation

class ControlConfig:
    """Control configuration settings"""
    # Timing
    CLICK_COOLDOWN = 0.3
    DRAG_RELEASE_TIME = 0.5
    SCROLL_COOLDOWN = 0.1
    QUIT_GESTURE_TIME = 2.0
    NAV_HOLD_DURATION = 1.5
    
    # Thresholds
    CLICK_MOVEMENT_THRESHOLD = 0.05  # Movement required for click (1 inch)
    PINCH_THRESHOLD = 0.04           # For OK gesture
    SCROLL_ACTIVATION_ANGLE = 45     # Degrees for scroll detection
    SCROLL_SENSITIVITY = 8          # Scroll speed
    SCROLL_PALM_ANGLE = 30           # Minimum palm tilt to activate

    # Screen
    SCREEN_PADDING = 0.1
    SMOOTHING_FACTOR = 0.8
    NAV_CORNER_SIZE = 0.22            # 20% of screen width/height
    
    # Keyboard
    QUIT_KEY = 'v' # Key to quit the program
    
    # Shortcuts
    SHORTCUT_MAP = {
        "THUMB_OUT_LEFT": "space",
        "PINKY_OUT_LEFT": "shift"
    }

def validate_configs():
    """Validate configuration parameters"""
    assert 0 < ControlConfig.PINCH_THRESHOLD < 1, "PINCH_THRESHOLD must be between 0 and 1"
    assert 0 < ControlConfig.SCROLL_ACTIVATION_ANGLE < 90, "SCROLL_ACTIVATION_ANGLE must be between 0-90 degrees"
    print("All configurations are valid!")

if __name__ == "__main__":
    validate_configs()