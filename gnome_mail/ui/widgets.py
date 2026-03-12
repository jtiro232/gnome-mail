"""Reusable UI components for Gnome Mail. All widgets built on Pygame primitives."""

import time
import pygame

from gnome_mail.ui.theme import (
    BUTTON_BG, BUTTON_HOVER, BUTTON_TEXT, INPUT_BG, INPUT_BORDER,
    TEXT_COLOR, TEXT_DIM, ACCENT_LIGHT, TOAST_BG, PANEL_BG,
    PADDING, DIVIDER, HOVER_BG, get_font,
)


def word_wrap_text(text, font, max_width):
    """Word-wrap text to fit within max_width. Returns list of strings."""
    if not text:
        return [""]
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test = (current_line + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                # Handle words wider than max_width
                if font.size(word)[0] > max_width:
                    # Break long word character by character
                    chunk = ""
                    for ch in word:
                        if font.size(chunk + ch)[0] > max_width and chunk:
                            lines.append(chunk)
                            chunk = ch
                        else:
                            chunk += ch
                    current_line = chunk
                else:
                    current_line = word
        if current_line:
            lines.append(current_line)
    return lines if lines else [""]


class Button:
    """Rounded rect button with hover state and click callback."""

    def __init__(self, rect, text, callback=None, font_key="body"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font_key = font_key
        self.hovered = False
        self.visible = True

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            old = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered != old
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface):
        if not self.visible:
            return
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        font = get_font(self.font_key)
        text_surf = font.render(self.text, True, BUTTON_TEXT)
        tx = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        ty = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))


