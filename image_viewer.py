# image_viewer.py
# This file seems unused now as image_window.py handles image display.
# Kept for reference but marked as deprecated. Remove if confident it's not needed.
import pygame
import settings
import os

class ImageViewer:
    def __init__(self):
        print("DEPRECATION WARNING: ImageViewer class is likely unused. Use ImageWindow instead.")
        self.image_surface = None
        self.is_displaying = False
        self.original_image = None # Keep reference to original if needed later?
        self.image_path = None

    def show_image(self, image_path):
        """Loads and prepares an image for display. DEPRECATED"""
        print("ImageViewer.show_image called (likely deprecated function)")
        if not image_path or not os.path.exists(image_path):
            print(f"ImageViewer Error: Invalid path or file missing: {image_path}")
            self.hide_image() # Ensure state is clean
            return False

        self.image_path = image_path
        try:
            # Load image
            img = pygame.image.load(image_path).convert_alpha()
            self.original_image = img
            img_rect = img.get_rect()

            # Basic scaling logic (might differ from ImageWindow)
            scale = 1.0
            if img_rect.width > 0 and img_rect.height > 0: # Avoid division by zero
                scale = min(settings.SCREEN_WIDTH / img_rect.width,
                            settings.SCREEN_HEIGHT / img_rect.height)
            # Only scale down, not up
            scale = min(scale, 1.0)
            # Ensure minimum size 1x1
            new_width = max(1, int(img_rect.width * scale))
            new_height = max(1, int(img_rect.height * scale))

            # Apply scaling
            self.image_surface = pygame.transform.smoothscale(img, (new_width, new_height))
            self.is_displaying = True
            print(f"ImageViewer: Displaying image (Deprecated Method): {image_path}")
            return True

        except pygame.error as e:
             print(f"ImageViewer Error loading '{image_path}': {e}")
             self.hide_image(); return False
        except Exception as e:
             print(f"ImageViewer Unexpected Error loading '{image_path}': {e}")
             self.hide_image(); return False

    def hide_image(self):
        """Stops displaying the image and clears resources. DEPRECATED"""
        if self.is_displaying:
             print(f"ImageViewer: Image closed ({os.path.basename(self.image_path or 'Unknown')}).")
        self.image_surface = None
        self.is_displaying = False
        self.original_image = None
        self.image_path = None

    def draw(self, surface):
        """Draws the image centered on the screen if active. DEPRECATED"""
        if self.is_displaying and self.image_surface:
            # Get screen center
            screen_rect = surface.get_rect()
            # Get rect for the scaled image, centered on screen
            image_rect = self.image_surface.get_rect(center=screen_rect.center)

            # Draw background fill (covers entire screen)
            surface.fill(settings.COLOR_BLACK) # Or a different backdrop color if desired
            # Blit the image
            surface.blit(self.image_surface, image_rect)

# --- End of File ---