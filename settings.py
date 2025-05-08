# --- START OF FILE settings.py ---

# settings.py
import pygame
import os
# --- Language Settings ---
LANGUAGES = {
    'en': 'English',
    'ar': 'العربية'  # Arabic
}
CURRENT_LANGUAGE = 'en'  # Default to English

# --- Pygame Init (needed for display/font info early) ---
# Initialize core pygame modules
pygame.init()
# Initialize font system FIRST
pygame.font.init()
# Initialize sound mixer with reasonable defaults. Add error handling.
# Add near the top with other settings

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    # Optionally set reserved channels if needed later, but auto is usually fine
    print("Sound Mixer initialized successfully.")
except pygame.error as e:
    print(f"WARNING: Sound Mixer failed to initialize: {e}")
    # Continue without sound if mixer fails
    pygame.mixer = None # Set mixer to None to disable sound features gracefully

# --- Screen ---
try:
    # Attempt to get the native screen resolution for fullscreen mode
    display_info = pygame.display.Info()
    SCREEN_WIDTH = display_info.current_w
    SCREEN_HEIGHT = display_info.current_h
    print(f"Detected screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except pygame.error as e:
    # Fallback if display info is unavailable (e.g., some headless environments)
    print(f"Warning: Could not get display info ({e}). Using default 1280x720.")
    SCREEN_WIDTH = 1280 # A common HD resolution as a fallback
    SCREEN_HEIGHT = 720

FPS = 60 # Increase FPS for smoother animations/UI
FULLSCREEN_MODE = True # User preference for fullscreen or windowed

# --- Base Directory ---
# Find the directory where this script (settings.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path to the 'resources' folder relative to the script location
RESOURCE_DIR = os.path.join(BASE_DIR, "resources")
print(f"Base directory detected: {BASE_DIR}")
print(f"Resource directory set to: {RESOURCE_DIR}")

# Function to safely join paths relative to the RESOURCE_DIR
def get_path(relative_path):
    """Constructs an absolute path to a resource file."""
    if not relative_path: return None
    # Use os.path.join for cross-platform compatibility
    abs_path = os.path.join(RESOURCE_DIR, relative_path)
    return abs_path

# --- Helper for NullX image paths ---
def get_nullx_path(image_filename):
     """Constructs the full path for a NullX image within resources."""
     if not image_filename: return None
     return os.path.join(RESOURCE_DIR, image_filename) # NullX images are directly in resources

# --- Asset Paths (Images) ---
CLICKABLE_IMAGE_PATH = get_path("image.jpg")        # Default image for levels 1 & 4
BACKGROUND_IMG_PATH = get_path("background.png")     # Desktop background
SECRET_IMG_LVL5_PATH = get_path("secret.png")       # Special image for level 5
TXT_ICON_PATH = get_path("txticon.png")             # Icon for text files
PDF_ICON_PATH = get_path("pdficon.png")             # Icon for PDF files
TERM_ICON_PATH = get_path("termicon.png")            # Icon for the terminal application
FILANALY_ICON_PATH = get_path("filanaly.png")        # Icon for the simulated analysis tool
EXE_ICON_PATH = get_path("exeicon.png")             # Icon for generic executables
ZIP_ICON_PATH = get_path("zipicon.png")             # Icon for zip archives
PNG_ICON_PATH = get_path("pngicon.png")             # Icon for PNG images

# --- Asset Paths (Fonts) ---
# FONT_PATH = get_path("cour.ttf")            # Main terminal/text window font
# PIXEL_FONT_PATH = get_path("Pixel_Font.ttf")    # Font for NullX presenter dialogue & Menu options
# MENU_FONT_PATH = get_path("Daydream.ttf")      # Font for the Main Menu Title
# LANGUAGE = "en"
# --- Asset Paths (Fonts) ---
FONT_PATH = get_path("cour.ttf")
PIXEL_FONT_PATH = get_path("Pixel_Font.ttf")
MENU_FONT_PATH = get_path("Daydream.ttf")
ARABIC_FONT_PATH = os.path.join("resources/Amiri-Regular.ttf")
print("Loading font from:", ARABIC_FONT_PATH)

font = pygame.font.Font(ARABIC_FONT_PATH, 36)


print(f"Final Arabic font path: {ARABIC_FONT_PATH}")
print(f"Path exists: {os.path.exists(ARABIC_FONT_PATH)}")

try:
    ARABIC_FONT = pygame.font.Font(ARABIC_FONT_PATH, 16)
    print("Arabic font loaded successfully!")
except Exception as e:
    print(f"Arabic font loading failed: {str(e)}")
    ARABIC_FONT = pygame.font.SysFont("arial", 16)
# --- Font Loading Calls ---
try:
    # ... existing font loading code ...

    #  Add Arabic font loading with better error handling
    try:
        if os.path.exists(ARABIC_FONT_PATH):
            ARABIC_FONT = ARABIC_FONT = pygame.font.Font(ARABIC_FONT_PATH, 16)
            print(f"Successfully loaded Arabic font from: {ARABIC_FONT_PATH}")
        else:
            raise FileNotFoundError(f"Arabic font not found at: {ARABIC_FONT_PATH}")
    except Exception as e:
        print(f"Error loading Arabic font: {str(e)}")
        print("Falling back to system Arabic font")
        ARABIC_FONT = pygame.font.SysFont("arial", 16)  # Fallback

except Exception as e:
    print(f"FATAL: Unexpected error during font initialization: {e}")
    if pygame.get_init(): pygame.quit()
    import sys
    sys.exit(1)

# --- Asset Paths (Sounds) ---
# SOUND_STARTUP = get_path("startup.wav")       # Removed
SOUND_DIA = get_path("dia.wav")             # Dialogue sound for NullX
SOUND_LEVEL_WIN = get_path("level_win.wav")   # Sound played upon level completion
SOUND_FINISH_GAME = get_path("finish_game.wav") # Sound played upon final level completion
MUSIC_BM1 = get_path("bm1.wav")             # Background music for the main menu
MUSIC_BM2 = get_path("bm2.wav")             # Background music for the main game

# --- Global Game Settings ---
MUSIC_ENABLED = True
SFX_ENABLED = True
# Placeholder for global game state reference - needs proper setup if used this way
GLOBAL_GAME_STATE = None

# --- Icon Settings ---
ICON_SIZE = (48, 48)            # Standard pixel dimensions for desktop icons
ICON_TEXT_OFFSET_Y = 8          # Vertical space between icon and its text label
ICON_GRID_PADDING_X = ICON_SIZE[0] + 65 # Horizontal spacing between icons on the grid
ICON_GRID_PADDING_Y = ICON_SIZE[1] + 55 # Vertical spacing between icons on the grid

# --- Popup Window Settings ---
# Default dimensions for different types of pop-up windows
POPUP_WINDOW_SIZE = (400, 300)        # Generic/Image window size
TEXT_POPUP_WINDOW_SIZE = (450, 350)   # Text viewer window size
TERMINAL_WINDOW_SIZE = (750, 550)     # Terminal window size
PASSWORD_WINDOW_SIZE = (350, 150)     # Password prompt window size
POPUP_TITLE_BAR_HEIGHT = 20           # Height of the title bar on popups
# Semi-transparent background for popups (R, G, B, Alpha)
POPUP_BG_COLOR = (50, 50, 50, 230)
# Slightly darker color for the title bar background
POPUP_TITLE_COLOR = (80, 80, 80, 240)
POPUP_BUTTON_RADIUS = 7               # Radius of the circular close button
POPUP_BUTTON_Y_OFFSET = POPUP_TITLE_BAR_HEIGHT // 2 # Vertical center alignment for buttons
POPUP_BUTTON_X_START = 15             # Horizontal starting position for buttons
POPUP_BUTTON_SPACING = 20             # Space between multiple buttons (if added later)
COLOR_CLOSE_BUTTON = (255, 95, 86)    # Color for the 'close window' button

# --- Colors (RGB tuples) ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_TASKBAR = (192, 192, 192)       # Color of the bottom taskbar
COLOR_TERMINAL_BG = (20, 20, 20)        # Background color of the terminal content area
COLOR_TERMINAL_TEXT = (0, 255, 0)       # Default text color in the terminal
COLOR_ERROR = (255, 100, 100)       # Color for error messages in terminal
COLOR_SUCCESS = (100, 255, 100)     # Color for success messages in terminal
COLOR_FILE_TEXT = COLOR_WHITE           # Color of icon labels on the desktop
COLOR_HINT_TEXT = (200, 200, 255)     # Color for hint messages in terminal/notes
COLOR_FLAG_CLICKABLE = (100, 180, 255)  # Color for clickable flag text in terminal
COLOR_B64_CLICKABLE = (255, 165, 0)   # Color for clickable Base64 text in terminal
COLOR_PASSWORD_INPUT_BG = (30, 30, 30)  # Background of password input field
COLOR_PASSWORD_INPUT_BORDER = (150, 150, 150) # Border color of password input
COLOR_PASSWORD_BUTTON = (60, 179, 113) # Color of the 'Extract' button
COLOR_PASSWORD_BUTTON_HOVER = (46, 139, 87) # Hover color for 'Extract'
COLOR_PASSWORD_BUTTON_TEXT = COLOR_WHITE  # Text color on 'Extract' button
COLOR_CANCEL_BUTTON = (180, 180, 180)   # Color of the 'Cancel' button
COLOR_CANCEL_BUTTON_HOVER = (150, 150, 150)# Hover color for 'Cancel'
COLOR_CANCEL_BUTTON_TEXT = COLOR_BLACK   # Text color on 'Cancel' button
# New Menu Colors
MENU_TEXT_COLOR = (240, 240, 240)
MENU_TEXT_HOVER_COLOR = (100, 200, 255)
SETTINGS_TEXT_COLOR = (220, 220, 220)
SETTINGS_VALUE_COLOR = (255, 255, 150)
SETTINGS_BUTTON_COLOR = (80, 80, 150)
SETTINGS_BUTTON_HOVER_COLOR = (100, 100, 180)
MENU_OVERLAY_COLOR = (0, 0, 0, 180) # Semi-transparent black for menu background

# --- Dimensions ---
TASKBAR_HEIGHT = 30                  # Pixel height of the bottom taskbar
# Usable desktop area height (screen height minus taskbar)
DESKTOP_HEIGHT = SCREEN_HEIGHT - TASKBAR_HEIGHT

# --- Terminal ---
CURSOR_BLINK_RATE = 0.5              # Seconds between cursor blink state changes
TERMINAL_MAX_HISTORY = 50            # Max number of commands stored in history

# --- Sound Channel Allocation ---
if pygame.mixer: # Only allocate if mixer exists
    BGM_CHANNEL = 0     # Channel reserved for background music
    DIALOGUE_CHANNEL = 1  # Channel reserved for NullX dialogue
    UI_CHANNEL = 2      # Channel for UI sounds (level win, etc.)
else:
    # Assign dummy values if mixer failed
    BGM_CHANNEL, DIALOGUE_CHANNEL, UI_CHANNEL = -1, -1, -1

# --- Load Fonts ---
# Pre-load fonts to catch errors early and improve performance
TERMINAL_FONT = None
UI_FONT = None
TEXT_WINDOW_FONT = None
PIXEL_FONT = None
MENU_FONT = None # Title font
MENU_OPTION_FONT = None # Separate variable for Pixel font for options

# Generic Font Loading Helper Function
def load_font(path, size, name="Font"):
    """Loads a font file or uses a system fallback."""
    loaded_font = None
    font_source = "File" # Track if loaded from file or system
    if path and os.path.exists(path):
        try:
            loaded_font = pygame.font.Font(path, size)
            if loaded_font:
                print(f"Loaded {name} from file: {os.path.basename(path)} @ size {size}")
            else:
                print(f"Warning: {name} loaded as None from existing path '{os.path.basename(path)}'.")
                raise pygame.error("Font file loaded as None")
        except (IOError, pygame.error, TypeError, FileNotFoundError) as e:
            print(f"Warning: {name} file '{os.path.basename(path or '')}' failed ({e}). Trying system fallback.")
            loaded_font = None
    else:
        if path: print(f"Info: {name} file '{os.path.basename(path)}' not found. Trying system fallback.")
        else: print(f"Info: No path specified for {name}. Trying system fallback.")

    # System fallback logic
    if not loaded_font:
        font_source = "System" # Mark as system font
        try:
            # Default list, overridden by specific needs
            sys_fonts = ["sans", "arial", "helvetica"]
            if name == "Terminal" or name == "Text Window":
                sys_fonts = ["consolas", "dejavusansmono", "liberationmono", "monaco", "monospace"]
            elif name == "Pixel" or name == "Menu Option": # Use specific fonts for Pixel/Menu Options if needed
                 # Pixel font fallback is tricky, might need specific choices or just default
                 sys_fonts = ["fixed", "courier", "monospace"] # Trying some fixed-width basics
                 print(f"Note: System fallback for '{name}'. Appearance may vary.")
            elif name == "Menu Title":
                sys_fonts = ["impact", "candara", "calibri", "sans-serif", "verdana", "sans"] # Different choices for title

            loaded_font = pygame.font.SysFont(sys_fonts, size)
            if loaded_font:
                font_display_name = loaded_font.get_name() if hasattr(loaded_font, 'get_name') else 'System Font'
                print(f"Using system font for {name}: {font_display_name} @ size {size}")
            else:
                 print(f"FATAL: No suitable system font found for {name}.")
        except Exception as e:
             print(f"FATAL: Error loading system font for {name}: {e}")
             loaded_font = None

    return loaded_font


# --- Font Loading Calls ---
try:
    TERMINAL_FONT = load_font(FONT_PATH, 16, "Terminal")

    # Load UI font (critical for window elements) - prioritize system default
    try:
        ui_sys_fonts = ["segoeui", "ubuntu", "calibri", "sans-serif", "sans"]
        UI_FONT = pygame.font.SysFont(ui_sys_fonts, 14)
        if UI_FONT:
            ui_font_name = UI_FONT.get_name() if hasattr(UI_FONT, 'get_name') else 'System UI Font'
            print(f"Loaded UI font: {ui_font_name} @ size 14")
        else:
            print("FATAL: Could not load essential system UI Font.")
            raise RuntimeError("Failed to load essential UI font.")
    except Exception as e:
        print(f"FATAL: Error loading system UI font: {e}")
        UI_FONT = None

    TEXT_WINDOW_FONT = TERMINAL_FONT # Use same font as terminal for consistency
    PIXEL_FONT = load_font(PIXEL_FONT_PATH, 14, "Pixel") # For NullX dialogue
    MENU_FONT = load_font(MENU_FONT_PATH, 72, "Menu Title") # Main menu title
    MENU_OPTION_FONT = load_font(PIXEL_FONT_PATH, 30, "Menu Option") # Main menu options (Pixel font, larger size)

    #  Arabic font loading section
    # Add this to your settings.py

    # Central Check for Essential Fonts AFTER loading attempts
    essential_fonts = {
        "Terminal": TERMINAL_FONT,
        "UI": UI_FONT,
        #  Arabic font not marked as essential since it's RTL specific
        "Text Window": TEXT_WINDOW_FONT,
        "Pixel": PIXEL_FONT,
        "Menu Title": MENU_FONT,
        "Menu Option": MENU_OPTION_FONT
    }
    if not all(essential_fonts.values()):
        missing = [name for name, font in essential_fonts.items() if not font]
        print(f"FATAL ERROR: Essential fonts failed to load: {', '.join(missing)}")
        raise RuntimeError("Essential fonts failed to load.")

except Exception as e:
    print(f"FATAL: Unexpected error during font initialization phase: {e}")
    if pygame.get_init(): pygame.quit() # Try to quit pygame if initialized
    import sys
    sys.exit(1)

# --- Load Sounds (Only if Mixer Initialized) ---
SFX_DIALOGUE = None
SFX_LEVEL_WIN = None
SFX_FINISH_GAME = None
MUSIC_MAIN_MENU = None
MUSIC_GAMEPLAY = None
SFX_STARTUP = None # Ensure this is defined as None

if pygame.mixer:
    def load_sound(path, name="Sound"):
        """Loads a sound file. Returns Sound object or None."""
        if not path or not os.path.exists(path):
            print(f"ERROR: Sound file not found: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(path)
            print(f"Loaded {name}: {os.path.basename(path)}")
            return sound
        except pygame.error as e:
            print(f"ERROR loading {name} '{os.path.basename(path)}': {e}")
            return None
    # Note: SFX_STARTUP is intentionally NOT loaded
    SFX_DIALOGUE = load_sound(SOUND_DIA, "Dialogue SFX")
    SFX_LEVEL_WIN = load_sound(SOUND_LEVEL_WIN, "Level Win SFX")
    SFX_FINISH_GAME = load_sound(SOUND_FINISH_GAME, "Finish Game SFX")
    MUSIC_MAIN_MENU = load_sound(MUSIC_BM1, "Main Menu BGM")
    MUSIC_GAMEPLAY = load_sound(MUSIC_BM2, "Gameplay BGM")

# --- Regex ---
import re
# Regex to find typical flag formats (adjust if your format differs)
FLAG_REGEX = re.compile(r"(FLAG\{[A-Za-z0-9_@!?-]*\})") # Slightly broader chars allowed
# Regex to find likely Base64 strings (can be tuned)
B64_LIKE_REGEX = re.compile(r"([A-Za-z0-9+/]{20,}[=]{0,2})") # >= 20 chars, 0-2 '=' pads

# --- Optional Version Info ---
VERSION = "2.1.1" # Update version number

# In settings.py
def save_settings():
    with open('config.ini', 'w') as f:
        f.write(f"[Settings]\nlanguage={CURRENT_LANGUAGE}\n")

def load_settings():
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = config.get('Settings', 'language', fallback='en')
    except:
        CURRENT_LANGUAGE = 'en'

# Call load_settings() when the game starts
# Temporary test code - remove after verification
if __name__ == "__main__":
    print("\n--- Font Verification ---")
    print(f"Arabic font path: {ARABIC_FONT_PATH}")
    print(f"Arabic font exists: {os.path.exists(ARABIC_FONT_PATH)}")
    print(f"Arabic font loaded: {ARABIC_FONT is not None}")

# --- End of File settings.py ---