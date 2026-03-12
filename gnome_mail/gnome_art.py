"""ALL gnome/mushroom pixel art drawn with Pygame primitives only. No image files."""

import math
import pygame

from gnome_mail.ui.theme import (
    GNOME_HAT_RED, GNOME_SKIN, MUSHROOM_RED, MUSHROOM_SPOT,
    TEXT_COLOR, TEXT_DIM, ACCENT, ACCENT_LIGHT, GREEN_ACCENT,
    BG_COLOR, PANEL_BG, ERROR_COLOR, DIVIDER,
)


def draw_gnome(surface, x, y, scale=1.0, pose="waving"):
    """Draw a gnome at (x, y). Poses: waving, reading, walking, thinking, sad."""
    s = scale

    # Boots (two small dark brown ovals)
    boot_color = (60, 40, 25)
    pygame.draw.ellipse(surface, boot_color,
                        (x - int(12 * s), y + int(28 * s), int(12 * s), int(7 * s)))
    pygame.draw.ellipse(surface, boot_color,
                        (x + int(2 * s), y + int(28 * s), int(12 * s), int(7 * s)))

    # Body (round green tunic)
    body_color = (70, 100, 55)
    pygame.draw.ellipse(surface, body_color,
                        (x - int(12 * s), y + int(5 * s), int(26 * s), int(26 * s)))

    # Belt
    belt_color = ACCENT
    pygame.draw.rect(surface, belt_color,
                     (x - int(12 * s), y + int(16 * s), int(26 * s), int(4 * s)))
    # Belt buckle
    pygame.draw.rect(surface, ACCENT_LIGHT,
                     (x - int(3 * s), y + int(15 * s), int(6 * s), int(6 * s)))

    # Head (skin circle)
    head_cx = x + int(1 * s)
    head_cy = y - int(2 * s)
    pygame.draw.circle(surface, GNOME_SKIN, (head_cx, head_cy), int(10 * s))

    # Beard (white, half-circle below head)
    beard_color = (240, 235, 225)
    pygame.draw.ellipse(surface, beard_color,
                        (head_cx - int(8 * s), head_cy + int(2 * s), int(16 * s), int(14 * s)))

    # Eyes (two small dots)
    eye_color = (40, 35, 30)
    pygame.draw.circle(surface, eye_color, (head_cx - int(4 * s), head_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.circle(surface, eye_color, (head_cx + int(4 * s), head_cy - int(2 * s)), max(1, int(2 * s)))

    # Hat (red pointy triangle)
    hat_points = [
        (head_cx, head_cy - int(30 * s)),  # tip
        (head_cx - int(12 * s), head_cy - int(5 * s)),  # left base
        (head_cx + int(12 * s), head_cy - int(5 * s)),  # right base
    ]
    pygame.draw.polygon(surface, GNOME_HAT_RED, hat_points)

    # Pose-specific arm/accessory details
    arm_color = body_color
    if pose == "waving":
        # Right arm raised up
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(24 * s), y - int(5 * s)), max(1, int(3 * s)))
        # Hand
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(24 * s), y - int(5 * s)), max(1, int(3 * s)))
    elif pose == "reading":
        # Both arms forward holding a scroll
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(18 * s), y + int(8 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(18 * s), y + int(8 * s)), max(1, int(3 * s)))
        # Scroll
        pygame.draw.rect(surface, (230, 220, 190),
                         (x - int(18 * s), y + int(4 * s), int(36 * s), int(8 * s)))
        pygame.draw.rect(surface, ACCENT,
                         (x - int(18 * s), y + int(4 * s), int(36 * s), int(8 * s)), 1)
    elif pose == "walking":
        # Left arm back, right arm forward
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(12 * s)),
                         (x - int(20 * s), y + int(18 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(12 * s)),
                         (x + int(20 * s), y + int(8 * s)), max(1, int(3 * s)))
        # Offset boots for walking
        pygame.draw.ellipse(surface, boot_color,
                            (x - int(16 * s), y + int(28 * s), int(12 * s), int(7 * s)))
    elif pose == "thinking":
        # Hand on chin
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(8 * s), y + int(2 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surface, GNOME_SKIN, (x + int(8 * s), y + int(2 * s)), max(1, int(3 * s)))
    elif pose == "sad":
        # Arms hanging down
        pygame.draw.line(surface, arm_color,
                         (x - int(12 * s), y + int(14 * s)),
                         (x - int(16 * s), y + int(26 * s)), max(1, int(3 * s)))
        pygame.draw.line(surface, arm_color,
                         (x + int(12 * s), y + int(14 * s)),
                         (x + int(16 * s), y + int(26 * s)), max(1, int(3 * s)))
        # Droopy mouth
        pygame.draw.arc(surface, eye_color,
                        (head_cx - int(4 * s), head_cy + int(3 * s), int(8 * s), int(4 * s)),
                        math.pi * 0.1, math.pi * 0.9, max(1, int(1 * s)))


