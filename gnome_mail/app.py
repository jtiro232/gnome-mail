"""Main Pygame loop, event handling, and scene manager for Gnome Mail."""

import queue
import random
import time

import pygame

from gnome_mail.ui.theme import (
    BG_COLOR, PANEL_BG, SIDEBAR_BG, TEXT_COLOR, DIVIDER, ACCENT_LIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH, HEADER_HEIGHT, PADDING,
    get_font,
)
from gnome_mail.ui.widgets import Button, ToastManager
from gnome_mail.ui.inbox_panel import InboxPanel
from gnome_mail.ui.message_panel import MessagePanel
from gnome_mail.ui.compose_screen import ComposeScreen
from gnome_mail.gnome_art import draw_mushroom_house, draw_tiny_mushroom
from gnome_mail import constants, db, ollama_worker


class GnomeMailApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption(constants.APP_NAME)

        # Initialize database
        db.init_db()

        # State
        self.running = True
        self.dirty = True
        self.result_queue = queue.Queue()
        self.clock = pygame.time.Clock()
        self.last_interaction_time = time.time()
        self.last_gnome_fact_time = time.time()

        # Toast manager
        self.toast_manager = ToastManager()

        # Calculate layout rects
        self._calc_layout()

        # Panels
        self.inbox_panel = InboxPanel(self._inbox_rect, on_select=self._on_select_conversation)
        self.message_panel = MessagePanel(self._message_rect)
        self.compose_screen = ComposeScreen(self.toast_manager)

        # Header button
        self.new_scroll_btn = Button(
            (0, 0, 120, 32),
            constants.NEW_SCROLL_BUTTON,
            callback=self._open_compose,
            font_key="body",
        )
        self._update_header_btn()

        # Load inbox
        self.inbox_panel.refresh()

    def _calc_layout(self):
        w, h = self.screen.get_size()
        self._inbox_rect = pygame.Rect(0, HEADER_HEIGHT, SIDEBAR_WIDTH, h - HEADER_HEIGHT)
        self._message_rect = pygame.Rect(SIDEBAR_WIDTH + 1, HEADER_HEIGHT, w - SIDEBAR_WIDTH - 1, h - HEADER_HEIGHT)

    def _update_header_btn(self):
        w = self.screen.get_width()
        self.new_scroll_btn.rect = pygame.Rect(w - 136, 8, 128, 32)

    def _open_compose(self):
        self.compose_screen.open(self.screen.get_size())
        self.dirty = True

    def _on_select_conversation(self, conversation_id):
        self.message_panel.load_conversation(conversation_id)
        self.dirty = True

    def _process_results(self):
        """Check for completed Ollama responses."""
        while not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
            except queue.Empty:
                break

            cid = result["conversation_id"]
            if result["success"]:
                db.update_response(cid, result["response_text"])
                # Find model name for toast
                conv = db.get_conversation(cid)
                model = conv["model"] if conv else "unknown"
                self.toast_manager.show(constants.TOAST_RECEIVED_TEMPLATE.format(model))
            else:
                db.update_error(cid, result["error_text"])
                conv = db.get_conversation(cid)
                model = conv["model"] if conv else "unknown"
                self.toast_manager.show(constants.TOAST_ERROR_TEMPLATE.format(model))

            # Refresh inbox
            self.inbox_panel.refresh()
            # Reload current message if it's the one that just completed
            if self.message_panel.current_id == cid:
                self.message_panel.reload_current()
            self.dirty = True

    def _check_gnome_facts(self):
        """Show a random gnome fact after 5 minutes of idle time."""
        now = time.time()
        if now - self.last_interaction_time > 300:  # 5 minutes
            if now - self.last_gnome_fact_time > 300:  # Don't repeat too often
                fact = random.choice(constants.RANDOM_GNOME_FACTS)
                self.toast_manager.show(fact)
                self.last_gnome_fact_time = now

    def run(self):
        while self.running:
            interacted = False

            # Process Ollama results
            self._process_results()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                    self._calc_layout()
                    self.inbox_panel.update_rect(self._inbox_rect)
                    self.message_panel.update_rect(self._message_rect)
                    self._update_header_btn()
                    if self.compose_screen.visible:
                        self.compose_screen._layout(self.screen.get_size())
                    self.dirty = True
                    continue

                interacted = True
                self.last_interaction_time = time.time()

                # Route events
                if self.compose_screen.visible:
                    self.compose_screen.handle_event(event)
                    # Check if compose just sent something
                    result = self.compose_screen.get_result()
                    if result:
                        db.save_conversation(result["id"], result["model"], result["subject"], result["user_message"])
                        ollama_worker.send_message(result["id"], result["model"], result["user_message"], self.result_queue)
                        self.inbox_panel.refresh()
                        self.inbox_panel.selected_id = result["id"]
                        self.inbox_panel.scroll_list.selected_index = 0
                        self.message_panel.load_conversation(result["id"])
                    self.dirty = True
                else:
                    # Header button
                    if self.new_scroll_btn.handle_event(event):
                        self.dirty = True

                    # Route to panels based on mouse position
                    if hasattr(event, "pos"):
                        if self._inbox_rect.collidepoint(event.pos):
                            if self.inbox_panel.handle_event(event):
                                self.dirty = True
                        elif self._message_rect.collidepoint(event.pos):
                            if self.message_panel.handle_event(event):
                                self.dirty = True
                    else:
                        # Keyboard events go to both panels
                        self.inbox_panel.handle_event(event)
                        self.message_panel.handle_event(event)
                        self.dirty = True

            # Check gnome facts
            self._check_gnome_facts()

            # Update toasts
            if self.toast_manager.update():
                self.dirty = True

            # Determine FPS
            if interacted:
                target_fps = 60
            elif self.toast_manager.is_animating:
                target_fps = 30
            else:
                target_fps = 10

            # Draw only if dirty
            if self.dirty:
                self._draw()
                self.dirty = False

            self.clock.tick(target_fps)

        pygame.quit()

    def _draw(self):
        w, h = self.screen.get_size()

        # Header bar
        pygame.draw.rect(self.screen, BG_COLOR, (0, 0, w, HEADER_HEIGHT))

        # Mushroom house + title
        draw_mushroom_house(self.screen, 28, 6, 0.5)
        font_header = get_font("title", bold=True)
        title_surf = font_header.render(constants.APP_NAME, True, TEXT_COLOR)
        self.screen.blit(title_surf, (52, (HEADER_HEIGHT - title_surf.get_height()) // 2))

        # New scroll button
        self.new_scroll_btn.draw(self.screen)

        # Header bottom divider
        pygame.draw.line(self.screen, DIVIDER, (0, HEADER_HEIGHT - 1), (w, HEADER_HEIGHT - 1))

        # Inbox panel
        self.inbox_panel.draw(self.screen)

        # Vertical divider
        pygame.draw.line(self.screen, DIVIDER,
                         (SIDEBAR_WIDTH, HEADER_HEIGHT), (SIDEBAR_WIDTH, h))

        # Message panel
        self.message_panel.draw(self.screen)

        # Compose overlay (on top of everything)
        self.compose_screen.draw(self.screen)

        # Toasts (on top of everything)
        self.toast_manager.draw(self.screen, w, h)

        pygame.display.flip()
