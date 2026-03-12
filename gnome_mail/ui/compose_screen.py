"""Full-screen compose overlay for writing new messages."""

import uuid
import pygame

from gnome_mail.ui.theme import (
    PANEL_BG, TEXT_COLOR, TEXT_DIM, ACCENT_LIGHT, PADDING, get_font,
)
from gnome_mail.ui.widgets import Button, TextArea, Dropdown, ToastManager
from gnome_mail.gnome_art import draw_gnome_with_quill, draw_toadstool_border
from gnome_mail import constants


class ComposeScreen:
    """Modal compose overlay. Captures all events when open."""

    PANEL_W = 600
    PANEL_H = 500

    def __init__(self, toast_manager):
        self.toast_manager = toast_manager
        self.visible = False
        self._models = []
        self._result = None  # Set when send succeeds, read by app

        # Widgets created on open()
        self.dropdown = None
        self.text_area = None
        self.send_btn = None
        self.cancel_btn = None
        self._panel_rect = pygame.Rect(0, 0, self.PANEL_W, self.PANEL_H)

    def open(self, window_size):
        """Open the compose screen. Fetches models from Ollama."""
        self.visible = True
        self._result = None
        self._layout(window_size)
        self._fetch_models()

    def _layout(self, window_size):
        """Recalculate widget positions based on window size."""
        ww, wh = window_size
        px = (ww - self.PANEL_W) // 2
        py = (wh - self.PANEL_H) // 2
        self._panel_rect = pygame.Rect(px, py, self.PANEL_W, self.PANEL_H)

        inner_x = px + PADDING
        inner_w = self.PANEL_W - 2 * PADDING
        y = py + 70  # After header + gnome sprite

        # Model dropdown label + dropdown
        self.dropdown = Dropdown(
            (inner_x, y + 20, inner_w, 32),
            options=[],
            selected=0,
            font_key="body",
        )
        y += 64

        # Text area
        ta_h = self.PANEL_H - 200
        self.text_area = TextArea(
            (inner_x, y, inner_w, ta_h),
            placeholder=constants.COMPOSE_PLACEHOLDER,
            font_key="body",
        )
        self.text_area.focused = True
        y += ta_h + 12

        # Buttons
        btn_w = 180
        btn_h = 36
        self.cancel_btn = Button(
            (inner_x, y, btn_w, btn_h),
            constants.CANCEL_BUTTON,
            callback=self._cancel,
        )
        self.send_btn = Button(
            (inner_x + inner_w - btn_w - 20, y, btn_w + 20, btn_h),
            constants.SEND_BUTTON,
            callback=self._send,
        )

    def _fetch_models(self):
        try:
            import ollama
            response = ollama.list()
            self._models = [m.model for m in response.models] if hasattr(response, 'models') else []
            if not self._models:
                # Try dict-style access
                if isinstance(response, dict) and "models" in response:
                    self._models = [m.get("model", m.get("name", "unknown")) for m in response["models"]]
        except Exception:
            self._models = []

        if self._models:
            self.dropdown.options = self._models
            self.dropdown.selected = 0
        else:
            self.dropdown.options = [constants.OLLAMA_UNAVAILABLE]
            self.dropdown.selected = 0
            self.toast_manager.show(constants.TOAST_ERROR_TEMPLATE.format("Ollama"))

    def _cancel(self):
        self.visible = False

    def _send(self):
        message = self.text_area.text.strip()
        if not message:
            self.toast_manager.show(constants.EMPTY_MESSAGE_WARNING)
            return

        model = self.dropdown.get_selected()
        if not model or model == constants.OLLAMA_UNAVAILABLE:
            self.toast_manager.show(constants.TOAST_ERROR_TEMPLATE.format("Ollama"))
            return

        conversation_id = str(uuid.uuid4())
        subject = message[:60]

        self._result = {
            "id": conversation_id,
            "model": model,
            "subject": subject,
            "user_message": message,
        }
        self.visible = False

    def get_result(self):
        """Return and clear the send result."""
        r = self._result
        self._result = None
        return r

    def handle_event(self, event):
        """Handle all events (modal). Returns True always when visible."""
        if not self.visible:
            return False

        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        # Route to widgets
        # Dropdown gets priority when expanded (renders on top)
        if self.dropdown and self.dropdown.expanded:
            self.dropdown.handle_event(event)
            return True

        if self.send_btn:
            self.send_btn.handle_event(event)
        if self.cancel_btn:
            self.cancel_btn.handle_event(event)
        if self.dropdown:
            self.dropdown.handle_event(event)
        if self.text_area:
            self.text_area.handle_event(event)

        return True  # Modal — consume all events

    def draw(self, surface):
        if not self.visible:
            return

        ww, wh = surface.get_size()

        # Semi-transparent dark backdrop
        backdrop = pygame.Surface((ww, wh), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 160))
        surface.blit(backdrop, (0, 0))

        # Panel background
        pygame.draw.rect(surface, PANEL_BG, self._panel_rect, border_radius=8)
        draw_toadstool_border(surface, self._panel_rect)

        # Header: gnome with quill + title
        px, py = self._panel_rect.x, self._panel_rect.y
        draw_gnome_with_quill(surface, px + 36, py + 32, 0.8)
        font_title = get_font("title", bold=True)
        title_surf = font_title.render(constants.COMPOSE_TITLE, True, TEXT_COLOR)
        surface.blit(title_surf, (px + 80, py + PADDING))

        # Model dropdown label
        font_small = get_font("small")
        label_surf = font_small.render(constants.MODEL_DROPDOWN_LABEL, True, TEXT_DIM)
        surface.blit(label_surf, (self.dropdown.rect.x, self.dropdown.rect.y - 16))

        # Widgets
        self.text_area.draw(surface)
        self.cancel_btn.draw(surface)
        self.send_btn.draw(surface)
        # Dropdown drawn last so expanded list renders on top
        self.dropdown.draw(surface)
