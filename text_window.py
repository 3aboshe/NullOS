# --- START OF FILE text_window.py ---

# text_window.py
import pygame
import arabic_reshaper
from bidi.algorithm import get_display
import settings # Access settings for sizes, fonts, colors
import os       # Used for potential future use like setting title from filename


class TextWindow:
    """A pop-up window designed to display multi-line text content with scrolling."""

    def __init__(self):
        """Initializes the text window state."""
        self.is_visible = False        # Is the window currently displayed?
        self.title = ""                # Title displayed in the window's title bar
        self.text_content = ""         # The original raw string content to be displayed
        self.rendered_lines = []       # List of pre-rendered Surface objects, one per wrapped line
        self.window_surface = None     # The Pygame Surface for drawing the entire window

        # --- Window Geometry & Layout ---
        # Initial size based on settings, positioned centered on screen
        self.window_rect = pygame.Rect(0, 0, *settings.TEXT_POPUP_WINDOW_SIZE)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

        # Rectangles for title bar and content area (calculated relative to window_rect)
        self.title_bar_rect = pygame.Rect(0, 0, self.window_rect.width, settings.POPUP_TITLE_BAR_HEIGHT)
        # Content area has padding (5px)
        self.content_rect = pygame.Rect(5, self.title_bar_rect.bottom + 5,
                                         self.window_rect.width - 10,
                                         self.window_rect.height - self.title_bar_rect.bottom - 10)

        self.close_button_rect = None # Rectangle for the close button
        self._calculate_button_rects() # Calculate initial button position

        # --- Dragging State ---
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # --- Font and Scrolling ---
        # Get the font specified for text windows in settings
        self.font = settings.TEXT_WINDOW_FONT
        if not self.font:
            # Critical error if the font didn't load in settings.py
            print("ERROR: TextWindow requires TEXT_WINDOW_FONT. Using fallback.")
            # Provide a basic fallback font
            self.font = pygame.font.SysFont("sans", 15)

        # Calculate line height based on font, add spacing for readability
        self.line_height = self.font.get_height() + 2 if self.font else 16
        # Scrolling offset: How many pixels the text content is scrolled *up*
        self.scroll_offset_y = 0
        # Total pixel height required to display all rendered lines
        self.total_content_height = 0

    def _calculate_button_rects(self):
        """Calculates the screen rectangle for the close button based on settings."""
        cx = settings.POPUP_BUTTON_X_START    # Horizontal distance from left edge
        cy = settings.POPUP_BUTTON_Y_OFFSET   # Vertical offset within title bar
        rad = settings.POPUP_BUTTON_RADIUS    # Radius of the circular button
        # Calculate rect ensuring minimum 1x1 size
        self.close_button_rect = pygame.Rect(cx - rad, cy - rad, max(1, rad*2), max(1, rad*2))

    def _update_layout_rects(self):
        """Updates internal layout rectangles (title bar, content area, buttons)
           if the main window_rect changes size or position."""
        self.title_bar_rect.width = self.window_rect.width
        self.content_rect = pygame.Rect(5, self.title_bar_rect.bottom + 5,
                                         self.window_rect.width - 10,
                                         self.window_rect.height - self.title_bar_rect.bottom - 10)
        # Recalculate button position relative to the updated layout
        self._calculate_button_rects()
        # Recalculate line height and potentially max lines if font could change dynamically (not currently the case)
        if self.font: self.line_height = self.font.get_height() + 2

    def _render_text_content(self):
        """Renders the raw self.text_content into a list of line Surfaces"""
        self.rendered_lines = []
        self.total_content_height = 0

        if not self.font or not self.text_content or self.line_height <= 0 or self.content_rect.width <= 0:
            return

        max_width = self.content_rect.width

        # Split by paragraphs first
        paragraphs = self.text_content.split('\n')

        for para in paragraphs:
            if not para.strip():
                self.rendered_lines.append(None)
                self.total_content_height += self.line_height
                continue

            # Handle Arabic text differently
            if settings.CURRENT_LANGUAGE == 'ar':
                # Reshape and display Arabic text
                reshaped_text = arabic_reshaper.reshape(para)
                bidi_text = get_display(reshaped_text)

                # Split into words (spaces are important in Arabic)
                words = bidi_text.split(' ')
                current_line = ""

                for word in words:
                    test_line = f"{current_line} {word}" if current_line else word

                    # Check width
                    try:
                        test_width = self.font.size(test_line)[0]
                    except:
                        test_width = len(test_line) * 10  # Fallback estimation

                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            # Render the current line
                            line_surf = self.font.render(current_line, True, settings.COLOR_WHITE)
                            self.rendered_lines.append(line_surf)
                            self.total_content_height += self.line_height
                        current_line = word

                # Add the last line
                if current_line:
                    line_surf = self.font.render(current_line, True, settings.COLOR_WHITE)
                    self.rendered_lines.append(line_surf)
                    self.total_content_height += self.line_height

            else:
                # Original LTR handling for other languages
                words = para.split(' ')
                current_line = ""

                for word in words:
                    test_line = f"{current_line} {word}" if current_line else word

                    try:
                        test_width = self.font.size(test_line)[0]
                    except:
                        test_width = len(test_line) * 10

                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            line_surf = self.font.render(current_line, True, settings.COLOR_WHITE)
                            self.rendered_lines.append(line_surf)
                            self.total_content_height += self.line_height
                        current_line = word

                if current_line:
                    line_surf = self.font.render(current_line, True, settings.COLOR_WHITE)
                    self.rendered_lines.append(line_surf)
                    self.total_content_height += self.line_height

    def show(self, title, text_content):
        """Prepares and displays the text window with the given title and content."""
        # Cannot show without a valid font
        if not self.font:
            print("Cannot show TextWindow: Font unavailable."); return

        self.title = title if title else "Text Document" # Set window title

        # --- Sanitize and Store Text Content ---
        # Ensure text_content is a single string, handling lists/tuples or None
        if isinstance(text_content, (list, tuple)):
            self.text_content = "\n".join(map(str, text_content))
        elif text_content is None:
            self.text_content = "" # Use empty string if None is passed
        else:
            self.text_content = str(text_content) # Convert any other type to string

        print(f"TextWindow: Showing '{self.title}'")

        # --- Recalculate Layout and Render Content ---
        # Reset window size/position to defaults
        self.window_rect = pygame.Rect(0, 0, *settings.TEXT_POPUP_WINDOW_SIZE)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        self._update_layout_rects() # Update internal rects based on size/position

        # Critical check before rendering: Ensure valid dimensions
        if self.content_rect.width <= 0 or self.content_rect.height <= 0 or self.line_height <= 0:
            print(f"Error: Invalid window/content dimensions for TextWindow '{self.title}'. Cannot render text.")
            # Potentially show an empty window or just fail silently?
            # Let's prevent showing if dimensions are invalid.
            return

        # Render the processed text_content into self.rendered_lines
        self._render_text_content()

        # --- Create Window Surface ---
        try:
            # Create the main surface for the window with transparency support
            self.window_surface = pygame.Surface(self.window_rect.size, pygame.SRCALPHA)
            # Fill with background color (handled in draw now)
            # self.window_surface.fill(settings.POPUP_BG_COLOR)
            # Draw title bar immediately (static element)
            # pygame.draw.rect(self.window_surface, settings.POPUP_TITLE_COLOR, self.title_bar_rect)
            # ---> Moved static drawing elements to draw() method for consistency. <---

        except (ValueError, pygame.error) as e:
            # Handle errors during surface creation
            print(f"Error creating TextWindow surface: {e}")
            self.hide(); return # Hide if surface creation fails

        # --- Reset State and Show ---
        self.scroll_offset_y = 0     # Start scrolled to the top
        self.is_visible = True       # Make the window visible
        self.is_dragging = False     # Reset drag state

    def hide(self):
        """Hides the text window and clears its content/state."""
        if self.is_visible: print(f"TextWindow '{self.title}' hidden.")
        self.is_visible = False
        self.rendered_lines = []     # Clear rendered text surfaces
        self.window_surface = None   # Release the drawing surface
        self.is_dragging = False     # Reset drag state
        self.text_content = ""       # Clear raw text content
        self.title = ""              # Clear title
        self.scroll_offset_y = 0     # Reset scroll position
        self.total_content_height = 0 # Reset calculated content height

    def handle_event(self, event, mouse_pos):
        """Handles input events: dragging, closing, and scrolling."""
        if not self.is_visible: return False # Ignore events if not visible

        # Convert global mouse coords to window-local coords for interaction checks
        local_mouse_pos = (mouse_pos[0] - self.window_rect.left, mouse_pos[1] - self.window_rect.top)
        handled = False # Flag indicating if this event was processed

        if event.type == pygame.MOUSEBUTTONDOWN:
            # --- Scrolling with Mouse Wheel ---
            # Check if click is mouse wheel up/down (button 4/5) AND within content area
            if self.content_rect.collidepoint(local_mouse_pos) and event.button in (4, 5):
                 # Only scroll if content is scrollable and line_height is valid
                 if self.line_height > 0 and self.total_content_height > self.content_rect.height:
                     scroll_amount = self.line_height * 3 # Scroll speed (3 lines per tick)
                     # Maximum scroll offset (pixels hidden above the view)
                     max_scroll = self.total_content_height - self.content_rect.height

                     if event.button == 4: # Scroll Up (Wheel Up)
                         self.scroll_offset_y = max(0, self.scroll_offset_y - scroll_amount) # Decrease offset, clamp at 0
                         handled = True
                     elif event.button == 5: # Scroll Down (Wheel Down)
                         self.scroll_offset_y = min(max_scroll, self.scroll_offset_y + scroll_amount) # Increase offset, clamp at max
                         handled = True

            # --- Left Mouse Button Click (Button 1) ---
            elif event.button == 1:
                # 1. Check Close Button click
                if self.close_button_rect and self.close_button_rect.collidepoint(local_mouse_pos):
                    self.hide() # Close the window
                    handled = True
                # 2. Check Title Bar Drag Start
                elif self.title_bar_rect.collidepoint(local_mouse_pos):
                    self.is_dragging = True
                    # Record mouse offset relative to window corner for smooth dragging
                    self.drag_offset_x = mouse_pos[0] - self.window_rect.left
                    self.drag_offset_y = mouse_pos[1] - self.window_rect.top
                    handled = True
                # 3. Check Clicks within Content Area
                elif self.content_rect.collidepoint(local_mouse_pos):
                     # Currently, clicking the content area does nothing but consumes the click
                     # Potential future use: text selection?
                     handled = True
                # 4. Clicks elsewhere on the window (background) - consume the click
                elif self.window_rect.collidepoint(mouse_pos): # Check with global coords here
                     handled = True


        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging when left mouse button is released
            if event.button == 1 and self.is_dragging:
                 self.is_dragging = False
                 handled = True

        elif event.type == pygame.MOUSEMOTION:
            # Update window position if dragging is active
            if self.is_dragging:
                # Calculate new top-left based on mouse movement and initial offset
                new_x = mouse_pos[0] - self.drag_offset_x
                new_y = mouse_pos[1] - self.drag_offset_y
                self.window_rect.topleft = (new_x, new_y)
                # Prevent dragging the window completely off-screen
                screen_rect = pygame.display.get_surface().get_rect()
                self.window_rect.clamp_ip(screen_rect) # Keep window within screen bounds
                handled = True

        # --- ESC Key Handling ---
        # Closing via ESC key is handled globally in game_state.py or main.py

        return handled # Return True if event was handled, False otherwise


    def draw(self, surface):
        """Draws the text window frame, content (scrolled), and scrollbar onto the target surface."""
        # Don't draw if hidden or critical components are missing
        if not self.is_visible or not self.window_surface or not self.font: return

        # --- 1. Redraw Static Window Frame Elements ---
        # Fill background, draw title bar, title text, close button onto self.window_surface
        self.window_surface.fill(settings.POPUP_BG_COLOR)
        pygame.draw.rect(self.window_surface, settings.POPUP_TITLE_COLOR, self.title_bar_rect)
        if settings.UI_FONT: # Draw Title Text using UI Font
             try:
                 title_surf = settings.UI_FONT.render(self.title, True, settings.COLOR_WHITE)
                 title_txt_rect = title_surf.get_rect(centerx=self.window_rect.width / 2, centery=settings.POPUP_TITLE_BAR_HEIGHT / 2)
                 self.window_surface.blit(title_surf, title_txt_rect)
             except Exception as e: print(f"Error rendering text window title: {e}")
        if self.close_button_rect: # Draw Close button circle
             pygame.draw.circle(self.window_surface, settings.COLOR_CLOSE_BUTTON, self.close_button_rect.center, settings.POPUP_BUTTON_RADIUS)


        # --- 2. Create Temporary Surface for Content Area ---
        # This is used for clipping text and drawing the scrollbar correctly relative to the content.
        content_surf = None
        # Ensure valid dimensions before creating surface
        if self.content_rect.width > 0 and self.content_rect.height > 0:
            try:
                 # Create a surface matching the content area size, with alpha support
                 content_surf = pygame.Surface(self.content_rect.size, pygame.SRCALPHA)
                 # Fill content area with its own background (can be transparent or same as window bg)
                 content_surf.fill(settings.POPUP_BG_COLOR) # Or a slightly different color?
            except (ValueError, pygame.error) as e:
                 print(f"Error creating TextWindow content surface: {e}")
                 # If content surface fails, just draw the frame and return
                 surface.blit(self.window_surface, self.window_rect.topleft)
                 return
        else: # Invalid content rect dimensions, draw frame only
             surface.blit(self.window_surface, self.window_rect.topleft); return


        # --- 3. Blit Rendered Text Lines onto Content Surface (with scrolling) ---
        # Only attempt if line_height is valid
        if self.line_height > 0:
            # Starting Y position for drawing, adjusted by scroll offset
            start_y = 0 - self.scroll_offset_y
            # Bottom edge of the visible content area (for culling)
            visible_content_bottom = self.content_rect.height

            # Iterate through the pre-rendered line Surfaces
            for line_surface in self.rendered_lines:
                # Calculate Y position of the bottom of this line
                line_bottom_pos = start_y + self.line_height

                # --- Culling Optimization ---
                # If the *top* of the line is already below the visible area, stop drawing subsequent lines
                if start_y >= visible_content_bottom: break
                # If the *bottom* of the line is above the visible area (scrolled past), skip drawing it but continue checking others
                if line_bottom_pos <= 0:
                     start_y += self.line_height # Advance Y position for the next line
                     continue # Skip the blit for this off-screen line

                # Draw the line if it's not a None placeholder (used for empty original lines)
                if line_surface:
                     # Blit onto the content_surf with small left padding
                     content_surf.blit(line_surface, (5, start_y))

                # Move Y position down for the next line
                start_y += self.line_height


        # --- 4. Draw Scrollbar (if needed) ---
        # Check if the total height of rendered content exceeds the visible content area height
        if self.total_content_height > self.content_rect.height:
            content_h = self.content_rect.height # Visible height
            # Max scroll offset in pixels (total height - visible height)
            max_scroll_pixel = max(1, self.total_content_height - content_h) # Avoid division by zero

            # --- Scrollbar Thumb Size ---
            # Thumb height is proportional to the ratio of visible height / total height
            visible_ratio = content_h / self.total_content_height if self.total_content_height > 0 else 1
            thumb_h = max(15, content_h * visible_ratio) # Ensure minimum thumb height

            # --- Scrollbar Thumb Position ---
            # Calculate vertical position (Y) of the thumb based on current scroll offset
            scrollable_track_h = content_h - thumb_h # Total distance thumb can travel
            # Calculate scroll ratio (0.0 = top, 1.0 = bottom)
            thumb_y_ratio = self.scroll_offset_y / max_scroll_pixel if max_scroll_pixel > 0 else 0
            # Calculate pixel Y position for the top of the thumb
            thumb_y = thumb_y_ratio * scrollable_track_h

            # Define the rectangle for the scrollbar thumb (position near right edge)
            scrollbar_width = 6
            scrollbar_rect = pygame.Rect(self.content_rect.width - scrollbar_width - 2, # X pos (right align)
                                           thumb_y,                  # Y pos calculated
                                           scrollbar_width,          # Fixed width
                                           thumb_h)                  # Height calculated

            # Draw the scrollbar thumb rectangle onto the content surface
            try:
                 pygame.draw.rect(content_surf, settings.COLOR_TASKBAR, scrollbar_rect, border_radius=3)
            except pygame.error as draw_err: print(f"Error drawing text window scrollbar: {draw_err}")


        # --- 5. Final Blits ---
        # a) Blit the content surface (containing text and scrollbar) onto the main window surface
        #    at the content area's position.
        self.window_surface.blit(content_surf, self.content_rect.topleft)
        # b) Blit the complete window surface (frame + content) onto the main game screen.
        surface.blit(self.window_surface, self.window_rect.topleft)
    def prepare_rtl_text(text):
        """Process text for RTL rendering"""
    # Split into paragraphs and reverse each line
        paragraphs = text.split('\n')
        processed = [p[::-1] for p in paragraphs]
        return '\n'.join(processed)

# --- END OF FILE text_window.py ---