"""Right panel — conversation view with lazy-loaded message bodies."""

import pygame

from gnome_mail.ui.theme import (
    PANEL_BG, TEXT_COLOR, TEXT_DIM, ACCENT_LIGHT, GREEN_ACCENT,
    ERROR_COLOR, DIVIDER, PADDING, BUTTON_BG, BUTTON_HOVER, BUTTON_TEXT,
    get_font,
)
from gnome_mail.ui.widgets import word_wrap_text, Button
from gnome_mail.gnome_art import (
    draw_gnome, draw_tiny_mushroom, draw_mini_gnome_head,
    draw_flower, draw_grass_tuft,
)
from gnome_mail import constants, db


class MessagePanel:
    def __init__(self, rect, on_delete=None, on_resend=None):
        self.rect = pygame.Rect(rect)
        self.current_conversation = None
        self.current_id = None
        self.scroll_offset = 0
        self._content_height = 0
        self._dirty = True
        self.on_delete = on_delete
        self.on_resend = on_resend

        # Action buttons (created lazily based on state)
        self._delete_btn = None
        self._resend_btn = None
        self._update_buttons()

    def _update_buttons(self):
        """Recreate action buttons based on current conversation state."""
        if not self.current_conversation:
            self._delete_btn = None
            self._resend_btn = None
            return

        btn_y = self.rect.y + PADDING
        btn_x = self.rect.right - PADDING

        # Delete button — always available
        del_font = get_font("small")
        del_w = del_font.size(constants.DELETE_BUTTON)[0] + 24
        del_h = 28
        self._delete_btn = Button(
            (btn_x - del_w, btn_y, del_w, del_h),
            constants.DELETE_BUTTON,
            callback=self._do_delete,
            font_key="small",
        )

        # Resend button — only for error state
        if self.current_conversation["status"] == "error":
            resend_font = get_font("small")
            resend_w = resend_font.size(constants.RESEND_BUTTON)[0] + 24
            resend_h = 28
            self._resend_btn = Button(
                (btn_x - del_w - resend_w - 8, btn_y, resend_w, resend_h),
                constants.RESEND_BUTTON,
                callback=self._do_resend,
                font_key="small",
            )
        else:
            self._resend_btn = None

    def _do_delete(self):
        if self.on_delete and self.current_id:
            self.on_delete(self.current_id)

    def _do_resend(self):
        if self.on_resend and self.current_id:
            self.on_resend(self.current_id)

    def update_rect(self, rect):
        self.rect = pygame.Rect(rect)
        self._update_buttons()
        self._dirty = True

    def load_conversation(self, conversation_id):
        """Load full conversation from DB. Releases previous body."""
        self.current_conversation = None  # Release old body
        self.current_id = conversation_id
        self.current_conversation = db.get_conversation(conversation_id)
        self.scroll_offset = 0
        self._update_buttons()
        self._dirty = True

    def reload_current(self):
        """Reload current conversation (e.g. after response arrives)."""
        if self.current_id:
            self.current_conversation = db.get_conversation(self.current_id)
            self._update_buttons()
            self._dirty = True

    def clear(self):
        self.current_conversation = None
        self.current_id = None
        self.scroll_offset = 0
        self._update_buttons()
        self._dirty = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            max_scroll = max(0, self._content_height - self.rect.height + 60)
            self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y * 30))
            self._dirty = True
            return True

        # Route to action buttons
        if self._delete_btn:
            if self._delete_btn.handle_event(event):
                self._dirty = True
                return True
        if self._resend_btn:
            if self._resend_btn.handle_event(event):
                self._dirty = True
                return True

        return False

    def draw(self, surface):
        pygame.draw.rect(surface, PANEL_BG, self.rect)

        if not self.current_conversation:
            # Empty state — reading gnome + hint text
            cx = self.rect.x + self.rect.width // 2
            cy = self.rect.y + self.rect.height // 2 - 40
            draw_gnome(surface, cx, cy, 1.5, "reading")
            font = get_font("body")
            hint = font.render("Select a scroll from the mushroom patch...", True, TEXT_DIM)
            surface.blit(hint, (
                cx - hint.get_width() // 2,
                cy + 70,
            ))
            self._dirty = False
            return

        conv = self.current_conversation
        content_x = self.rect.x + PADDING
        content_w = self.rect.width - 2 * PADDING - 8  # 8 for scrollbar
        y = self.rect.y + PADDING - self.scroll_offset

        old_clip = surface.get_clip()
        surface.set_clip(self.rect)

        # Header with tiny mushroom decorations
        font_title = get_font("title", bold=True)
        font_body = get_font("body")
        font_small = get_font("small")

        # Show gnome name with avatar
        gnome_name = constants.get_gnome_name(conv["model"])
        header_text = gnome_name
        draw_mini_gnome_head(surface, content_x + 12, y + 12, 0.5, conv["model"])
        header_surf = font_title.render(header_text, True, ACCENT_LIGHT)
        surface.blit(header_surf, (content_x + 30, y))
        draw_tiny_mushroom(surface, content_x + 30 + header_surf.get_width() + 10, y + 8)
        draw_tiny_mushroom(surface, content_x + 30 + header_surf.get_width() + 28, y + 10)
        y += header_surf.get_height() + 12

        # Divider
        pygame.draw.line(surface, DIVIDER, (content_x, y), (content_x + content_w, y))
        y += 12

        # "You whispered" label
        you_surf = font_small.render(constants.YOU_LABEL, True, ACCENT_LIGHT)
        surface.blit(you_surf, (content_x, y))
        y += you_surf.get_height() + 6

        # User message (word-wrapped)
        user_lines = word_wrap_text(conv["user_message"], font_body, content_w)
        for line in user_lines:
            line_surf = font_body.render(line, True, TEXT_COLOR)
            surface.blit(line_surf, (content_x, y))
            y += font_body.get_linesize()
        y += 20

        # Divider
        pygame.draw.line(surface, DIVIDER, (content_x, y), (content_x + content_w, y))
        y += 12

        status = conv["status"]
        if status == "complete" and conv.get("assistant_response"):
            # Response label with gnome name
            resp_label = constants.RESPONSE_LABEL_TEMPLATE.format(gnome_name)
            resp_label_surf = font_small.render(resp_label, True, GREEN_ACCENT)
            surface.blit(resp_label_surf, (content_x, y))
            y += resp_label_surf.get_height() + 6

            # Response text (word-wrapped)
            resp_lines = word_wrap_text(conv["assistant_response"], font_body, content_w)
            for line in resp_lines:
                line_surf = font_body.render(line, True, TEXT_COLOR)
                surface.blit(line_surf, (content_x, y))
                y += font_body.get_linesize()

        elif status == "pending":
            # Walking gnome + waiting text
            gnome_x = content_x + content_w // 2
            gnome_y = y + 20
            draw_gnome(surface, gnome_x, gnome_y, 1.2, "walking")
            y += 80
            wait_surf = font_body.render(constants.WAITING_RESPONSE, True, TEXT_DIM)
            surface.blit(wait_surf, (content_x + (content_w - wait_surf.get_width()) // 2, y))
            y += wait_surf.get_height()

        elif status == "error":
            # Sad gnome + error text
            gnome_x = content_x + content_w // 2
            gnome_y = y + 20
            draw_gnome(surface, gnome_x, gnome_y, 1.2, "sad")
            y += 80

            # Error detail header
            detail_surf = font_small.render(constants.ERROR_DETAIL, True, ERROR_COLOR)
            surface.blit(detail_surf, (content_x, y))
            y += detail_surf.get_height() + 6

            error_text = conv.get("error_text", "Unknown error")
            error_lines = word_wrap_text(error_text, font_body, content_w)
            for line in error_lines:
                line_surf = font_body.render(line, True, ERROR_COLOR)
                surface.blit(line_surf, (content_x, y))
                y += font_body.get_linesize()

        self._content_height = y + self.scroll_offset - self.rect.y

        # Scrollbar
        if self._content_height > self.rect.height:
            bar_x = self.rect.x + self.rect.width - 6
            visible_ratio = self.rect.height / self._content_height
            bar_h = max(20, int(self.rect.height * visible_ratio))
            max_scroll = self._content_height - self.rect.height + 60
            ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            bar_y = self.rect.y + int((self.rect.height - bar_h) * ratio)
            pygame.draw.rect(surface, DIVIDER, (bar_x, bar_y, 4, bar_h), border_radius=2)

        surface.set_clip(old_clip)

        # Decorative footer sprites (bottom corners, outside scrollable content)
        footer_y = self.rect.bottom - 12
        draw_grass_tuft(surface, self.rect.x + 20, footer_y, 0.5)
        draw_flower(surface, self.rect.x + 50, footer_y, 0.25, (220, 180, 60))
        draw_grass_tuft(surface, self.rect.right - 60, footer_y, 0.5)
        draw_flower(surface, self.rect.right - 35, footer_y, 0.25, (200, 140, 180))
        draw_tiny_mushroom(surface, self.rect.right - 80, footer_y - 2)

        # Draw action buttons ON TOP of clip area (so they're always visible)
        if self._delete_btn:
            self._delete_btn.draw(surface)
        if self._resend_btn:
            self._resend_btn.draw(surface)

        self._dirty = False
