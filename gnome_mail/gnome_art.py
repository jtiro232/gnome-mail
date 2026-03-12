"""ALL gnome/mushroom pixel art drawn with Pygame primitives only. No image files.
20+ unique gnome sprites, multiple mushroom types, trees, scenery, shading."""

import math
import pygame

from gnome_mail.ui.theme import (
    GNOME_HAT_RED, GNOME_SKIN, MUSHROOM_RED, MUSHROOM_SPOT,
    TEXT_COLOR, TEXT_DIM, ACCENT, ACCENT_LIGHT, GREEN_ACCENT,
    BG_COLOR, PANEL_BG, ERROR_COLOR, DIVIDER, SIDEBAR_BG,
)

# ── Helper: draw a shadow ellipse beneath something ──
def _shadow(surface, cx, cy, w, h, alpha=40):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), (0, 0, w, h))
    surface.blit(s, (cx - w // 2, cy - h // 2))


# ── Helper: gradient rect (vertical) ──
def _gradient_rect(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))


# ── Hat color variations ──
HAT_COLORS = [
    (160, 40, 40),   # classic red
    (40, 100, 160),  # blue
    (140, 60, 140),  # purple
    (40, 130, 80),   # green
    (180, 130, 40),  # gold
    (180, 80, 40),   # orange
    (100, 60, 40),   # brown
    (160, 50, 80),   # pink
]

TUNIC_COLORS = [
    (70, 100, 55),   # green
    (80, 70, 120),   # purple
    (100, 80, 55),   # brown
    (60, 90, 110),   # blue-grey
    (110, 85, 50),   # tan
    (75, 105, 75),   # sage
]


def _base_gnome(surface, x, y, s, hat_color=None, tunic_color=None):
    """Draw the base gnome body. Returns (head_cx, head_cy, body_color, boot_color, eye_color)."""
    hat_color = hat_color or GNOME_HAT_RED
    body_color = tunic_color or (70, 100, 55)
    boot_color = (60, 40, 25)
    eye_color = (40, 35, 30)
    beard_color = (240, 235, 225)

    # Shadow beneath gnome
    _shadow(surface, x, y + int(33 * s), int(28 * s), int(8 * s), 30)

    # Boots
    pygame.draw.ellipse(surface, boot_color,
                        (x - int(12 * s), y + int(28 * s), int(12 * s), int(7 * s)))
    pygame.draw.ellipse(surface, boot_color,
                        (x + int(2 * s), y + int(28 * s), int(12 * s), int(7 * s)))

    # Body
    pygame.draw.ellipse(surface, body_color,
                        (x - int(12 * s), y + int(5 * s), int(26 * s), int(26 * s)))
    # Body shading (darker at bottom)
    darker = tuple(max(0, c - 20) for c in body_color)
    pygame.draw.ellipse(surface, darker,
                        (x - int(10 * s), y + int(18 * s), int(22 * s), int(12 * s)))

    # Belt
    pygame.draw.rect(surface, ACCENT,
                     (x - int(12 * s), y + int(16 * s), int(26 * s), int(4 * s)))
    pygame.draw.rect(surface, ACCENT_LIGHT,
                     (x - int(3 * s), y + int(15 * s), int(6 * s), int(6 * s)))

    # Head
    head_cx = x + int(1 * s)
    head_cy = y - int(2 * s)
    pygame.draw.circle(surface, GNOME_SKIN, (head_cx, head_cy), int(10 * s))
    # Cheek blush
    pygame.draw.circle(surface, (220, 160, 140), (head_cx - int(7 * s), head_cy + int(2 * s)), max(1, int(3 * s)))
    pygame.draw.circle(surface, (220, 160, 140), (head_cx + int(7 * s), head_cy + int(2 * s)), max(1, int(3 * s)))

    # Nose
    pygame.draw.circle(surface, (195, 155, 120), (head_cx, head_cy + int(2 * s)), max(1, int(3 * s)))

    # Beard
    pygame.draw.ellipse(surface, beard_color,
                        (head_cx - int(8 * s), head_cy + int(2 * s), int(16 * s), int(14 * s)))
    # Beard highlight
    pygame.draw.ellipse(surface, (250, 248, 240),
                        (head_cx - int(5 * s), head_cy + int(3 * s), int(10 * s), int(8 * s)))

    # Eyes
    # White
    pygame.draw.circle(surface, (250, 248, 240), (head_cx - int(4 * s), head_cy - int(2 * s)), max(1, int(3 * s)))
    pygame.draw.circle(surface, (250, 248, 240), (head_cx + int(4 * s), head_cy - int(2 * s)), max(1, int(3 * s)))
    # Pupil
    pygame.draw.circle(surface, eye_color, (head_cx - int(4 * s), head_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.circle(surface, eye_color, (head_cx + int(4 * s), head_cy - int(2 * s)), max(1, int(2 * s)))
    # Eye shine
    pygame.draw.circle(surface, (255, 255, 255), (head_cx - int(3 * s), head_cy - int(3 * s)), max(1, int(1 * s)))
    pygame.draw.circle(surface, (255, 255, 255), (head_cx + int(5 * s), head_cy - int(3 * s)), max(1, int(1 * s)))

    # Hat with shading
    hat_points = [
        (head_cx, head_cy - int(30 * s)),
        (head_cx - int(12 * s), head_cy - int(5 * s)),
        (head_cx + int(12 * s), head_cy - int(5 * s)),
    ]
    pygame.draw.polygon(surface, hat_color, hat_points)
    # Hat highlight stripe
    lighter_hat = tuple(min(255, c + 40) for c in hat_color)
    pygame.draw.line(surface, lighter_hat,
                     (head_cx - int(2 * s), head_cy - int(25 * s)),
                     (head_cx - int(8 * s), head_cy - int(7 * s)), max(1, int(2 * s)))
    # Hat brim
    pygame.draw.ellipse(surface, tuple(max(0, c - 15) for c in hat_color),
                        (head_cx - int(13 * s), head_cy - int(7 * s), int(26 * s), int(6 * s)))

    return head_cx, head_cy, body_color, boot_color, eye_color


def draw_gnome(surface, x, y, scale=1.0, pose="waving"):
    """Draw a gnome. 20 poses: waving, reading, walking, thinking, sad,
    dancing, sleeping, fishing, gardening, cooking, singing, pointing,
    carrying, sitting, crafting, sweeping, celebrating, sneaking, mining, painting."""
    s = scale
    hat_idx = hash(pose) % len(HAT_COLORS)
    tunic_idx = hash(pose) % len(TUNIC_COLORS)
    head_cx, head_cy, body_color, boot_color, eye_color = _base_gnome(
        surface, x, y, s, HAT_COLORS[hat_idx], TUNIC_COLORS[tunic_idx])
    arm_color = body_color

    if pose == "waving":
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(24 * s), y - int(5 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(24 * s), y - int(5 * s)), max(1, int(3 * s)))
        # Left arm at side
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(12 * s)),
                         (x - int(18 * s), y + int(22 * s)), max(1, int(3 * s)))

    elif pose == "reading":
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(18 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(18 * s), y + int(8 * s)), max(1, int(3 * s)))
        # Scroll with detail
        pygame.draw.rect(surface, (230, 220, 190),
                         (x - int(18 * s), y + int(4 * s), int(36 * s), int(8 * s)))
        pygame.draw.rect(surface, ACCENT,
                         (x - int(18 * s), y + int(4 * s), int(36 * s), int(8 * s)), 1)
        # Scroll ends (rolled)
        pygame.draw.circle(surface, (220, 210, 180), (x - int(18 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, (220, 210, 180), (x + int(18 * s), y + int(8 * s)), max(1, int(3 * s)))

    elif pose == "walking":
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(12 * s)),
                         (x - int(20 * s), y + int(18 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(20 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.ellipse(surface, boot_color,
                            (x - int(16 * s), y + int(28 * s), int(12 * s), int(7 * s)))

    elif pose == "thinking":
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(8 * s), y + int(2 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(8 * s), y + int(2 * s)), max(1, int(3 * s)))
        # Thought bubble
        for i, (dx, dy, r) in enumerate([(18, -20, 3), (22, -28, 2), (24, -34, 1)]):
            pygame.draw.circle(surface, (200, 200, 200),
                               (x + int(dx * s), y + int(dy * s)), max(1, int(r * s)))

    elif pose == "sad":
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(16 * s), y + int(26 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(16 * s), y + int(26 * s)), max(1, int(3 * s)))
        # Tear drop
        pygame.draw.circle(surface, (100, 160, 220),
                           (head_cx + int(6 * s), head_cy + int(1 * s)), max(1, int(2 * s)))

    elif pose == "dancing":
        # Both arms up
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(10 * s)),
                         (x - int(22 * s), y - int(5 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(10 * s)),
                         (x + int(22 * s), y - int(5 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x - int(22 * s), y - int(5 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(22 * s), y - int(5 * s)), max(1, int(3 * s)))
        # Offset foot for dance pose
        pygame.draw.ellipse(surface, boot_color,
                            (x + int(8 * s), y + int(26 * s), int(12 * s), int(7 * s)))
        # Music notes
        for dx, dy in [(20, -15), (25, -25)]:
            pygame.draw.circle(surface, ACCENT_LIGHT, (x + int(dx * s), y + int(dy * s)), max(1, int(2 * s)))
            pygame.draw.line(surface, ACCENT_LIGHT,
                             (x + int(dx * s) + max(1, int(2 * s)), y + int(dy * s)),
                             (x + int(dx * s) + max(1, int(2 * s)), y + int((dy - 8) * s)), 1)

    elif pose == "sleeping":
        # Arms crossed on body
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(12 * s)),
                         (x + int(5 * s), y + int(14 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x - int(5 * s), y + int(14 * s)), max(1, int(3 * s)))
        # ZZZ
        font = pygame.font.Font(None, max(12, int(14 * s)))
        zzz = font.render("Zzz", True, TEXT_DIM)
        surface.blit(zzz, (x + int(14 * s), y - int(20 * s)))

    elif pose == "fishing":
        # Right arm holding rod
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(20 * s), y + int(5 * s)), max(1, int(3 * s)))
        # Fishing rod
        pygame.draw.line(surface, (120, 90, 50),
                         (x + int(20 * s), y + int(5 * s)),
                         (x + int(35 * s), y - int(15 * s)), max(1, int(2 * s)))
        # Line
        pygame.draw.line(surface, (180, 180, 180),
                         (x + int(35 * s), y - int(15 * s)),
                         (x + int(35 * s), y + int(30 * s)), 1)
        # Hook/float
        pygame.draw.circle(surface, MUSHROOM_RED, (x + int(35 * s), y + int(30 * s)), max(1, int(2 * s)))

    elif pose == "gardening":
        # Holding a watering can
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(22 * s), y + int(16 * s)), max(1, int(3 * s)))
        # Watering can
        pygame.draw.rect(surface, (140, 140, 140),
                         (x + int(18 * s), y + int(14 * s), int(10 * s), int(8 * s)))
        pygame.draw.line(surface, (140, 140, 140),
                         (x + int(28 * s), y + int(14 * s)),
                         (x + int(32 * s), y + int(10 * s)), max(1, int(2 * s)))
        # Water drops
        for i in range(3):
            pygame.draw.circle(surface, (100, 160, 220),
                               (x + int((30 + i * 3) * s), y + int((18 + i * 4) * s)), max(1, int(1 * s)))
        # Small flower nearby
        pygame.draw.line(surface, (60, 120, 40),
                         (x + int(30 * s), y + int(28 * s)),
                         (x + int(30 * s), y + int(22 * s)), max(1, int(1 * s)))
        pygame.draw.circle(surface, (220, 180, 60), (x + int(30 * s), y + int(21 * s)), max(1, int(3 * s)))

    elif pose == "cooking":
        # Holding a pot
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(20 * s), y + int(18 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(20 * s), y + int(18 * s)), max(1, int(3 * s)))
        # Pot
        pygame.draw.rect(surface, (100, 100, 100),
                         (x - int(18 * s), y + int(20 * s), int(36 * s), int(10 * s)), border_radius=max(1, int(2 * s)))
        # Steam
        for i in range(3):
            pygame.draw.arc(surface, (200, 200, 200),
                            (x - int(8 * s) + i * int(8 * s), y + int((10 - i * 4) * s), int(8 * s), int(6 * s)),
                            0, math.pi, 1)

    elif pose == "singing":
        # Mouth open
        pygame.draw.ellipse(surface, (180, 80, 60),
                            (head_cx - int(3 * s), head_cy + int(5 * s), int(6 * s), int(4 * s)))
        # Arms out expressively
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(10 * s)),
                         (x - int(24 * s), y + int(5 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(10 * s)),
                         (x + int(24 * s), y + int(5 * s)), max(1, int(3 * s)))
        # Musical notes
        for dx, dy in [(-20, -18), (22, -22), (-16, -28)]:
            pygame.draw.circle(surface, ACCENT_LIGHT, (x + int(dx * s), y + int(dy * s)), max(1, int(2 * s)))
            pygame.draw.line(surface, ACCENT_LIGHT,
                             (x + int(dx * s) + max(1, int(2 * s)), y + int(dy * s)),
                             (x + int(dx * s) + max(1, int(2 * s)), y + int((dy - 6) * s)), 1)

    elif pose == "pointing":
        # Right arm pointing forward
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(28 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(28 * s), y + int(8 * s)), max(1, int(2 * s)))
        # Left arm at hip
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(16 * s), y + int(18 * s)), max(1, int(3 * s)))

    elif pose == "carrying":
        # Arms up holding a crate
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(10 * s)),
                         (x - int(14 * s), y - int(2 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(10 * s)),
                         (x + int(14 * s), y - int(2 * s)), max(1, int(3 * s)))
        # Crate on head
        pygame.draw.rect(surface, (140, 110, 70),
                         (x - int(14 * s), y - int(14 * s), int(28 * s), int(14 * s)))
        pygame.draw.rect(surface, (120, 90, 55),
                         (x - int(14 * s), y - int(14 * s), int(28 * s), int(14 * s)), 1)
        # Cross planks on crate
        pygame.draw.line(surface, (120, 90, 55),
                         (x - int(14 * s), y - int(7 * s)), (x + int(14 * s), y - int(7 * s)), 1)
        pygame.draw.line(surface, (120, 90, 55),
                         (x, y - int(14 * s)), (x, y), 1)

    elif pose == "sitting":
        # Legs out front (overrides boots)
        pygame.draw.rect(surface, boot_color,
                         (x - int(10 * s), y + int(26 * s), int(24 * s), int(6 * s)), border_radius=max(1, int(2 * s)))
        # Arms resting on knees
        pygame.draw.line(surface, arm_color,
                         (x - int(10 * s), y + int(14 * s)),
                         (x - int(8 * s), y + int(24 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(10 * s), y + int(14 * s)),
                         (x + int(8 * s), y + int(24 * s)), max(1, int(3 * s)))

    elif pose == "crafting":
        # Hammer in right hand
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(22 * s), y + int(4 * s)), max(1, int(3 * s)))
        # Hammer handle
        pygame.draw.line(surface, (130, 100, 60),
                         (x + int(22 * s), y + int(4 * s)),
                         (x + int(22 * s), y - int(10 * s)), max(1, int(2 * s)))
        # Hammer head
        pygame.draw.rect(surface, (150, 150, 155),
                         (x + int(18 * s), y - int(14 * s), int(10 * s), int(6 * s)))
        # Sparkle from hammering
        pygame.draw.circle(surface, (255, 240, 150), (x + int(26 * s), y - int(12 * s)), max(1, int(2 * s)))

    elif pose == "sweeping":
        # Broom in both hands
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(16 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(6 * s), y + int(18 * s)), max(1, int(3 * s)))
        # Broom handle
        pygame.draw.line(surface, (130, 100, 60),
                         (x + int(16 * s), y + int(8 * s)),
                         (x - int(10 * s), y + int(34 * s)), max(1, int(2 * s)))
        # Broom bristles
        for dx in range(-4, 5, 2):
            pygame.draw.line(surface, (180, 160, 100),
                             (x - int(10 * s) + int(dx * s), y + int(34 * s)),
                             (x - int(12 * s) + int(dx * s), y + int(38 * s)), 1)

    elif pose == "celebrating":
        # Both arms up, confetti
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(10 * s)),
                         (x - int(20 * s), y - int(8 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(10 * s)),
                         (x + int(20 * s), y - int(8 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x - int(20 * s), y - int(8 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(20 * s), y - int(8 * s)), max(1, int(3 * s)))
        # Confetti
        confetti_colors = [(220, 60, 60), (60, 180, 60), (60, 100, 220), (220, 200, 40), (200, 100, 200)]
        for i, (dx, dy) in enumerate([(-15, -20), (18, -18), (-8, -28), (12, -30), (0, -24)]):
            pygame.draw.circle(surface, confetti_colors[i % len(confetti_colors)],
                               (x + int(dx * s), y + int(dy * s)), max(1, int(2 * s)))

    elif pose == "sneaking":
        # Hunched, tiptoeing
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(18 * s), y + int(10 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(18 * s), y + int(10 * s)), max(1, int(3 * s)))
        # Tiptoe boots (slightly raised)
        pygame.draw.ellipse(surface, boot_color,
                            (x - int(8 * s), y + int(30 * s), int(8 * s), int(5 * s)))
        pygame.draw.ellipse(surface, boot_color,
                            (x + int(4 * s), y + int(30 * s), int(8 * s), int(5 * s)))

    elif pose == "mining":
        # Pickaxe in hand
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(10 * s)),
                         (x + int(24 * s), y + int(2 * s)), max(1, int(3 * s)))
        # Pickaxe handle
        pygame.draw.line(surface, (130, 100, 60),
                         (x + int(24 * s), y + int(2 * s)),
                         (x + int(18 * s), y - int(14 * s)), max(1, int(2 * s)))
        # Pickaxe head
        pygame.draw.line(surface, (160, 160, 170),
                         (x + int(12 * s), y - int(14 * s)),
                         (x + int(24 * s), y - int(14 * s)), max(1, int(3 * s)))
        # Sparks
        pygame.draw.circle(surface, (255, 240, 100), (x + int(28 * s), y + int(4 * s)), max(1, int(1 * s)))
        # Gem on ground
        pygame.draw.polygon(surface, (100, 200, 220), [
            (x + int(30 * s), y + int(28 * s)),
            (x + int(34 * s), y + int(24 * s)),
            (x + int(38 * s), y + int(28 * s)),
            (x + int(34 * s), y + int(32 * s)),
        ])

    elif pose == "painting":
        # Holding palette and brush
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(12 * s)),
                         (x - int(20 * s), y + int(8 * s)), max(1, int(3 * s)))
        # Palette
        pygame.draw.ellipse(surface, (180, 150, 100),
                            (x - int(28 * s), y + int(4 * s), int(16 * s), int(10 * s)))
        # Paint dots on palette
        for dx, dy, color in [(-24, 7, (220, 50, 50)), (-20, 6, (50, 150, 220)), (-22, 10, (50, 180, 50))]:
            pygame.draw.circle(surface, color, (x + int(dx * s), y + int(dy * s)), max(1, int(2 * s)))
        # Brush in right hand
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(22 * s), y + int(2 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, (130, 100, 60),
                         (x + int(22 * s), y + int(2 * s)),
                         (x + int(28 * s), y - int(6 * s)), max(1, int(2 * s)))
        # Brush tip
        pygame.draw.circle(surface, (220, 50, 50), (x + int(28 * s), y - int(6 * s)), max(1, int(2 * s)))
        # Easel
        pygame.draw.rect(surface, (200, 195, 180),
                         (x + int(30 * s), y - int(10 * s), int(16 * s), int(20 * s)), 1)

    else:
        # Default: arms at sides
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(18 * s), y + int(22 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(18 * s), y + int(22 * s)), max(1, int(3 * s)))


