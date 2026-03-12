"""Settings overlay for renaming gnomes."""

import pygame

from gnome_mail.ui.theme import (
    PANEL_BG, TEXT_COLOR, TEXT_DIM, ACCENT_LIGHT, INPUT_BG, INPUT_BORDER,
    PADDING, DIVIDER, HOVER_BG, get_font,
)
from gnome_mail.ui.widgets import Button, TextInput
from gnome_mail.gnome_art import draw_gnome_with_wrench, draw_mini_gnome_head
from gnome_mail import constants


class SettingsScreen:
    """Modal settings overlay for renaming gnome personas."""

    PANEL_W = 560
    PANEL_H = 480

    def __init__(self, toast_manager):
        self.toast_manager = toast_manager
        self.visible = False
        self._models = []
        self._editing_index = -1
        self._edit_input = None
        self._scroll_offset = 0
        self._item_height = 44
        self._panel_rect = pygame.Rect(0, 0, self.PANEL_W, self.PANEL_H)
        self._list_rect = pygame.Rect(0, 0, 0, 0)
        self._close_btn = None
        self._hovered_index = -1

    def open(self, window_size):
        """Open settings, refreshing the model list."""
        self.visible = True
        self._editing_index = -1
        self._edit_input = None
        self._scroll_offset = 0
        self._hovered_index = -1
        self._layout(window_size)
        self._refresh_models()

    def _layout(self, window_size):
        ww, wh = window_size
        px = (ww - self.PANEL_W) // 2
        py = (wh - self.PANEL_H) // 2
        self._panel_rect = pygame.Rect(px, py, self.PANEL_W, self.PANEL_H)

        inner_x = px + PADDING
        inner_w = self.PANEL_W - 2 * PADDING

        # Close button
        self._close_btn = Button(
            (inner_x + inner_w - 80, py + PADDING, 80, 28),
            "Done",
            callback=self._close,
            font_key="body",
        )

        # List area below header
        list_top = py + 64
        list_h = self.PANEL_H - 64 - PADDING
        self._list_rect = pygame.Rect(inner_x, list_top, inner_w, list_h)

    def _refresh_models(self):
        """Get current models from Ollama."""
        try:
            import ollama
            response = ollama.list()
            if hasattr(response, "models"):
                self._models = [m.model for m in response.models]
            elif isinstance(response, dict) and "models" in response:
                self._models = [m.get("model", m.get("name", "unknown")) for m in response["models"]]
            else:
                self._models = []
        except Exception:
            self._models = []
        # Also include any models we have names for but aren't currently running
        assigned = constants.get_all_assigned_names()
        for model in assigned:
            if model not in self._models:
                self._models.append(model)

    def _close(self):
        self.visible = False

    def _start_editing(self, index):
        if index < 0 or index >= len(self._models):
            return
        model = self._models[index]
        current_name = constants.get_gnome_name(model)
        self._editing_index = index

        # Create text input at the right position
        iy = self._list_rect.y + index * self._item_height - self._scroll_offset
        input_x = self._list_rect.x + 32
        input_w = self._list_rect.width - 32 - 80
        self._edit_input = TextInput(
            (input_x, iy + 6, input_w, 30),
            placeholder="Enter gnome name...",
            font_key="body",
        )
        self._edit_input.text = current_name
        self._edit_input.cursor_pos = len(current_name)
        self._edit_input.focused = True

    def _confirm_edit(self):
        if self._editing_index < 0 or not self._edit_input:
            return
        new_name = self._edit_input.text.strip()
        if new_name:
            model = self._models[self._editing_index]
            constants.set_custom_gnome_name(model, new_name)
            self.toast_manager.show(f"Renamed to {new_name}!")
        self._editing_index = -1
        self._edit_input = None

    def _cancel_edit(self):
        self._editing_index = -1
        self._edit_input = None

    def handle_event(self, event):
        if not self.visible:
            return False

        # ESC to close (or cancel edit)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self._editing_index >= 0:
                self._cancel_edit()
            else:
                self.visible = False
            return True

        # ENTER to confirm edit
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self._editing_index >= 0:
            self._confirm_edit()
            return True

        # Close button
        if self._close_btn and self._close_btn.handle_event(event):
            return True

        # Editing mode — route to text input
        if self._editing_index >= 0 and self._edit_input:
            self._edit_input.handle_event(event)
            return True

        # Scroll
        if event.type == pygame.MOUSEWHEEL and self._list_rect.collidepoint(pygame.mouse.get_pos()):
            max_scroll = max(0, len(self._models) * self._item_height - self._list_rect.height)
            self._scroll_offset = max(0, min(max_scroll, self._scroll_offset - event.y * 30))
            return True

        # Hover
        if event.type == pygame.MOUSEMOTION:
            if self._list_rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self._list_rect.y + self._scroll_offset
                idx = int(rel_y // self._item_height)
                self._hovered_index = idx if 0 <= idx < len(self._models) else -1
            else:
                self._hovered_index = -1
            return True

        # Double-click to edit
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._list_rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self._list_rect.y + self._scroll_offset
                idx = int(rel_y // self._item_height)
                if 0 <= idx < len(self._models):
                    self._start_editing(idx)
                    return True
            return True

        return True  # Modal — consume all events

    def draw(self, surface):
        if not self.visible:
            return

        ww, wh = surface.get_size()

        # Backdrop
        backdrop = pygame.Surface((ww, wh), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 160))
        surface.blit(backdrop, (0, 0))

        # Panel
        pygame.draw.rect(surface, PANEL_BG, self._panel_rect, border_radius=8)
        pygame.draw.rect(surface, ACCENT_LIGHT, self._panel_rect, 1, border_radius=8)

        px, py = self._panel_rect.x, self._panel_rect.y

        # Header: wrench gnome + title
        draw_gnome_with_wrench(surface, px + 40, py + 32, 0.6)
        font_title = get_font("title", bold=True)
        title_surf = font_title.render("Gnome Workshop", True, TEXT_COLOR)
        surface.blit(title_surf, (px + 72, py + PADDING))
        font_small = get_font("small")
        hint_surf = font_small.render("Click a gnome to rename them", True, TEXT_DIM)
        surface.blit(hint_surf, (px + 72, py + PADDING + 24))

        # Close button
        self._close_btn.draw(surface)

        # List of gnomes
        old_clip = surface.get_clip()
        surface.set_clip(self._list_rect)

        font_body = get_font("body")
        for i, model in enumerate(self._models):
            iy = self._list_rect.y + i * self._item_height - self._scroll_offset
            if iy + self._item_height < self._list_rect.y or iy > self._list_rect.y + self._list_rect.height:
                continue

            item_rect = pygame.Rect(self._list_rect.x, iy, self._list_rect.width, self._item_height)

            # Hover highlight
            if i == self._hovered_index and i != self._editing_index:
                pygame.draw.rect(surface, HOVER_BG, item_rect, border_radius=4)

            # Divider between items
            if i > 0:
                pygame.draw.line(surface, DIVIDER,
                                 (self._list_rect.x, iy),
                                 (self._list_rect.x + self._list_rect.width, iy))

            gnome_name = constants.get_gnome_name(model)

            # Mini gnome head avatar
            draw_mini_gnome_head(surface, self._list_rect.x + 14, iy + 22, 0.4, model)

            if i == self._editing_index and self._edit_input:
                # Update input position for scrolling
                self._edit_input.rect.y = iy + 6
                self._edit_input.draw(surface)
            else:
                # Gnome name
                name_surf = font_body.render(gnome_name, True, TEXT_COLOR)
                surface.blit(name_surf, (self._list_rect.x + 32, iy + 8))
                # Model id in small dim text below
                model_surf = font_small.render(model, True, TEXT_DIM)
                surface.blit(model_surf, (self._list_rect.x + 32, iy + 26))

        surface.set_clip(old_clip)

        # Scrollbar
        total_h = len(self._models) * self._item_height
        if total_h > self._list_rect.height:
            bar_x = self._list_rect.x + self._list_rect.width - 6
            bar_h = max(20, int(self._list_rect.height * self._list_rect.height / total_h))
            max_scroll = total_h - self._list_rect.height
            ratio = self._scroll_offset / max_scroll if max_scroll > 0 else 0
            bar_y = self._list_rect.y + int((self._list_rect.height - bar_h) * ratio)
            pygame.draw.rect(surface, DIVIDER, (bar_x, bar_y, 4, bar_h), border_radius=2)
