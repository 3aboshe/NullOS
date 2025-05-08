# main_menu.py
import pygame
import settings
import arabic_reshaper
from bidi.algorithm import get_display


class MainMenu:
    def __init__(self):
        self.title_font = settings.MENU_FONT
        self.option_font = settings.MENU_OPTION_FONT

        if not self.title_font:
            print("ERROR: MainMenu title font missing! Using fallback.")
            self.title_font = pygame.font.SysFont("impact", 72)
        if not self.option_font:
            print("ERROR: MainMenu option font missing! Using fallback.")
            self.option_font = pygame.font.SysFont("monospace", 30)

        self.options_en = ["Play", "Language", "Settings", "Quit"]
        self.options_ar = ["ابدأ", "اللغة", "الإعدادات", "خروج"]
        self.selected_option = 0
        self.option_rects = {}
        self.rendered_options = {}
        self.menu_active = True

    def _prepare_text(self, text, font, color, rtl=False):
        if rtl:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return font.render(bidi_text, True, color)
        else:
            return font.render(text, True, color)

    def _render_options(self, surface):
        center_x = settings.SCREEN_WIDTH // 2
        title_y = settings.SCREEN_HEIGHT * 0.25
        start_y = settings.SCREEN_HEIGHT * 0.55
        option_spacing = self.option_font.get_height() + 25

        self.option_rects.clear()
        self.rendered_options.clear()

        # Render Title
        try:
            title_text = "NullOS"
            title_surf = self.title_font.render(title_text, True, settings.MENU_TEXT_COLOR)
            title_rect = title_surf.get_rect(centerx=center_x, centery=title_y)
            surface.blit(title_surf, title_rect)
        except Exception as e:
            print(f"Error rendering menu title: {e}")

        # Language check
        current_lang = settings.CURRENT_LANGUAGE
        font = settings.ARABIC_FONT if current_lang == 'ar' and settings.ARABIC_FONT else self.option_font
        options = self.options_ar if current_lang == 'ar' else self.options_en
        rtl = (current_lang == 'ar')

        current_y = start_y
        for i, option in enumerate(options):
            try:
                normal_surf = self._prepare_text(option, font, settings.MENU_TEXT_COLOR, rtl)
                hover_surf = self._prepare_text(option, font, settings.MENU_TEXT_HOVER_COLOR, rtl)

                self.rendered_options[i] = (normal_surf, hover_surf)
                option_rect = normal_surf.get_rect(centerx=center_x, top=current_y)
                self.option_rects[i] = option_rect
                current_y += option_spacing
            except Exception as e:
                print(f"Error rendering option '{option}': {e}")

    def handle_event(self, event, mouse_pos):
        if not self.menu_active:
            return None

        action = None
        hover_found = False

        for i, rect in self.option_rects.items():
            if rect.collidepoint(mouse_pos):
                self.selected_option = i
                hover_found = True
                break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hover_found and self.selected_option in range(len(self.options_en)):
                action = self.options_en[self.selected_option]
                if action == 'Language':
                    settings.CURRENT_LANGUAGE = 'ar' if settings.CURRENT_LANGUAGE == 'en' else 'en'
                    settings.save_settings()
                    action = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options_en)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options_en)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                action = self.options_en[self.selected_option]
                if action == 'Language':
                    settings.CURRENT_LANGUAGE = 'ar' if settings.CURRENT_LANGUAGE == 'en' else 'en'
                    settings.save_settings()
                    action = None
            elif event.key == pygame.K_ESCAPE:
                action = "Quit"

        return action

    def draw(self, surface):
        if not self.menu_active:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(settings.MENU_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        self._render_options(surface)

        for i, rect in self.option_rects.items():
            normal_surf, hover_surf = self.rendered_options[i]
            surf = hover_surf if i == self.selected_option else normal_surf
            surface.blit(surf, rect)

        # Draw language label
        lang_code = settings.CURRENT_LANGUAGE
        lang_name = settings.LANGUAGES.get(lang_code, lang_code)
        font = settings.ARABIC_FONT if lang_code == 'ar' and settings.ARABIC_FONT else self.option_font

        if lang_code == 'ar':
            lang_text = get_display(arabic_reshaper.reshape("اللغة: العربية"))
        else:
            lang_text = f"Language: {lang_name}"

        try:
            lang_surf = font.render(lang_text, True, settings.MENU_TEXT_HOVER_COLOR)
            lang_rect = lang_surf.get_rect(bottomright=(settings.SCREEN_WIDTH - 20, settings.SCREEN_HEIGHT - 20))
            surface.blit(lang_surf, lang_rect)
        except Exception as e:
            print(f"Error rendering language label: {e}")