class TextInput:
    """Single-line text input with cursor and focus state."""

    def __init__(self, rect, placeholder="", font_key="body"):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.font_key = font_key
        self.focused = False
        self.cursor_pos = 0
        self.scroll_offset = 0
        self._cursor_visible = True
        self._cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            old_focus = self.focused
            self.focused = self.rect.collidepoint(event.pos)
            if self.focused:
                self._cursor_timer = time.time()
                self._cursor_visible = True
            return self.focused != old_focus

        if not self.focused:
            return False

        if event.type == pygame.KEYDOWN:
            self._cursor_timer = time.time()
            self._cursor_visible = True
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :]
                    self.cursor_pos -= 1
                    return True
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[: self.cursor_pos] + self.text[self.cursor_pos + 1 :]
                    return True
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    return True
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                    return True
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                return True
            elif event.unicode and event.unicode >= " " and event.key != pygame.K_RETURN:
                self.text = self.text[: self.cursor_pos] + event.unicode + self.text[self.cursor_pos :]
                self.cursor_pos += 1
                return True
        return False

    def draw(self, surface):
        # Background and border
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=4)
        border_color = ACCENT_LIGHT if self.focused else INPUT_BORDER
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)

        font = get_font(self.font_key)
        inner_x = self.rect.x + 8
        inner_w = self.rect.width - 16

        if self.text:
            # Scroll to keep cursor visible
            cursor_x = font.size(self.text[: self.cursor_pos])[0]
            if cursor_x - self.scroll_offset > inner_w - 4:
                self.scroll_offset = cursor_x - inner_w + 4
            if cursor_x - self.scroll_offset < 0:
                self.scroll_offset = max(0, cursor_x)

            text_surf = font.render(self.text, True, TEXT_COLOR)
            clip = pygame.Rect(inner_x, self.rect.y, inner_w, self.rect.height)
            old_clip = surface.get_clip()
            surface.set_clip(clip)
            surface.blit(text_surf, (inner_x - self.scroll_offset, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
            surface.set_clip(old_clip)
        else:
            text_surf = font.render(self.placeholder, True, TEXT_DIM)
            surface.blit(text_surf, (inner_x, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Cursor
        if self.focused:
            now = time.time()
            if now - self._cursor_timer > 0.5:
                self._cursor_visible = not self._cursor_visible
                self._cursor_timer = now
            if self._cursor_visible:
                cx = inner_x + font.size(self.text[: self.cursor_pos])[0] - self.scroll_offset
                cy = self.rect.y + 4
                ch = self.rect.height - 8
                pygame.draw.line(surface, TEXT_COLOR, (cx, cy), (cx, cy + ch), 1)


class TextArea:
    """Multi-line text input with word wrapping, scrolling, and cursor."""

    def __init__(self, rect, placeholder="", font_key="body"):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.font_key = font_key
        self.focused = False
        self.cursor_pos = 0
        self.scroll_offset = 0
        self._cursor_visible = True
        self._cursor_timer = 0
        self._line_height = 0

    def _get_wrapped_lines(self):
        font = get_font(self.font_key)
        return word_wrap_text(self.text, font, self.rect.width - 24)

    def _cursor_to_line_col(self, lines):
        """Convert absolute cursor_pos to (line, col)."""
        pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            # Account for the newline/space between wrapped lines
            if pos + line_len >= self.cursor_pos:
                return (i, self.cursor_pos - pos)
            pos += line_len + 1  # +1 for space/newline
        return (len(lines) - 1, len(lines[-1]) if lines else 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            old_focus = self.focused
            self.focused = self.rect.collidepoint(event.pos)
            if self.focused:
                self._cursor_timer = time.time()
                self._cursor_visible = True
            return self.focused != old_focus

        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_offset = max(0, self.scroll_offset - event.y * 20)
            return True

        if not self.focused:
            return False

        if event.type == pygame.KEYDOWN:
            self._cursor_timer = time.time()
            self._cursor_visible = True
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :]
                    self.cursor_pos -= 1
                    return True
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[: self.cursor_pos] + self.text[self.cursor_pos + 1 :]
                    return True
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    return True
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                    return True
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                return True
            elif event.key == pygame.K_RETURN:
                self.text = self.text[: self.cursor_pos] + "\n" + self.text[self.cursor_pos :]
                self.cursor_pos += 1
                return True
            elif event.unicode and event.unicode >= " ":
                self.text = self.text[: self.cursor_pos] + event.unicode + self.text[self.cursor_pos :]
                self.cursor_pos += 1
                return True
        return False

    def draw(self, surface):
        # Background and border
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=4)
        border_color = ACCENT_LIGHT if self.focused else INPUT_BORDER
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)

        font = get_font(self.font_key)
        self._line_height = font.get_linesize()
        inner_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 8,
                                 self.rect.width - 16, self.rect.height - 16)

        old_clip = surface.get_clip()
        surface.set_clip(inner_rect)

        if not self.text and not self.focused:
            # Placeholder
            text_surf = font.render(self.placeholder, True, TEXT_DIM)
            surface.blit(text_surf, (inner_rect.x, inner_rect.y))
        else:
            lines = self._get_wrapped_lines()

            # Ensure scroll keeps cursor visible
            cursor_line, cursor_col = self._cursor_to_line_col(lines)
            cursor_y = cursor_line * self._line_height
            visible_h = inner_rect.height
            if cursor_y - self.scroll_offset < 0:
                self.scroll_offset = cursor_y
            if cursor_y + self._line_height - self.scroll_offset > visible_h:
                self.scroll_offset = cursor_y + self._line_height - visible_h

            for i, line in enumerate(lines):
                ly = inner_rect.y + i * self._line_height - self.scroll_offset
                if ly + self._line_height < inner_rect.y or ly > inner_rect.y + inner_rect.height:
                    continue
                text_surf = font.render(line, True, TEXT_COLOR)
                surface.blit(text_surf, (inner_rect.x, ly))

            # Cursor
            if self.focused:
                now = time.time()
                if now - self._cursor_timer > 0.5:
                    self._cursor_visible = not self._cursor_visible
                    self._cursor_timer = now
                if self._cursor_visible:
                    line_text = lines[cursor_line] if cursor_line < len(lines) else ""
                    cx = inner_rect.x + font.size(line_text[:cursor_col])[0]
                    cy = inner_rect.y + cursor_line * self._line_height - self.scroll_offset
                    pygame.draw.line(surface, TEXT_COLOR, (cx, cy), (cx, cy + self._line_height), 1)

        surface.set_clip(old_clip)

        # Scrollbar
        lines = self._get_wrapped_lines()
        total_h = len(lines) * self._line_height
        if total_h > inner_rect.height:
            bar_x = self.rect.x + self.rect.width - 6
            bar_h = max(20, int(inner_rect.height * inner_rect.height / total_h))
            max_scroll = total_h - inner_rect.height
            bar_y = self.rect.y + 4 + int((self.rect.height - 8 - bar_h) * min(1, self.scroll_offset / max_scroll)) if max_scroll > 0 else self.rect.y + 4
            pygame.draw.rect(surface, DIVIDER, (bar_x, bar_y, 4, bar_h), border_radius=2)


class ScrollableList:
    """Vertically scrollable list with mouse wheel scrolling and click detection."""

    def __init__(self, rect, item_height, render_item_fn=None):
        self.rect = pygame.Rect(rect)
        self.item_height = item_height
        self.render_item_fn = render_item_fn
        self.items = []
        self.scroll_offset = 0
        self.selected_index = -1
        self.hovered_index = -1

    def set_items(self, items):
        self.items = items
        # Clamp scroll
        max_scroll = max(0, len(self.items) * self.item_height - self.rect.height)
        self.scroll_offset = min(self.scroll_offset, max_scroll)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            max_scroll = max(0, len(self.items) * self.item_height - self.rect.height)
            self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y * 30))
            return True

        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.rect.y + self.scroll_offset
                new_hover = int(rel_y // self.item_height)
                if new_hover >= len(self.items):
                    new_hover = -1
                if new_hover != self.hovered_index:
                    self.hovered_index = new_hover
                    return True
            else:
                if self.hovered_index != -1:
                    self.hovered_index = -1
                    return True
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.rect.y + self.scroll_offset
                clicked = int(rel_y // self.item_height)
                if 0 <= clicked < len(self.items):
                    self.selected_index = clicked
                    return True
        return False

    def draw(self, surface):
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)

        for i, item in enumerate(self.items):
            iy = self.rect.y + i * self.item_height - self.scroll_offset
            if iy + self.item_height < self.rect.y or iy > self.rect.y + self.rect.height:
                continue
            item_rect = pygame.Rect(self.rect.x, iy, self.rect.width - 8, self.item_height)
            selected = (i == self.selected_index)
            hovered = (i == self.hovered_index)
            if self.render_item_fn:
                self.render_item_fn(surface, item, item_rect, selected, hovered)

        surface.set_clip(old_clip)

        # Scrollbar
        total_h = len(self.items) * self.item_height
        if total_h > self.rect.height:
            bar_x = self.rect.x + self.rect.width - 6
            bar_h = max(20, int(self.rect.height * self.rect.height / total_h))
            max_scroll = total_h - self.rect.height
            ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            bar_y = self.rect.y + int((self.rect.height - bar_h) * ratio)
            pygame.draw.rect(surface, DIVIDER, (bar_x, bar_y, 4, bar_h), border_radius=2)


class Dropdown:
    """Click to expand list of options, click to select."""

    def __init__(self, rect, options=None, selected=0, font_key="body"):
        self.rect = pygame.Rect(rect)
        self.options = options or []
        self.selected = selected
        self.expanded = False
        self.font_key = font_key
        self.hovered_option = -1
        self._item_height = 32

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.expanded:
                # Check if clicked on an option
                for i in range(len(self.options)):
                    oy = self.rect.y + self.rect.height + i * self._item_height
                    option_rect = pygame.Rect(self.rect.x, oy, self.rect.width, self._item_height)
                    if option_rect.collidepoint(event.pos):
                        self.selected = i
                        self.expanded = False
                        return True
                # Clicked outside — close
                self.expanded = False
                return True
            elif self.rect.collidepoint(event.pos):
                self.expanded = True
                return True
            return False

        if event.type == pygame.MOUSEMOTION and self.expanded:
            old_hover = self.hovered_option
            self.hovered_option = -1
            for i in range(len(self.options)):
                oy = self.rect.y + self.rect.height + i * self._item_height
                option_rect = pygame.Rect(self.rect.x, oy, self.rect.width, self._item_height)
                if option_rect.collidepoint(event.pos):
                    self.hovered_option = i
                    break
            return self.hovered_option != old_hover

        return False

    def get_selected(self):
        if 0 <= self.selected < len(self.options):
            return self.options[self.selected]
        return None

    def draw(self, surface):
        # Main box
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=4)
        border_color = ACCENT_LIGHT if self.expanded else INPUT_BORDER
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)

        font = get_font(self.font_key)
        if self.options:
            selected_text = self.options[self.selected] if self.selected < len(self.options) else ""
        else:
            selected_text = ""
        text_surf = font.render(selected_text, True, TEXT_COLOR)
        surface.blit(text_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Arrow
        arrow_x = self.rect.x + self.rect.width - 20
        arrow_y = self.rect.y + self.rect.height // 2
        if self.expanded:
            pts = [(arrow_x, arrow_y + 3), (arrow_x + 8, arrow_y + 3), (arrow_x + 4, arrow_y - 3)]
        else:
            pts = [(arrow_x, arrow_y - 3), (arrow_x + 8, arrow_y - 3), (arrow_x + 4, arrow_y + 3)]
        pygame.draw.polygon(surface, TEXT_DIM, pts)

        # Expanded options
        if self.expanded and self.options:
            drop_h = len(self.options) * self._item_height
            drop_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, drop_h)
            pygame.draw.rect(surface, PANEL_BG, drop_rect, border_radius=4)
            pygame.draw.rect(surface, INPUT_BORDER, drop_rect, 1, border_radius=4)
            for i, opt in enumerate(self.options):
                oy = self.rect.y + self.rect.height + i * self._item_height
                opt_rect = pygame.Rect(self.rect.x, oy, self.rect.width, self._item_height)
                if i == self.hovered_option:
                    pygame.draw.rect(surface, HOVER_BG, opt_rect)
                text_surf = font.render(opt, True, TEXT_COLOR)
                surface.blit(text_surf, (opt_rect.x + 8, opt_rect.y + (self._item_height - text_surf.get_height()) // 2))


class ToastManager:
    """Queue-based toast notification system with fade in/out."""

    FADE_IN_MS = 300
    HOLD_MS = 3000
    FADE_OUT_MS = 300

    def __init__(self):
        self._queue = []
        self._current = None  # {"text": str, "state": str, "start_time": float}
        self._alpha = 0

    def show(self, message):
        self._queue.append(message)

    @property
    def is_animating(self):
        return self._current is not None or len(self._queue) > 0

    def update(self):
        """Call each frame. Returns True if visual state changed (dirty)."""
        now = time.time() * 1000  # ms

        if self._current is None:
            if self._queue:
                self._current = {
                    "text": self._queue.pop(0),
                    "state": "fade_in",
                    "start_time": now,
                }
                self._alpha = 0
                return True
            return False

        elapsed = now - self._current["start_time"]
        state = self._current["state"]

        if state == "fade_in":
            self._alpha = min(255, int(255 * elapsed / self.FADE_IN_MS))
            if elapsed >= self.FADE_IN_MS:
                self._current["state"] = "hold"
                self._current["start_time"] = now
                self._alpha = 255
            return True
        elif state == "hold":
            if elapsed >= self.HOLD_MS:
                self._current["state"] = "fade_out"
                self._current["start_time"] = now
            return False
        elif state == "fade_out":
            self._alpha = max(0, 255 - int(255 * elapsed / self.FADE_OUT_MS))
            if elapsed >= self.FADE_OUT_MS:
                self._current = None
                self._alpha = 0
            return True
        return False

    def draw(self, surface, window_width, window_height):
        if self._current is None:
            return
        font = get_font("body")
        text_surf = font.render(self._current["text"], True, TEXT_COLOR)
        tw, th = text_surf.get_size()
        pw = tw + 32
        ph = th + 16
        px = (window_width - pw) // 2
        py = window_height - ph - 24

        # Create toast surface with alpha
        toast_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        toast_surf.fill((*TOAST_BG, self._alpha))
        pygame.draw.rect(toast_surf, (*ACCENT_LIGHT, self._alpha), (0, 0, pw, ph), 1, border_radius=8)

        # Render text with alpha
        text_alpha_surf = text_surf.copy()
        text_alpha_surf.set_alpha(self._alpha)

        surface.blit(toast_surf, (px, py))
        surface.blit(text_alpha_surf, (px + 16, py + 8))
