# --- START OF FILE credits_screen.py ---

import pygame
import settings
import time

class CreditsScreen:
    """Displays scrolling credits at the end of the game."""

    CREDITS_TEXT = [
        "", "", "", # Add some initial empty lines for spacing
        "NullOS CTF Challenge",
        "",
        "Created by:",
        "",
        "Abdulrahman Majid",
        "Ayman Rasheed",
        "Maryam Talaat",
        "Faede Abdulrazaq",
        "", "", "",
        "Advisor:",
        "",
        "Dr.Ann Alkazaz",
        "","","",
        "Thank you for playing!",
        "", "", "", # Add more blank lines so it scrolls off screen
    ]

    SCROLL_SPEED = 70  # Pixels per second

    def __init__(self):
        self.is_active = False
        # Use a readable font, UI or Menu Option font are good choices
        self.font = settings.MENU_OPTION_FONT or settings.UI_FONT
        if not self.font:
            print("ERROR: CreditsScreen font missing! Using fallback.")
            self.font = pygame.font.SysFont("sans", 24)

        self.rendered_lines = []    # List of (surface, rect) tuples
        self.total_height = 0       # Total pixel height of all rendered lines + spacing
        self.scroll_y = 0           # Current vertical scroll position (top of the text block)
        self.line_spacing = 10      # Extra vertical space between lines

        self._render_lines() # Pre-render text surfaces

    def _render_lines(self):
        """Pre-renders the credit text lines."""
        self.rendered_lines = []
        self.total_height = 0
        if not self.font: return

        current_h = 0
        line_height = self.font.get_height() + self.line_spacing

        for line_text in self.CREDITS_TEXT:
            try:
                text_surf = self.font.render(line_text, True, settings.MENU_TEXT_COLOR)
                text_rect = text_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2)
                # Store the surface and its relative rect (y position will be calculated in draw)
                self.rendered_lines.append((text_surf, text_rect))
                current_h += line_height
            except Exception as e:
                print(f"Error rendering credits line '{line_text}': {e}")
                # Add placeholder height even on error
                current_h += line_height

        self.total_height = current_h

    def show(self):
        """Activates the credits screen and resets scrolling."""
        print("Credits screen activated.")
        self.is_active = True
        # Start scrolling from below the screen
        self.scroll_y = settings.SCREEN_HEIGHT
        # Ensure lines are rendered if they weren't (e.g., font loaded late)
        if not self.rendered_lines:
            self._render_lines()

    def hide(self):
        """Deactivates the credits screen."""
        self.is_active = False

    def update(self, dt):
        """Updates the scroll position."""
        if not self.is_active: return

        # Scroll upwards
        self.scroll_y -= self.SCROLL_SPEED * dt

        # Optional: Check if scrolling is finished (when bottom of text is above screen top)
        # if self.scroll_y + self.total_height < 0:
        #     print("Credits finished scrolling.")
        #     # Could potentially loop or trigger something else here
        #     pass

    def handle_event(self, event, mouse_pos):
        """Handles input to exit the credits screen."""
        if not self.is_active: return None

        action = None
        # Exit on ESC key or any mouse click
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Credits screen exited via ESC.")
            action = 'Quit'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("Credits screen exited via Mouse Click.")
            action = 'Quit'

        return action # Returns 'Quit' or None

    def draw(self, surface):
        """Draws the scrolling credits."""
        if not self.is_active or not self.rendered_lines: return

        # 1. Draw Background (simple black or overlay)
        surface.fill(settings.COLOR_BLACK) # Full black background
        # Or use an overlay similar to the menu:
        # overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # overlay.fill(settings.MENU_OVERLAY_COLOR)
        # surface.blit(overlay, (0, 0))

        # 2. Draw each rendered line based on current scroll position
        current_draw_y = self.scroll_y
        line_height = self.font.get_height() + self.line_spacing

        for text_surf, text_rect in self.rendered_lines:
            # Calculate the absolute screen Y position for this line's top edge
            absolute_y = current_draw_y
            # Optimization: Only draw if the line is potentially visible
            if absolute_y + line_height > 0 and absolute_y < settings.SCREEN_HEIGHT:
                # Center the pre-calculated rect horizontally and set its vertical position
                final_rect = text_rect.copy()
                final_rect.top = int(absolute_y)
                final_rect.centerx = settings.SCREEN_WIDTH // 2 # Ensure centering
                surface.blit(text_surf, final_rect)

            # Move drawing position down for the next line
            current_draw_y += line_height

        # Optional: Add an "Exit" prompt at the bottom
        if settings.UI_FONT:
             try:
                 exit_font = settings.UI_FONT
                 exit_surf = exit_font.render("[Press ESC or Click to Exit]", True, settings.MENU_TEXT_HOVER_COLOR)
                 exit_rect = exit_surf.get_rect(centerx=settings.SCREEN_WIDTH // 2, bottom=settings.SCREEN_HEIGHT - 15)
                 surface.blit(exit_surf, exit_rect)
             except Exception as e: print(f"Warn: Could not render credits exit prompt: {e}")
