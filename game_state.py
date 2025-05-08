# --- START OF FILE game_state.py ---

import pygame
import os
import time
import settings # Import settings for sounds, colors, etc.
import level_manager
from terminal import Terminal
from image_window import ImageWindow
from text_window import TextWindow
from password_window import PasswordWindow
from nullx_presenter import NullXPresenter # Import NullX
from credits_screen import CreditsScreen # Import CreditsScreen
import base64
import binascii
import shlex # For robust command line parsing

class GameState:
    def __init__(self):
        """Initializes the core game state, including windows and level tracking."""
        # Core game components (windows, character presenter)
        self.active_terminal = Terminal()
        self.image_window = ImageWindow()
        self.text_window = TextWindow()
        self.password_window = PasswordWindow(self) # Pass self reference for callback
        self.nullx_presenter = NullXPresenter() # Handles NullX dialogue/presentation
        self.credits_screen = CreditsScreen()   # Handles the end credits display

        # Level and view state management
        self.current_level_id = 0 # 0 typically means not started or intro
        # Game View Modes: determines what is active and how input/drawing is handled
        # 'LOADING': Initial state before anything interactive appears
        # 'NULLX_PRESENTATION': NullX dialogue is showing
        # 'DESKTOP': Main OS simulation view with icons and popups
        # 'TRANSITION': Fullscreen message overlay between levels
        # 'CREDITS': Scrolling end credits screen
        self.current_view_mode = 'LOADING' # Start in loading state
        self.game_started = False # Flag to track if the game has begun after the main menu

        # Asset loading and transition related flags/data
        self.pending_level_asset_load = False # True if NullX is showing before assets are loaded
        self.transition_info = None # Stores data for level transitions (message, timing)

        # Desktop elements
        self.background_img = None # Surface for the scaled desktop background
        self.desktop_elements = {} # Permanent elements like the Terminal icon
        self.temp_desktop_files = {} # Level-specific files/icons, cleared each level
        self.icon_cache = {} # Cache for loaded and scaled icon surfaces

        # Saved state for pausing/resuming
        self.saved_state = None

    # -------------------------------------
    # Core State Flow & Initialization
    # -------------------------------------

    def start_first_level(self):
        """Called ONCE when the game starts (e.g., after clicking 'Play' in the main menu)."""
        print("GameState: Starting first level sequence.")
        self.load_background() # Load the desktop background image
        self.game_started = True
        self.saved_state = None # Clear any previous saved state on new game start
        # Now, initiate loading for level 1 (this might trigger NullX first)
        self.start_new_level(1) # Start with Level 1

    def start_new_level(self, level_id):
        """Initiates the process of loading and starting a specific level."""
        print(f"GameState: Initiating Level {level_id} sequence...")
        self.current_level_id = level_id

        # Reset state for the new level
        # Clear temporary files from the previous level
        self.temp_desktop_files.clear()
        # Hide all popup windows
        self.image_window.hide(); self.text_window.hide(); self.password_window.hide()

        # Ensure the permanent Terminal icon is present on the desktop
        if "Terminal" not in self.desktop_elements:
            term_icon = self._load_and_scale_icon(settings.TERM_ICON_PATH)
            if term_icon:
                self._add_desktop_element("Terminal", {
                    'icon_surface': term_icon,
                    'clickable': True,
                    'action': 'show_terminal',
                    'icon_type': 'terminal'},
                    is_temporary=False,
                    target_dict=self.desktop_elements)
            else: print("CRITICAL WARNING: Terminal icon failed to load.")

        # Start the NullX dialogue presenter for the current level
        if self.nullx_presenter.start_presentation(self.current_level_id):
             print(f"GameState: NullX presentation started for Level {level_id}.")
             self.current_view_mode = 'NULLX_PRESENTATION'
             self.pending_level_asset_load = True
             # Clear terminal before adding NullX content (only if not restoring state)
             if not self.saved_state: # Don't clear if we are restoring a saved game
                self.active_terminal.output_lines = []
                self.active_terminal.scroll_offset = 0
                self.active_terminal.add_output(f"...Initializing Level {level_id} Environment...", settings.COLOR_HINT_TEXT, self)
        else:
             print(f"GameState: No NullX dialogue for Level {level_id}, or skipped. Loading assets directly.")
             self.current_view_mode = 'DESKTOP'
             self.actually_load_desktop_assets() # Load icons, welcome message
             self.pending_level_asset_load = False

    # -------------------------------------
    # Save & Restore State (for pausing)
    # -------------------------------------

    def save_state(self):
        """Save the current game state for potential resume."""
        try:
            # Convert terminal output tuples to lists for simpler storage (JSON compatible if needed)
            terminal_output_serializable = []
            for line_tuple in self.active_terminal.output_lines:
                if isinstance(line_tuple, tuple) and len(line_tuple) == 3:
                    # Store (text, color_tuple, clickable_info_dict_or_None)
                    terminal_output_serializable.append([line_tuple[0], list(line_tuple[1]), line_tuple[2]])
                else:
                    # Handle potential malformed lines gracefully
                    print(f"Warning: Skipping non-standard terminal line during save: {line_tuple}")

            # Simplify desktop element storage (store names/types, reconstruct on load)
            # For now, storing full state - could be optimized later
            permanent_files_state = {}
            for name, data in self.desktop_elements.items():
                 permanent_files_state[name] = {
                     'icon_type': data.get('icon_type'),
                     # Add other necessary info if needed for reconstruction
                 }
            temporary_files_state = {}
            for name, data in self.temp_desktop_files.items():
                 temporary_files_state[name] = {
                     'icon_type': data.get('icon_type'),
                     'clickable': data.get('clickable'),
                     'target_image': data.get('target_image'),
                     'target_text': data.get('target_text'),
                     'action': data.get('action'),
                 }

            self.saved_state = {
                'current_level_id': self.current_level_id,
                'current_view_mode': self.current_view_mode, # Save current mode
                'terminal_output': terminal_output_serializable,
                'terminal_scroll': self.active_terminal.scroll_offset,
                'terminal_input': self.active_terminal.input_buffer,
                'terminal_cursor_pos': self.active_terminal.cursor_pos,
                'terminal_history': self.active_terminal.command_history[:], # Copy history
                'terminal_visible': self.active_terminal.is_visible,
                'image_window_visible': self.image_window.is_visible,
                'image_window_path': self.image_window.image_path,
                'text_window_visible': self.text_window.is_visible,
                'text_window_title': self.text_window.title,
                'text_window_content': self.text_window.text_content,
                'text_window_scroll': self.text_window.scroll_offset_y,
                'password_window_visible': self.password_window.is_visible,
                'password_window_target': self.password_window.target_zip_file,
                # Store simplified desktop state
                'desktop_permanent_files': permanent_files_state,
                'desktop_temporary_files': temporary_files_state,
                'nullx_active': self.nullx_presenter.is_visible,
                'nullx_level': self.nullx_presenter.level_id,
                'nullx_segment_index': self.nullx_presenter.current_segment_index,
                # Add other relevant state variables here...
            }
            print(f"Game state saved at level {self.current_level_id}, mode {self.current_view_mode}")
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            self.saved_state = None # Ensure invalid state isn't kept
            return False

    def restore_state(self):
        """Restore the saved game state."""
        if not hasattr(self, 'saved_state') or not self.saved_state:
            print("No saved state to restore.")
            return False

        try:
            state = self.saved_state # Use local variable for clarity
            print(f"Restoring game state for level {state['current_level_id']}, mode {state['current_view_mode']}")

            # Restore basic level and mode
            self.current_level_id = state['current_level_id']
            self.current_view_mode = state['current_view_mode']

            # Restore terminal state
            self.active_terminal.output_lines = [
                (line_data[0], tuple(line_data[1]), line_data[2])
                for line_data in state['terminal_output']
                if isinstance(line_data, list) and len(line_data) == 3 # Basic validation
            ]
            self.active_terminal.scroll_offset = state['terminal_scroll']
            self.active_terminal.input_buffer = state['terminal_input']
            self.active_terminal.cursor_pos = state['terminal_cursor_pos']
            self.active_terminal.command_history = state['terminal_history'][:] # Restore copy
            if state['terminal_visible']: self.active_terminal.show()
            else: self.active_terminal.hide()

            # Restore windows visibility and content
            if state['image_window_visible'] and state['image_window_path']:
                self.image_window.show(state['image_window_path'])
            else: self.image_window.hide()

            if state['text_window_visible'] and state['text_window_content'] is not None:
                 self.text_window.show(state['text_window_title'], state['text_window_content'])
                 self.text_window.scroll_offset_y = state['text_window_scroll'] # Restore scroll pos
            else: self.text_window.hide()

            if state['password_window_visible'] and state['password_window_target']:
                 self.password_window.show(state['password_window_target'])
            else: self.password_window.hide()

            # --- Reconstruct Desktop State ---
            self.desktop_elements.clear()
            self.temp_desktop_files.clear()
            # Re-add permanent elements (like Terminal icon)
            term_icon_path = settings.TERM_ICON_PATH
            term_icon_surf = self._load_and_scale_icon(term_icon_path)
            if term_icon_surf:
                 self._add_desktop_element("Terminal", {
                     'icon_surface': term_icon_surf, 'clickable': True,
                     'action': 'show_terminal', 'icon_type': 'terminal'
                 }, is_temporary=False)
            # Re-add temporary files based on saved state
            icon_type_to_path = { # Map used in actually_load_desktop_assets
                "text": settings.TXT_ICON_PATH, "pdf": settings.PDF_ICON_PATH,
                "filanaly": settings.FILANALY_ICON_PATH, "executable": settings.EXE_ICON_PATH,
                "zip": settings.ZIP_ICON_PATH, "png": settings.PNG_ICON_PATH,
                "image": settings.CLICKABLE_IMAGE_PATH, "terminal": settings.TERM_ICON_PATH,
            }
            for name, data in state['desktop_temporary_files'].items():
                 icon_type = data.get('icon_type', 'text')
                 icon_path = icon_type_to_path.get(icon_type, settings.TXT_ICON_PATH)
                 icon_surf = self._load_and_scale_icon(icon_path)
                 self._add_desktop_element(name, {
                     'icon_surface': icon_surf, 'clickable': data.get('clickable'),
                     'target_image': data.get('target_image'), 'target_text': data.get('target_text'),
                     'action': data.get('action'), 'icon_type': icon_type
                 }, is_temporary=True)

            # Restore NullX state if it was active
            if state['nullx_active']:
                 # Attempt to restart presentation at the correct segment
                 # Note: This might re-trigger the start sound briefly
                 if self.nullx_presenter.start_presentation(state['nullx_level']):
                     # If successfully restarted, jump to the saved segment
                     if 0 <= state['nullx_segment_index'] < len(self.nullx_presenter.dialogue_segments):
                          self.nullx_presenter.current_segment_index = state['nullx_segment_index']
                          self.nullx_presenter._load_segment(self.nullx_presenter.current_segment_index)
                          # Optionally skip animation if needed, or let it replay
                          # self.nullx_presenter.animation_complete = True
                          # self.nullx_presenter.display_text = self.nullx_presenter.current_text
                 else:
                      # Failed to restart presentation, default back to desktop
                      self.current_view_mode = 'DESKTOP'
            else:
                 self.nullx_presenter.finish_presentation() # Ensure it's hidden if saved inactive

            print(f"Game state restored successfully for level {self.current_level_id}")
            self.saved_state = None # Clear saved state after successful restore
            return True

        except Exception as e:
            print(f"Error restoring game state: {e}")
            # Attempt to recover by starting the saved level fresh
            try:
                level_to_start = self.saved_state.get('current_level_id', 1) if self.saved_state else 1
                print(f"Attempting recovery by restarting level {level_to_start}...")
                self.saved_state = None # Clear broken saved state
                self.start_new_level(level_to_start)
                return True # Indicate recovery happened
            except Exception as recovery_e:
                print(f"Recovery attempt failed: {recovery_e}")
                # Critical failure, maybe force quit or return to menu?
                return False

    def load_level(self, level_id):
        """Wrapper for start_new_level to maintain compatibility if called elsewhere."""
        self.start_new_level(level_id)

    # -------------------------------------
    # Update Loop (Called every frame)
    # -------------------------------------
    def update(self, dt):
        """Main update loop for the GameState, handles time-based changes."""
        if self.current_view_mode == 'NULLX_PRESENTATION':
             self.nullx_presenter.update(dt)
             if not self.nullx_presenter.is_visible and self.pending_level_asset_load:
                 print("GameState: NullX finished. Loading level assets now.")
                 self.actually_load_desktop_assets() # Load icons and terminal message
                 self.pending_level_asset_load = False # Mark assets as loaded
                 self.current_view_mode = 'DESKTOP' # Switch to desktop view AFTER loading

        elif self.current_view_mode == 'DESKTOP':
             if self.active_terminal.is_visible: self.active_terminal.update_cursor()
             # Other desktop mode updates could go here

        elif self.current_view_mode == 'TRANSITION':
             self.update_transition()

        elif self.current_view_mode == 'CREDITS':
             self.credits_screen.update(dt)

    # -------------------------------------
    # Event Handling (Input Processing)
    # -------------------------------------
    def handle_event(self, event, mouse_pos):
        """Handles user input events based on the current view mode."""

        # --- NULLX_PRESENTATION Mode ---
        if self.current_view_mode == 'NULLX_PRESENTATION':
            if self.nullx_presenter.handle_event(event, mouse_pos):
                # If NullX finished via this event, check if we need to load assets
                if not self.nullx_presenter.is_visible and self.pending_level_asset_load:
                     print("GameState: NullX finished via event. Loading level assets now.")
                     self.actually_load_desktop_assets()
                     self.pending_level_asset_load = False
                     self.current_view_mode = 'DESKTOP'
                return True # NullX consumed the event
            else:
                return True # Consume event anyway to prevent passthrough

        # --- TRANSITION Mode ---
        elif self.current_view_mode == 'TRANSITION':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 print("ESC pressed during transition, quitting game...");
                 pygame.event.post(pygame.event.Event(pygame.QUIT))
                 return True
            return True # Consume all other events during transition

        # --- CREDITS Mode ---
        elif self.current_view_mode == 'CREDITS':
             action = self.credits_screen.handle_event(event, mouse_pos)
             if action == 'Quit':
                 pygame.event.post(pygame.event.Event(pygame.QUIT)) # Signal quit
                 return True # Event handled
             return True # Consume other events during credits

        # --- DESKTOP Mode ---
        elif self.current_view_mode == 'DESKTOP':
            # Determine which window (if any) is currently on top and should get events first
            # Z-Order (topmost first): Password -> Image -> Text -> Terminal
            active_window = None
            if self.password_window.is_visible: active_window = self.password_window
            elif self.image_window.is_visible: active_window = self.image_window
            elif self.text_window.is_visible: active_window = self.text_window
            elif self.active_terminal.is_visible: active_window = self.active_terminal

            # 1. Pass event to the topmost active window's event handler first
            window_event_handled = False
            if active_window:
                try:
                    window_event_handled = active_window.handle_event(event, mouse_pos)
                except Exception as e:
                    print(f"ERROR during event handling for {type(active_window)}: {e}")
                    window_event_handled = True # Assume handled on error

            # 2. Terminal Keyboard Input Special Handling
            if not window_event_handled and event.type == pygame.KEYDOWN and active_window == self.active_terminal:
                 if self.active_terminal.handle_input(event, self): # handle_input returns True if 'exit' was entered
                      window_event_handled = True
                 else:
                      window_event_handled = True # Mark as handled so later handlers ignore it

            # 3. Handle Global ESC Key Fallback (Close windows or Pause)
            if not window_event_handled and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                closed_window = False
                # Close popups first
                if self.password_window.is_visible: self.password_window.hide(); closed_window = True
                elif self.image_window.is_visible: self.image_window.hide(); closed_window = True
                elif self.text_window.is_visible: self.text_window.hide(); closed_window = True
                elif self.active_terminal.is_visible: self.active_terminal.hide(); closed_window = True
                else:
                     # If no windows open, ESC pauses the game and goes to main menu
                     print("GameState: ESC pressed on desktop, pausing and returning to menu...")
                     self.save_state() # Save the current state
                     self.current_view_mode = 'MAIN_MENU' # Request mode change (handled by main.py)
                     # Let main.py handle music change
                     closed_window = True # Mark as handled

                if closed_window: window_event_handled = True

            # 4. Handle Desktop Icon Clicks (only if event not handled above)
            if not window_event_handled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 if self.handle_desktop_click(mouse_pos):
                     window_event_handled = True

            return window_event_handled

        # --- Fallback: Event Not Handled ---
        return False

    # -------------------------------------
    # Drawing Methods
    # -------------------------------------
    def draw(self, surface):
        """Draws the game elements based on the current view mode. DOES NOT draw the background."""

        # --- Draw Desktop Icons & Taskbar (if applicable) ---
        # This is drawn on top of the background managed by main.py
        if self.current_view_mode in ['DESKTOP', 'TRANSITION', 'NULLX_PRESENTATION', 'CREDITS']:
            # Call a modified draw_desktop or directly draw taskbar/icons here
            self.draw_taskbar_and_icons(surface) # Renamed/refactored function needed

        # --- Draw Windows (on top of desktop elements) ---
        if self.current_view_mode == 'DESKTOP':
            if self.active_terminal.is_visible: self.active_terminal.draw(surface)
            if self.text_window.is_visible: self.text_window.draw(surface)
            if self.image_window.is_visible: self.image_window.draw(surface)
            if self.password_window.is_visible: self.password_window.draw(surface)

        # --- Draw NullX Presenter (on top of desktop elements) ---
        if self.current_view_mode == 'NULLX_PRESENTATION':
             self.nullx_presenter.draw(surface)

        # --- Draw Transition Overlay (Highest Layer except menus) ---
        elif self.current_view_mode == 'TRANSITION':
            self.draw_transition(surface)

        # --- Draw Credits Screen ---
        elif self.current_view_mode == 'CREDITS':
            # CreditsScreen's draw method should handle its own background (e.g., black fill or overlay)
            self.credits_screen.draw(surface)

    def draw_taskbar_and_icons(self, surface):
         """Draws ONLY the taskbar and desktop icons, not the background."""
         # 1. Draw Taskbar
         taskbar_rect = pygame.Rect(0, settings.SCREEN_HEIGHT - settings.TASKBAR_HEIGHT,
                                     settings.SCREEN_WIDTH, settings.TASKBAR_HEIGHT)
         pygame.draw.rect(surface, settings.COLOR_TASKBAR, taskbar_rect)

         # Draw Level Name/ID on Taskbar
         level_data = self.get_current_level_data()
         # Initialize default values
         level_name = "Loading..."
         level_id_display = "N/A"

         # --- FIX: Add the logic to update level_name and level_id_display ---
         if self.game_started and level_data:
              # If the game has started and we have valid level data
              level_name = level_data.get('name', 'Unknown Level')
              level_id_display = str(self.current_level_id) if self.current_level_id > 0 else "Intro"
         elif not self.game_started:
             # If the game hasn't started (e.g., main menu is showing)
             level_name = "Main Menu"
             level_id_display = "" # No level ID needed for the main menu
         # --- END FIX ---

         # Now render the text using the potentially updated variables
         if settings.UI_FONT:
             try:
                 # Format the text string correctly
                 if not level_id_display: # Handle empty level ID for main menu
                     taskbar_text = level_name
                 else:
                     taskbar_text = f"Lvl {level_id_display}: {level_name}"

                 t_surf = settings.UI_FONT.render(taskbar_text, True, settings.COLOR_BLACK)
                 surface.blit(t_surf, t_surf.get_rect(left = 15, centery = taskbar_rect.centery))
             except Exception as e: print(f"Warn: Taskbar text render fail: {e}")

         # 2. Draw Desktop Icons (Copied from draw_desktop)
         start_x, start_y = 60, 50
         padding_x = settings.ICON_GRID_PADDING_X
         padding_y = settings.ICON_GRID_PADDING_Y
         all_files = self.get_all_desktop_files()
         element_names = sorted(list(all_files.keys()))
         current_x, current_y = start_x, start_y
         icon_w, icon_h = settings.ICON_SIZE
         text_offset_y = settings.ICON_TEXT_OFFSET_Y
         max_x = settings.SCREEN_WIDTH - padding_x

         for name in element_names:
             data = all_files.get(name) # Use .get for safety
             if not data: continue # Skip if data is missing for some reason

             icon_surf = data.get('icon')
             text_surf = data.get('text')
             if icon_w <= 0 or icon_h <= 0: continue

             icon_rect = pygame.Rect(current_x, current_y, icon_w, icon_h)
             text_rect = None; combined_h = icon_h
             if text_surf:
                 text_rect = text_surf.get_rect(centerx=icon_rect.centerx, top=icon_rect.bottom + text_offset_y)
                 combined_h = text_rect.bottom - icon_rect.top
             else:
                  estimated_text_h = settings.UI_FONT.get_height() if settings.UI_FONT else 14
                  combined_h += text_offset_y + estimated_text_h

             click_rect_width = max(icon_w + 10, (text_rect.width + 10) if text_rect else (icon_w + 10))
             click_rect = pygame.Rect(icon_rect.centerx - click_rect_width // 2, icon_rect.top, click_rect_width, combined_h)
             data['rect'] = click_rect # Store the calculated clickable rect

             # Draw the icon
             if icon_surf: surface.blit(icon_surf, icon_rect.topleft)
             else: pygame.draw.rect(surface, (100, 100, 100), icon_rect, 1) # Draw placeholder if icon missing

             # Draw the text label
             if text_surf and text_rect: surface.blit(text_surf, text_rect.topleft)

             # Move to the next grid position
             current_x += padding_x
             if current_x > max_x:
                  current_x = start_x
                  current_y += padding_y
             if current_y > settings.DESKTOP_HEIGHT - padding_y:
                 pass
    # -------------------------------------
    # Asset Loading & Management
    # -------------------------------------
    def load_background(self):
        """Loads and scales the desktop background image."""
        self.background_img = None # Reset first
        bg_path = settings.BACKGROUND_IMG_PATH
        if not bg_path or not os.path.exists(bg_path):
             print(f"Error: Background image file not found: {bg_path}"); return
        try:
            raw_bg = pygame.image.load(bg_path).convert()
            self.background_img = pygame.transform.smoothscale(raw_bg, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            print("Desktop background loaded and scaled.")
        except pygame.error as e: print(f"Warning: Could not load/scale background image: {e}")

    def _load_and_scale_icon(self, icon_path):
        """Loads an icon, scales it, caches it, and returns the scaled Surface."""
        if not icon_path: return None
        cache_key = os.path.basename(icon_path)
        if cache_key in self.icon_cache: return self.icon_cache[cache_key]
        if not os.path.exists(icon_path):
            print(f"Icon file missing: {icon_path}"); self.icon_cache[cache_key] = None; return None
        try:
            original_icon = pygame.image.load(icon_path).convert_alpha()
            scaled_icon = pygame.transform.smoothscale(original_icon, settings.ICON_SIZE)
            self.icon_cache[cache_key] = scaled_icon; return scaled_icon
        except Exception as e:
             print(f"  Error loading/scaling icon '{cache_key}': {e}"); self.icon_cache[cache_key] = None; return None

    def _add_desktop_element(self, name, data, is_temporary=True, target_dict=None):
         """Helper function to add an icon/element to the desktop dictionaries."""
         if target_dict is None:
             target_dict = self.temp_desktop_files if is_temporary else self.desktop_elements

         text_surface = None
         if settings.UI_FONT:
             try:
                 text_surface = settings.UI_FONT.render(str(name), True, settings.COLOR_FILE_TEXT)
             except Exception as e: print(f"  Warn: Failed render text for '{name}': {e}")

         element_dict = {
             'name': str(name),
             'icon': data.get('icon_surface'),
             'text': text_surface,
             'rect': None, # Calculated during draw
             'clickable': data.get("clickable", False),
             'target_image': data.get("target_image"),
             'target_text': data.get("target_text"),
             'action': data.get("action"),
             'icon_type': data.get('icon_type')
         }
         target_dict[str(name)] = element_dict

    def actually_load_desktop_assets(self):
        """Loads level-specific desktop files/icons and welcome message. Called AFTER NullX finishes."""
        level_data = level_manager.get_level_data(self.current_level_id)
        if not level_data:
            print(f"Error: No data found for level {self.current_level_id} assets load."); return

        print(f"GameState: Loading desktop assets for Level {self.current_level_id}...")
        files_data = level_data.get("desktop_files", {})
        self.temp_desktop_files.clear() # Clear previous temp files

        icon_type_to_path = {
            "text": settings.TXT_ICON_PATH, "pdf": settings.PDF_ICON_PATH,
            "filanaly": settings.FILANALY_ICON_PATH, "executable": settings.EXE_ICON_PATH,
            "zip": settings.ZIP_ICON_PATH, "png": settings.PNG_ICON_PATH,
            "image": settings.CLICKABLE_IMAGE_PATH, "terminal": settings.TERM_ICON_PATH,
        }

        for filename, file_info in files_data.items():
             icon_type = file_info.get("icon_type", "text")
             icon_path = icon_type_to_path.get(icon_type, settings.TXT_ICON_PATH)
             icon_surface = self._load_and_scale_icon(icon_path)
             if not icon_surface: print(f"  Warning: Icon load failed for '{filename}' ({icon_type}).")

             self._add_desktop_element(filename, {
                 'icon_surface': icon_surface, 'clickable': file_info.get("clickable", False),
                 'target_image': file_info.get("target_image"), 'target_text': file_info.get("target_text"),
                 'action': file_info.get("action"), 'icon_type': icon_type},
                 is_temporary=True)

        # --- Add Welcome Message to Terminal ---
        new_level_name = level_data.get("name", f"Level {self.current_level_id}")
        # Only clear if not pending load (i.e., NullX just finished or there was none)
        # and not restoring state (handled in restore_state)
        if not self.pending_level_asset_load and not self.saved_state:
            self.active_terminal.output_lines = []
            self.active_terminal.scroll_offset = 0
        # Always add level intro if not restoring
        if not self.saved_state:
            self.active_terminal.add_output(f"--- Level {self.current_level_id}: {new_level_name} ---", settings.COLOR_SUCCESS, self)
            self.active_terminal.add_output("Objective: Find and submit the flag.", settings.COLOR_HINT_TEXT, self)

    # -------------------------------------
    # Interaction & Commands
    # -------------------------------------
    def get_current_level_data(self):
        """Safely retrieves the data dictionary for the current level."""
        return level_manager.get_level_data(self.current_level_id)

    def get_all_desktop_files(self):
        """Returns a combined dictionary of permanent and temporary desktop files."""
        all_files = self.desktop_elements.copy()
        all_files.update(self.temp_desktop_files)
        return all_files

    def _attempt_unzip(self, password):
        """Handles the logic for the 'unzip' command or password prompt for Level 5."""
        level_data = self.get_current_level_data()
        if not level_data or self.current_level_id != 5:
             self.active_terminal.add_output("Unzip command not applicable here.", settings.COLOR_ERROR, self)
             return

        target_zip_name = "encrypted.zip"
        correct_pw = level_data.get("password")
        if not correct_pw:
            print("CRITICAL: Password missing in level 5 data!");
            self.active_terminal.add_output("Error: Level configuration issue.", settings.COLOR_ERROR, self); return

        output, output_color = None, settings.COLOR_TERMINAL_TEXT
        zip_contents_def = level_data.get("zip_contents", {}) # Should now only contain secret.png

        if password == correct_pw:
            # Check if ALL files defined in zip_contents are already on the desktop
            all_files_extracted = all(name in self.temp_desktop_files for name in zip_contents_def.keys())

            if all_files_extracted:
                output = f"Files already extracted from {target_zip_name}."
                output_color = settings.COLOR_HINT_TEXT
            else:
                output = [f"Archive: {target_zip_name}"]
                # Only add the image file now
                output.extend([f" inflating: {fname}" for fname in zip_contents_def.keys() if fname == "secret.png"])
                output.append("Unzip successful!")
                output_color = settings.COLOR_SUCCESS

                # Add ONLY the extracted PNG file to desktop
                icon_map = {"png": settings.PNG_ICON_PATH} # Map only needed for PNG now
                for fname, finfo in zip_contents_def.items():
                    if fname == "secret.png": # Ensure we only add the PNG
                        icon_type = finfo.get("icon_type", "png")
                        icon_path = icon_map.get(icon_type, settings.PNG_ICON_PATH)
                        icon_surf = self._load_and_scale_icon(icon_path)
                        self._add_desktop_element(fname, {
                            'icon_surface': icon_surf, 'clickable': finfo.get("clickable", True),
                            'target_image': finfo.get("target_image"), # Keep target_image association
                            'target_text': None, # No text content directly for PNG
                            'icon_type': icon_type},
                            is_temporary=True)
        else:
            output = f"Error: Invalid password for {target_zip_name}."
            output_color = settings.COLOR_ERROR

        if output:
            if not self.active_terminal.is_visible: self.active_terminal.show()
            self.active_terminal.add_output(output, output_color, self)

    def execute_command(self, command_str):
        """Parses and executes a command entered in the terminal."""
        if not self.active_terminal.is_visible: self.active_terminal.show()
        level_data = self.get_current_level_data()
        if not level_data:
            self.active_terminal.add_output("Error: Invalid level state.", settings.COLOR_ERROR, self); return False

        try: parts = shlex.split(command_str)
        except ValueError:
            self.active_terminal.add_output("Error: Invalid command syntax (check quotes).", settings.COLOR_ERROR, self); return False

        command = parts[0].lower() if parts else ""
        args_list = parts[1:]
        output, output_color, is_exit_command, auto_submitted = None, settings.COLOR_TERMINAL_TEXT, False, False

        all_visible_files = self.get_all_desktop_files()
        all_visible_filenames = list(all_visible_files.keys())
        correct_flag = level_data.get("flag")

        # --- Command Implementations ---

        if command == "wrap": # Developer command
             if len(args_list) == 1 and args_list[0].isdigit():
                 target_level = int(args_list[0])
                 all_levels = level_manager.get_all_level_ids()
                 if target_level in all_levels and target_level != self.current_level_id:
                     next_level_data = level_manager.get_level_data(target_level)
                     next_level_name = next_level_data.get('name', f'L{target_level}') if next_level_data else f'L{target_level}'
                     message = f"Wrap drive activated!\nLoading: {next_level_name}..."
                     self.image_window.hide(); self.text_window.hide(); self.password_window.hide()
                     self.transition_info = {"message": message, "start_time": time.time(),
                                              "duration": 1.5, "next_level_id": target_level,
                                              "is_cheat_skip": True}
                     self.current_view_mode = 'TRANSITION'
                 elif target_level == self.current_level_id:
                     output, output_color = "Already on that level.", settings.COLOR_HINT_TEXT
                 else: output, output_color = f"Invalid level ID: {target_level}.", settings.COLOR_ERROR
             else: output, output_color = "Usage: wrap <level_id> (Dev command)", settings.COLOR_HINT_TEXT

        elif command == "exit":
            is_exit_command = True
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif command == "clear":
            self.active_terminal.output_lines = []
            self.active_terminal.scroll_offset = 0

        elif command == "help":
             core_commands = {"ls", "cat", "submit", "clear", "help", "exit"}
             special_commands_help = set()
             level_help = level_data.get("commands", {}).get("help", [])
             special_commands_help.update(level_help) # Start with defined help

             # Dynamically Add Contextual Commands based on visible files or level
             if any(f.get('icon_type') in ['image', 'pdf', 'zip', 'png'] for f in all_visible_files.values()):
                 special_commands_help.add(" exif <filename>")
             if any(f.get('icon_type') in ['filanaly','executable','zip','png'] for f in all_visible_files.values()): # Added png to strings check
                 special_commands_help.add(" strings <filename>")
             if any(f.get('icon_type') == 'zip' for f in all_visible_files.values()):
                 special_commands_help.add(" unzip <zipfile> [-p <password>]")
             # Added general extract for level 4/5 PNG
             if self.current_level_id == 4 or (self.current_level_id == 5 and "secret.png" in all_visible_files):
                  special_commands_help.add(" extract <filename>")
             if self.current_level_id in [3, 5]: special_commands_help.add(" decode64 <base64_string>")
             # Git log only if secret_note.txt is visible (meaning extracted)
             if self.current_level_id == 5 and "secret_note.txt" in all_visible_files:
                  special_commands_help.add(" git log <text_file>")

             output = ["Available Commands:", "--- Core ---"]
             output.extend(sorted([f"  {cmd}" for cmd in core_commands]))
             if special_commands_help:
                # Filter out core commands from contextual help if accidentally added
                cleaned_help = set(f"  {line.strip()}" for line in special_commands_help if line.strip() and line.strip().split(' ')[0] not in core_commands)
                if cleaned_help:
                    output.append("--- Contextual ---")
                    output.extend(sorted(list(cleaned_help)))
             output.append("\nHint: Left-Click flags/Base64 in terminal output.")
             output.append("Hint: Right-Click terminal to paste.")

        elif command == "ls":
            output = sorted(all_visible_filenames) if all_visible_filenames else "(Desktop is empty)"

        elif command == "submit":
             flag_arg = args_list[0] if args_list else ""
             if not flag_arg:
                 output, output_color = "Usage: submit FLAG{...}", settings.COLOR_HINT_TEXT
             elif correct_flag and flag_arg == correct_flag:
                 output, output_color = f"Correct! {level_data.get('win_message', 'Complete!')}", settings.COLOR_SUCCESS
                 self.start_level_transition()
                 next_level = level_data.get("next_level")
                 win_sound = settings.SFX_FINISH_GAME if next_level is None else settings.SFX_LEVEL_WIN
                 if settings.SFX_ENABLED and win_sound and pygame.mixer: # Added mixer check
                     pygame.mixer.Channel(settings.UI_CHANNEL).play(win_sound)
             elif flag_arg in level_data.get("fake_flags", []):
                 output, output_color = "Incorrect flag. (That's a known fake)", settings.COLOR_ERROR
             else:
                 output, output_color = "Incorrect flag.", settings.COLOR_ERROR

        elif command == "cat":
            target_file = args_list[0] if args_list else ""
            if not target_file: output, output_color = "Usage: cat <filename>", settings.COLOR_HINT_TEXT
            elif target_file == "secret_note.txt" and self.current_level_id == 5 and target_file not in all_visible_files:
                 # Specific hint if trying to cat the note before extracting
                 output, output_color = f"cat: File '{target_file}' not found. (Hint: Maybe 'extract' it first?)", settings.COLOR_ERROR
            else:
                 file_data = all_visible_files.get(target_file)
                 if file_data:
                     # Check if the icon itself has target_text (like notes.txt, hint.txt, or the *extracted* secret_note.txt)
                     if file_data.get('target_text') is not None:
                          file_content = file_data['target_text']
                          if isinstance(file_content, str): output = file_content.split('\n')
                          else: output = [f"Content for '{target_file}':", str(file_content)]
                          # Check if the actual flag is in the text content
                          if correct_flag and isinstance(file_content, str) and correct_flag in file_content: output_color = settings.COLOR_SUCCESS
                     else:
                          # If no direct target_text, check command simulations (e.g., for binary files)
                          cmd_output = level_data.get("commands", {}).get(f"cat {target_file}")
                          if cmd_output:
                              output = cmd_output
                              # Check if the simulated output contains the flag
                              is_output_string = isinstance(cmd_output, str)
                              is_output_list = isinstance(cmd_output, list)
                              if correct_flag and ((is_output_string and correct_flag in cmd_output) or \
                                                  (is_output_list and any(correct_flag in str(line) for line in cmd_output))):
                                  output_color = settings.COLOR_SUCCESS
                          else: output, output_color = f"cat: Cannot display content of '{target_file}'.", settings.COLOR_HINT_TEXT
                 else: output, output_color = f"cat: '{target_file}': No such file.", settings.COLOR_ERROR

        elif command == "exif":
             target_file = args_list[0] if args_list else ""; file_data = all_visible_files.get(target_file)
             if not target_file: output, output_color = "Usage: exif <filename>", settings.COLOR_HINT_TEXT
             elif file_data:
                  icon_type = file_data.get('icon_type')
                  valid_types = ['image', 'pdf', 'zip', 'png']
                  if icon_type in valid_types:
                      cmd_key = f"exif {target_file}"
                      cmd_output = level_data.get("commands", {}).get(cmd_key)
                      if cmd_output:
                           output = cmd_output
                           if correct_flag and ((isinstance(cmd_output, str) and correct_flag in cmd_output) or (isinstance(cmd_output, list) and any(correct_flag in str(line) for line in cmd_output))): output_color = settings.COLOR_SUCCESS
                      else: output, output_color = f"exif: No simulated metadata for '{target_file}'.", settings.COLOR_HINT_TEXT
                  else: output, output_color = f"exif: File type '{icon_type}' doesn't support EXIF.", settings.COLOR_HINT_TEXT
             else: output, output_color = f"exif: '{target_file}': No such file.", settings.COLOR_ERROR

        elif command == "strings":
              target_file = args_list[0] if args_list else ""; file_data = all_visible_files.get(target_file)
              if not target_file: output, output_color = "Usage: strings <filename>", settings.COLOR_HINT_TEXT
              elif file_data:
                  icon_type = file_data.get('icon_type')
                  invalid_types = ['text'] # Don't run strings on plain text
                  if icon_type not in invalid_types:
                       cmd_key = f"strings {target_file}"
                       cmd_output = level_data.get("commands", {}).get(cmd_key)
                       if cmd_output:
                            output = cmd_output
                            if correct_flag and ((isinstance(cmd_output, str) and correct_flag in cmd_output) or (isinstance(cmd_output, list) and any(correct_flag in str(line) for line in cmd_output))): output_color = settings.COLOR_SUCCESS
                       else: output, output_color = f"strings: No simulated output for '{target_file}'.", settings.COLOR_HINT_TEXT
                  else: output, output_color = f"strings: Not typically useful on '{icon_type}' files.", settings.COLOR_HINT_TEXT
              else: output, output_color = f"strings: '{target_file}': No such file.", settings.COLOR_ERROR

        elif command == "decode64":
              if self.current_level_id not in [3, 5]: # Only available on levels 3 and 5
                   output, output_color = f"Command not found: {command}", settings.COLOR_ERROR
              else:
                   b64_string = args_list[0] if args_list else ""
                   if b64_string:
                       try:
                           # Attempt decoding (same logic as before)
                           missing_padding = len(b64_string) % 4
                           if missing_padding: b64_string += '=' * (4 - missing_padding)
                           decoded_bytes = base64.b64decode(b64_string, validate=True)
                           try: decoded_string = decoded_bytes.decode('utf-8')
                           except UnicodeDecodeError: decoded_string = decoded_bytes.decode('latin-1', errors='ignore')

                           # Check if the decoded string is the real flag or a known fake flag
                           output = f"Decoded: {decoded_string}"
                           if correct_flag and decoded_string == correct_flag:
                               output += "\nFlag confirmed! Auto-submitting..."
                               output_color = settings.COLOR_SUCCESS
                               self.active_terminal.add_output(output, output_color, self) # Add output BEFORE submitting
                               self.execute_command(f"submit {decoded_string}") # Submit the flag
                               auto_submitted = True # Prevent double output
                           elif decoded_string in level_data.get('fake_flags', []):
                               output += " (Looks like a fake flag)"
                               output_color = settings.COLOR_HINT_TEXT
                           else: output_color = settings.COLOR_TERMINAL_TEXT # Default color for other decoded text
                       except (binascii.Error, ValueError) as e:
                            output, output_color = f"Decode Error: Invalid Base64 string. ({e})", settings.COLOR_ERROR
                       except Exception as e_generic:
                           output, output_color = f"Decode Error: An unexpected error occurred. ({e_generic})", settings.COLOR_ERROR
                   else:
                        # Show help if no argument provided
                        default_help = level_data.get("commands", {}).get("decode64")
                        output, output_color = default_help or "Usage: decode64 <base64_string>", settings.COLOR_HINT_TEXT

        elif command == "extract":
             # Extract is now potentially relevant in Level 4 (image.jpg) and Level 5 (secret.png)
             target_file = args_list[0] if args_list else ""
             if not target_file: output, output_color = "Usage: extract <filename>", settings.COLOR_HINT_TEXT
             else:
                 file_data = all_visible_files.get(target_file)
                 if not file_data: output, output_color = f"extract: '{target_file}': No such file.", settings.COLOR_ERROR
                 # --- Level 4 Extraction Logic ---
                 elif self.current_level_id == 4 and target_file == "image.jpg":
                      if "extracted_flag.txt" in self.temp_desktop_files:
                           output, output_color = "'extracted_flag.txt' already exists.", settings.COLOR_HINT_TEXT
                      else:
                           cmd_output_def = level_data.get("commands", {}).get(f"extract {target_file}", ["Extraction simulation failed."])
                           flag_content_def = level_data.get("commands", {}).get("cat extracted_flag.txt", [f"{correct_flag or 'FLAG{L4_MISSING}'}"])
                           extracted_content = "\n".join(map(str, flag_content_def)) if isinstance(flag_content_def, list) else str(flag_content_def)
                           ext_file_data = {'icon_surface': self._load_and_scale_icon(settings.TXT_ICON_PATH),
                                            'clickable': True, 'target_text': extracted_content, 'icon_type': 'text'}
                           self._add_desktop_element("extracted_flag.txt", ext_file_data, is_temporary=True)
                           msg_add = "New file created. Use 'cat' or click it."
                           if isinstance(cmd_output_def, list): output = cmd_output_def + [msg_add]
                           elif isinstance(cmd_output_def, str): output = [cmd_output_def, msg_add]
                           else: output = ["Extraction successful!", msg_add]
                           output_color = settings.COLOR_SUCCESS
                 # --- Level 5 Extraction Logic ---
                 elif self.current_level_id == 5 and target_file == "secret.png":
                      if "secret_note.txt" in self.temp_desktop_files:
                           output, output_color = "'secret_note.txt' already exists.", settings.COLOR_HINT_TEXT
                      elif target_file not in self.temp_desktop_files: # Check if the source PNG exists
                            output, output_color = f"extract: File '{target_file}' not found. (Hint: 'unzip' first?).", settings.COLOR_ERROR
                      else:
                           cmd_output_def = level_data.get("commands", {}).get(f"extract {target_file}", ["Extraction simulation failed."])
                           # Get the note content from the new key in level_manager
                           note_content_lines = level_data.get("extracted_note_content", ["Error: Note content missing."])
                           extracted_content = "\n".join(note_content_lines)

                           # Create the secret_note.txt desktop element
                           note_file_data = {'icon_surface': self._load_and_scale_icon(settings.TXT_ICON_PATH),
                                             'clickable': True, 'target_text': extracted_content, 'icon_type': 'text'}
                           self._add_desktop_element("secret_note.txt", note_file_data, is_temporary=True)

                           msg_add = "New file created. Use 'cat' or click it."
                           if isinstance(cmd_output_def, list): output = cmd_output_def + [msg_add]
                           elif isinstance(cmd_output_def, str): output = [cmd_output_def, msg_add]
                           else: output = ["Extraction successful!", msg_add]
                           output_color = settings.COLOR_SUCCESS
                 # --- General Extract Failure Cases ---
                 else:
                     fail_output = level_data.get("commands", {}).get(f"extract {target_file}")
                     if fail_output: output = fail_output # Use defined failure message if exists
                     else: output = f"extract: Cannot extract from '{target_file}' or command not applicable here."
                     output_color = settings.COLOR_HINT_TEXT


        elif command == "unzip":
              if self.current_level_id != 5:
                  output, output_color = f"Command not found: {command}", settings.COLOR_ERROR
              else:
                  target_zip = "encrypted.zip"
                  # Check if command is 'unzip encrypted.zip -p PASSWORD'
                  if len(args_list) >= 3 and args_list[0] == target_zip and args_list[1] == '-p':
                      password_attempt = args_list[2]
                      self._attempt_unzip(password_attempt) # Call helper, don't set output here
                  # Check if command is 'unzip encrypted.zip' (for prompt)
                  elif len(args_list) == 1 and args_list[0] == target_zip:
                       self.password_window.show(target_zip)
                       output, output_color = f"Password required for '{target_zip}'.\nUse prompt or '{command} {target_zip} -p <password>'", settings.COLOR_HINT_TEXT
                  # Handle incorrect usage
                  else:
                       default_help = level_data.get("commands", {}).get("unzip")
                       output, output_color = default_help or ["Usage: unzip <file.zip> -p <password>", f"Or:    unzip {target_zip} (for prompt)"], settings.COLOR_HINT_TEXT

        elif command == "git":
             if self.current_level_id != 5:
                  output, output_color = f"Command not found: {command}", settings.COLOR_ERROR
             else:
                 git_sub_command = args_list[0].lower() if args_list else ""
                 target_file = args_list[1] if len(args_list) > 1 else ""
                 # Check specifically for 'git log secret_note.txt'
                 if git_sub_command == "log" and target_file == "secret_note.txt":
                     # Check if the note file *exists* (meaning it was extracted)
                     if target_file in self.temp_desktop_files:
                         cmd_key = f"git log {target_file}"
                         cmd_output = level_data.get("commands", {}).get(cmd_key)
                         if cmd_output:
                             output = cmd_output
                             # Highlight if flag is present
                             if correct_flag and ((isinstance(cmd_output, str) and correct_flag in cmd_output) or (isinstance(cmd_output, list) and any(correct_flag in str(line) for line in cmd_output))):
                                 output_color = settings.COLOR_SUCCESS
                         else: output = "Error: Git log simulation data missing."
                     else:
                         # Give hint if the note file doesn't exist yet
                         output, output_color = f"git log: File '{target_file}' not found. (Hint: Have you extracted it yet?)", settings.COLOR_ERROR
                 elif git_sub_command == "log":
                     output, output_color = "Usage: git log <filename> (Try 'secret_note.txt' after extracting it)", settings.COLOR_HINT_TEXT
                 else:
                      default_help = level_data.get("commands", {}).get("git")
                      output, output_color = default_help or ["Usage: git log <filename>"], settings.COLOR_HINT_TEXT

        else: # Command Not Found
            if command:
                output, output_color = f"Command not found: {command}", settings.COLOR_ERROR

        # --- Output Result to Terminal ---
        # Only add output if it wasn't auto-submitted and command wasn't 'clear' or handled internally ('unzip -p')
        if output is not None and not auto_submitted and command != "clear" and not (command == "unzip" and len(args_list) >= 3):
            self.active_terminal.add_output(output, output_color, self)

        return is_exit_command    # -------------------------------------
    # Desktop Interaction
    # -------------------------------------
    def handle_desktop_click(self, pos):
        """Handles left-clicks on desktop icons."""
        all_files = self.get_all_desktop_files()
        for name, data in all_files.items():
            if data.get('rect') and data['rect'].collidepoint(pos):
                print(f"Clicked desktop icon: {name}")
                if self.current_level_id == 5 and name == "encrypted.zip":
                    self.password_window.show(name)
                    self.active_terminal.add_output("Password prompt opened.", settings.COLOR_HINT_TEXT, self)
                    return True

                elif data.get('clickable'):
                    action = data.get('action')
                    img_path = data.get('target_image')
                    text_content = data.get('target_text')

                    if action == 'show_terminal':
                         self.active_terminal.show()
                    elif img_path:
                         if os.path.exists(img_path):
                             self.image_window.show(img_path)
                         else:
                             errmsg=f"Error: Image file not found '{os.path.basename(img_path)}'"
                             print(errmsg); self.active_terminal.add_output(errmsg, settings.COLOR_ERROR, self)
                    elif text_content is not None:
                         self.text_window.show(name, text_content)
                    else:
                         no_action_msg = f"Double-clicking '{name}' does not perform any specific action."
                         print(no_action_msg)
                         if not self.active_terminal.is_visible: self.active_terminal.show()
                         self.active_terminal.add_output(no_action_msg, settings.COLOR_HINT_TEXT, self)
                else:
                     not_clickable_msg = f"'{name}' is not interactive."
                     print(not_clickable_msg)
                     if not self.active_terminal.is_visible: self.active_terminal.show()
                     self.active_terminal.add_output(not_clickable_msg, settings.COLOR_HINT_TEXT, self)
                return True # Click on an icon consumed the event

        return False # Click was not on any icon

    # -------------------------------------
    # Level Transition Methods
    # -------------------------------------
    def start_level_transition(self):
        """Initiates the visual transition effect between levels or to credits screen."""
        level_data = self.get_current_level_data()
        if not level_data or self.transition_info or self.current_view_mode == 'TRANSITION':
            return

        next_level_id = level_data.get("next_level")
        win_message = level_data.get("win_message", "Level Complete!")

        if next_level_id is not None and level_manager.get_level_data(next_level_id):
            next_level_data = level_manager.get_level_data(next_level_id)
            next_level_name = next_level_data.get('name', f'Level {next_level_id}')
            message = f"{win_message}\n\nLoading: {next_level_name}..."
            print(f"Starting transition from level {self.current_level_id} to {next_level_id}...")
        else:
            message = f"{win_message}\n\nAll levels finished! Congratulations!"
            next_level_id = None # Explicitly mark as final level
            print(f"Starting transition from final level {self.current_level_id} to credits screen...")

        self.image_window.hide(); self.text_window.hide(); self.password_window.hide()

        self.transition_info = {
            "message": message, "start_time": time.time(),
            "duration": 3.0, "next_level_id": next_level_id,
            "is_cheat_skip": False
        }
        self.current_view_mode = 'TRANSITION'

    def update_transition(self):
        """Updates the state of the level transition (e.g., fade timer)."""
        if not self.transition_info or self.current_view_mode != 'TRANSITION':
            return

        now = time.time()
        elapsed = now - self.transition_info["start_time"]
        duration = self.transition_info["duration"]

        if elapsed > duration:
            next_level_id = self.transition_info.get("next_level_id")
            is_cheat = self.transition_info.get("is_cheat_skip", False)
            self.transition_info = None # Clear transition data

            if next_level_id is not None and (level_manager.get_level_data(next_level_id) or is_cheat):
                print(f"Transition complete. Initiating level {next_level_id} loading...")
                self.start_new_level(next_level_id)
            elif next_level_id is None and not is_cheat:
                # Natural end of the game - SWITCH TO CREDITS MODE
                print("Transition complete. All levels finished! Starting credits...")
                self.current_view_mode = 'CREDITS' # Switch to Credits mode
                # The main loop will handle activating the credits screen via game_state.credits_screen.show()
            else:
                print(f"Transition ended: Invalid next level '{next_level_id}' or cheat end.")
                self.current_view_mode = 'DESKTOP' # Revert safely

    # -------------------------------------
    # Component Drawing Methods
    # -------------------------------------

    def draw_desktop(self, surface):
        """Draws the desktop background, taskbar, and icons."""
        # 1. Draw Background Image
        if self.background_img:
            surface.blit(self.background_img, (0, 0))
        else: surface.fill(settings.COLOR_BLACK)

        # 2. Draw Taskbar
        taskbar_rect = pygame.Rect(0, settings.SCREEN_HEIGHT - settings.TASKBAR_HEIGHT,
                                    settings.SCREEN_WIDTH, settings.TASKBAR_HEIGHT)
        pygame.draw.rect(surface, settings.COLOR_TASKBAR, taskbar_rect)

        # Draw Level Name/ID on Taskbar
        level_data = self.get_current_level_data()
        level_name = "Loading..." ; level_id_display = "N/A"
        if self.game_started and level_data:
             level_name = level_data.get('name', 'Unknown Level')
             level_id_display = str(self.current_level_id) if self.current_level_id > 0 else "Intro"
        elif not self.game_started:
            level_name = "Main Menu"; level_id_display = ""

        if settings.UI_FONT:
            try:
                taskbar_text = f"Lvl {level_id_display}: {level_name}".strip()
                t_surf = settings.UI_FONT.render(taskbar_text, True, settings.COLOR_BLACK)
                surface.blit(t_surf, t_surf.get_rect(left = 15, centery = taskbar_rect.centery))
            except Exception as e: print(f"Warn: Taskbar text render fail: {e}")

        # 3. Draw Desktop Icons (Grid Layout)
        start_x, start_y = 60, 50
        padding_x = settings.ICON_GRID_PADDING_X
        padding_y = settings.ICON_GRID_PADDING_Y
        max_x = settings.SCREEN_WIDTH - padding_x
        current_x, current_y = start_x, start_y
        icon_w, icon_h = settings.ICON_SIZE
        text_offset_y = settings.ICON_TEXT_OFFSET_Y

        all_files = self.get_all_desktop_files()
        element_names = sorted(list(all_files.keys()))

        for name in element_names:
             data = all_files[name]
             icon_surf = data.get('icon')
             text_surf = data.get('text')

             if icon_w <= 0 or icon_h <= 0: continue

             icon_rect = pygame.Rect(current_x, current_y, icon_w, icon_h)
             text_rect = None
             combined_h = icon_h

             if text_surf:
                 text_rect = text_surf.get_rect(centerx=icon_rect.centerx, top=icon_rect.bottom + text_offset_y)
                 combined_h = text_rect.bottom - icon_rect.top
             else:
                  estimated_text_h = settings.UI_FONT.get_height() if settings.UI_FONT else 14
                  combined_h += text_offset_y + estimated_text_h

             click_rect_width = max(icon_w + 10, (text_rect.width + 10) if text_rect else (icon_w + 10))
             click_rect = pygame.Rect(icon_rect.centerx - click_rect_width // 2, icon_rect.top,
                                        click_rect_width, combined_h)
             data['rect'] = click_rect

             if icon_surf: surface.blit(icon_surf, icon_rect.topleft)
             else: pygame.draw.rect(surface, (100, 100, 100), icon_rect, 1) # Placeholder
             if text_surf and text_rect: surface.blit(text_surf, text_rect.topleft)

             current_x += padding_x
             if current_x > max_x:
                  current_x = start_x; current_y += padding_y
             if current_y > settings.DESKTOP_HEIGHT - padding_y: pass # Stop drawing if off screen


    def draw_transition(self, surface):
        """Draws the level transition overlay effect."""
        if not self.transition_info or self.current_view_mode != 'TRANSITION': return
        font = settings.TERMINAL_FONT or settings.UI_FONT
        if not font: return

        # 1. Draw Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        now = time.time(); elapsed = now - self.transition_info["start_time"]
        duration = self.transition_info["duration"]; fade_dur = 0.5
        max_alpha = 200; alpha = max_alpha
        if elapsed < fade_dur: alpha = int(max_alpha * (elapsed / fade_dur))
        elif elapsed > duration - fade_dur: alpha = int(max_alpha * ((duration - elapsed) / fade_dur))
        alpha = max(0, min(alpha, max_alpha))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        # 2. Draw Text
        try:
            message = self.transition_info["message"]
            lines = message.split('\n')
            line_h = font.get_height()
            total_h = len(lines) * line_h
            start_y = settings.SCREEN_HEIGHT // 2 - total_h // 2
            for i, line in enumerate(lines):
                 text_surf = font.render(line, True, settings.COLOR_SUCCESS)
                 text_rect = text_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, y=start_y + i * line_h)
                 surface.blit(text_surf, text_rect)
        except Exception as e: print(f"Warn: Failed transition text render: {e}")

# --- END OF FILE game_state.py ---