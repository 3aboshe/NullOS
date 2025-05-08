# --- START OF FILE main.py ---

import pygame
import sys
import settings
from game_state import GameState
from main_menu import MainMenu
from settings_menu import SettingsMenu
# Note: CreditsScreen is managed within GameState, no direct import needed here
import os
import time


def main():
    # Initialization
    print("--- Pygame, Fonts, and Mixer Initialized ---")

    # Font Check
    fonts_ok = True
    # Use the dictionary defined in settings if available
    font_checks = settings.essential_fonts if hasattr(settings, 'essential_fonts') else {
        # Fallback check if essential_fonts dict isn't in settings
        "Terminal": settings.TERMINAL_FONT, "UI": settings.UI_FONT,
        "Text Window": settings.TEXT_WINDOW_FONT, "Pixel": settings.PIXEL_FONT,
        "Menu Title": settings.MENU_FONT, "Menu Option": settings.MENU_OPTION_FONT,
        "Arabic": settings.ARABIC_FONT # Added Arabic Font Check
    }
    for name, font_obj in font_checks.items():
        if not font_obj:
            # Allow Arabic font to be optional if path wasn't found, but warn
            if name == "Arabic" and not os.path.exists(settings.ARABIC_FONT_PATH):
                 print(f"Warning: Optional font '{name}' not found or failed to load. Arabic text might not render correctly.")
            else:
                print(f"FATAL ERROR: Essential font '{name}' failed to load.")
                fonts_ok = False
    if not fonts_ok:
        print("-----------------------------------------------------")
        print("Essential fonts failed to load. Cannot continue.")
        print("-----------------------------------------------------")
        if pygame.get_init(): pygame.quit()
        sys.exit(1)
    else:
        print("Essential fonts verified (or optional fonts noted).")

    # Sound Check
    if not pygame.mixer:
        print("WARNING: Pygame mixer is unavailable. No sound will be played.")
        settings.MUSIC_ENABLED = False
        settings.SFX_ENABLED = False
    else:
        # Check for essential sound files (can add more specific checks if needed)
        if not settings.MUSIC_MAIN_MENU or not settings.MUSIC_GAMEPLAY:
            print("WARNING: Background music file(s) failed to load.")
        if not settings.SFX_DIALOGUE or not settings.SFX_LEVEL_WIN or not settings.SFX_FINISH_GAME:
            print("WARNING: Core sound effect file(s) failed to load.")
        print("Sound system active (individual files may have failed).")

    # Screen Setup
    screen_flags = 0
    if settings.FULLSCREEN_MODE:
        screen_flags |= pygame.FULLSCREEN | pygame.SCALED # Use SCALED for better compatibility
        print(f"Setting screen mode: Fullscreen (target {settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT})")
    else:
        print(f"Setting screen mode: Windowed ({settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT})")

    try:
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), screen_flags)
        pygame.display.set_caption("NullOS - CTF Forensics Challenge")
        actual_width, actual_height = screen.get_size()
        print(f"Actual screen surface size: {actual_width}x{actual_height}")
        if settings.FULLSCREEN_MODE and (
                actual_width != settings.SCREEN_WIDTH or actual_height != settings.SCREEN_HEIGHT):
            print("Note: Screen scaling might be active in fullscreen mode.")
    except pygame.error as e:
        print(f"FATAL ERROR: Failed to set display mode: {e}")
        pygame.quit()
        sys.exit(1)

    # Clipboard Initialization
    clipboard_available = False
    try:
        if hasattr(pygame, 'scrap') and callable(pygame.scrap.init):
            pygame.scrap.init()
            if pygame.scrap.get_init():
                print("Clipboard initialized successfully.")
                clipboard_available = True
            else:
                print("Warning: Clipboard system failed to initialize. Paste function inactive.")
        else:
            print("Warning: pygame.scrap module not available or usable. Paste function inactive.")
    except (pygame.error, NotImplementedError) as e:
        print(f"Warning: Clipboard (scrap) initialization failed: {e}. Paste function inactive.")
    except Exception as e:
        print(f"Warning: Unexpected clipboard initialization error: {e}.")

    # Game Components Initialization
    clock = pygame.time.Clock()
    try:
        main_menu = MainMenu()
        settings_menu = SettingsMenu()
        game_state = GameState() # This now includes credits_screen instance
        settings.GLOBAL_GAME_STATE = game_state # Set global reference if needed by other modules
        game_state.load_background() # Load background early
        print("Initial background loaded.")
        print("Menu and Game state objects created.")
    except Exception as e:
        print(f"FATAL ERROR: Could not initialize game components: {e}")
        pygame.quit(); sys.exit(1)

    # Game Mode Management
    # Use GameState's view mode as the single source of truth for the *application state*
    game_state.current_view_mode = 'MAIN_MENU' # Start GameState in menu mode
    main_menu.menu_active = True # Keep menu flags for their internal logic/drawing checks
    settings_menu.menu_active = False

    game_state_was_saved = False # Track if we have a saved game state to restore
    last_mode = None # Track previous mode to detect changes

    # --- Music Control Functions ---
    def play_music(music_object, source=""):
        """Plays background music if enabled and available."""
        if not pygame.mixer or settings.BGM_CHANNEL == -1: return
        pygame.mixer.Channel(settings.BGM_CHANNEL).stop() # Stop previous music first
        if music_object and settings.MUSIC_ENABLED:
            try:
                # Attempt to get a readable name for logging
                sound_filename = "Unknown"
                # Check if it's a pygame Sound object (has get_length)
                if hasattr(music_object, 'get_length'):
                     # Cannot easily get filename back from Sound object, use source hint
                     sound_filename = f"(from {source})" if source else "(direct Sound object)"
                # Add checks for other potential wrapper types if you use them

                pygame.mixer.Channel(settings.BGM_CHANNEL).play(music_object, loops=-1)
                print(f"Playing BGM: {sound_filename}")
            except pygame.error as e:
                print(f"Error playing BGM: {e}")
            except AttributeError:
                 print(f"Error playing BGM (source: {source}): Invalid sound object type?")
            except Exception as e:
                 print(f"Unexpected error playing BGM (source: {source}): {e}")

        elif not music_object:
            print(f"Could not play BGM (source: {source}): Music object is None.")

    def stop_music():
        """Stops background music if enabled and available."""
        if not pygame.mixer or settings.BGM_CHANNEL == -1: return
        # Check if the channel is actually playing before stopping to avoid redundant logs
        if pygame.mixer.Channel(settings.BGM_CHANNEL).get_busy():
            print("Stopping BGM.")
            pygame.mixer.Channel(settings.BGM_CHANNEL).stop()

    # Play initial menu music
    if pygame.mixer:
        play_music(settings.MUSIC_MAIN_MENU, "Initial Load")

    # Main Loop
    running = True
    print("--- Entering Main Application Loop ---")
    while running:
        try:
            # Calculate delta time (time since last frame in seconds)
            dt = clock.tick(settings.FPS) / 1000.0
            # Prevent excessively large dt if game hangs briefly
            dt = min(dt, 0.1)
        except OverflowError:
            dt = 1 / settings.FPS # Fallback dt
            print("Warning: Clock tick resulted in OverflowError. Using default dt.")

        current_mode = game_state.current_view_mode # Get current mode from GameState

        # --- Detect Mode Change and Trigger Entry Actions ---
        if current_mode != last_mode:
            print(f"Mode changed: {last_mode} -> {current_mode}")
            # Actions to take when *entering* a new mode
            if current_mode == 'CREDITS':
                 if game_state.credits_screen: game_state.credits_screen.show()
                 if pygame.mixer: play_music(settings.MUSIC_MAIN_MENU, "Credits Start")
            elif current_mode == 'DESKTOP': # Assuming 'GAME' state maps to 'DESKTOP' visually mostly
                 if pygame.mixer: play_music(settings.MUSIC_GAMEPLAY, "Game Start/Resume")
            elif current_mode == 'MAIN_MENU':
                 main_menu.menu_active = True
                 settings_menu.hide() # Ensure settings is visually inactive
                 if pygame.mixer: play_music(settings.MUSIC_MAIN_MENU, "Menu Start")
            elif current_mode == 'SETTINGS':
                 main_menu.menu_active = False
                 settings_menu.show() # Activate settings visuals
                 if pygame.mixer: play_music(settings.MUSIC_MAIN_MENU, "Settings Start")
            elif current_mode == 'TRANSITION':
                 stop_music() # Optional: Stop music during transitions
            elif current_mode == 'NULLX_PRESENTATION':
                # Music should likely be game music during NullX
                if pygame.mixer: play_music(settings.MUSIC_GAMEPLAY, "NullX Start")
            # Add other modes if necessary

            last_mode = current_mode # Update last_mode *after* processing the change

        mouse_pos = pygame.mouse.get_pos()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; continue # Exit loop immediately on QUIT

            action_result = None # Stores action string like 'Play', 'Quit', 'Back'

            # Delegate event handling based on the *true* current mode from GameState
            if current_mode == 'MAIN_MENU':
                action_result = main_menu.handle_event(event, mouse_pos)
            elif current_mode == 'SETTINGS':
                action_result = settings_menu.handle_event(event, mouse_pos)
            else:
                # For all other modes (DESKTOP, NULLX_PRESENTATION, CREDITS, TRANSITION, LOADING),
                # let GameState handle the event. GameState will internally check its
                # current_view_mode and delegate further if necessary.
                game_state.handle_event(event, mouse_pos)
                # Check if GameState handling resulted in a mode change back to menu
                if game_state.current_view_mode == 'MAIN_MENU' and current_mode != 'MAIN_MENU':
                     game_state_was_saved = True # Assume ESC from game saves state

            # Process actions returned *specifically* from Menus
            # (GameState actions like Quit are handled internally by posting pygame.QUIT)
            if action_result:
                if action_result == 'Play':
                    if current_mode == 'MAIN_MENU': # Ensure action is from the correct context
                        print("Returning to game..." if game_state_was_saved else "Starting new game...")
                        # Set the desired *initial* state for the game within GameState
                        game_state.current_view_mode = 'DESKTOP' # Default starting point for gameplay

                        if game_state_was_saved:
                            if not game_state.restore_state(): # Attempt restore
                                print("Failed to restore saved state. Starting new game.")
                                game_state.start_first_level() # Start fresh if restore fails
                                game_state_was_saved = False
                        else: # No saved state, start new game
                            game_state.start_first_level() # This might change game_state.current_view_mode again (e.g., to NULLX)
                            game_state_was_saved = False
                        # Let the mode change detection handle music etc. at start of next loop

                elif action_result == 'Language':
                    settings.CURRENT_LANGUAGE = 'ar' if settings.CURRENT_LANGUAGE == 'en' else 'en'
                    print(f"Language changed to {settings.LANGUAGES[settings.CURRENT_LANGUAGE]}")
                    settings.save_settings() # Persist language setting
                    # Menus should re-render automatically in their draw calls based on the new setting

                elif action_result == 'Settings':
                    if current_mode == 'MAIN_MENU':
                        print("Entering Settings Menu...")
                        game_state.current_view_mode = 'SETTINGS' # Change game state mode

                elif action_result == 'Quit': # From Main Menu
                    running = False # Signal main loop to exit

                elif action_result == 'Back': # From Settings Menu
                    if current_mode == 'SETTINGS':
                        print("Returning to Main Menu...")
                        game_state.current_view_mode = 'MAIN_MENU' # Change game state mode


        # --- Music Management (Ensure correct music for current mode) ---
        # This can be slightly simplified by relying more on the mode change detection,
        # but this check handles changes in settings.MUSIC_ENABLED during gameplay.
        if pygame.mixer and settings.BGM_CHANNEL != -1:
            try:
                channel = pygame.mixer.Channel(settings.BGM_CHANNEL)
                is_playing = channel.get_busy()

                # Stop music immediately if disabled
                if not settings.MUSIC_ENABLED and is_playing:
                    stop_music()
                # Starting/changing music is now primarily handled by the mode change detection block

            except pygame.error as e: print(f"Error checking BGM enabled status: {e}")
            except Exception as e: print(f"Unexpected BGM check error: {e}")


        # --- Updates ---
        # GameState update handles updates for all active game components based on its internal mode
        game_state.update(dt)
        # Menus generally don't need per-frame updates unless they have animations

        # --- Drawing ---
        screen.fill(settings.COLOR_BLACK) # Base fill, prevents flickering artifacts

        # 1. Draw the persistent background if available (drawn by main for all modes)
        if game_state.background_img:
            screen.blit(game_state.background_img, (0, 0))
        else:
             # If background failed, ensure a black background anyway
             screen.fill(settings.COLOR_BLACK)

        # 2. Let GameState draw its current view
        #    (desktop icons, taskbar, windows, nullx, credits overlay, transition overlay)
        #    GameState's draw method should NOT draw the background itself.
        game_state.draw(screen)

        # 3. Draw Menus on top *if* they are the active mode according to GameState
        if game_state.current_view_mode == 'MAIN_MENU':
            main_menu.draw(screen) # Draws its own overlay, etc.
        elif game_state.current_view_mode == 'SETTINGS':
            settings_menu.draw(screen) # Draws its own overlay, etc.

        # Flip the display buffer to show the newly drawn frame
        pygame.display.flip()

    # Cleanup
    print("--- Exiting Application ---")
    if pygame.mixer: pygame.mixer.quit() # Quit mixer cleanly
    pygame.quit() # Uninitialize all pygame modules
    print("Pygame quit successfully.")
    sys.exit(0) # Exit the program


