"""Left panel — inbox list with pagination."""

import pygame

from gnome_mail.ui.theme import (
    SIDEBAR_BG, SELECTED_BG, HOVER_BG, TEXT_COLOR, TEXT_DIM,
    ACCENT_LIGHT, ERROR_COLOR, GREEN_ACCENT, DIVIDER,
    INBOX_ITEM_HEIGHT, PADDING, get_font,
)
from gnome_mail.ui.widgets import ScrollableList, Button
from gnome_mail.gnome_art import (
    draw_gnome_mail_carrier, draw_tiny_mushroom, draw_sidebar_forest_footer,
)
from gnome_mail import constants, db


def _truncate_to_width(text, font, max_width):
    """Truncate text with ellipsis to fit within max_width pixels."""
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    ew = font.size(ellipsis)[0]
    for i in range(len(text), 0, -1):
        if font.size(text[:i])[0] + ew <= max_width:
            return text[:i] + ellipsis
    return ellipsis


class InboxPanel:
    def __init__(self, rect, on_select=None, on_delete=None):
        self.rect = pygame.Rect(rect)
        self.on_select = on_select
        self.on_delete = on_delete
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

        # Track delete button hover per item
        self._delete_hovered_index = -1

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

    def _get_delete_rect(self, item_rect):
        """Return the rect for the delete (X) button on an inbox item."""
        bw, bh = 20, 20
        return pygame.Rect(
            item_rect.right - bw - 8,
            item_rect.y + (item_rect.height - bh) // 2,
            bw, bh,
        )

    def handle_event(self, event):
        dirty = False
        old_selected = self.scroll_list.selected_index

        if self.load_more_btn.visible:
            dirty |= self.load_more_btn.handle_event(event)

        # Check for delete button clicks before scroll list
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Check if click is on a delete button
                for i, item in enumerate(self.conversations):
                    iy = self.scroll_list.rect.y + i * INBOX_ITEM_HEIGHT - self.scroll_list.scroll_offset
                    if iy + INBOX_ITEM_HEIGHT < self.scroll_list.rect.y or iy > self.scroll_list.rect.bottom:
                        continue
                    item_rect = pygame.Rect(self.scroll_list.rect.x, iy,
                                            self.scroll_list.rect.width - 8, INBOX_ITEM_HEIGHT)
                    del_rect = self._get_delete_rect(item_rect)
                    if del_rect.collidepoint(event.pos):
                        if self.on_delete:
                            self.on_delete(item["id"])
                        return True

        # Track hover over delete buttons
        if event.type == pygame.MOUSEMOTION:
            old_del_hover = self._delete_hovered_index
            self._delete_hovered_index = -1
            if self.rect.collidepoint(event.pos):
                for i in range(len(self.conversations)):
                    iy = self.scroll_list.rect.y + i * INBOX_ITEM_HEIGHT - self.scroll_list.scroll_offset
                    if iy + INBOX_ITEM_HEIGHT < self.scroll_list.rect.y or iy > self.scroll_list.rect.bottom:
                        continue
                    item_rect = pygame.Rect(self.scroll_list.rect.x, iy,
                                            self.scroll_list.rect.width - 8, INBOX_ITEM_HEIGHT)
                    del_rect = self._get_delete_rect(item_rect)
                    if del_rect.collidepoint(event.pos):
                        self._delete_hovered_index = i
                        break
            if self._delete_hovered_index != old_del_hover:
                dirty = True

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
        max_text_w = rect.width - PADDING * 2 - 30  # Reserve space for delete btn

        # Tiny mushroom + model gnome name
        draw_tiny_mushroom(surface, x + 6, y + 6)
        font_small = get_font("small")
        gnome_name = constants.get_gnome_name(item["model"])
        display_model = f"{gnome_name} ({item['model']})"
        display_model = _truncate_to_width(display_model, font_small, max_text_w - 20)
        model_surf = font_small.render(display_model, True, ACCENT_LIGHT)
        surface.blit(model_surf, (x + 18, y))

        # Subject — truncate by pixel width
        font_body = get_font("body")
        subject = _truncate_to_width(item["subject"], font_body, max_text_w)
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
            sub_text = _truncate_to_width(sub_text, font_small, max_text_w)
            sub_surf = font_small.render(sub_text, True, sub_color)
            surface.blit(sub_surf, (x, y + 38))

        # Delete button (X) — show on hover or selected
        if selected or hovered:
            del_rect = self._get_delete_rect(rect)
            idx = None
            for i, c in enumerate(self.conversations):
                if c["id"] == item["id"]:
                    idx = i
                    break
            del_hovered = (idx == self._delete_hovered_index)
            btn_color = ERROR_COLOR if del_hovered else TEXT_DIM
            pygame.draw.rect(surface, btn_color, del_rect, 1, border_radius=3)
            font_x = get_font("small")
            x_surf = font_x.render("X", True, btn_color)
            surface.blit(x_surf, (
                del_rect.x + (del_rect.width - x_surf.get_width()) // 2,
                del_rect.y + (del_rect.height - x_surf.get_height()) // 2,
            ))

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

        # Forest footer at very bottom
        footer_h = 40
        footer_rect = (self.rect.x, self.rect.bottom - footer_h, self.rect.width, footer_h)
        draw_sidebar_forest_footer(surface, footer_rect)

        self._dirty = False
