# image_window.py
import pygame
import settings
import os # Needed for basename

class ImageWindow:
    def __init__(self):
        self.is_visible = False
        self.image_surface = None # Scaled image for display
        self.window_surface = None # The drawing surface for the entire window
        # Initial size/position (might be re-centered on show)
        self.window_rect = pygame.Rect(0, 0, *settings.POPUP_WINDOW_SIZE)
        self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

        self.title_bar_rect = pygame.Rect(0, 0, self.window_rect.width, settings.POPUP_TITLE_BAR_HEIGHT)
        # Content area below title bar, with padding
        self.content_rect = pygame.Rect(5, settings.POPUP_TITLE_BAR_HEIGHT + 5,
                                         self.window_rect.width - 10,
                                         self.window_rect.height - settings.POPUP_TITLE_BAR_HEIGHT - 10)

        self.close_button_rect = None
        self._calculate_button_rects() # Calculate initial button positions

        self.image_path = ""
        self.title = ""
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def _calculate_button_rects(self):
        """Calculates the relative rects for title bar buttons."""
        # Positions based on constants from settings.py
        cx = settings.POPUP_BUTTON_X_START
        cy = settings.POPUP_BUTTON_Y_OFFSET
        rad = settings.POPUP_BUTTON_RADIUS
        self.close_button_rect = pygame.Rect(cx - rad, cy - rad, max(1, rad*2), max(1, rad*2))

    def _update_layout_rects(self):
        """Updates internal rects based on current window_rect size/position."""
        self.title_bar_rect.width = self.window_rect.width
        self.content_rect = pygame.Rect(5, self.title_bar_rect.bottom + 5,
                                         self.window_rect.width - 10,
                                         self.window_rect.height - self.title_bar_rect.bottom - 10)
        self._calculate_button_rects() # Recalculate button pos relative to top-left

    def show(self, image_path):
        """Loads an image, creates the window surface, and makes it visible."""
        if not image_path or not os.path.exists(image_path):
             print(f"ImageWindow Error: Image path invalid or missing: {image_path}")
             self.hide()
             return

        try:
            # Load the image first
            try:
                img = pygame.image.load(image_path).convert_alpha() # Use convert_alpha for transparency
            except pygame.error as load_error:
                 print(f"ImageWindow Error: Failed to load image '{image_path}': {load_error}")
                 self.hide()
                 return

            self.image_path = image_path
            self.title = os.path.basename(image_path) # Use filename as title
            print(f"ImageWindow: Loading '{self.title}'")

            # --- Window Setup ---
            # Reset window to default size and re-center
            self.window_rect = pygame.Rect(0, 0, *settings.POPUP_WINDOW_SIZE)
            self.window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
            self._update_layout_rects() # Update title bar, content area, buttons

            # Check for valid dimensions *after* resetting
            if self.content_rect.width <= 0 or self.content_rect.height <= 0:
                 print(f"ImageWindow Error: Invalid content area size calculated: {self.content_rect.size}")
                 self.hide()
                 return

            # --- Image Scaling ---
            img_rect = img.get_rect()
            max_w, max_h = self.content_rect.width, self.content_rect.height
            # Calculate scale factor to fit image within content area while maintaining aspect ratio
            scale = 1.0 # Default scale
            if img_rect.width > 0 and img_rect.height > 0: # Avoid division by zero
                scale = min(max_w / img_rect.width, max_h / img_rect.height)
            # Don't scale up if image is smaller than the window
            scale = min(scale, 1.0)
            # Calculate new dimensions, ensuring they are at least 1x1
            new_width = max(1, int(img_rect.width * scale))
            new_height = max(1, int(img_rect.height * scale))

            # Scale the image
            try:
                 self.image_surface = pygame.transform.smoothscale(img, (new_width, new_height))
            except (ValueError, pygame.error) as scale_error:
                 print(f"ImageWindow Error: Failed to scale image '{self.title}': {scale_error}")
                 self.hide()
                 return

            # --- Create Window Surface ---
            try:
                self.window_surface = pygame.Surface(self.window_rect.size, pygame.SRCALPHA) # Use SRCALPHA for potential transparency
                self.window_surface.fill(settings.POPUP_BG_COLOR) # Fill with background color
                # Draw title bar
                pygame.draw.rect(self.window_surface, settings.POPUP_TITLE_COLOR, self.title_bar_rect)
            except (ValueError, pygame.error) as surface_error:
                 print(f"ImageWindow Error: Failed to create window surface: {surface_error}")
                 self.hide(); return


            # Draw Title Text
            if settings.UI_FONT:
                 try:
                     title_surf = settings.UI_FONT.render(self.title, True, settings.COLOR_WHITE)
                     title_txt_rect = title_surf.get_rect(centerx=self.window_rect.width / 2, centery=settings.POPUP_TITLE_BAR_HEIGHT / 2)
                     self.window_surface.blit(title_surf, title_txt_rect)
                 except Exception as e: print(f"Error rendering image window title: {e}")

            # Draw Close Button on title bar
            if self.close_button_rect:
                pygame.draw.circle(self.window_surface, settings.COLOR_CLOSE_BUTTON, self.close_button_rect.center, settings.POPUP_BUTTON_RADIUS)

            # Blit scaled image onto window surface, centered in the content area
            # Get rect for the scaled image, centered within the content_rect
            img_display_rect = self.image_surface.get_rect(center=self.content_rect.center)
            self.window_surface.blit(self.image_surface, img_display_rect.topleft) # Blit relative to window surface

            # Make visible
            self.is_visible = True
            self.is_dragging = False

        except pygame.error as e:
             print(f"ImageWindow Error processing '{image_path}': {e}")
             self.hide()
        except Exception as e:
             print(f"ImageWindow Unexpected Error: {e}")
             self.hide()

    def hide(self):
        """Makes the window invisible and clears associated resources."""
        if self.is_visible: print(f"ImageWindow '{self.title}' hidden.")
        self.is_visible = False
        self.image_surface = None
        self.window_surface = None
        self.is_dragging = False
        self.image_path = ""
        self.title = ""

    def handle_event(self, event, mouse_pos):
        """Handles events specifically for this window (dragging, closing)."""
        if not self.is_visible: return False

        # Convert screen mouse coordinates to window-local coordinates
        local_mouse_pos = (mouse_pos[0] - self.window_rect.left, mouse_pos[1] - self.window_rect.top)
        handled = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                # Check close button
                if self.close_button_rect and self.close_button_rect.collidepoint(local_mouse_pos):
                     self.hide()
                     handled = True
                # Check title bar for dragging
                elif self.title_bar_rect.collidepoint(local_mouse_pos):
                    self.is_dragging = True
                    self.drag_offset_x = mouse_pos[0] - self.window_rect.left
                    self.drag_offset_y = mouse_pos[1] - self.window_rect.top
                    handled = True
                # Consume clicks within the content area (no specific action here)
                elif self.content_rect.collidepoint(local_mouse_pos):
                     handled = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                 self.is_dragging = False
                 handled = True # Handle mouse up after drag

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Update window position based on drag
                new_x = mouse_pos[0] - self.drag_offset_x
                new_y = mouse_pos[1] - self.drag_offset_y
                self.window_rect.topleft = (new_x, new_y)
                # Keep window on screen
                screen_rect = pygame.display.get_surface().get_rect()
                self.window_rect.clamp_ip(screen_rect)
                handled = True

        # ESC key to close is handled in game_state.py or main.py loop

        return handled

    def draw(self, surface):
        """Draws the image window onto the target surface if visible."""
        if self.is_visible and self.window_surface:
            surface.blit(self.window_surface, self.window_rect.topleft)