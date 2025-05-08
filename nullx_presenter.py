# --- START REPLACEMENT CODE for nullx_presenter.py ---

# nullx_presenter.py
import pygame
import settings           # Access settings for paths, fonts, colors, sounds
import os
import time
from nullx_dialogue import NULLX_DIALOGUE # Import the dialogue data structure
from nullx_dialogue import NULLX_DIALOGUE as NULLX_DIALOGUE_EN
from nullx_dialogue_ar import NULLX_DIALOGUE as NULLX_DIALOGUE_AR
# Removed incorrect/redundant imports and the relative import below
import arabic_reshaper
from bidi.algorithm import get_display
print("ء آ أ إ ئ ؤ ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن هـ و ي")


try:
    from nullx_dialogue_ar import NULLX_DIALOGUE as NULLX_DIALOGUE_AR
except ImportError:
    print("Warning: Arabic translations not found. Using English as fallback.")
    NULLX_DIALOGUE_AR = NULLX_DIALOGUE_EN
# No longer need relative import here, will use settings.CURRENT_LANGUAGE directly


class NullXPresenter:
    """Handles displaying the NullX character and associated dialogue text."""

    # --- Constants ---
    SCALE_FACTOR = 1.5 # How much to scale the original NullX images (e.g., 1.5 = 150%)
    TYPING_SPEED = 0.025 # Seconds between each character appearing in the dialogue text

    def __init__(self):
        """Initializes the NullX presenter state."""
        self.is_visible = False       # Is NullX currently being displayed?
        self.level_id = -1            # Which level's dialogue is currently loaded (-1 = none)
        self.dialogue_segments = []   # List of dialogue dictionaries for the current level
        self.current_segment_index = 0 # Index of the currently showing dialogue segment

        # Content of the current segment
        self.current_text = ""          # The full text of the current segment
        self.current_image_name = None  # Filename of the current NullX image
        self.current_image_surface = None # The *scaled* Surface object for the current image

        # Font setup (Crucial for rendering text)
        self.font = settings.PIXEL_FONT # Use the specific pixel font defined in settings
        if not self.font:
            # Fallback if pixel font failed to load (use UI font or system default)
            print("ERROR: NullXPresenter pixel font missing! Falling back to UI font.")
            self.font = settings.UI_FONT or pygame.font.SysFont("monospace", 16)

        # Text Animation State
        self.display_text = ""          # The portion of current_text actually shown so far
        self.char_index = 0             # Index of the next character to reveal in current_text
        self.time_since_last_char = 0   # Timer for character animation speed
        self.animation_complete = False # True when all characters of the current segment are shown

        # Positioning and Layout
        self.padding_from_edge = 20   # Distance from screen edges for NullX image
        self.nullx_image_pos = (0, 0) # Top-left screen coordinates of the scaled image

        # --- Speech Bubble Definition ---
        # These rectangles define the text area RELATIVE TO THE *ORIGINAL* (unscaled) NullX image dimensions.
        # The `draw` method scales these dynamically based on SCALE_FACTOR.
        # Adjust these values precisely based on where the speech bubble appears in your image files.
        # Format: { 'image_filename.png': pygame.Rect(left, top, width, height) }
        self.speech_bubble_rects = {
            'NullX_explaining.png': pygame.Rect(175, 15, 290, 155),
            'NullX_speaking.png':   pygame.Rect(175, 15, 290, 155),
            'NullX_Happy.png':      pygame.Rect(175, 15, 290, 155),
            'NullX_Cheering.png':   pygame.Rect(175, 15, 290, 155),
            'NullX_normal.png':     pygame.Rect(175, 15, 290, 155),
            'NullX_Wondering.png':  pygame.Rect(175, 15, 290, 155),
            'NullX_Sad.png':        pygame.Rect(175, 15, 290, 155),
            'NullX_angry.png':      pygame.Rect(175, 15, 290, 155),
            # Add entries for ALL NullX image files used in nullx_dialogue.py
        }
        # Store adjusted text drawing rect based on scaling and padding (calculated in draw)
        self.text_draw_rect = None

        # --- Continue Prompt ---
        self.continue_prompt_text = "[Click Here or on NullX to continue]"
        # Use a clear UI font for the prompt
        self.continue_prompt_font = settings.UI_FONT or self.font # Fallback to pixel font if UI font fails
        self.continue_prompt_rect = None # Calculated during draw when needed

        # Cache for loaded *original* image Surfaces to avoid reloading from disk
        self.image_cache = {}

        # --- Sound Control ---
        # Get the designated channel, handle potential init failure in settings
        self.dialogue_sound_channel = None
        if pygame.mixer and settings.DIALOGUE_CHANNEL != -1:
            try:
                self.dialogue_sound_channel = pygame.mixer.Channel(settings.DIALOGUE_CHANNEL)
            except pygame.error as e:
                print(f"Warning: Could not get dialogue channel ({settings.DIALOGUE_CHANNEL}): {e}")
        self.is_playing_dialogue_sound = False

    def _load_image(self, image_name):
        """Loads an original image, caches it, scales it, and returns the scaled surface."""
        if not image_name:
            print("Error: Attempted to load NullX image with no name."); return None

        scaled_image_surface = None
        original_image = None

        # Check cache first for the original image
        if image_name in self.image_cache:
            original_image = self.image_cache[image_name]
        else:
            # Image not in cache, load from disk
            image_path = settings.get_nullx_path(image_name) # Get full path using helper
            if not image_path or not os.path.exists(image_path):
                print(f"Error: NullX image file not found: {image_name} at path {image_path}"); return None
            try:
                # Load with alpha transparency
                original_image = pygame.image.load(image_path).convert_alpha()
                self.image_cache[image_name] = original_image # Store original in cache
                print(f"Loaded original NullX image: {image_name}")
            except pygame.error as e:
                print(f"Error loading original NullX image '{image_name}': {e}"); return None

        # Scale the original image if it was loaded successfully
        if original_image:
            try:
                original_size = original_image.get_size()
                # Calculate scaled dimensions, ensure they are at least 1x1
                scaled_width = max(1, int(original_size[0] * self.SCALE_FACTOR))
                scaled_height = max(1, int(original_size[1] * self.SCALE_FACTOR))
                # Use smooth scaling for better quality, though scale() is faster if needed
                scaled_image_surface = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
            except (pygame.error, ValueError) as e:
                print(f"Error scaling NullX image '{image_name}': {e}"); return None

        return scaled_image_surface

    # --- REPLACE THIS FUNCTION ---
    def start_presentation(self, level_id):
        """Loads dialogue for the specified level based on current language and starts presentation."""
        # Essential checks
        if not self.font:
            print("Cannot start NullX presentation: Required font missing.")
            return False
        if not self.dialogue_sound_channel and settings.SFX_ENABLED:
            print("Warning: NullX dialogue channel not available, sound will be skipped.")

        self.level_id = level_id

        # Choose the appropriate dialogue based on language
        if settings.CURRENT_LANGUAGE == 'ar':
            self.dialogue_segments = NULLX_DIALOGUE_AR.get(level_id, [])
        else:
            self.dialogue_segments = NULLX_DIALOGUE_EN.get(level_id, [])

        # Handle case where no dialogue exists for the level
        if not self.dialogue_segments:
            print(f"Warning: No NullX dialogue found for level {level_id}. Skipping presentation.")
            self.is_visible = False
            self.finish_presentation() # Ensure state is fully reset
            return False

        # Reset state and load the first segment
        self.current_segment_index = 0
        self.is_visible = True
        # Call _load_segment which will handle image, text, AND sound for the first segment
        load_success = self._load_segment(0)

        # Check if the initial segment load failed (e.g., image missing)
        if not load_success:
            print(f"Error during initial NullX segment load for Level {level_id}. Aborting presentation.")
            self.finish_presentation() # Clean up state if initial load failed
            return False

        # If loading succeeded, the presentation is active
        print(f"NullX presentation started for Level {level_id}.")
        return True
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def _load_segment(self, index):
        """Loads the content (image, text) for a specific dialogue segment index and handles sound."""
        if not self.is_visible or index < 0 or index >= len(self.dialogue_segments):
            self.finish_presentation() # Finish if index is out of bounds
            return False # Indicate loading failed or finished

        segment = self.dialogue_segments[index]
        self.current_text = segment.get('text', '')
        new_image_name = segment.get('image')

        # --- Image Loading ---
        if new_image_name != self.current_image_name or not self.current_image_surface:
             self.current_image_name = new_image_name
             self.current_image_surface = self._load_image(self.current_image_name)
             if not self.current_image_surface:
                  print(f"!!! Error: Failed to load/scale image '{self.current_image_name}' for segment {index}. Aborting.")
                  self.finish_presentation()
                  return False # Indicate failure

             # Calculate image position after successful load/scale
             img_rect = self.current_image_surface.get_rect()
             self.nullx_image_pos = (
                 settings.SCREEN_WIDTH - img_rect.width - self.padding_from_edge,
                 settings.SCREEN_HEIGHT - img_rect.height - self.padding_from_edge - settings.TASKBAR_HEIGHT
             )

        # --- Reset Animation State ---
        self.char_index = 0
        self.display_text = ""
        self.time_since_last_char = 0
        self.animation_complete = False

        # --- Sound Control ---
        self._stop_dialogue_sound() # Stop any previous sound first
        self._play_dialogue_sound() # Attempt to play sound for the *new* segment

        return True # Indicate successful loading
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def finish_presentation(self):
        """Hides the presenter, stops sound, and cleans up state."""
        if self.is_visible:
            print(f"NullX presentation finished for Level {self.level_id}")

        self._stop_dialogue_sound() # Ensure sound is stopped

        self.is_visible = False
        self.level_id = -1
        self.current_segment_index = 0
        self.dialogue_segments = []
        self.current_text = ""
        self.display_text = ""
        self.animation_complete = False
        self.current_image_name = None
        # Keep current_image_surface until next segment loads or cleared elsewhere
        # Optional: self.image_cache.clear() # If memory is a concern
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def _play_dialogue_sound(self):
        """Plays the looping dialogue sound if SFX are enabled and channel is available."""
        # Check all conditions before attempting to play
        if (settings.SFX_ENABLED and
                settings.SFX_DIALOGUE and
                self.dialogue_sound_channel and
                not self.is_playing_dialogue_sound):
            try:
                self.dialogue_sound_channel.play(settings.SFX_DIALOGUE, loops=-1)
                self.is_playing_dialogue_sound = True
                # print("DEBUG: Started dialogue sound.") # Optional debug
            except pygame.error as e:
                 print(f"Error playing dialogue sound: {e}")
        # else: print("DEBUG: Conditions not met for playing dialogue sound.") # Optional debug
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def _stop_dialogue_sound(self):
        """Stops the looping dialogue sound if it's playing and channel exists."""
        if self.dialogue_sound_channel and self.is_playing_dialogue_sound:
             try:
                 self.dialogue_sound_channel.stop()
                 # print("DEBUG: Stopped dialogue sound.") # Optional debug
             except pygame.error as e:
                  print(f"Error stopping dialogue sound: {e}")
             self.is_playing_dialogue_sound = False
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def update(self, dt):
        """Updates the text animation character by character and manages sound completion."""
        if not self.is_visible or self.animation_complete:
            # If animation is already complete, ensure sound is stopped (redundant check, but safe)
            if self.animation_complete:
                self._stop_dialogue_sound()
            return

        self.time_since_last_char += dt
        # Add characters based on typing speed
        while self.time_since_last_char >= self.TYPING_SPEED and self.char_index < len(self.current_text):
            self.display_text += self.current_text[self.char_index]
            self.char_index += 1
            self.time_since_last_char -= self.TYPING_SPEED

        # Check if animation just completed in this frame
        if not self.animation_complete and self.char_index >= len(self.current_text):
             self.animation_complete = True
             # Stop the sound naturally when text finishes typing
             self._stop_dialogue_sound()
    # --- END REPLACE FUNCTION ---

    # --- REPLACE THIS FUNCTION ---
    def handle_event(self, event, mouse_pos):
        """Handles clicks to advance dialogue or skip animation, managing sound accordingly."""
        if not self.is_visible: return False

        click_detected = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            img_rect = self.current_image_surface.get_rect(topleft=self.nullx_image_pos) if self.current_image_surface else None
            if img_rect and img_rect.collidepoint(mouse_pos):
                 click_detected = True
            elif self.animation_complete and self.continue_prompt_rect and self.continue_prompt_rect.collidepoint(mouse_pos):
                 click_detected = True

        if click_detected:
             if not self.animation_complete:
                  # Skip animation: show full text, mark complete, STOP sound
                  self.animation_complete = True
                  self.display_text = self.current_text
                  self.char_index = len(self.current_text)
                  self.time_since_last_char = 0
                  self._stop_dialogue_sound() # Stop sound on skip
             else:
                  # Advance to next segment
                  self.current_segment_index += 1
                  if self.current_segment_index < len(self.dialogue_segments):
                       # _load_segment handles stopping old sound and starting new
                       self._load_segment(self.current_segment_index)
                  else:
                       # No more segments, finish presentation (stops sound)
                       self.finish_presentation()
             return True # Click handled

        # Handle ESC key to skip entire presentation
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("NullX presentation skipped via ESC.")
            self.finish_presentation() # This ensures sound stops
            return True

        return False # Event not handled by NullX
    # --- END REPLACE FUNCTION ---


    def _wrap_text(self, text, max_width, font):
        """Wraps text to fit within a given width using a specific font.
           Returns a list of strings, where each string is a wrapped line."""
        lines = []
        if not isinstance(text, str) or not font:
            return lines

        # Do NOT reverse words for Arabic. The Bidi algorithm handles RTL.
        words = text.split(' ')
        current_line = ""

        for word in words:
            # Test adding the next word to the current line
            test_line = current_line + (" " if current_line else "") + word
            try:
                 # Calculate the width of the test line
                 line_width, _ = font.size(test_line)
            except (pygame.error, AttributeError) as e:
                 print(f"Warning: Font error sizing NullX text '{test_line[:30]}...': {e}")
                 line_width = max_width + 1 # Assume too wide if error occurs

            # If the test line fits within the max width
            if line_width <= max_width:
                current_line = test_line # Add the word to the current line
            else:
                # Line doesn't fit. Finalize the previous line (if it has content)
                if current_line:
                    lines.append(current_line)
                # Start the new line with the current word
                # Check if the word itself is too long (rare case)
                try:
                     word_width_check, _ = font.size(word)
                     if word_width_check > max_width:
                         # Word is wider than the entire text area. Append it anyway.
                         print(f"Warning: NullX word '{word}' is wider than the text area.")
                         lines.append(word) # Add the single long word as its own line
                         current_line = "" # Start fresh on the next line
                     else:
                          current_line = word # Start the new line normally
                except (pygame.error, AttributeError) as e:
                     print(f"Warning: Font error sizing NullX single word '{word}': {e}")
                     current_line = word # Try to continue if sizing fails

        # Append the very last line after the loop finishes
        if current_line:
            lines.append(current_line)

        return lines


    def draw(self, surface):
        """Draws the SCALED NullX character, speech bubble text, and continue prompt."""
        if not self.is_visible or not self.font or not self.current_image_surface:
             return # Don't draw if not visible or critical assets missing

        # Draw the character image first
        surface.blit(self.current_image_surface, self.nullx_image_pos)

        # Get the base speech bubble rectangle for the current character image (from the original, unscaled coordinates)
        bubble_local_rect_orig = self.speech_bubble_rects.get(self.current_image_name)

        # Check if speech bubble dimensions are defined for this image
        if bubble_local_rect_orig:
            # Calculate the SCALED position and dimensions of the speech bubble on the screen
            scaled_bubble_left = int(bubble_local_rect_orig.left * self.SCALE_FACTOR)
            scaled_bubble_top = int(bubble_local_rect_orig.top * self.SCALE_FACTOR)
            scaled_bubble_width = max(1, int(bubble_local_rect_orig.width * self.SCALE_FACTOR))
            scaled_bubble_height = max(1, int(bubble_local_rect_orig.height * self.SCALE_FACTOR))

            # The final screen rectangle where the conceptual speech bubble exists
            scaled_bubble_screen_rect = pygame.Rect(
                self.nullx_image_pos[0] + scaled_bubble_left, # Top-left X on screen
                self.nullx_image_pos[1] + scaled_bubble_top,  # Top-left Y on screen
                scaled_bubble_width,
                scaled_bubble_height)

            # --- Calculate Text Drawing Area based on *Scaled* Bubble ---
            # Define padding WITHIN the scaled bubble area to position the text.
            # These paddings determine the final box where text wrapping occurs.
            # Adjust these until text fits nicely inside the visual bubble graphic.
            if settings.CURRENT_LANGUAGE == 'ar':
                padding_left = -110  # Increased padding from left bubble edge
                padding_top = 45  # Increased padding from top bubble edge
                padding_right = 280  # Increased padding from right bubble edge
                padding_bottom = 20  # Increased
            else:
                padding_left = -180 # Increased padding from left bubble edge
                padding_top = 45 # Increased padding from top bubble edge
                padding_right = 280 # Increased padding from right bubble edge
                padding_bottom = 20 # Increased padding from bottom bubble edge

            # Calculate the rectangle where text will actually be drawn and wrapped
            self.text_draw_rect = pygame.Rect(
                scaled_bubble_screen_rect.left + padding_left,
                scaled_bubble_screen_rect.top + padding_top,
                scaled_bubble_screen_rect.width - (padding_left + padding_right), # Final text width
                scaled_bubble_screen_rect.height - (padding_top + padding_bottom) # Final text height
            )
            # Ensure calculated width and height are positive
            self.text_draw_rect.width = max(1, self.text_draw_rect.width)
            self.text_draw_rect.height = max(1, self.text_draw_rect.height)

            # --- Draw Text if Area is Valid ---
            if self.text_draw_rect.width > 1 and self.text_draw_rect.height > 1:
                 # Wrap the currently visible portion of the dialogue text
                 wrapped_lines = self._wrap_text(self.display_text, self.text_draw_rect.width, self.font)

                 # Position for drawing lines
                 current_y = self.text_draw_rect.top
                 line_height = self.font.get_height() + 2 # Add small spacing between lines

                 # Draw each wrapped line
                 # In the draw method's text rendering loop:
                 for line in wrapped_lines:
                     if current_y + line_height > self.text_draw_rect.bottom:
                         break
                     try:
                         target_font = self.font # Default to normal pixel font
                         align_right = False
                         if settings.CURRENT_LANGUAGE == 'ar':
                             line = arabic_reshaper.reshape(line)
                             line = get_display(line)
                             if settings.ARABIC_FONT: # Use Arabic font if available
                                target_font = settings.ARABIC_FONT
                             align_right = True # Align Arabic text to the right

                         # Render using the chosen font
                         line_surf = target_font.render(line, True, settings.COLOR_BLACK)

                         # Position based on alignment
                         if align_right:
                             line_rect = line_surf.get_rect(topright=(self.text_draw_rect.right, current_y))
                         else:
                             line_rect = line_surf.get_rect(topleft=(self.text_draw_rect.left, current_y))

                         surface.blit(line_surf, line_rect)
                         current_y += line_height
                     except Exception as e:
                         print(f"Error rendering text line: {e}")
                         current_y += line_height


            else: # Handle case where calculated text area is invalid
                 print(f"Warning: NullX text draw area calculated with invalid size: {self.text_draw_rect.size}")

        # --- Draw "Continue" Prompt ---
        self.continue_prompt_rect = None # Reset rect each frame
        # Show prompt only when the text animation for the current segment is complete
        if self.animation_complete and self.continue_prompt_font:
            try:
                 # Render the prompt text
                 prompt_surf = self.continue_prompt_font.render(self.continue_prompt_text, True, settings.COLOR_WHITE)

                 # Position the prompt above the character image, centered horizontally relative to the image
                 img_center_x = self.nullx_image_pos[0] + self.current_image_surface.get_width() // 2
                 # Calculate Y pos above the image, with padding, ensuring it's not off-screen top
                 prompt_y = self.nullx_image_pos[1] - prompt_surf.get_height() - 15
                 # Final rectangle for the prompt text surface
                 self.continue_prompt_rect = prompt_surf.get_rect(centerx=img_center_x, top=max(5, prompt_y))

                 # --- Draw subtle background for prompt text ---
                 # Create a slightly larger rect for the background
                 prompt_bg_rect = self.continue_prompt_rect.inflate(10, 6)
                 # Create a surface for the background with alpha
                 bg_surf = pygame.Surface(prompt_bg_rect.size, pygame.SRCALPHA)
                 # Fill with semi-transparent black
                 bg_surf.fill((0, 0, 0, 180))
                 # Blit the background surface
                 surface.blit(bg_surf, prompt_bg_rect.topleft)
                 # Optional: Draw a border around the background
                 pygame.draw.rect(surface, (100, 100, 100, 180), prompt_bg_rect, 1, border_radius=4)

                 # Draw the prompt text on top of the background
                 surface.blit(prompt_surf, self.continue_prompt_rect)
            except (pygame.error, AttributeError) as e:
                 # Handle errors rendering the prompt
                 print(f"Error rendering NullX continue prompt: {e}")

# --- END REPLACEMENT CODE for nullx_presenter.py ---