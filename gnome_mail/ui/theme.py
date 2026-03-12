"""ALL colors, fonts, sizes, and spacing for Gnome Mail. Import from here everywhere."""

import pygame

# Colors — earthy woodland palette
BG_COLOR = (34, 40, 34)
PANEL_BG = (45, 52, 45)
SIDEBAR_BG = (38, 45, 38)
SELECTED_BG = (62, 80, 58)
HOVER_BG = (55, 68, 52)
TEXT_COLOR = (220, 215, 200)
TEXT_DIM = (140, 135, 120)
ACCENT = (139, 90, 43)
ACCENT_LIGHT = (180, 130, 70)
MUSHROOM_RED = (180, 50, 50)
MUSHROOM_SPOT = (240, 230, 210)
GNOME_HAT_RED = (160, 40, 40)
GNOME_SKIN = (210, 175, 140)
GREEN_ACCENT = (80, 140, 60)
ERROR_COLOR = (170, 60, 50)
INPUT_BG = (55, 62, 55)
INPUT_BORDER = (80, 90, 75)
BUTTON_BG = (90, 65, 35)
BUTTON_HOVER = (110, 80, 45)
BUTTON_TEXT = (240, 235, 220)
TOAST_BG = (60, 50, 35)
DIVIDER = (60, 68, 58)

# Layout
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
SIDEBAR_WIDTH = 340
INBOX_ITEM_HEIGHT = 72
HEADER_HEIGHT = 48
PADDING = 16
FONT_SIZES = {"title": 20, "body": 16, "small": 13, "header": 24}

# Fonts
FONT_FAMILY = "DejaVu Sans"
FONT_FAMILY_MONO = "DejaVu Sans Mono"

# Font cache
_font_cache = {}


def get_font(size_key="body", bold=False, mono=False):
    """Get a cached pygame font. size_key is a key from FONT_SIZES or an int."""
    if isinstance(size_key, int):
        size = size_key
    else:
        size = FONT_SIZES.get(size_key, FONT_SIZES["body"])

    cache_key = (size, bold, mono)
    if cache_key not in _font_cache:
        family = FONT_FAMILY_MONO if mono else FONT_FAMILY
        try:
            _font_cache[cache_key] = pygame.font.SysFont(family, size, bold=bold)
        except Exception:
            _font_cache[cache_key] = pygame.font.Font(None, size)
    return _font_cache[cache_key]