if __name__ == "__main__":
    # --- Version and Resource Checks (Keep these as they are essential) ---
    print(f"--- Starting CTF OS Simulation v{settings.VERSION if hasattr(settings, 'VERSION') else 'N/A'} ---")

    if not os.path.isdir(settings.RESOURCE_DIR):
        print(f"\n!!! FATAL ERROR !!!")
        print(f"Resource directory not found at: '{settings.RESOURCE_DIR}'")
        print("Please ensure the 'resources' folder exists in the same directory as the script.")
        sys.exit(1)
    else:
        print(f"Resource directory found: {settings.RESOURCE_DIR}")

    essential_files = {
        "Background": settings.BACKGROUND_IMG_PATH,
        "Terminal Font File": settings.FONT_PATH, # Font paths are checked at load time now
        "Pixel Font File": settings.PIXEL_FONT_PATH,
        "Menu Font File": settings.MENU_FONT_PATH,
        "Arabic Font File": settings.ARABIC_FONT_PATH, # Checked at load time too
        "Text Icon": settings.TXT_ICON_PATH, "PDF Icon": settings.PDF_ICON_PATH,
        "Terminal Icon": settings.TERM_ICON_PATH, "File Analysis Icon": settings.FILANALY_ICON_PATH,
        "Executable Icon": settings.EXE_ICON_PATH, "ZIP Icon": settings.ZIP_ICON_PATH,
        "PNG Icon": settings.PNG_ICON_PATH, "Level 1/4 Image": settings.CLICKABLE_IMAGE_PATH,
        "Level 5 Secret Image": settings.SECRET_IMG_LVL5_PATH,
        # Add all required NullX images explicitly
        "NullX Explaining": settings.get_nullx_path("NullX_explaining.png"),
        "NullX Speaking": settings.get_nullx_path("NullX_speaking.png"),
        "NullX Happy": settings.get_nullx_path("NullX_Happy.png"),
        "NullX Wondering": settings.get_nullx_path("NullX_Wondering.png"),
        "NullX Cheering": settings.get_nullx_path("NullX_Cheering.png"),
        "NullX Sad": settings.get_nullx_path("NullX_Sad.png"),
        "NullX Angry": settings.get_nullx_path("NullX_angry.png"),
        "NullX Normal": settings.get_nullx_path("NullX_normal.png"),
        # Add Sounds
        "Dialogue SFX": settings.SOUND_DIA,
        "Level Win SFX": settings.SOUND_LEVEL_WIN, "Finish Game SFX": settings.SOUND_FINISH_GAME,
        "Main Menu BGM": settings.MUSIC_BM1, "Gameplay BGM": settings.MUSIC_BM2,
    }

    missing, unreadable = [], []
    for name, f_path in essential_files.items():
        # Skip font paths here, as they are checked during font loading
        if name.endswith("Font File"): continue
        # Skip checks for None paths (e.g., if a sound is optional and failed to load)
        if f_path is None:
            # print(f"Info: Asset '{name}' path is None (optional or load failure?). Skipping check.")
            continue

        if not os.path.isfile(f_path):
            missing.append(f"{name} ('{os.path.basename(f_path)}')")
        elif not os.access(f_path, os.R_OK): # Check read permissions
            unreadable.append(f"{name} ('{os.path.basename(f_path)}')")

    if missing or unreadable:
        print("\n---------------- !!! FATAL ERROR !!! -----------------")
        if missing: print("  Missing Essential Asset Files/Paths:"); [print(f"    - {item}") for item in missing]
        if unreadable: print("\n  Unreadable Asset Files (Check Permissions):"); [print(f"    - {item}") for item in unreadable]
        print("-----------------------------------------------------\n")
        sys.exit(1)
    else:
        print("Essential non-font asset files checked successfully.")

    # Start the main game function
    main()

# --- END OF FILE main.py ---