# ── Mushroom variants ──

def draw_mushroom(surface, x, y, scale=1.0, variant="red_spotted"):
    """Draw a mushroom. Variants: red_spotted, brown, small_cluster, blue_glow, golden, purple."""
    s = scale

    if variant == "small_cluster":
        for ox, oy, ss, v in [(-10, 4, 0.5, "red_spotted"), (0, 0, 0.7, "brown"), (12, 3, 0.4, "red_spotted")]:
            draw_mushroom(surface, x + int(ox * s), y + int(oy * s), s * ss, v)
        return

    # Shadow
    _shadow(surface, x, y + int(14 * s), int(20 * s), int(6 * s), 25)

    # Stem with shading
    stem_colors = {
        "red_spotted": ((220, 210, 185), (200, 190, 165)),
        "brown": ((190, 175, 150), (170, 155, 130)),
        "blue_glow": ((180, 200, 220), (160, 180, 200)),
        "golden": ((230, 220, 170), (210, 200, 150)),
        "purple": ((200, 190, 210), (180, 170, 190)),
    }
    stem_c, stem_dark = stem_colors.get(variant, stem_colors["red_spotted"])
    stem_w = int(10 * s)
    stem_h = int(16 * s)
    pygame.draw.rect(surface, stem_c, (x - stem_w // 2, y, stem_w, stem_h))
    # Stem shading
    pygame.draw.rect(surface, stem_dark, (x - stem_w // 2, y, stem_w // 3, stem_h))

    # Cap colors
    cap_colors = {
        "red_spotted": MUSHROOM_RED,
        "brown": (140, 100, 65),
        "blue_glow": (60, 120, 180),
        "golden": (200, 180, 60),
        "purple": (130, 70, 160),
    }
    cap_color = cap_colors.get(variant, MUSHROOM_RED)
    cap_w = int(24 * s)
    cap_h = int(14 * s)
    cap_dark = tuple(max(0, c - 30) for c in cap_color)

    # Cap with shading
    pygame.draw.ellipse(surface, cap_color,
                        (x - cap_w // 2, y - cap_h + int(4 * s), cap_w, cap_h))
    # Cap highlight
    cap_light = tuple(min(255, c + 40) for c in cap_color)
    pygame.draw.ellipse(surface, cap_light,
                        (x - cap_w // 4, y - cap_h + int(5 * s), cap_w // 3, cap_h // 2))

    # Spots
    if variant in ("red_spotted", "blue_glow", "purple"):
        spot_r = max(1, int(2.5 * s))
        spot_color = MUSHROOM_SPOT if variant == "red_spotted" else (220, 230, 255)
        for sx, sy in [(-5, -4), (3, -6), (7, -2), (-2, -8)]:
            pygame.draw.circle(surface, spot_color, (x + int(sx * s), y + int(sy * s)), spot_r)

    if variant == "blue_glow":
        # Glow effect
        glow = pygame.Surface((int(30 * s), int(20 * s)), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (60, 120, 180, 40), (0, 0, int(30 * s), int(20 * s)))
        surface.blit(glow, (x - int(15 * s), y - int(14 * s)))

    # Cap underside
    pygame.draw.arc(surface, (200, 190, 170),
                    (x - cap_w // 2 + int(2 * s), y - int(2 * s), cap_w - int(4 * s), int(6 * s)),
                    0, math.pi, max(1, int(1 * s)))


# ── Trees ──

def draw_tree(surface, x, y, scale=1.0, variant="oak"):
    """Draw a tree. Variants: oak, pine, birch."""
    s = scale
    if variant == "pine":
        # Pine tree - triangular layers
        trunk_w = int(8 * s)
        trunk_h = int(20 * s)
        pygame.draw.rect(surface, (80, 55, 35),
                         (x - trunk_w // 2, y, trunk_w, trunk_h))
        # Three layers of foliage
        for i, (w, h_off) in enumerate([(36, -8), (28, -22), (18, -34)]):
            color = (35 + i * 8, 70 + i * 5, 30 + i * 5)
            hw = int(w * s) // 2
            top = y + int(h_off * s)
            pts = [(x, top - int(14 * s)), (x - hw, top + int(6 * s)), (x + hw, top + int(6 * s))]
            pygame.draw.polygon(surface, color, pts)
            # Snow/highlight on tips
            pygame.draw.line(surface, (80, 110, 70), (x - hw + int(4 * s), top + int(5 * s)),
                             (x, top - int(12 * s)), 1)
    elif variant == "birch":
        # Birch - white trunk with marks
        trunk_w = int(6 * s)
        trunk_h = int(40 * s)
        pygame.draw.rect(surface, (220, 215, 200),
                         (x - trunk_w // 2, y - trunk_h, trunk_w, trunk_h))
        # Birch marks
        for i in range(4):
            my = y - trunk_h + int((8 + i * 10) * s)
            pygame.draw.line(surface, (60, 55, 50),
                             (x - trunk_w // 3, my), (x + trunk_w // 3, my), 1)
        # Canopy
        canopy_r = int(16 * s)
        pygame.draw.circle(surface, (80, 130, 50), (x, y - trunk_h - int(4 * s)), canopy_r)
        pygame.draw.circle(surface, (65, 115, 40), (x - int(6 * s), y - trunk_h - int(8 * s)), int(canopy_r * 0.6))
    else:
        # Oak - thick trunk, round canopy
        trunk_w = int(10 * s)
        trunk_h = int(30 * s)
        pygame.draw.rect(surface, (70, 50, 35), (x - trunk_w // 2, y - trunk_h, trunk_w, trunk_h))
        # Bark texture
        pygame.draw.rect(surface, (60, 42, 28), (x - trunk_w // 2, y - trunk_h, trunk_w // 3, trunk_h))
        # Canopy layers
        canopy_r = int(22 * s)
        pygame.draw.circle(surface, (40, 75, 35), (x, y - trunk_h - int(8 * s)), canopy_r)
        pygame.draw.circle(surface, (50, 85, 40), (x - int(8 * s), y - trunk_h - int(12 * s)), int(canopy_r * 0.7))
        pygame.draw.circle(surface, (45, 80, 38), (x + int(6 * s), y - trunk_h - int(6 * s)), int(canopy_r * 0.65))
        # Highlight
        pygame.draw.circle(surface, (60, 100, 50), (x - int(4 * s), y - trunk_h - int(16 * s)), int(canopy_r * 0.3))


# ── Decorative elements ──

def draw_grass_tuft(surface, x, y, scale=1.0):
    """Small grass tuft decoration."""
    s = scale
    colors = [(50, 90, 40), (60, 100, 45), (45, 80, 35)]
    for i, dx in enumerate([-3, 0, 3, -1, 2]):
        color = colors[i % len(colors)]
        h = int((6 + (i % 3) * 3) * s)
        lean = int((i - 2) * 1.5 * s)
        pygame.draw.line(surface, color, (x + int(dx * s), y), (x + int(dx * s) + lean, y - h), max(1, int(1 * s)))


def draw_flower(surface, x, y, scale=1.0, color=(220, 180, 60)):
    """Small flower."""
    s = scale
    # Stem
    pygame.draw.line(surface, (60, 120, 40), (x, y), (x, y - int(10 * s)), max(1, int(1 * s)))
    # Leaf
    pygame.draw.ellipse(surface, (50, 100, 35),
                        (x + int(1 * s), y - int(5 * s), int(5 * s), int(3 * s)))
    # Petals
    r = max(2, int(3 * s))
    for angle in range(0, 360, 72):
        px = x + int(math.cos(math.radians(angle)) * r * 1.2)
        py = y - int(10 * s) + int(math.sin(math.radians(angle)) * r * 1.2)
        pygame.draw.circle(surface, color, (px, py), r)
    # Center
    pygame.draw.circle(surface, (200, 170, 40), (x, y - int(10 * s)), max(1, int(2 * s)))


def draw_rock(surface, x, y, scale=1.0):
    """Small rock."""
    s = scale
    pygame.draw.ellipse(surface, (110, 105, 95),
                        (x - int(8 * s), y - int(4 * s), int(16 * s), int(10 * s)))
    pygame.draw.ellipse(surface, (125, 120, 108),
                        (x - int(6 * s), y - int(4 * s), int(10 * s), int(6 * s)))


def draw_firefly(surface, x, y, scale=1.0):
    """Glowing firefly dot."""
    s = scale
    glow = pygame.Surface((int(12 * s), int(12 * s)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (200, 220, 100, 60), (int(6 * s), int(6 * s)), int(6 * s))
    pygame.draw.circle(glow, (240, 250, 150, 180), (int(6 * s), int(6 * s)), max(1, int(2 * s)))
    surface.blit(glow, (x - int(6 * s), y - int(6 * s)))


# ── Composite scenes ──

def draw_toadstool_border(surface, rect):
    """Decorative mushroom border with shading."""
    x, y, w, h = rect
    # Outer glow
    glow_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
    pygame.draw.rect(surface, (80, 60, 35), glow_rect, 3, border_radius=8)
    # Main border
    pygame.draw.rect(surface, ACCENT, rect, 2, border_radius=6)

    # Mushrooms at corners and along edges
    for cx, cy in [(x + 8, y + 2), (x + w - 8, y + 2), (x + 8, y + h - 2), (x + w - 8, y + h - 2)]:
        draw_tiny_mushroom(surface, cx, cy)

    spacing = max(50, w // 8)
    for i in range(1, int(w / spacing)):
        mx = x + i * spacing
        if abs(mx - x - 8) > 20 and abs(mx - x - w + 8) > 20:
            draw_tiny_mushroom(surface, mx, y + 2)
    # Bottom mushrooms
    for i in range(1, int(w / spacing)):
        mx = x + i * spacing + spacing // 2
        if abs(mx - x - 8) > 20 and abs(mx - x - w + 8) > 20 and mx < x + w - 20:
            draw_tiny_mushroom(surface, mx, y + h - 2)


def draw_forest_scene(surface, rect):
    """Rich background forest scene with trees, mushrooms, grass, gnomes, fireflies."""
    x, y, w, h = rect

    # Sky gradient at top
    _gradient_rect(surface, (x, y, w, int(h * 0.7)), (25, 35, 40), (35, 50, 35))

    # Ground with gradient
    ground_y = y + int(h * 0.7)
    _gradient_rect(surface, (x, ground_y, w, h - int(h * 0.7)), (35, 55, 30), (28, 42, 24))

    # Background trees (distant, smaller, dimmer)
    for tx_pct in [0.08, 0.22, 0.38, 0.55, 0.72, 0.92]:
        draw_tree(surface, x + int(w * tx_pct), ground_y, 0.4, "pine")

    # Foreground trees
    draw_tree(surface, x + int(w * 0.12), ground_y, 0.7, "oak")
    draw_tree(surface, x + int(w * 0.45), ground_y, 0.8, "pine")
    draw_tree(surface, x + int(w * 0.78), ground_y, 0.6, "birch")

    # Grass throughout
    for i in range(0, w, 12):
        draw_grass_tuft(surface, x + i, ground_y, 0.6 + (i % 3) * 0.2)

    # Mushrooms on the ground
    draw_mushroom(surface, x + int(w * 0.18), ground_y - 2, 0.8, "red_spotted")
    draw_mushroom(surface, x + int(w * 0.35), ground_y - 2, 0.6, "brown")
    draw_mushroom(surface, x + int(w * 0.55), ground_y - 2, 0.5, "blue_glow")
    draw_mushroom(surface, x + int(w * 0.65), ground_y - 2, 0.7, "golden")
    draw_mushroom(surface, x + int(w * 0.82), ground_y - 2, 0.5, "small_cluster")

    # Flowers
    draw_flower(surface, x + int(w * 0.25), ground_y, 0.7, (220, 180, 60))
    draw_flower(surface, x + int(w * 0.42), ground_y, 0.5, (200, 120, 180))
    draw_flower(surface, x + int(w * 0.7), ground_y, 0.6, (180, 200, 220))

    # Rocks
    draw_rock(surface, x + int(w * 0.3), ground_y + 2, 0.6)
    draw_rock(surface, x + int(w * 0.6), ground_y + 3, 0.4)

    # Gnomes
    draw_gnome(surface, x + int(w * 0.2), ground_y - 35, 0.7, "waving")
    draw_gnome(surface, x + int(w * 0.5), ground_y - 35, 0.6, "gardening")
    draw_gnome(surface, x + int(w * 0.75), ground_y - 35, 0.5, "reading")

    # Fireflies in the upper area
    for fx, fy in [(0.15, 0.25), (0.4, 0.15), (0.65, 0.3), (0.85, 0.2), (0.3, 0.4)]:
        draw_firefly(surface, x + int(w * fx), y + int(h * fy), 0.8)


def draw_gnome_mail_carrier(surface, x, y, scale=1.0):
    """A gnome carrying a satchel of scrolls."""
    s = scale
    draw_gnome(surface, x, y, scale, "walking")

    # Satchel
    satchel_color = (100, 70, 40)
    sx = x + int(14 * s)
    sy = y + int(8 * s)
    pygame.draw.rect(surface, satchel_color,
                     (sx, sy, int(14 * s), int(16 * s)), border_radius=max(1, int(3 * s)))
    # Satchel shading
    pygame.draw.rect(surface, (80, 55, 30),
                     (sx, sy + int(8 * s), int(14 * s), int(8 * s)), border_radius=max(1, int(3 * s)))
    # Strap
    pygame.draw.line(surface, satchel_color,
                     (sx + int(7 * s), sy), (x - int(4 * s), y - int(8 * s)), max(1, int(2 * s)))
    # Scrolls peeking out
    scroll_color = (230, 220, 190)
    for i in range(3):
        pygame.draw.rect(surface, scroll_color,
                         (sx + int(2 * s) + i * int(4 * s), sy - int(3 * s), int(3 * s), int(6 * s)),
                         border_radius=max(1, int(1 * s)))
        # Scroll ribbon
        pygame.draw.line(surface, MUSHROOM_RED,
                         (sx + int(3 * s) + i * int(4 * s), sy - int(1 * s)),
                         (sx + int(3 * s) + i * int(4 * s), sy + int(1 * s)), 1)


def draw_gnome_with_quill(surface, x, y, scale=1.0):
    """A gnome writing with a feather quill."""
    s = scale
    draw_gnome(surface, x, y, scale, "reading")

    # Quill
    quill_start = (x + int(20 * s), y + int(6 * s))
    quill_tip = (x + int(28 * s), y + int(18 * s))
    pygame.draw.line(surface, (180, 170, 150), quill_start, quill_tip, max(1, int(2 * s)))
    # Feather barbs
    feather_color = (200, 190, 170)
    for t in [0.2, 0.4, 0.6]:
        fx = int(quill_start[0] + t * (quill_tip[0] - quill_start[0]))
        fy = int(quill_start[1] + t * (quill_tip[1] - quill_start[1]))
        pygame.draw.line(surface, feather_color, (fx, fy), (fx - int(5 * s), fy - int(3 * s)), 1)
        pygame.draw.line(surface, feather_color, (fx, fy), (fx + int(5 * s), fy - int(3 * s)), 1)
    # Ink drops
    pygame.draw.circle(surface, (30, 30, 60), quill_tip, max(1, int(1.5 * s)))
    pygame.draw.circle(surface, (30, 30, 60), (quill_tip[0] + int(2 * s), quill_tip[1] + int(3 * s)), max(1, int(1 * s)))


def draw_mushroom_house(surface, x, y, scale=1.0):
    """A mushroom with a door and windows, like a gnome home."""
    s = scale

    # Shadow
    _shadow(surface, x, y + int(30 * s), int(30 * s), int(8 * s), 35)

    # Stem (house body) with shading
    stem_w = int(24 * s)
    stem_h = int(28 * s)
    pygame.draw.rect(surface, (210, 200, 175),
                     (x - stem_w // 2, y, stem_w, stem_h), border_radius=max(1, int(4 * s)))
    pygame.draw.rect(surface, (195, 185, 160),
                     (x - stem_w // 2, y, stem_w // 3, stem_h), border_radius=max(1, int(4 * s)))

    # Cap (roof) with shading
    cap_w = int(40 * s)
    cap_h = int(22 * s)
    pygame.draw.ellipse(surface, MUSHROOM_RED,
                        (x - cap_w // 2, y - cap_h + int(6 * s), cap_w, cap_h))
    # Cap highlight
    pygame.draw.ellipse(surface, (200, 70, 70),
                        (x - cap_w // 4, y - cap_h + int(7 * s), cap_w // 3, cap_h // 2))
    # Spots
    spot_r = max(1, int(3 * s))
    for sx, sy in [(-8, -8), (5, -10), (10, -4), (-3, -14)]:
        pygame.draw.circle(surface, MUSHROOM_SPOT, (x + int(sx * s), y + int(sy * s)), spot_r)

    # Door with arch
    door_color = (100, 70, 40)
    dw = int(8 * s)
    dh = int(12 * s)
    pygame.draw.rect(surface, door_color,
                     (x - dw // 2, y + stem_h - dh, dw, dh), border_radius=max(1, int(3 * s)))
    # Door highlight
    pygame.draw.rect(surface, (120, 85, 50),
                     (x - dw // 2 + 1, y + stem_h - dh + 1, dw // 2 - 1, dh - 2), border_radius=max(1, int(2 * s)))
    # Doorknob
    pygame.draw.circle(surface, ACCENT_LIGHT,
                       (x + int(2 * s), y + stem_h - dh // 2), max(1, int(1.5 * s)))

    # Windows with glow
    window_color = (180, 200, 140)
    window_glow = (200, 220, 160, 80)
    wr = max(2, int(4 * s))
    for wx_off in [-8, 8]:
        wx = x + int(wx_off * s)
        wy = y + int(8 * s)
        # Glow
        glow_s = pygame.Surface((wr * 4, wr * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, window_glow, (wr * 2, wr * 2), wr * 2)
        surface.blit(glow_s, (wx - wr * 2, wy - wr * 2))
        # Window
        pygame.draw.circle(surface, window_color, (wx, wy), wr)
        # Cross
        pygame.draw.line(surface, door_color, (wx - wr, wy), (wx + wr, wy), 1)
        pygame.draw.line(surface, door_color, (wx, wy - wr), (wx, wy + wr), 1)

    # Chimney
    pygame.draw.rect(surface, (180, 170, 150),
                     (x + int(6 * s), y - cap_h + int(8 * s), int(5 * s), int(10 * s)))
    # Smoke
    for i, (dx, dy) in enumerate([(0, -3), (2, -7), (-1, -11)]):
        alpha = 120 - i * 30
        smoke = pygame.Surface((int(6 * s), int(6 * s)), pygame.SRCALPHA)
        pygame.draw.circle(smoke, (200, 200, 200, alpha), (int(3 * s), int(3 * s)), int(3 * s))
        surface.blit(smoke, (x + int((8 + dx) * s), y - cap_h + int((5 + dy) * s)))


def draw_tiny_mushroom(surface, x, y):
    """A very small mushroom for inline decoration, about 12-16px."""
    # Stem
    pygame.draw.rect(surface, (210, 200, 180), (x - 2, y, 4, 6))
    # Cap
    pygame.draw.ellipse(surface, MUSHROOM_RED, (x - 6, y - 5, 12, 8))
    # Cap highlight
    pygame.draw.ellipse(surface, (200, 70, 70), (x - 3, y - 4, 5, 4))
    # Spots
    pygame.draw.circle(surface, MUSHROOM_SPOT, (x - 2, y - 3), 1)
    pygame.draw.circle(surface, MUSHROOM_SPOT, (x + 3, y - 2), 1)


# ── Sidebar decorations ──

def draw_sidebar_forest_footer(surface, rect):
    """Draw a forest floor scene at the bottom of the sidebar."""
    x, y, w, h = rect
    # Ground gradient
    _gradient_rect(surface, (x, y, w, h), SIDEBAR_BG, (30, 45, 28))

    # Grass
    for i in range(0, w, 8):
        draw_grass_tuft(surface, x + i, y + 4, 0.4 + (i % 4) * 0.1)

    # Mushrooms
    draw_mushroom(surface, x + int(w * 0.15), y + 4, 0.4, "red_spotted")
    draw_mushroom(surface, x + int(w * 0.5), y + 6, 0.3, "brown")
    draw_mushroom(surface, x + int(w * 0.8), y + 4, 0.35, "purple")

    # Flowers
    draw_flower(surface, x + int(w * 0.3), y + 6, 0.35, (220, 180, 60))
    draw_flower(surface, x + int(w * 0.65), y + 6, 0.3, (200, 140, 180))


def draw_header_decoration(surface, x, y, w):
    """Draw decorative elements for the header bar."""
    # Subtle vine/leaves along the bottom
    vine_color = (50, 75, 42)
    for i in range(0, w, 40):
        vx = x + i
        # Small leaf
        pygame.draw.ellipse(surface, vine_color, (vx, y - 3, 8, 4))
        if i % 80 == 0:
            draw_tiny_mushroom(surface, vx + 20, y - 4)
