"""Left panel — inbox list with pagination."""

import pygame

from gnome_mail.ui.theme import (
    SIDEBAR_BG, SELECTED_BG, HOVER_BG, TEXT_COLOR, TEXT_DIM,
    ACCENT_LIGHT, ERROR_COLOR, GREEN_ACCENT, DIVIDER,
    INBOX_ITEM_HEIGHT, PADDING, get_font,
)
from gnome_mail.ui.widgets import ScrollableList, Button
from gnome_mail.gnome_art import draw_gnome_mail_carrier, draw_tiny_mushroom
from gnome_mail import constants, db


class InboxPanel:
    def __init__(self, rect, on_select=None):
        self.rect = pygame.Rect(rect)
        self.on_select = on_select
        self.conversations = []
        self.selected_id = None
        self.total_count = 0
        self._dirty = True

        # Header area
        header_h = 40
        list_y = self.rect.y + header_h
        list_h = self.rect.height - header_h

        self.scroll_list = ScrollableList(
            (self.rect.x, list_y, self.rect.width, list_h),
            INBOX_ITEM_HEIGHT,
            self._render_item,
        )

        self.load_more_btn = Button(
            (self.rect.x + PADDING, self.rect.y + self.rect.height - 36,
             self.rect.width - 2 * PADDING, 30),
            constants.LOAD_MORE,
            callback=self._load_more,
            font_key="small",
        )
        self.load_more_btn.visible = False

    def update_rect(self, rect):
        self.rect = pygame.Rect(rect)
        header_h = 40
        list_y = self.rect.y + header_h
        list_h = self.rect.height - header_h - (36 if self.load_more_btn.visible else 0)
        self.scroll_list.rect = pygame.Rect(self.rect.x, list_y, self.rect.width, list_h)
        self.load_more_btn.rect = pygame.Rect(
            self.rect.x + PADDING, self.rect.y + self.rect.height - 36,
            self.rect.width - 2 * PADDING, 30,
        )
        self._dirty = True

    def refresh(self):
        self.conversations = db.get_conversations(0, constants.INBOX_PAGE_SIZE)
        self.total_count = db.get_total_count()
        self.scroll_list.set_items(self.conversations)
        self.load_more_btn.visible = len(self.conversations) < self.total_count
        self._update_list_height()
        # Restore selection index
        self.scroll_list.selected_index = -1
        if self.selected_id:
            for i, c in enumerate(self.conversations):
                if c["id"] == self.selected_id:
                    self.scroll_list.selected_index = i
                    break
        self._dirty = True

    def _load_more(self):
        offset = len(self.conversations)
        more = db.get_conversations(offset, constants.INBOX_PAGE_SIZE)
        self.conversations.extend(more)
        self.total_count = db.get_total_count()
        self.scroll_list.set_items(self.conversations)
        self.load_more_btn.visible = len(self.conversations) < self.total_count
        self._update_list_height()
        self._dirty = True

    def _update_list_height(self):
        header_h = 40
        btn_h = 36 if self.load_more_btn.visible else 0
        list_h = self.rect.height - header_h - btn_h
        self.scroll_list.rect = pygame.Rect(
            self.rect.x, self.rect.y + header_h, self.rect.width, list_h
        )

    def handle_event(self, event):
        dirty = False
        old_selected = self.scroll_list.selected_index

        if self.load_more_btn.visible:
            dirty |= self.load_more_btn.handle_event(event)

        dirty |= self.scroll_list.handle_event(event)

        if self.scroll_list.selected_index != old_selected and self.scroll_list.selected_index >= 0:
            idx = self.scroll_list.selected_index
            if idx < len(self.conversations):
                self.selected_id = self.conversations[idx]["id"]
                if self.on_select:
                    self.on_select(self.selected_id)
                dirty = True

        if dirty:
            self._dirty = True
        return dirty

    def _render_item(self, surface, item, rect, selected, hovered):
        # Background
        if selected:
            pygame.draw.rect(surface, SELECTED_BG, rect)
        elif hovered:
            pygame.draw.rect(surface, HOVER_BG, rect)

        x = rect.x + PADDING
        y = rect.y + 8

        # Tiny mushroom + model name
        draw_tiny_mushroom(surface, x + 6, y + 6)
        font_small = get_font("small")
        model_surf = font_small.render(item["model"], True, ACCENT_LIGHT)
        surface.blit(model_surf, (x + 18, y))

        # Subject
        font_body = get_font("body")
        subject = item["subject"]
        if len(subject) > 45:
            subject = subject[:42] + "..."
        subject_surf = font_body.render(subject, True, TEXT_COLOR)
        surface.blit(subject_surf, (x, y + 18))

        # Status subtitle
        status = item["status"]
        if status == "pending":
            sub_text = constants.PENDING_SUBTITLE
            sub_color = TEXT_DIM
        elif status == "error":
            sub_text = constants.ERROR_SUBTITLE
            sub_color = ERROR_COLOR
        else:
            sub_text = ""
            sub_color = TEXT_DIM
        if sub_text:
            sub_surf = font_small.render(sub_text, True, sub_color)
            surface.blit(sub_surf, (x, y + 38))

        # Bottom divider
        pygame.draw.line(surface, DIVIDER, (rect.x + 8, rect.bottom - 1), (rect.right - 8, rect.bottom - 1))

    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, SIDEBAR_BG, self.rect)

        # Header
        font_title = get_font("title", bold=True)
        title_surf = font_title.render(constants.INBOX_TITLE, True, TEXT_COLOR)
        surface.blit(title_surf, (self.rect.x + PADDING, self.rect.y + 8))

        # Tiny mushroom decorations in header
        draw_tiny_mushroom(surface, self.rect.x + PADDING + title_surf.get_width() + 10, self.rect.y + 14)
        draw_tiny_mushroom(surface, self.rect.x + PADDING + title_surf.get_width() + 28, self.rect.y + 16)

        if not self.conversations:
            # Empty state
            cx = self.rect.x + self.rect.width // 2
            cy = self.rect.y + self.rect.height // 2 - 30
            draw_gnome_mail_carrier(surface, cx, cy, 1.5)
            font = get_font("body")
            empty_surf = font.render(constants.EMPTY_INBOX, True, TEXT_DIM)
            surface.blit(empty_surf, (cx - empty_surf.get_width() // 2, cy + 70))
        else:
            self.scroll_list.draw(surface)
            if self.load_more_btn.visible:
                self.load_more_btn.draw(surface)

        self._dirty = False
