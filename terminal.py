# --- START OF FILE terminal.py ---

# terminal.py
import pygame
import time
import settings        # Access settings for fonts, colors, sizes, regex, etc.
import level_manager   # Used for context checks (e.g., specific level Base64 strings)

class Terminal:
    """Simulates a command-line terminal window within the game."""

    def __init__(self):
        """Initializes the terminal window and its internal state."""
        # --- Window Properties ---
        self.is_visible = False        # Is the terminal currently shown?
        self.window_surface = None     # The Pygame Surface object for drawing the terminal window
        # Initial size based on settings, position centered on screen
        self.window_rect = pygame.Rect(0, 0, *settings.TERMINAL_WINDOW_SIZE)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

        # Define rectangles for title bar and main content area relative to window
        self.title_bar_rect = pygame.Rect(0, 0, self.window_rect.width, settings.POPUP_TITLE_BAR_HEIGHT)
        # Content area has padding (5px) from window edges and below title bar
        self.content_rect = pygame.Rect(5, self.title_bar_rect.bottom + 5,
                                         self.window_rect.width - 10, # Width - left/right padding
                                         self.window_rect.height - self.title_bar_rect.bottom - 10) # Height - top/bottom padding

        self.close_button_rect = None # Rect for the close button (calculated later)
        self._calculate_button_rects() # Calculate initial button position

        # Drag state for moving the window
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # --- Terminal State ---
        self.font = settings.TERMINAL_FONT # Get the pre-loaded terminal font
        if not self.font:
            # Critical error if the font didn't load in settings.py
            raise RuntimeError("Terminal requires the TERMINAL_FONT to be loaded in settings.")

        self.input_buffer = ""          # Stores the command currently being typed
        # List storing output history. Each element is a tuple:
        # (line_text: str, color: tuple, clickable_info: dict or None)
        self.output_lines = []
        # Ensure line_height is calculated correctly even if font failed momentarily (though caught above)
        self.line_height = self.font.get_height() if self.font else 16
        # Calculate maximum number of lines visible in the content area
        self.max_lines_display = max(1, (self.content_rect.height // self.line_height) - 1) if self.line_height > 0 else 1 # Reserve 1 line for input
        # Scroll offset: How many lines are scrolled *up* (0 = bottom lines visible)
        self.scroll_offset = 0
        # Cursor position within the input_buffer (character index)
        self.cursor_pos = 0
        # Stores previously entered commands for history navigation (Up/Down arrows)
        self.command_history = []
        # Index for command history navigation (-1 = not navigating, 0 = oldest, len-1 = newest)
        self.history_index = -1
        # Temporarily stores the current input when starting history navigation
        self.current_input_on_nav_start = ""

        # Cursor blink state
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()

        # Stores clickable regions found during rendering (for mouse interaction)
        # List of tuples: (screen_rect: pygame.Rect, clickable_info: dict)
        self.clickable_regions = []

        # Define the command prompt string
        self.prompt = "agent@ctf-os:~$ "
        # Initial greeting/level messages are added by GameState when a level starts.


    def _calculate_button_rects(self):
        """Calculates the screen rectangle for the close button in the title bar."""
        # Position based on constants defined in settings.py
        cx = settings.POPUP_BUTTON_X_START # X distance from left edge
        cy = settings.POPUP_BUTTON_Y_OFFSET # Y position relative to title bar top
        rad = settings.POPUP_BUTTON_RADIUS # Radius of the button circle
        # Calculate top-left corner based on center and radius, ensuring minimum size
        self.close_button_rect = pygame.Rect(cx - rad, cy - rad, max(1, rad*2), max(1, rad*2))


    def _redraw_frame(self):
        """Redraws the static elements of the terminal window (border, title bar, buttons).
           Called at the beginning of the main draw() method."""
        if not self.window_surface: return # Cannot draw if surface doesn't exist

        # Fill the entire window surface with the background color
        # (Alpha value allows underlying elements to potentially show through if < 255)
        self.window_surface.fill(settings.POPUP_BG_COLOR)
        # Draw the title bar rectangle
        pygame.draw.rect(self.window_surface, settings.POPUP_TITLE_COLOR, self.title_bar_rect)
        # Draw the window title text ("Terminal") centered in the title bar
        if settings.UI_FONT: # Use the standard UI font for the title
            try:
                title_surf = settings.UI_FONT.render("Terminal", True, settings.COLOR_WHITE)
                # Calculate position to center the text
                title_rect = title_surf.get_rect(centerx=self.window_rect.width / 2, centery=settings.POPUP_TITLE_BAR_HEIGHT / 2)
                self.window_surface.blit(title_surf, title_rect)
            except Exception as e: print(f"Error rendering terminal title: {e}")
        # Draw the circular close button
        if self.close_button_rect:
            pygame.draw.circle(self.window_surface, settings.COLOR_CLOSE_BUTTON, self.close_button_rect.center, settings.POPUP_BUTTON_RADIUS)


    def show(self):
        """Makes the terminal visible and ensures its state is up-to-date."""
        if not self.font: return # Cannot show without a font
        print("Terminal window shown.")
        self.is_visible = True
        self.is_dragging = False # Ensure dragging is reset

        # --- Recalculate Geometry --- (Important if screen size could change)
        # Reset window size to standard defined in settings
        self.window_rect.size = settings.TERMINAL_WINDOW_SIZE
        # Re-center the window on the current screen
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        # Recalculate internal rectangles based on potentially new window size/position
        self.title_bar_rect.width = self.window_rect.width
        self.content_rect = pygame.Rect(5, self.title_bar_rect.bottom + 5,
                                         self.window_rect.width - 10,
                                         self.window_rect.height - self.title_bar_rect.bottom - 10)
        self._calculate_button_rects() # Update button position

        # Recalculate how many lines can fit in the content area
        self.line_height = self.font.get_height() # Ensure line height is current
        self.max_lines_display = max(1, (self.content_rect.height // self.line_height) - 1) if self.line_height > 0 else 1

        # --- Create/Update Drawing Surface ---
        # Create the surface if it doesn't exist or if size changed implicitly
        # Using SRCALPHA allows for transparency effects if POPUP_BG_COLOR has alpha < 255
        try:
            self.window_surface = pygame.Surface(self.window_rect.size, pygame.SRCALPHA)
            self._redraw_frame() # Draw the initial static frame elements
        except (pygame.error, ValueError) as e:
             print(f"Error creating/updating Terminal surface: {e}")
             self.is_visible = False # Prevent showing if surface fails
             return

        # Reset scroll position and clear clickable regions when shown
        self.scroll_offset = 0
        self.clickable_regions.clear()
        # Reset cursor state
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        # Note: Terminal content (output_lines) is NOT cleared here; it's managed by GameState on level change.


    def hide(self):
        """Makes the terminal invisible."""
        if self.is_visible: print("Terminal window hidden.")
        self.is_visible = False
        self.is_dragging = False # Stop dragging if it was hidden while dragging
        self.clickable_regions.clear() # Clear interactive regions
        # Optional: self.window_surface = None # Release surface memory immediately (redraw on next show)


    def add_output(self, text_or_list, color=settings.COLOR_TERMINAL_TEXT, game_state=None):
        """Adds text (string or list of strings) to the terminal's output buffer,
           detecting and tagging clickable elements like flags or Base64 strings."""
        if not self.font: return # Cannot process without font

        # Standardize input to a list of strings
        if isinstance(text_or_list, (list, tuple)):
            lines = [str(item) for item in text_or_list] # Convert all items to string
        elif isinstance(text_or_list, str):
            lines = text_or_list.split('\n') # Split multi-line strings
        else:
            lines = [str(text_or_list)] # Convert single non-string items

        # Get context for detecting specific clickable items (relevant level Base64)
        current_level_id = game_state.current_level_id if game_state else 0
        # Pre-fetch potential Base64 strings relevant to specific levels if game_state is available
        l3_enc = l5_enc = None
        if game_state:
            l3_data = level_manager.get_level_data(3); l5_data = level_manager.get_level_data(5)
            if l3_data: l3_enc = l3_data.get('encoded_flag')           # Base64 string for level 3
            if l5_data: l5_enc = l5_data.get('embedded_fake_flag_b64') # Fake Base64 string for level 5

        # Process each line to find clickable elements
        for line_text in lines:
             # *** Clean potential null characters from input line text ***
             safe_line_text = line_text.replace('\x00', '')
             clickable_info = None # Dictionary to store info if clickable element found

             # --- Find Clickable Patterns using safe_line_text ---
             match_flag = settings.FLAG_REGEX.search(safe_line_text)
             if match_flag:
                  clickable_text = match_flag.group(1)
                  pre_text = safe_line_text[:match_flag.start()]
                  post_text = safe_line_text[match_flag.end():]
                  clickable_info = {'type': 'flag', 'text': clickable_text, 'pre_text': pre_text, 'post_text': post_text}
             elif game_state:
                  b64_target = None
                  if current_level_id == 3 and l3_enc and l3_enc in safe_line_text:
                       b64_target = l3_enc; click_type = 'base64_l3'
                  elif current_level_id == 5 and l5_enc and l5_enc in safe_line_text:
                       b64_target = l5_enc; click_type = 'base64_l5'

                  if b64_target:
                       start_index = safe_line_text.find(b64_target)
                       if start_index != -1:
                           pre_text = safe_line_text[:start_index]
                           post_text = safe_line_text[start_index + len(b64_target):]
                           clickable_info = {'type': click_type, 'text': b64_target, 'pre_text': pre_text, 'post_text': post_text}

             # Append the original line_text (or safe_line_text?) and other info
             # Let's store the original line_text but use safe versions for searching/rendering if needed
             self.output_lines.append((line_text, color, clickable_info)) # Store original line text


        # --- History Limit & Scrolling ---
        # Limit the total number of lines stored in the output buffer
        MAX_OUTPUT_LINES = settings.TERMINAL_MAX_HISTORY * 10 # Allow more scrollback (e.g., 500 lines)
        if len(self.output_lines) > MAX_OUTPUT_LINES:
           amount_to_remove = len(self.output_lines) - MAX_OUTPUT_LINES
           self.output_lines = self.output_lines[amount_to_remove:] # Keep only the newest lines
           # Adjust scroll offset if we removed lines currently visible or above
           self.scroll_offset = max(0, self.scroll_offset - amount_to_remove)

        # Auto-scroll to the bottom when new output is added
        # This ensures the user always sees the latest command results.
        if self.is_visible: # Only scroll if window is currently visible
            self.scroll_to_bottom()

        # Clickable regions are recalculated during the draw phase.


    def scroll_to_bottom(self):
        """Calculates and sets the scroll_offset to view the latest lines."""
        total_lines = len(self.output_lines)
        # Max lines display might change if window resized, recalculate defensively
        self.max_lines_display = max(1, (self.content_rect.height // self.line_height) - 1) if self.line_height > 0 else 1
        # Maximum scroll offset is the number of lines hidden above the visible area
        max_scroll = max(0, total_lines - self.max_lines_display)
        self.scroll_offset = max_scroll # Set offset to max to show the bottom

    # --- Clipboard Interaction ---

    def _get_clipboard_text(self):
        """Safely retrieves text from the system clipboard. Returns the text string or None if unavailable/failed."""
        clipboard_text = None
        try:
            # Crucial check: ensure pygame.scrap was initialized successfully in main.py
            if not pygame.scrap.get_init():
                #print("Scrap not initialized, cannot get clipboard.") # Optional debug
                return None

            # pygame.scrap operates with bytes, get text content type
            clipboard_bytes = pygame.scrap.get(pygame.SCRAP_TEXT)
            if clipboard_bytes:
                # Decode bytes into a string. Start with UTF-8, fallback if needed.
                try:
                    clipboard_text = clipboard_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        # Attempt decoding using system locale (might work sometimes)
                        clipboard_text = clipboard_bytes.decode(pygame.scrap.get_locale())
                    except (UnicodeDecodeError, TypeError, AttributeError):
                        try:
                             # Fallback to latin-1, ignoring errors (might mangle some chars)
                             clipboard_text = clipboard_bytes.decode('latin-1', errors='ignore')
                        except UnicodeDecodeError:
                             # Should be very rare if latin-1 ignore is used
                             print("Clipboard decode failed with multiple encoding attempts.")
            # else: print("Clipboard is empty.") # Optional debug

        except (AttributeError, pygame.error, NotImplementedError) as e:
            # Handle cases where scrap is not supported or failed during init/get
            # print(f"Clipboard access error (pygame.scrap): {e}") # Optional debug
            pass
        except Exception as e:
            # Catch any other unexpected errors during clipboard access
            print(f"Unexpected clipboard get error: {e}")

        # *** Final sanity check for null characters in clipboard text ***
        if clipboard_text and '\x00' in clipboard_text:
            print("Warning: Null character detected in clipboard text, removing.")
            clipboard_text = clipboard_text.replace('\x00', '')

        return clipboard_text

    def _paste_into_input(self, game_state):
         """Handles pasting text from clipboard into the terminal input buffer."""
         pasted_text = self._get_clipboard_text() # Get text from clipboard (already sanitized for null)
         if pasted_text:
             # --- Sanitize Pasted Text ---
             # Remove newline/carriage return characters to prevent multi-line pastes
             pasted_text = pasted_text.replace('\n', '').replace('\r', '')
             # Optional: Could add more sanitization (e.g., remove tabs, limit length)

             # Insert the sanitized text at the current cursor position
             self.input_buffer = self.input_buffer[:self.cursor_pos] + pasted_text + self.input_buffer[self.cursor_pos:]
             # Move the cursor position past the newly inserted text
             self.cursor_pos += len(pasted_text)
             # Make cursor visible immediately after paste action
             self.cursor_visible = True
             self.last_cursor_toggle = time.time()
             print(f"Pasted text into terminal input.") # Log paste action
             return True
         else:
              # Don't add message to terminal on paste fail, just log it.
              print("Paste failed: Clipboard unavailable, empty, or paste error.")
              return False


    # --- Event Handling Methods ---

    def handle_input(self, event, game_state):
        """Handles KEYDOWN events related to typing in the input buffer, command history, and submission."""
        # This method is ONLY called for KEYDOWN events when the terminal is the active window
        # and the event wasn't consumed by terminal.handle_event (e.g. mouse scroll).
        if not self.is_visible or not self.font or event.type != pygame.KEYDOWN:
             return False

        key = event.key     # Key code (e.g., pygame.K_RETURN)
        mod = event.mod     # Modifier keys state (e.g., pygame.KMOD_CTRL)

        # --- Command Execution (Enter Key) ---
        if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
             # *** Clean input buffer BEFORE adding to output and processing ***
            safe_input = self.input_buffer.replace('\x00', '')
            full_command = safe_input # Use the sanitized version

            # Add the prompt + entered command to the output history
            self.add_output(self.prompt + full_command, settings.COLOR_TERMINAL_TEXT, game_state)

            trimmed_command = full_command.strip() # Use trimmed version for logic/history

            # Clear the input buffer and reset cursor position *after* adding to output
            self.input_buffer = ""
            self.cursor_pos = 0

            # Only process/add to history if the command wasn't empty
            if trimmed_command:
                # Add to command history only if it's different from the last command
                if not self.command_history or self.command_history[-1] != trimmed_command:
                    self.command_history.append(trimmed_command)
                    # Limit the size of the command history queue
                    if len(self.command_history) > settings.TERMINAL_MAX_HISTORY:
                        self.command_history.pop(0) # Remove the oldest command
                # Execute the command via the main GameState
                is_exit = game_state.execute_command(trimmed_command)
            else:
                 is_exit = False # Empty command doesn't exit

            # Reset command history navigation index after any command execution
            self.history_index = -1
            self.current_input_on_nav_start = ""
            return is_exit # Return True if 'exit' was typed

        # --- Text Manipulation Keys ---
        elif key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0: # Delete character before cursor
                 self.input_buffer = self.input_buffer[:self.cursor_pos-1] + self.input_buffer[self.cursor_pos:]
                 self.cursor_pos -= 1
        elif key == pygame.K_DELETE:
            if self.cursor_pos < len(self.input_buffer): # Delete character at/after cursor
                self.input_buffer = self.input_buffer[:self.cursor_pos] + self.input_buffer[self.cursor_pos+1:]
        elif key == pygame.K_LEFT: # Move cursor left
             self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == pygame.K_RIGHT: # Move cursor right
             self.cursor_pos = min(len(self.input_buffer), self.cursor_pos + 1)
        elif key == pygame.K_HOME: # Move cursor to start of line
             self.cursor_pos = 0
        elif key == pygame.K_END: # Move cursor to end of line
             self.cursor_pos = len(self.input_buffer)

        # --- Command History Navigation (Up/Down Arrows) ---
        elif key == pygame.K_UP:
             if self.command_history: # Only if history exists
                 if self.history_index == -1: # If starting history navigation
                     self.current_input_on_nav_start = self.input_buffer
                     self.history_index = len(self.command_history) - 1
                 elif self.history_index > 0: # Move to the previous (older) command
                     self.history_index -= 1
                 # Use try-except to prevent crash if history_index becomes invalid
                 try:
                      self.input_buffer = self.command_history[self.history_index]
                      self.cursor_pos = len(self.input_buffer)
                 except IndexError:
                      print("Warning: History index out of bounds (Up). Resetting.")
                      self.history_index = -1 # Reset navigation state
        elif key == pygame.K_DOWN:
             if self.history_index != -1: # If currently navigating history
                 if self.history_index < len(self.command_history) - 1: # Move to the next (newer) command
                     self.history_index += 1
                     try:
                         self.input_buffer = self.command_history[self.history_index]
                     except IndexError:
                         print("Warning: History index out of bounds (Down). Resetting.")
                         self.history_index = -1 # Reset navigation state
                 else: # Reached the newest command, restore the original input
                     self.history_index = -1
                     self.input_buffer = self.current_input_on_nav_start
                 self.cursor_pos = len(self.input_buffer)

        # --- Pasting (Ctrl+V / Cmd+V) ---
        # This is generally handled in `handle_event`, but including it here for completeness
        # if it somehow slips through. Pasting is NOT usually a simple KEYDOWN unicode event.
        # Best handled via MOUSEBUTTONDOWN (right-click) or specific key combo checks in handle_event.
        elif key == pygame.K_v and (mod & pygame.KMOD_CTRL or mod & pygame.KMOD_META):
            # Pass control back to handle_event or call paste directly
            # Calling _paste_into_input here might duplicate if called by handle_event too.
            # It's safer to let handle_event manage paste.
             print("Terminal handle_input ignoring Ctrl+V (handled by main event loop).")
             pass


        # --- Typing Printable Characters ---
        # event.unicode contains the actual character, respecting Shift/Capslock
        # Filter out non-printable characters explicitly, although event.unicode should usually be safe.
        # Disallow null character '\x00' specifically.
        elif event.unicode and event.unicode.isprintable() and '\x00' not in event.unicode:
             # Insert the character at the cursor position
             self.input_buffer = self.input_buffer[:self.cursor_pos] + event.unicode + self.input_buffer[self.cursor_pos:]
             # Move cursor position forward
             self.cursor_pos += 1
        elif event.unicode and '\x00' in event.unicode:
             print("Warning: Ignored attempt to input null character.")


        # --- Reset Cursor Blink on Key Action ---
        # If any significant key modifying the input buffer or cursor position was pressed
        # (excludes modifiers like Shift, Ctrl, Alt)
        non_modifier_keys = (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL,
                             pygame.K_LALT, pygame.K_RALT, pygame.K_LMETA, pygame.K_RMETA,
                             pygame.K_CAPSLOCK, pygame.K_NUMLOCK, pygame.K_SCROLLOCK,
                             pygame.K_MODE, pygame.K_HELP, pygame.K_PRINT, pygame.K_SYSREQ,
                             pygame.K_BREAK, pygame.K_MENU, pygame.K_POWER, pygame.K_EURO)
        if key not in non_modifier_keys:
             self.cursor_visible = True
             self.last_cursor_toggle = time.time()

        return False # Default: typing input does not cause game exit


    def handle_event(self, event, mouse_pos):
        """Handles MOUSE events (drag, close, paste, scroll, clicks on content) for the terminal window."""
        # THIS METHOD IS NOW PRIMARILY FOR MOUSE AND WINDOW-SPECIFIC EVENTS.
        # KEYBOARD TYPING IS HANDLED BY `handle_input`.
        if not self.is_visible: return False

        local_mouse_pos = (mouse_pos[0] - self.window_rect.left, mouse_pos[1] - self.window_rect.top)
        handled = False

        # MOUSE BUTTON DOWN events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # --- Right Mouse Button (Paste) ---
            if event.button == 3: # Right-click
                if self.content_rect.collidepoint(local_mouse_pos):
                     # Check if pygame.scrap is initialized
                     if pygame.scrap.get_init():
                          # Get clipboard text safely using the helper method
                          clipboard_content = self._get_clipboard_text()
                          if clipboard_content:
                              # Insert pasted text (handle_input is not called for mouse events)
                              pasted_text = clipboard_content.replace('\n', '').replace('\r', '') # Sanitize
                              self.input_buffer = self.input_buffer[:self.cursor_pos] + pasted_text + self.input_buffer[self.cursor_pos:]
                              self.cursor_pos += len(pasted_text)
                              self.cursor_visible = True; self.last_cursor_toggle = time.time()
                              print("Pasted via right-click.")
                              handled = True
                          else:
                              print("Clipboard empty or unavailable for paste.")
                              handled = True # Consume click even if paste fails
                     else:
                          print("Paste unavailable: Clipboard (scrap) not initialized.")
                          handled = True # Consume click

            # --- Left Mouse Button ---
            elif event.button == 1: # Left-click
                if self.close_button_rect and self.close_button_rect.collidepoint(local_mouse_pos):
                    self.hide()
                    handled = True
                elif self.title_bar_rect.collidepoint(local_mouse_pos):
                    self.is_dragging = True
                    self.drag_offset_x = mouse_pos[0] - self.window_rect.left
                    self.drag_offset_y = mouse_pos[1] - self.window_rect.top
                    handled = True
                elif self.content_rect.collidepoint(local_mouse_pos):
                    # Click within content area - check for clickable links FIRST
                    item_clicked = False
                    for region_rect, info in self.clickable_regions:
                        # Collision check uses GLOBAL mouse position vs screen rect
                        if region_rect.collidepoint(mouse_pos):
                            click_type = info['type']; click_text = info['text']
                            print(f"Clicked terminal '{click_type}': '{click_text[:40]}...'")

                            # Try to copy to clipboard
                            try:
                                if pygame.scrap.get_init():
                                     safe_click_text = click_text.replace('\x00', '')
                                     pygame.scrap.put(pygame.SCRAP_TEXT, safe_click_text.encode('utf-8'))
                                     print(f"Copied '{click_type}' to clipboard.")
                            except Exception as e: print(f"Clipboard copy error on click: {e}")

                            # Trigger game logic associated with the click
                            # Need game_state reference for execute_command or adding output directly
                            game_state_ref = settings.GLOBAL_GAME_STATE # Assuming you have this global ref available
                            if game_state_ref:
                                if click_type == 'flag':
                                    game_state_ref.execute_command(f"submit {click_text}")
                                elif 'base64' in click_type:
                                    safe_click_text = click_text.replace('\x00', '')
                                    self.input_buffer = f"decode64 {safe_click_text}"
                                    self.cursor_pos = len(self.input_buffer)
                                    self.add_output(f"Prepared 'decode64' for clicked text.", settings.COLOR_HINT_TEXT, game_state_ref)
                                    self.cursor_visible = True; self.last_cursor_toggle = time.time()
                            else:
                                print("Warning: GameState reference missing for terminal click action.")


                            item_clicked = True
                            handled = True
                            break # Stop checking after first hit
                    if not item_clicked:
                        # If click was inside content but not on a link, consume it anyway
                        handled = True

            # --- Mouse Wheel Scroll ---
            # Scroll events ARE MOUSEBUTTONDOWN with buttons 4 (up) and 5 (down)
            elif event.button == 4 or event.button == 5:
                 if self.content_rect.collidepoint(local_mouse_pos):
                     scroll_speed = 3 # Number of lines to scroll per wheel tick
                     if event.button == 4: # Wheel UP -> Scroll content DOWN (increase offset)
                         self.scroll(scroll_speed) # <<< CORRECTED: Use positive amount
                     else: # Wheel DOWN -> Scroll content UP (decrease offset)
                         self.scroll(-scroll_speed) # <<< CORRECTED: Use negative amount
                     handled = True


        # MOUSE BUTTON UP events
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging: # Left button up
                 self.is_dragging = False
                 handled = True

        # MOUSE MOTION events
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                new_x = mouse_pos[0] - self.drag_offset_x
                new_y = mouse_pos[1] - self.drag_offset_y
                self.window_rect.topleft = (new_x, new_y)
                screen_rect = pygame.display.get_surface().get_rect()
                self.window_rect.clamp_ip(screen_rect)
                handled = True

        # KEYDOWN/KEYUP should be handled by game_state passing to handle_input
        # If a key event somehow reaches here and wasn't handled, it's likely safe to ignore.

        return handled # Return True if handled by MOUSE interactions


    # --- Update and Draw Methods ---

    def update_cursor(self):
        """Updates the visibility state of the blinking cursor based on time."""
        if not self.is_visible: return # No need to update if terminal is hidden
        now = time.time()
        # Check if enough time has passed since the last toggle
        if now - self.last_cursor_toggle > settings.CURSOR_BLINK_RATE:
            self.cursor_visible = not self.cursor_visible # Flip visibility state
            self.last_cursor_toggle = now # Reset timer


    def draw(self, surface):
        """Draws the complete terminal window (frame, content, input, cursor, scrollbar)
           onto the main screen surface."""
        if not self.is_visible or not self.window_surface or not self.font:
             return

        # 1. Redraw the static window frame
        self._redraw_frame()

        # 2. Create a subsurface for the content area.
        content_surface = None
        try:
             # Prevent subsurface creation if dimensions are invalid (0 or negative)
             if self.content_rect.width > 0 and self.content_rect.height > 0:
                  content_surface = self.window_surface.subsurface(self.content_rect)
                  content_surface.fill(settings.COLOR_TERMINAL_BG)
             else:
                  # If dimensions are bad, just draw the frame and exit drawing for terminal
                  surface.blit(self.window_surface, self.window_rect.topleft)
                  return
        except ValueError as e:
             # This catch handles cases where rect might be invalid (e.g., outside parent)
             print(f"Error creating terminal subsurface (maybe invalid rect: {self.content_rect}): {e}")
             surface.blit(self.window_surface, self.window_rect.topleft); return

        # 3. --- Draw Output Lines ---
        self.clickable_regions.clear() # Clear regions before redrawing
        line_x_start = 5
        total_lines = len(self.output_lines)
        # Ensure max_lines is at least 1 and based on current rect/font height
        self.max_lines_display = max(1, (self.content_rect.height // self.line_height) - 1) if self.line_height > 0 else 1
        # Clamp scroll offset to valid range [0, max_scroll]
        max_scroll = max(0, total_lines - self.max_lines_display)
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

        # Determine which lines are visible based on scroll offset
        start_index = max(0, total_lines - self.max_lines_display - self.scroll_offset)
        end_index = min(total_lines, start_index + self.max_lines_display)
        lines_to_render = self.output_lines[start_index:end_index]

        current_draw_y = 0 # Y position relative to the content_surface
        for i, (line_text, line_color, clickable_info) in enumerate(lines_to_render):
            # Ensure line doesn't draw past the bottom edge of the content area
            # Adjust check slightly to ensure full line visibility
            if current_draw_y + self.line_height > self.content_rect.height:
                 break

            # *** Clean line text JUST before rendering output lines too ***
            safe_render_text = line_text.replace('\x00', '')

            try:
                if clickable_info:
                    # Render clickable lines segment by segment
                    pre_text = clickable_info.get('pre_text', '').replace('\x00', '')
                    click_text = clickable_info.get('text', '').replace('\x00', '')
                    post_text = clickable_info.get('post_text', '').replace('\x00', '')
                    click_type=clickable_info['type']
                    click_color_map = {'flag': settings.COLOR_FLAG_CLICKABLE,
                                       'base64_l3': settings.COLOR_B64_CLICKABLE,
                                       'base64_l5': settings.COLOR_B64_CLICKABLE} # More specific map keys
                    clickable_color = click_color_map.get(click_type, settings.COLOR_HINT_TEXT)

                    # Render each segment
                    pre_surf = self.font.render(pre_text, True, line_color)
                    click_surf = self.font.render(click_text, True, clickable_color)
                    post_surf = self.font.render(post_text, True, line_color)

                    # Draw segments sequentially
                    current_x = line_x_start
                    content_surface.blit(pre_surf, (current_x, current_draw_y))
                    current_x += pre_surf.get_width()

                    # Calculate SCREEN coordinates for the clickable part for mouse interaction
                    click_screen_rect = pygame.Rect(
                        self.window_rect.left + self.content_rect.left + current_x, # Global X
                        self.window_rect.top + self.content_rect.top + current_draw_y, # Global Y
                        click_surf.get_width(), click_surf.get_height())
                    self.clickable_regions.append((click_screen_rect, clickable_info)) # Store clickable region

                    content_surface.blit(click_surf, (current_x, current_draw_y))
                    current_x += click_surf.get_width()
                    content_surface.blit(post_surf, (current_x, current_draw_y))
                else:
                    # Render the safe version of the normal line
                    text_surface = self.font.render(safe_render_text, True, line_color)
                    content_surface.blit(text_surface, (line_x_start, current_draw_y))
            except pygame.error as e:
                # Log rendering errors with more context
                print(f"Terminal line render pygame error: {e} on text '{safe_render_text[:50]}...'")
            except Exception as e: print(f"Terminal line render generic error: {e}")

            current_draw_y += self.line_height


        # 4. --- Draw Input Line ---
        input_y = self.content_rect.height - self.line_height # Y position for the input line at the bottom
        # Only draw if it fits within the content rect height
        if input_y >= 0:
             try:
                # --- Clean ALL strings JUST before rendering input line ---
                safe_prompt = self.prompt.replace('\x00', '')
                safe_buffer = self.input_buffer.replace('\x00', '')
                # Ensure cursor position is valid for the potentially cleaned buffer
                safe_pos = min(self.cursor_pos, len(safe_buffer))

                # Render prompt
                prompt_surf = self.font.render(safe_prompt, True, settings.COLOR_TERMINAL_TEXT)

                # Render text segments before and after the cursor
                text_before_cursor = safe_buffer[:safe_pos]
                text_after_cursor = safe_buffer[safe_pos:]
                surf_before = self.font.render(text_before_cursor, True, settings.COLOR_TERMINAL_TEXT)
                surf_after = self.font.render(text_after_cursor, True, settings.COLOR_TERMINAL_TEXT)

                prompt_width = prompt_surf.get_width()
                before_width = surf_before.get_width()
                # Starting X position for the text buffer (after the prompt)
                input_start_x = line_x_start + prompt_width

                # --- Blit Input Line Components ---
                # Blit the prompt string
                content_surface.blit(prompt_surf, (line_x_start, input_y))
                # Blit the text typed before the cursor
                content_surface.blit(surf_before, (input_start_x, input_y))

                # --- Draw Cursor (if visible) ---
                if self.cursor_visible:
                    # Calculate cursor's X position
                    cursor_x = input_start_x + before_width
                    # Define cursor rectangle (vertical bar)
                    cursor_rect = pygame.Rect(cursor_x, input_y + 1, 2, self.line_height - 2) # Slightly padded vertically
                    pygame.draw.rect(content_surface, settings.COLOR_TERMINAL_TEXT, cursor_rect)

                # Blit the text typed after the cursor
                after_x = input_start_x + before_width
                content_surface.blit(surf_after, (after_x, input_y))

             except pygame.error as e:
                 print(f"Input line render error: {e}. Prompt='{safe_prompt}', Before='{text_before_cursor}', After='{text_after_cursor}'")
             except Exception as e: print(f"Unexpected Input line render error: {e}")


        # 5. --- Draw Scroll Bar ---
        # Only draw scrollbar if content height exceeds visible area
        if total_lines > self.max_lines_display:
            # --- Scroll Bar Dimensions ---
            scroll_bar_area_height = self.content_rect.height # Height of the track
            visible_ratio = self.max_lines_display / total_lines if total_lines > 0 else 1 # Portion visible
            bar_height = max(15, scroll_bar_area_height * visible_ratio) # Calc height, min size 15
            # --- Scroll Bar Position ---
            scroll_range_pixels = scroll_bar_area_height - bar_height # Pixel range bar can move
            # Calculate scroll position ratio (0.0 top, 1.0 bottom)
            bar_y_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            # Convert ratio to pixel position
            bar_y = bar_y_ratio * scroll_range_pixels
            scroll_bar_width = 6 # Fixed width
            # --- Scroll Bar Rect ---
            scroll_bar_rect = pygame.Rect(self.content_rect.width - scroll_bar_width - 2, # Right align X
                                           bar_y, scroll_bar_width, bar_height)
            # Draw the scroll bar rectangle
            try:
                pygame.draw.rect(content_surface, settings.COLOR_TASKBAR, scroll_bar_rect, border_radius=3)
            except pygame.error as draw_err: print(f"Scrollbar draw error: {draw_err}")


        # 6. --- Final Blit ---
        # Draw the completed terminal window surface onto the main screen
        surface.blit(self.window_surface, self.window_rect.topleft)


    def scroll(self, direction_amount_lines):
        """Scrolls the terminal output view up or down by a specified number of lines."""
        # Ensure calculations are safe
        if not self.font or self.line_height <= 0: return

        total_lines = len(self.output_lines)
        # Recalculate max_lines_display in case window resized
        self.max_lines_display = max(1, (self.content_rect.height // self.line_height) - 1)
        # Maximum scroll offset (number of lines scrolled off the top)
        max_scroll = max(0, total_lines - self.max_lines_display)

        # Calculate the new proposed scroll offset
        new_offset = self.scroll_offset + direction_amount_lines
        # Clamp the new offset within the valid range [0, max_scroll]
        self.scroll_offset = max(0, min(max_scroll, new_offset))

        # Clear clickable regions as they are position-dependent and need recalculation on draw
        self.clickable_regions.clear()

    def prepare_rtl_text(text):
        """Process text for RTL rendering"""
    # Split into paragraphs and reverse each line
        paragraphs = text.split('\n')
        processed = [p[::-1] for p in paragraphs]
        return '\n'.join(processed)

# --- END OF FILE terminal.py ---