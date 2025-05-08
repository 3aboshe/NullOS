# --- START OF FILE password_window.py ---

# password_window.py
import pygame
import settings  # Access settings for sizes, colors, fonts
import time      # Used for the blinking cursor effect

class PasswordWindow:
    """A pop-up window for entering passwords, typically for simulated file decryption/unzipping."""

    def __init__(self, game_state):
        """Initializes the password window."""
        # Keep a reference to the main GameState object.
        # This is needed to call the actual unzip/decryption logic defined in GameState.
        self.game_state = game_state
        self.is_visible = False        # Is the window currently displayed?
        self.window_surface = None     # The Pygame Surface object for drawing the window content

        # --- Window Geometry ---
        # Set initial size based on settings, position centered on screen.
        self.window_rect = pygame.Rect(0, 0, *settings.PASSWORD_WINDOW_SIZE)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

        # --- Window Content & State ---
        self.title = "Password Required"   # Default window title
        self.prompt_text = ""              # Text displayed above input field (e.g., "Password for file:")
        self.password_buffer = ""          # Stores the actual password characters typed by the user
        self.target_zip_file = ""          # Stores the name of the file this password prompt relates to

        # --- Internal UI Element Rectangles ---
        # These are calculated dynamically in _calculate_layout based on window size and content.
        self.label_surf = None             # Rendered Surface for the prompt_text label
        self.label_rect = None             # Rect for positioning the label_surf
        self.input_field_rect = None       # Rect defining the password input box area
        self.extract_button_rect = None    # Rect for the "Extract" or "OK" button
        self.cancel_button_rect = None     # Rect for the "Cancel" button

        # --- Input State ---
        self.cursor_visible = True         # Flag for blinking cursor visibility
        self.last_cursor_toggle = time.time() # Timestamp of the last cursor visibility toggle
        self.cursor_pos = 0                # Current character position of the cursor within the password_buffer

        # --- Font Setup ---
        self.ui_font = settings.UI_FONT          # Font for labels and buttons
        self.input_font = settings.TERMINAL_FONT # Use monospace font for password field (consistency)
        if not self.ui_font or not self.input_font:
            print("ERROR: PasswordWindow requires UI_FONT and TERMINAL_FONT.")
            # Provide basic fallback fonts if settings ones failed
            self.ui_font = self.ui_font or pygame.font.SysFont("sans", 14)
            self.input_font = self.input_font or pygame.font.SysFont("monospace", 16)

    def _calculate_layout(self):
        """Calculates the positions and sizes of internal UI elements (label, input field, buttons)
           relative to the window's current dimensions."""
        padding = 15  # General padding from window edges and between elements
        label_y = padding  # Y position to start drawing the label

        # Label position: needs to be rendered first to get its height
        label_height = self.label_rect.height if self.label_rect else 20 # Use rendered height or estimate
        input_y = label_y + label_height + 10  # Y position for input field, below label with spacing

        # Input Field: Spans most of window width, standard height
        input_h = self.input_font.get_height() + 10 # Height based on font + padding
        input_w = self.window_rect.width - 2 * padding # Width minus left/right padding
        self.input_field_rect = pygame.Rect(padding, input_y, input_w, input_h)

        # Buttons: Positioned below the input field
        button_h = 30              # Fixed height for buttons
        button_w = 80              # Fixed width for buttons
        button_y = input_y + input_h + 15 # Y position for buttons, below input field
        button_spacing = 20       # Horizontal space between buttons

        # Calculate horizontal starting position to center the two buttons
        total_button_width = button_w * 2 + button_spacing
        buttons_start_x = (self.window_rect.width - total_button_width) // 2 # Center calculation
        # Define rectangles for Cancel and Extract buttons
        self.cancel_button_rect = pygame.Rect(buttons_start_x, button_y, button_w, button_h)
        self.extract_button_rect = pygame.Rect(buttons_start_x + button_w + button_spacing, button_y, button_w, button_h)

        # Optional: Dynamically adjust window height if content requires more space.
        # Keep fixed size for now based on settings.PASSWORD_WINDOW_SIZE.
        # required_height = button_y + button_h + padding
        # self.window_rect.height = max(settings.PASSWORD_WINDOW_SIZE[1], required_height)


    def _render_static_elements(self):
        """Pre-renders the text label surface ('Password for...') to optimize drawing."""
        if not self.ui_font: return # Cannot render without font
        try:
            # Render the label text (using self.prompt_text which is updated in show())
            self.label_surf = self.ui_font.render(self.prompt_text, True, settings.COLOR_WHITE)
            # Calculate the rectangle for the label, centering it horizontally near the top
            self.label_rect = self.label_surf.get_rect(centerx=self.window_rect.width // 2, top=15)
        except Exception as e:
            # Catch potential rendering errors (e.g., font issues)
            print(f"Error rendering password window label: {e}")
            self.label_surf = None
            self.label_rect = None # Ensure rect is also None if rendering failed

    def show(self, target_file):
        """Makes the password window visible and prepares it for the specified target file."""
        # Essential check: Cannot function without necessary fonts
        if not self.ui_font or not self.input_font:
            print("Cannot show PasswordWindow: Required fonts missing.")
            return

        self.target_zip_file = target_file                 # Store the filename (e.g., "encrypted.zip")
        self.prompt_text = f"Password for '{self.target_zip_file}':" # Update the label text
        self.password_buffer = ""                          # Clear any previous password input
        self.cursor_pos = 0                                # Reset cursor position
        self.is_visible = True                             # Mark the window as visible
        print(f"Password prompt shown for '{self.target_zip_file}'")

        # --- Recalculate Geometry and Layout ---
        # Ensure window uses the standard size from settings
        self.window_rect.size = settings.PASSWORD_WINDOW_SIZE
        # Re-center the window on the screen (important if screen resolution changed)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        # Render the label surface first (needed for layout calculation)
        self._render_static_elements()
        # Calculate positions of input field and buttons based on new size/label
        self._calculate_layout()

        # --- Create Drawing Surface ---
        try:
            # Create the surface with SRCALPHA for potential transparency effects
            self.window_surface = pygame.Surface(self.window_rect.size, pygame.SRCALPHA)
            # Background filling and borders are handled within the main draw() method
        except (pygame.error, ValueError) as e:
             print(f"Error creating PasswordWindow surface: {e}")
             self.hide() # Hide window immediately if surface creation fails
             return

    def hide(self):
        """Hides the password window and resets its state."""
        if self.is_visible: print("Password prompt hidden.")
        self.is_visible = False
        self.window_surface = None   # Release the Surface object to free memory
        self.password_buffer = ""    # Clear password
        self.target_zip_file = ""    # Clear target file info


    def handle_event(self, event, mouse_pos):
        """Handles input events (keyboard typing, button clicks) specifically for the password window."""
        if not self.is_visible: return False # Ignore events if not visible

        # Convert global mouse coordinates to coordinates relative to the password window
        local_mouse_pos = (mouse_pos[0] - self.window_rect.left, mouse_pos[1] - self.window_rect.top)
        handled = False # Flag to indicate if this event was processed by the password window

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button clicked
                # --- Check Button Clicks ---
                if self.extract_button_rect and self.extract_button_rect.collidepoint(local_mouse_pos):
                    # Clicked the "Extract" button
                    print(f"Attempting extract for '{self.target_zip_file}' via Extract button...")
                    # Call the game_state's unzip logic with the current password buffer
                    self.game_state._attempt_unzip(self.password_buffer)
                    self.hide() # Close the password window after attempt
                    handled = True
                elif self.cancel_button_rect and self.cancel_button_rect.collidepoint(local_mouse_pos):
                    # Clicked the "Cancel" button
                    print("Password prompt cancelled via Cancel button.")
                    self.hide() # Close the password window
                    handled = True
                # Clicking anywhere inside the input field (currently just consumes the click)
                elif self.input_field_rect and self.input_field_rect.collidepoint(local_mouse_pos):
                    # Potential future use: set focus, move cursor based on click position
                    handled = True
                # Clicking anywhere else within the window's bounds (title bar, background)
                elif self.window_rect.collidepoint(mouse_pos): # Check using global coordinates here
                     # Consumes the click to prevent interaction with elements underneath
                     handled = True


        elif event.type == pygame.KEYDOWN: # Handle keyboard input
            key = event.key # The key code that was pressed

            # --- Enter Key: Submit Password ---
            if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                print(f"Attempting extract for '{self.target_zip_file}' via Enter key...")
                # Call game_state logic, same as Extract button
                self.game_state._attempt_unzip(self.password_buffer)
                self.hide()
                handled = True

            # --- Escape Key: Cancel ---
            elif key == pygame.K_ESCAPE:
                 print("Password prompt cancelled via Escape key.")
                 self.hide()
                 handled = True

            # --- Backspace Key: Delete Character Before Cursor ---
            elif key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0: # Only if cursor is not at the beginning
                    # Remove character before the cursor
                    self.password_buffer = self.password_buffer[:self.cursor_pos-1] + self.password_buffer[self.cursor_pos:]
                    self.cursor_pos -= 1 # Move cursor back
                handled = True

            # --- Delete Key: Delete Character At/After Cursor ---
            elif key == pygame.K_DELETE:
                 if self.cursor_pos < len(self.password_buffer): # Only if cursor is not at the end
                     # Remove character at the cursor position
                     self.password_buffer = self.password_buffer[:self.cursor_pos] + self.password_buffer[self.cursor_pos+1:]
                     # Cursor position does not change relative to remaining text
                 handled = True

            # --- Arrow Keys: Move Cursor ---
            elif key == pygame.K_LEFT:
                 self.cursor_pos = max(0, self.cursor_pos - 1) # Move left, clamp at 0
                 handled = True
            elif key == pygame.K_RIGHT:
                 self.cursor_pos = min(len(self.password_buffer), self.cursor_pos + 1) # Move right, clamp at end
                 handled = True

            # --- Home/End Keys: Move Cursor to Extremes ---
            elif key == pygame.K_HOME:
                 self.cursor_pos = 0 # Move to beginning
                 handled = True
            elif key == pygame.K_END:
                 self.cursor_pos = len(self.password_buffer) # Move to end
                 handled = True

            # --- Printable Characters: Insert into Buffer ---
            # event.unicode captures the actual character typed, respecting Shift, etc.
            elif event.unicode.isprintable():
                 # Optional: Limit password length?
                 # if len(self.password_buffer) < settings.MAX_PASSWORD_LENGTH:
                 # Insert the typed character at the cursor position
                 self.password_buffer = self.password_buffer[:self.cursor_pos] + event.unicode + self.password_buffer[self.cursor_pos:]
                 self.cursor_pos += 1 # Move cursor forward
                 handled = True

            # --- Cursor Blinking Reset ---
            # After any key press that affects input, reset the cursor blink timer to make it visible
            if handled: # Check if any of the above keyboard actions occurred
                self.cursor_visible = True
                self.last_cursor_toggle = time.time()

        # Return True if the event was handled by this window, False otherwise
        return handled


    def draw(self, surface):
        """Draws the password input window onto the main screen surface."""
        # Don't draw if not visible or essential resources are missing
        if not self.is_visible or not self.window_surface or not self.ui_font or not self.input_font: return

        # --- Update Cursor Blink ---
        now = time.time()
        if now - self.last_cursor_toggle > settings.CURSOR_BLINK_RATE:
            self.cursor_visible = not self.cursor_visible # Toggle visibility
            self.last_cursor_toggle = now              # Reset timer

        # --- Redraw Window Background ---
        # Fill the window surface with the background color (semi-transparent)
        self.window_surface.fill(settings.POPUP_BG_COLOR)
        # Optional: Draw a border around the window
        # pygame.draw.rect(self.window_surface, settings.COLOR_WHITE, self.window_surface.get_rect(), 1)

        # --- Draw Text Label ---
        if self.label_surf and self.label_rect:
            # Blit the pre-rendered label surface onto the window surface
            self.window_surface.blit(self.label_surf, self.label_rect.topleft)

        # --- Draw Input Field Area ---
        if self.input_field_rect:
            # Draw the background rectangle for the input field
            pygame.draw.rect(self.window_surface, settings.COLOR_PASSWORD_INPUT_BG, self.input_field_rect)
            # Draw a border around the input field
            pygame.draw.rect(self.window_surface, settings.COLOR_PASSWORD_INPUT_BORDER, self.input_field_rect, 1)

            # --- Draw Password Text (as asterisks) ---
            try:
                # Create a string of asterisks representing the password buffer length
                password_display = "*" * len(self.password_buffer)
                # Render the asterisks using the input font
                pass_surf = self.input_font.render(password_display, True, settings.COLOR_WHITE)
                # Position the text slightly inside the input field, vertically centered
                text_padding_x = 5
                pass_rect = pass_surf.get_rect(left=self.input_field_rect.left + text_padding_x,
                                                centery=self.input_field_rect.centery)
                # Define a clipping rectangle to prevent text overflowing the input box boundaries
                clip_rect = self.input_field_rect.inflate(-text_padding_x * 2, -4) # Shrink rect for clipping
                # Apply clipping to the window surface before drawing text
                self.window_surface.set_clip(clip_rect)
                # Blit the password text (asterisks) onto the window surface (respecting clip)
                self.window_surface.blit(pass_surf, pass_rect.topleft)
                # Remove the clipping rectangle to allow drawing other elements normally
                self.window_surface.set_clip(None)

                # --- Draw Cursor ---
                if self.cursor_visible:
                     # Calculate the horizontal (X) position of the cursor based on the rendered width
                     # of the password characters (asterisks) *before* the cursor's logical position.
                    pre_cursor_text = "*" * self.cursor_pos
                    # Get width of text before cursor using the input font's size() method
                    cursor_x_offset = self.input_font.size(pre_cursor_text)[0]
                    # Calculate absolute X position within the input field
                    cursor_x = self.input_field_rect.left + text_padding_x + cursor_x_offset
                    # Define cursor dimensions (make it slightly shorter than the input field height)
                    cursor_height = self.input_field_rect.height - 6
                    cursor_y = self.input_field_rect.top + (self.input_field_rect.height - cursor_height) // 2 # Center vertically
                    cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, cursor_height) # Create cursor rectangle (width 2)

                    # Draw the cursor rectangle only if it's visually within the input field boundaries
                    # (This prevents drawing it if text exceeds the visible area, although it shouldn't with clipping)
                    if self.input_field_rect.contains(cursor_rect.inflate(2,0)): # Slightly inflate check width
                         pygame.draw.rect(self.window_surface, settings.COLOR_WHITE, cursor_rect)

            except Exception as e:
                # Catch potential errors during text rendering or cursor calculation
                print(f"Error rendering password input field content: {e}")

        # --- Draw Buttons ---
        # Get current mouse position to handle hover effects
        mouse_pos = pygame.mouse.get_pos() # Global mouse position
        # Convert to window-local coordinates for button collision checks
        local_mouse_pos = (mouse_pos[0] - self.window_rect.left, mouse_pos[1] - self.window_rect.top)

        # Cancel Button Drawing
        if self.cancel_button_rect:
            # Check if mouse is hovering over the cancel button
            is_cancel_hover = self.cancel_button_rect.collidepoint(local_mouse_pos)
            # Select appropriate color based on hover state
            cancel_color = settings.COLOR_CANCEL_BUTTON_HOVER if is_cancel_hover else settings.COLOR_CANCEL_BUTTON
            # Draw the button rectangle with rounded corners
            pygame.draw.rect(self.window_surface, cancel_color, self.cancel_button_rect, border_radius=3)
            # Draw the button text ("Cancel") centered on the button
            try:
                cancel_text_surf = self.ui_font.render("Cancel", True, settings.COLOR_CANCEL_BUTTON_TEXT)
                cancel_text_rect = cancel_text_surf.get_rect(center=self.cancel_button_rect.center)
                self.window_surface.blit(cancel_text_surf, cancel_text_rect)
            except Exception as e: print(f"Error rendering Cancel button text: {e}")

        # Extract Button Drawing (Similar logic to Cancel button)
        if self.extract_button_rect:
            is_extract_hover = self.extract_button_rect.collidepoint(local_mouse_pos)
            extract_color = settings.COLOR_PASSWORD_BUTTON_HOVER if is_extract_hover else settings.COLOR_PASSWORD_BUTTON
            pygame.draw.rect(self.window_surface, extract_color, self.extract_button_rect, border_radius=3)
            # Draw the button text ("Extract") centered
            try:
                extract_text_surf = self.ui_font.render("Extract", True, settings.COLOR_PASSWORD_BUTTON_TEXT)
                extract_text_rect = extract_text_surf.get_rect(center=self.extract_button_rect.center)
                self.window_surface.blit(extract_text_surf, extract_text_rect)
            except Exception as e: print(f"Error rendering Extract button text: {e}")

        # --- Final Blit ---
        # Draw the fully rendered password window surface onto the main game screen surface
        surface.blit(self.window_surface, self.window_rect.topleft)

# --- END OF FILE password_window.py ---