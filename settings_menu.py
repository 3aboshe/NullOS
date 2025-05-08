# --- START OF FILE settings_menu.py ---

# settings_menu.py
import pygame
import settings

class SettingsMenu:
    def __init__(self):
        """Initializes the Settings Menu elements."""
        # Use UI font for settings labels (Music:, Sound Effects:)
        self.option_font = settings.UI_FONT
        # Use same font for the On/Off values for simplicity
        self.value_font = settings.UI_FONT
        # Font for the "Back" button (can be same or different)
        self.button_font = settings.UI_FONT

        # Check if required fonts are loaded
        if not self.option_font or not self.value_font or not self.button_font:
            print("ERROR: SettingsMenu requires UI_FONT. Using fallback.")
            # Use a basic fallback font if UI font failed to load
            fallback_font = pygame.font.SysFont("sans", 22)
            self.option_font = self.option_font or fallback_font
            self.value_font = self.value_font or fallback_font
            self.button_font = self.button_font or fallback_font

        # --- Menu Structure ---
        # Each key is the setting label, value indicates if it's toggleable
        self.options = {
            "Music": True,
            "Sound Effects": True,
            "Back": False, # Not a toggle, just an action
        }
        self.option_order = ["Music", "Sound Effects", "Back"] # Define display order
        self.selected_option_index = 0
        self.label_rects = {} # Stores {label: rect} for the "Music:", "Sound Effects:" parts
        self.value_rects = {} # Stores {label: rect} for the "On/Off" or "Back" button visual area
        self.button_rects = {} # Stores {label: rect} for clickable area of entire row

        self.menu_active = False # Settings menu isn't active by default

    def _render_options(self, surface):
        """Renders settings options and calculates their positions."""
        start_y = settings.SCREEN_HEIGHT * 0.3 # Position settings higher up
        option_spacing = self.option_font.get_height() + 30 # Increased spacing
        column_spacing = 50 # Space between setting label and its value/button
        self.label_rects.clear()
        self.value_rects.clear()
        self.button_rects.clear()

        center_x = settings.SCREEN_WIDTH // 2

        # 1. Render Title ("Settings")
        try:
             # Try using Menu title font, fallback if necessary
             settings_title_font = settings.MENU_FONT or pygame.font.SysFont("sans", 60)
             # Adjust size if using the specific Menu font
             if settings.MENU_FONT:
                 try: # Safely adjust font size if using a file font
                    settings_title_font = pygame.font.Font(settings.MENU_FONT_PATH, 60)
                 except: pass # Keep original MENU_FONT if sizing fails

             title_surf = settings_title_font.render("Settings", True, settings.MENU_TEXT_COLOR)
             title_rect = title_surf.get_rect(centerx=center_x, centery=settings.SCREEN_HEIGHT * 0.15)
             surface.blit(title_surf, title_rect)
        except Exception as e: print(f"Error rendering settings title: {e}")

        # 2. Render each setting option row
        for i, label in enumerate(self.option_order):
            is_toggle = self.options[label]
            is_back_button = (label == "Back")
            current_y = start_y + i * option_spacing

            # Determine Colors based on selection
            label_color = settings.MENU_TEXT_HOVER_COLOR if i == self.selected_option_index else settings.SETTINGS_TEXT_COLOR
            value_color = settings.SETTINGS_VALUE_COLOR # Color for "On"/"Off" text

            # --- Render Label (Only if NOT the back button) ---
            if not is_back_button:
                try:
                    # Render text like "Music:", "Sound Effects:"
                    label_surf = self.option_font.render(f"{label}:", True, label_color)
                    # Align the RIGHT edge of the label text to the left of the center column gap
                    label_rect = label_surf.get_rect(right=center_x - column_spacing / 2, centery=current_y)
                    surface.blit(label_surf, label_rect)
                    self.label_rects[label] = label_rect # Store rect for row calculation
                except Exception as e: print(f"Error rendering setting label '{label}': {e}")

            # --- Render Value (On/Off) OR Back Button ---
            value_text = ""
            if is_toggle: # Determine On/Off state for toggles
                if label == "Music": value_text = "On" if settings.MUSIC_ENABLED else "Off"
                elif label == "Sound Effects": value_text = "On" if settings.SFX_ENABLED else "Off"
            elif is_back_button: # Text for the back button
                value_text = "Back"

            # Proceed only if there's text/button to render
            if value_text:
                try:
                    value_rect_for_row_calc = None # Rect used to define the row width
                    if is_back_button: # Draw the Back button
                        # Choose color based on selection hover
                        button_color = settings.SETTINGS_BUTTON_HOVER_COLOR if i == self.selected_option_index else settings.SETTINGS_BUTTON_COLOR
                        # Render the button text first to determine size needed
                        value_surf = self.button_font.render(value_text, True, settings.MENU_TEXT_COLOR) # Use button font
                        # Create button rect centered horizontally, slightly inflated for visual appeal
                        button_visual_rect = value_surf.get_rect(center=(center_x, current_y)).inflate(60, 20) # Increased padding
                        pygame.draw.rect(surface, button_color, button_visual_rect, border_radius=5)
                        # Center the text surface within the button rectangle
                        text_rect_in_button = value_surf.get_rect(center=button_visual_rect.center)
                        surface.blit(value_surf, text_rect_in_button) # Draw text onto button
                        self.value_rects[label] = button_visual_rect # Store visual rect for interaction
                        value_rect_for_row_calc = button_visual_rect # Use button for row size
                    else: # Draw normal "On" / "Off" text for toggles
                         value_surf = self.value_font.render(value_text, True, value_color)
                         # Align the LEFT edge of the value text to the right of the center column gap
                         value_visual_rect = value_surf.get_rect(left=center_x + column_spacing / 2, centery=current_y)
                         surface.blit(value_surf, value_visual_rect) # Draw the text
                         self.value_rects[label] = value_visual_rect # Store text rect for interaction
                         value_rect_for_row_calc = value_visual_rect # Use text for row size

                    # --- Define Clickable Row Area ---
                    # Use the rendered label (if present) and value/button rect to define the clickable area
                    label_part_rect = self.label_rects.get(label)
                    value_part_rect = value_rect_for_row_calc

                    # Calculate union of label and value rects to get the full visual row extent
                    if label_part_rect and value_part_rect:
                         full_row_rect = label_part_rect.union(value_part_rect)
                    elif value_part_rect: # Handles "Back" button row (no label)
                         full_row_rect = value_part_rect
                    else: continue # Skip row definition if essential parts missing

                    # Inflate the union rect slightly to make hovering/clicking easier
                    self.button_rects[label] = full_row_rect.inflate(25, 15)

                except Exception as e: print(f"Error rendering setting value/button '{label}': {e}")


    def handle_event(self, event, mouse_pos):
        """Handles input for the settings menu.
        Returns 'Back' if the back button is activated, None otherwise.
        """
        if not self.menu_active: return None

        action = None

        # --- Mouse Hover ---
        hover_found = False
        # Use the larger, inflated `button_rects` for hover detection across the whole row
        for i, label in enumerate(self.option_order):
             if label in self.button_rects and self.button_rects[label].collidepoint(mouse_pos):
                 self.selected_option_index = i
                 hover_found = True
                 break

        # --- Mouse Click ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check collision with the clickable `button_rects` again for click activation
            clicked_option_index = -1
            for i, label in enumerate(self.option_order):
                if label in self.button_rects and self.button_rects[label].collidepoint(mouse_pos):
                     clicked_option_index = i
                     break

            if clicked_option_index != -1: # If a valid row was clicked
                 selected_label = self.option_order[clicked_option_index]
                 self.selected_option_index = clicked_option_index # Update visual selection

                 print(f"Settings Action Clicked: {selected_label}")

                 # Perform action based on clicked label
                 if self.options[selected_label]: # If it's a toggleable option
                     if selected_label == "Music":
                         settings.MUSIC_ENABLED = not settings.MUSIC_ENABLED
                         print(f"Music Enabled set to: {settings.MUSIC_ENABLED}")
                     elif selected_label == "Sound Effects":
                         settings.SFX_ENABLED = not settings.SFX_ENABLED
                         print(f"Sound Effects Enabled set to: {settings.SFX_ENABLED}")
                 elif selected_label == "Back":
                     action = "Back" # Signal main loop to return

        # --- Keyboard Navigation ---
        if event.type == pygame.KEYDOWN:
            original_selection = self.selected_option_index
            if event.key == pygame.K_UP:
                self.selected_option_index = (self.selected_option_index - 1) % len(self.option_order)
            elif event.key == pygame.K_DOWN:
                self.selected_option_index = (self.selected_option_index + 1) % len(self.option_order)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                 # Ensure selection is valid before acting
                 if 0 <= self.selected_option_index < len(self.option_order):
                    selected_label = self.option_order[self.selected_option_index]
                    print(f"Settings Action Selected (Enter): {selected_label}")
                    if self.options[selected_label]: # Toggle setting
                         if selected_label == "Music": settings.MUSIC_ENABLED = not settings.MUSIC_ENABLED
                         elif selected_label == "Sound Effects": settings.SFX_ENABLED = not settings.SFX_ENABLED
                    elif selected_label == "Back":
                         action = "Back" # Signal return
            elif event.key == pygame.K_ESCAPE: # Allow ESC to go back
                 action = "Back"
                 print("Settings closed via Escape.")

            # Play UI feedback sound on keyboard navigation? (Optional)
            # if self.selected_option_index != original_selection and settings.SFX_ENABLED and settings.SFX_SELECT:
            #    pygame.mixer.Channel(settings.UI_CHANNEL).play(settings.SFX_SELECT)

        return action # Return 'Back' or None

    def show(self):
        """Activates the settings menu."""
        self.menu_active = True
        self.selected_option_index = 0 # Reset selection to the top option

    def hide(self):
        """Deactivates the settings menu."""
        self.menu_active = False

    def draw(self, surface):
        """Draws the settings screen elements."""
        if not self.menu_active: return

        # 1. Draw semi-transparent overlay (provides background contrast)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(settings.MENU_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        # 2. Render title, options, values/buttons (calculates positions dynamically)
        self._render_options(surface)


# --- END OF FILE settings_menu.py ---