def draw_mushroom(surface, x, y, scale=1.0, variant="red_spotted"):
    """Draw a mushroom. Variants: red_spotted, brown, small_cluster."""
    s = scale

    if variant == "small_cluster":
        # Draw 3 small mushrooms
        for ox, oy, ss in [(-8, 4, 0.5), (0, 0, 0.7), (10, 3, 0.4)]:
            draw_mushroom(surface, x + int(ox * s), y + int(oy * s), s * ss, "red_spotted")
        return

    # Stem
    stem_color = (220, 210, 185) if variant == "red_spotted" else (190, 175, 150)
    stem_w = int(10 * s)
    stem_h = int(16 * s)
    pygame.draw.rect(surface, stem_color,
                     (x - stem_w // 2, y, stem_w, stem_h))

    # Cap
    cap_color = MUSHROOM_RED if variant == "red_spotted" else (140, 100, 65)
    cap_w = int(24 * s)
    cap_h = int(14 * s)
    pygame.draw.ellipse(surface, cap_color,
                        (x - cap_w // 2, y - cap_h + int(4 * s), cap_w, cap_h))

    # Spots (white dots on red cap)
    if variant == "red_spotted":
        spot_r = max(1, int(2.5 * s))
        spots = [(-5, -4), (3, -6), (7, -2), (-2, -8)]
        for sx, sy in spots:
            pygame.draw.circle(surface, MUSHROOM_SPOT,
                               (x + int(sx * s), y + int(sy * s)), spot_r)

    # Cap underside (small curved line)
    pygame.draw.arc(surface, (200, 190, 170),
                    (x - cap_w // 2 + int(2 * s), y - int(2 * s), cap_w - int(4 * s), int(6 * s)),
                    0, math.pi, max(1, int(1 * s)))


def draw_toadstool_border(surface, rect):
    """Draw decorative mushroom border around a rect."""
    x, y, w, h = rect
    border_color = ACCENT
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)

    # Small mushrooms at corners
    for cx, cy in [(x + 6, y + 2), (x + w - 6, y + 2), (x + 6, y + h - 2), (x + w - 6, y + h - 2)]:
        draw_tiny_mushroom(surface, cx, cy)

    # Small mushrooms along top edge
    spacing = max(60, w // 6)
    for i in range(1, int(w / spacing)):
        mx = x + i * spacing
        if abs(mx - x - 6) > 20 and abs(mx - x - w + 6) > 20:
            draw_tiny_mushroom(surface, mx, y + 2)


def draw_forest_scene(surface, rect):
    """Draw a background forest scene with trees, mushrooms, grass, gnomes."""
    x, y, w, h = rect

    # Ground
    ground_y = y + int(h * 0.7)
    pygame.draw.rect(surface, (35, 55, 30), (x, ground_y, w, h - int(h * 0.7)))

    # Grass tufts
    grass_color = (55, 85, 45)
    for i in range(0, w, 15):
        gx = x + i
        gy = ground_y
        for dx in [-3, 0, 3]:
            pygame.draw.line(surface, grass_color, (gx + dx, gy), (gx + dx - 2, gy - 8), 1)

    # Trees
    trunk_color = (70, 50, 35)
    leaf_color = (40, 70, 35)
    for tx, th_factor in [(w * 0.15, 0.5), (w * 0.5, 0.6), (w * 0.85, 0.45)]:
        tx = x + int(tx)
        trunk_h = int(h * th_factor * 0.4)
        pygame.draw.rect(surface, trunk_color,
                         (tx - 4, ground_y - trunk_h, 8, trunk_h))
        # Canopy
        canopy_r = int(h * th_factor * 0.2)
        pygame.draw.circle(surface, leaf_color, (tx, ground_y - trunk_h - canopy_r // 2), canopy_r)
        darker_leaf = (30, 55, 28)
        pygame.draw.circle(surface, darker_leaf, (tx - canopy_r // 3, ground_y - trunk_h - canopy_r // 3), int(canopy_r * 0.6))

    # Mushrooms on the ground
    draw_mushroom(surface, x + int(w * 0.25), ground_y - 2, 0.8, "red_spotted")
    draw_mushroom(surface, x + int(w * 0.6), ground_y - 2, 0.6, "brown")
    draw_mushroom(surface, x + int(w * 0.75), ground_y - 2, 0.5, "small_cluster")

    # A gnome in the scene
    draw_gnome(surface, x + int(w * 0.4), ground_y - 35, 0.8, "waving")


def draw_gnome_mail_carrier(surface, x, y, scale=1.0):
    """A gnome carrying a satchel of scrolls."""
    s = scale
    draw_gnome(surface, x, y, scale, "walking")

    # Satchel (brown bag on the side)
    satchel_color = (100, 70, 40)
    sx = x + int(14 * s)
    sy = y + int(8 * s)
    pygame.draw.rect(surface, satchel_color,
                     (sx, sy, int(14 * s), int(16 * s)), border_radius=max(1, int(3 * s)))
    # Satchel strap
    pygame.draw.line(surface, satchel_color,
                     (sx + int(7 * s), sy), (x - int(4 * s), y - int(8 * s)), max(1, int(2 * s)))
    # Scrolls peeking out
    scroll_color = (230, 220, 190)
    for i in range(3):
        pygame.draw.rect(surface, scroll_color,
                         (sx + int(2 * s) + i * int(4 * s), sy - int(3 * s), int(3 * s), int(6 * s)),
                         border_radius=max(1, int(1 * s)))


def draw_gnome_with_quill(surface, x, y, scale=1.0):
    """A gnome writing with a feather quill."""
    s = scale
    draw_gnome(surface, x, y, scale, "reading")

    # Quill in right hand
    quill_start = (x + int(20 * s), y + int(6 * s))
    quill_tip = (x + int(28 * s), y + int(18 * s))
    # Feather shaft
    pygame.draw.line(surface, (180, 170, 150), quill_start, quill_tip, max(1, int(2 * s)))
    # Feather barbs
    feather_color = (200, 190, 170)
    for t in [0.2, 0.4, 0.6]:
        fx = int(quill_start[0] + t * (quill_tip[0] - quill_start[0]))
        fy = int(quill_start[1] + t * (quill_tip[1] - quill_start[1]))
        pygame.draw.line(surface, feather_color, (fx, fy), (fx - int(5 * s), fy - int(3 * s)), 1)
        pygame.draw.line(surface, feather_color, (fx, fy), (fx + int(5 * s), fy - int(3 * s)), 1)
    # Ink at tip
    pygame.draw.circle(surface, (30, 30, 60), quill_tip, max(1, int(1.5 * s)))


def draw_mushroom_house(surface, x, y, scale=1.0):
    """A mushroom with a door and windows, like a gnome home."""
    s = scale

    # Stem (house body)
    stem_color = (210, 200, 175)
    stem_w = int(24 * s)
    stem_h = int(28 * s)
    pygame.draw.rect(surface, stem_color,
                     (x - stem_w // 2, y, stem_w, stem_h),
                     border_radius=max(1, int(4 * s)))

    # Cap (roof)
    cap_color = MUSHROOM_RED
    cap_w = int(40 * s)
    cap_h = int(22 * s)
    pygame.draw.ellipse(surface, cap_color,
                        (x - cap_w // 2, y - cap_h + int(6 * s), cap_w, cap_h))
    # Spots on roof
    spot_r = max(1, int(3 * s))
    for sx, sy in [(-8, -8), (5, -10), (10, -4), (-3, -14)]:
        pygame.draw.circle(surface, MUSHROOM_SPOT,
                           (x + int(sx * s), y + int(sy * s)), spot_r)

    # Door
    door_color = (100, 70, 40)
    dw = int(8 * s)
    dh = int(12 * s)
    pygame.draw.rect(surface, door_color,
                     (x - dw // 2, y + stem_h - dh, dw, dh),
                     border_radius=max(1, int(3 * s)))
    # Doorknob
    pygame.draw.circle(surface, ACCENT_LIGHT,
                       (x + int(2 * s), y + stem_h - dh // 2), max(1, int(1.5 * s)))

    # Windows
    window_color = (180, 200, 140)
    wr = max(2, int(4 * s))
    pygame.draw.circle(surface, window_color, (x - int(8 * s), y + int(8 * s)), wr)
    pygame.draw.circle(surface, window_color, (x + int(8 * s), y + int(8 * s)), wr)
    # Window crosses
    for wx in [x - int(8 * s), x + int(8 * s)]:
        wy = y + int(8 * s)
        pygame.draw.line(surface, door_color, (wx - wr, wy), (wx + wr, wy), 1)
        pygame.draw.line(surface, door_color, (wx, wy - wr), (wx, wy + wr), 1)


def draw_tiny_mushroom(surface, x, y):
    """A very small mushroom for inline decoration, about 12-16px."""
    # Stem
    pygame.draw.rect(surface, (210, 200, 180), (x - 2, y, 4, 6))
    # Cap
    pygame.draw.ellipse(surface, MUSHROOM_RED, (x - 6, y - 5, 12, 8))
    # Spots
    pygame.draw.circle(surface, MUSHROOM_SPOT, (x - 2, y - 3), 1)
    pygame.draw.circle(surface, MUSHROOM_SPOT, (x + 2, y - 2), 1)
