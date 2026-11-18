"""
GTA VI / Vice City (GTX 6) Pro Stream Deck Icon Suite (Bold Edition)
Engineered for Ulanzi, Elgato, and Touch Portal hardware decks.
Features:
- Large, bold proportions (glyph occupies 55% - 65% of keycap area)
- Thick 4px to 8px line weights & solid fills for instant legibility
- Neon luminescence & soft bloom in Electric Cyan, Hot Magenta, and Sunset Gold
- 48 Icons covering OBS Control Room, Media Controls, and GTA VI Gaming
- 1x Keycaps (186x186), 2x Hi-DPI (372x372), and Transparent Glyphs (32-bit RGBA)
"""

import os
import math
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "themes", "gta6_vice")

DIRS = {
    "game_keys": os.path.join(OUTPUT_DIR, "gaming_icons", "keycaps"),
    "game_trans": os.path.join(OUTPUT_DIR, "gaming_icons", "transparent_glyphs"),
    "game_hidpi": os.path.join(OUTPUT_DIR, "gaming_icons", "high_dpi_2x"),
    "strm_keys": os.path.join(OUTPUT_DIR, "streaming_icons", "keycaps"),
    "strm_trans": os.path.join(OUTPUT_DIR, "streaming_icons", "transparent_glyphs"),
    "strm_hidpi": os.path.join(OUTPUT_DIR, "streaming_icons", "high_dpi_2x"),
    "widgets": os.path.join(OUTPUT_DIR, "widget_backgrounds"),
    "widgets_hidpi": os.path.join(OUTPUT_DIR, "widget_backgrounds", "high_dpi_2x"),
    "widgets_prev": os.path.join(OUTPUT_DIR, "widget_backgrounds", "simulated_previews"),
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

KEY_SIZE = 186

# Color Palette (BGR)
C_CYAN = (255, 240, 0)       # Electric Cyan #00F0FF
C_MAGENTA = (216, 34, 118)   # Hot Magenta #D82276
C_PINK = (255, 85, 163)      # Neon Pink #FF55A3
C_GOLD = (68, 160, 255)      # Sunset Peach/Gold #FFA044
C_WHITE = (255, 255, 255)
C_RED = (40, 40, 255)        # Hot Red Alert
C_GREEN = (80, 255, 100)     # Neon Mint / Active Green

def create_vice_gradient_keycap(w=186, h=186):
    """
    Creates a rich Vice City aesthetic keycap with deep violet gradient,
    subtle horizon sunset glow, and glowing neon beveled border.
    """
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # 1. Background: Deep Vice Violet Gradient (#160824 to #2B0C3C)
    for y in range(h):
        t = y / float(h)
        b = int(36 * (1 - t) + 60 * t)
        g = int(8 * (1 - t) + 12 * t)
        r = int(22 * (1 - t) + 43 * t)
        img[y, :] = (b, g, r)

    # 2. Subtle sunset glow along bottom edge
    glow_h = int(h * 0.35)
    horizon_glow = np.zeros((h, w, 3), dtype=np.float32)
    for y in range(h - glow_h, h):
        factor = (y - (h - glow_h)) / float(glow_h)
        horizon_glow[y, :, 0] += factor * 30   # B
        horizon_glow[y, :, 1] += factor * 50   # G
        horizon_glow[y, :, 2] += factor * 140  # R
    img = np.clip(img.astype(np.float32) + horizon_glow, 0, 255).astype(np.uint8)

    # 3. Corner palm tree silhouettes
    cv2.ellipse(img, (w + 12, h - 18), (55, 85), 35, 180, 290, (14, 5, 18), 3, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (-12, h - 18), (55, 85), -35, 250, 360, (14, 5, 18), 3, lineType=cv2.LINE_AA)

    # 4. Beveled Neon Rim (Dark outer chamfer + hot magenta inner line)
    cv2.rectangle(img, (2, 2), (w - 3, h - 3), (28, 10, 36), 3, lineType=cv2.LINE_AA)
    
    # Inner glowing neon frame
    cv2.rectangle(img, (5, 5), (w - 6, h - 6), C_MAGENTA, 2, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (7, 7), (w - 8, h - 8), (C_MAGENTA[0]//2, C_MAGENTA[1]//2, C_MAGENTA[2]//2), 1, lineType=cv2.LINE_AA)

    # Soft ambient neon edge bloom
    edge_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(edge_mask, (6, 6), (w - 7, h - 7), 255, 2, lineType=cv2.LINE_AA)
    edge_blur = cv2.GaussianBlur(edge_mask, (11, 11), 0) / 255.0
    for c, val in enumerate([70, 30, 160]):
        img[:, :, c] = np.clip(img[:, :, c].astype(np.float32) + edge_blur * val, 0, 255).astype(np.uint8)

    return img

def enhance_2x(img):
    """Lanczos super-sampled 2x render."""
    h, w = img.shape[:2]
    upscaled = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.8)
    return cv2.addWeighted(upscaled, 1.25, gaussian, -0.25, 0)

# ==============================================================================
# BOLD SYMBOL DRAWING ENGINE (Large 95-120px Glyphs, 4-8px Line Weights)
# ==============================================================================

def draw_bold_symbol(canvas, symbol_id, center=(93, 72), has_label=True):
    """
    Renders large, bold, punchy vector glyphs.
    If has_label is True, center is at (93, 72) with scale ~0.9.
    If has_label is False, center is at (93, 93) with scale ~1.2 (full keycap hero).
    """
    cx, cy = center
    sc = 0.95 if has_label else 1.25
    
    # Pre-render onto mask for neon drop glow
    mask = np.zeros(canvas.shape[:2], dtype=np.uint8)
    
    # Temporary draw function for both mask and canvas
    def render_geometry(target, is_mask=False):
        c_w = 255 if is_mask else C_WHITE
        c_c = 255 if is_mask else C_CYAN
        c_m = 255 if is_mask else C_MAGENTA
        c_g = 255 if is_mask else C_GOLD
        c_r = 255 if is_mask else C_RED
        c_gr = 255 if is_mask else C_GREEN
        
        # --- MEDIA & STREAM CONTROLS (From Ulanzi / OBS References) ---
        if symbol_id == "play":
            # Huge solid Play Triangle
            pts = np.array([
                [int(cx - 30 * sc), int(cy - 42 * sc)],
                [int(cx + 42 * sc), int(cy)],
                [int(cx - 30 * sc), int(cy + 42 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w if not is_mask else 255, lineType=cv2.LINE_AA)
            if not is_mask:
                cv2.polylines(target, [pts], True, c_c, 3, lineType=cv2.LINE_AA)

        elif symbol_id == "pause":
            # Two thick vertical rounded bars
            bw = int(18 * sc)
            bh = int(72 * sc)
            gap = int(16 * sc)
            x1 = cx - gap//2 - bw
            x2 = cx + gap//2
            cv2.rectangle(target, (x1, int(cy - bh//2)), (x1 + bw, int(cy + bh//2)), c_w, -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (x2, int(cy - bh//2)), (x2 + bw, int(cy + bh//2)), c_w, -1, lineType=cv2.LINE_AA)
            if not is_mask:
                cv2.rectangle(target, (x1, int(cy - bh//2)), (x1 + bw, int(cy + bh//2)), c_c, 2, lineType=cv2.LINE_AA)
                cv2.rectangle(target, (x2, int(cy - bh//2)), (x2 + bw, int(cy + bh//2)), c_c, 2, lineType=cv2.LINE_AA)

        elif symbol_id == "play_next":
            # Next track (>|)
            pts = np.array([
                [int(cx - 28 * sc), int(cy - 36 * sc)],
                [int(cx + 12 * sc), int(cy)],
                [int(cx - 28 * sc), int(cy + 36 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx + 18 * sc), int(cy - 36 * sc)), (int(cx + 28 * sc), int(cy + 36 * sc)), c_c, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "play_prev":
            # Previous track (|<)
            pts = np.array([
                [int(cx + 28 * sc), int(cy - 36 * sc)],
                [int(cx - 12 * sc), int(cy)],
                [int(cx + 28 * sc), int(cy + 36 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 28 * sc), int(cy - 36 * sc)), (int(cx - 18 * sc), int(cy + 36 * sc)), c_c, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "skip_forward":
            # Fast-forward double arrows (>>)
            for off in [-16, 14]:
                pts = np.array([
                    [int((cx + off - 18) * sc), int((cy - 34) * sc)],
                    [int((cx + off + 14) * sc), int(cy * sc)],
                    [int((cx + off - 18) * sc), int((cy + 34) * sc)]
                ], np.int32)
                cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)

        elif symbol_id == "alert_bell":
            # Solid prominent notification bell
            pts = np.array([
                [int(cx - 32 * sc), int(cy + 24 * sc)],
                [int(cx + 32 * sc), int(cy + 24 * sc)],
                [int(cx + 24 * sc), int(cy + 16 * sc)],
                [int(cx + 20 * sc), int(cy - 12 * sc)],
                [int(cx), int(cy - 36 * sc)],
                [int(cx - 20 * sc), int(cy - 12 * sc)],
                [int(cx - 24 * sc), int(cy + 16 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 36 * sc)), int(6 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy + 30 * sc)), int(7 * sc), c_g, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "alert_mute":
            # Bell with red slash
            pts = np.array([
                [int(cx - 32 * sc), int(cy + 24 * sc)],
                [int(cx + 32 * sc), int(cy + 24 * sc)],
                [int(cx + 24 * sc), int(cy + 16 * sc)],
                [int(cx + 20 * sc), int(cy - 12 * sc)],
                [int(cx), int(cy - 36 * sc)],
                [int(cx - 20 * sc), int(cy - 12 * sc)],
                [int(cx - 24 * sc), int(cy + 16 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 36 * sc)), int(6 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy + 30 * sc)), int(7 * sc), c_g, -1, lineType=cv2.LINE_AA)
            # Red slash across
            cv2.line(target, (int(cx - 36 * sc), int(cy + 36 * sc)), (int(cx + 36 * sc), int(cy - 36 * sc)), c_r, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "scene_switch":
            # Overlapping Scene windows
            w_box, h_box = int(48 * sc), int(36 * sc)
            # Back window
            cv2.rectangle(target, (int(cx - 18 * sc), int(cy - 28 * sc)), (int(cx - 18 * sc + w_box), int(cy - 28 * sc + h_box)), c_m, int(4 * sc), lineType=cv2.LINE_AA)
            # Front window (filled)
            cv2.rectangle(target, (int(cx - 30 * sc), int(cy - 12 * sc)), (int(cx - 30 * sc + w_box), int(cy - 12 * sc + h_box)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 24 * sc), int(cy + 4 * sc)), (int(cx - 24 * sc + 18 * sc), int(cy + 14 * sc)), c_c, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "record":
            # Heavy video camera with glowing red record dot
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 22 * sc)), (int(cx + 10 * sc), int(cy + 24 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            # Lens cone
            pts = np.array([
                [int(cx + 10 * sc), int(cy - 8 * sc)],
                [int(cx + 36 * sc), int(cy - 24 * sc)],
                [int(cx + 36 * sc), int(cy + 26 * sc)],
                [int(cx + 10 * sc), int(cy + 10 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            # Red record circle inside
            cv2.circle(target, (int(cx - 13 * sc), int(cy + 1 * sc)), int(11 * sc), c_r, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "stream":
            # Broadcast camera with radio signal arcs
            cv2.rectangle(target, (int(cx - 32 * sc), int(cy - 20 * sc)), (int(cx + 14 * sc), int(cy + 22 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx + 14 * sc), int(cy - 6 * sc)],
                [int(cx + 36 * sc), int(cy - 20 * sc)],
                [int(cx + 36 * sc), int(cy + 22 * sc)],
                [int(cx + 14 * sc), int(cy + 8 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)
            # Broadcast waves above
            cv2.ellipse(target, (int(cx - 9 * sc), int(cy - 28 * sc)), (int(14 * sc), int(10 * sc)), 0, 190, 350, c_g, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "virtual_cam":
            # Webcam lens on circular pedestal
            cv2.circle(target, (cx, int(cy - 12 * sc)), int(26 * sc), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 12 * sc)), int(12 * sc), c_c, -1, lineType=cv2.LINE_AA)
            # Pedestal
            pts = np.array([
                [int(cx - 34 * sc), int(cy + 30 * sc)],
                [int(cx + 34 * sc), int(cy + 30 * sc)],
                [int(cx + 20 * sc), int(cy + 16 * sc)],
                [int(cx - 20 * sc), int(cy + 16 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_m, lineType=cv2.LINE_AA)

        elif symbol_id == "studio_mode":
            # Monitor with audio/level sliders
            cv2.rectangle(target, (int(cx - 38 * sc), int(cy - 30 * sc)), (int(cx + 38 * sc), int(cy + 18 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 16 * sc), int(cy + 24 * sc)), (int(cx + 16 * sc), int(cy + 24 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            # Sliders inside
            for sx, sh in [(-22, 10), (-6, 18), (10, 14), (26, 22)]:
                cv2.line(target, (int((cx + sx) * sc), int((cy + 10) * sc)), (int((cx + sx) * sc), int((cy + 10 - sh) * sc)), c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "reload_overlays":
            # Bold circular reload/refresh arrows
            cv2.ellipse(target, (cx, cy), (int(34 * sc), int(34 * sc)), 0, 30, 310, c_c, int(6 * sc), lineType=cv2.LINE_AA)
            # Arrowhead
            pts = np.array([
                [int(cx + 24 * sc), int(cy - 38 * sc)],
                [int(cx + 44 * sc), int(cy - 24 * sc)],
                [int(cx + 26 * sc), int(cy - 12 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)

        elif symbol_id == "viewer_requests":
            # Speech bubble with chat text dots
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 26 * sc)), (int(cx + 36 * sc), int(cy + 16 * sc)), c_c, int(5 * sc), lineType=cv2.LINE_AA)
            # Tail
            pts = np.array([
                [int(cx - 16 * sc), int(cy + 16 * sc)],
                [int(cx - 26 * sc), int(cy + 34 * sc)],
                [int(cx + 2 * sc), int(cy + 16 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)
            # Dots
            for dx in [-18, 0, 18]:
                cv2.circle(target, (int((cx + dx) * sc), int((cy - 5) * sc)), int(4 * sc), c_w, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "widget_toggle":
            # Gear settings with checkmark
            cv2.circle(target, (cx, cy), int(26 * sc), c_c, int(5 * sc), lineType=cv2.LINE_AA)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = int(cx + 26 * sc * math.cos(rad))
                y1 = int(cy + 26 * sc * math.sin(rad))
                x2 = int(cx + 36 * sc * math.cos(rad))
                y2 = int(cy + 36 * sc * math.sin(rad))
                cv2.line(target, (x1, y1), (x2, y2), c_c, int(5 * sc), lineType=cv2.LINE_AA)
            # Checkmark inside
            pts = np.array([[int(cx - 14 * sc), cy], [int(cx - 4 * sc), int(cy + 10 * sc)], [int(cx + 14 * sc), int(cy - 12 * sc)]], np.int32)
            cv2.polylines(target, [pts], False, c_gr, int(5 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "video_toggle":
            # Eye with glowing pupil
            pts_top = []
            pts_bot = []
            for t in np.linspace(-1, 1, 20):
                x = int(cx + t * 40 * sc)
                y_top = int(cy - (1 - t*t) * 26 * sc)
                y_bot = int(cy + (1 - t*t) * 26 * sc)
                pts_top.append([x, y_top])
                pts_bot.append([x, y_bot])
            all_pts = pts_top + pts_bot[::-1]
            cv2.polylines(target, [np.array(all_pts, np.int32)], True, c_c, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(14 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(6 * sc), c_m, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "volume_up":
            # Speaker with plus (+)
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 14 * sc)), (int(cx - 20 * sc), int(cy + 14 * sc)), c_c, -1, lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx - 20 * sc), int(cy - 14 * sc)],
                [int(cx - 2 * sc), int(cy - 30 * sc)],
                [int(cx - 2 * sc), int(cy + 30 * sc)],
                [int(cx - 20 * sc), int(cy + 14 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)
            # Plus
            cv2.line(target, (int(cx + 14 * sc), cy), (int(cx + 34 * sc), cy), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 24 * sc), int(cy - 10 * sc)), (int(cx + 24 * sc), int(cy + 10 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "volume_down":
            # Speaker with minus (-)
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 14 * sc)), (int(cx - 20 * sc), int(cy + 14 * sc)), c_c, -1, lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx - 20 * sc), int(cy - 14 * sc)],
                [int(cx - 2 * sc), int(cy - 30 * sc)],
                [int(cx - 2 * sc), int(cy + 30 * sc)],
                [int(cx - 20 * sc), int(cy + 14 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)
            # Minus
            cv2.line(target, (int(cx + 14 * sc), cy), (int(cx + 34 * sc), cy), c_w, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "volume_mute":
            # Speaker with slash
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 14 * sc)), (int(cx - 20 * sc), int(cy + 14 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx - 20 * sc), int(cy - 14 * sc)],
                [int(cx - 2 * sc), int(cy - 30 * sc)],
                [int(cx - 2 * sc), int(cy + 30 * sc)],
                [int(cx - 20 * sc), int(cy + 14 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_m, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 10 * sc), int(cy - 20 * sc)), (int(cx + 34 * sc), int(cy + 20 * sc)), c_r, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 34 * sc), int(cy - 20 * sc)), (int(cx + 10 * sc), int(cy + 20 * sc)), c_r, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "volume_levels":
            # Speaker with dynamic soundwaves
            cv2.rectangle(target, (int(cx - 36 * sc), int(cy - 14 * sc)), (int(cx - 20 * sc), int(cy + 14 * sc)), c_c, -1, lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx - 20 * sc), int(cy - 14 * sc)],
                [int(cx - 2 * sc), int(cy - 30 * sc)],
                [int(cx - 2 * sc), int(cy + 30 * sc)],
                [int(cx - 20 * sc), int(cy + 14 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)
            # 3 soundwave arcs
            cv2.ellipse(target, (int(cx + 6 * sc), cy), (int(12 * sc), int(16 * sc)), 0, -45, 45, c_g, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (int(cx + 6 * sc), cy), (int(22 * sc), int(26 * sc)), 0, -45, 45, c_g, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (int(cx + 6 * sc), cy), (int(32 * sc), int(36 * sc)), 0, -45, 45, c_g, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "mic_mute":
            # Bold studio microphone
            cv2.rectangle(target, (int(cx - 14 * sc), int(cy - 36 * sc)), (int(cx + 14 * sc), int(cy + 4 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 36 * sc)), int(14 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy - 4 * sc)), (int(24 * sc), int(24 * sc)), 0, 0, 180, c_c, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (cx, int(cy + 20 * sc)), (cx, int(cy + 36 * sc)), c_c, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 18 * sc), int(cy + 36 * sc)), (int(cx + 18 * sc), int(cy + 36 * sc)), c_c, int(5 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "headphone_deafen":
            # DJ Headphones with slash
            cv2.ellipse(target, (cx, int(cy - 4 * sc)), (int(32 * sc), int(32 * sc)), 0, 180, 360, c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 38 * sc), int(cy - 8 * sc)), (int(cx - 24 * sc), int(cy + 24 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx + 24 * sc), int(cy - 8 * sc)), (int(cx + 38 * sc), int(cy + 24 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 30 * sc), int(cy + 30 * sc)), (int(cx + 30 * sc), int(cy - 30 * sc)), c_r, int(6 * sc), lineType=cv2.LINE_AA)

        # --- GTA VI GAMING ICONS (Heavy 95-120px Glyphs) ---
        elif symbol_id == "engine_ignition":
            # Bold Car Key & Ignition Ring
            cv2.circle(target, (cx, int(cy - 12 * sc)), int(24 * sc), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy + 14 * sc)), (int(26 * sc), int(26 * sc)), 0, 130, 410, c_g, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (cx, int(cy - 2 * sc)), (cx, int(cy + 18 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "headlights_highbeam":
            # Bold Headlight beam
            cv2.ellipse(target, (int(cx - 14 * sc), cy), (int(22 * sc), int(32 * sc)), 0, 270, 90, c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 14 * sc), int(cy - 32 * sc)), (int(cx - 14 * sc), int(cy + 32 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            for off in [-24, -8, 8, 24]:
                cv2.line(target, (int((cx + 10) * sc), int((cy + off) * sc)), (int((cx + 42) * sc), int((cy + off) * sc)), c_c, int(5 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "nitro_boost":
            # Nitro bottle & flame blast
            cv2.rectangle(target, (int(cx - 26 * sc), int(cy - 24 * sc)), (int(cx + 4 * sc), int(cy + 32 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 18 * sc), int(cy - 36 * sc)), (int(cx - 4 * sc), int(cy - 24 * sc)), c_c, -1, lineType=cv2.LINE_AA)
            # Chunky turbo flame
            pts = np.array([
                [int(cx + 8 * sc), int(cy - 14 * sc)],
                [int(cx + 40 * sc), int(cy - 22 * sc)],
                [int(cx + 26 * sc), int(cy)],
                [int(cx + 44 * sc), int(cy + 8 * sc)],
                [int(cx + 10 * sc), int(cy + 26 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_g, lineType=cv2.LINE_AA)

        elif symbol_id == "handbrake_drift":
            # Brake disc with drift curves
            cv2.circle(target, (int(cx - 8 * sc), cy), int(28 * sc), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 8 * sc), int(cy - 12 * sc)), (int(cx - 8 * sc), int(cy + 4 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 8 * sc), int(cy + 12 * sc)), int(3 * sc), c_w, -1, lineType=cv2.LINE_AA)
            # Heavy drift arcs
            cv2.ellipse(target, (int(cx + 24 * sc), int(cy + 12 * sc)), (int(20 * sc), int(30 * sc)), -25, 180, 290, c_g, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (int(cx + 32 * sc), int(cy + 18 * sc)), (int(20 * sc), int(30 * sc)), -25, 180, 290, c_g, int(5 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "vice_radio":
            # Vice City radio station note & dial
            cv2.circle(target, (int(cx - 22 * sc), int(cy + 16 * sc)), int(10 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 2 * sc), int(cy + 10 * sc)), int(10 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 12 * sc), int(cy + 16 * sc)), (int(cx - 12 * sc), int(cy - 26 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 8 * sc), int(cy + 10 * sc)), (int(cx + 8 * sc), int(cy - 32 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 12 * sc), int(cy - 26 * sc)), (int(cx + 8 * sc), int(cy - 32 * sc)), c_c, int(6 * sc), lineType=cv2.LINE_AA)
            # >> fast forward
            for off in [18, 32]:
                pts = np.array([
                    [int((cx + off) * sc), int((cy - 12) * sc)],
                    [int((cx + off + 12) * sc), int(cy * sc)],
                    [int((cx + off) * sc), int((cy + 12) * sc)]
                ], np.int32)
                cv2.fillPoly(target, [pts], c_g, lineType=cv2.LINE_AA)

        elif symbol_id == "cinematic_cam":
            # 35mm Movie camera
            cv2.rectangle(target, (int(cx - 28 * sc), int(cy - 16 * sc)), (int(cx + 12 * sc), int(cy + 22 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 16 * sc), int(cy - 26 * sc)), int(11 * sc), c_m, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx + 2 * sc), int(cy - 26 * sc)), int(11 * sc), c_m, int(4 * sc), lineType=cv2.LINE_AA)
            pts = np.array([
                [int(cx + 12 * sc), int(cy - 4 * sc)],
                [int(cx + 36 * sc), int(cy - 20 * sc)],
                [int(cx + 36 * sc), int(cy + 26 * sc)],
                [int(cx + 12 * sc), int(cy + 10 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_c, lineType=cv2.LINE_AA)

        elif symbol_id == "vtol_landing_gear":
            # Aircraft jet & wheels
            cv2.line(target, (cx, int(cy - 34 * sc)), (cx, int(cy + 20 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 36 * sc), int(cy - 6 * sc)), (int(cx + 36 * sc), int(cy - 6 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 18 * sc), int(cy + 18 * sc)), (int(cx + 18 * sc), int(cy + 18 * sc)), c_w, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy + 30 * sc)), int(5 * sc), c_g, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 20 * sc), int(cy + 8 * sc)), int(5 * sc), c_g, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx + 20 * sc), int(cy + 8 * sc)), int(5 * sc), c_g, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "vehicle_lock":
            # Sports car with padlock
            cv2.rectangle(target, (int(cx - 14 * sc), int(cy - 28 * sc)), (int(cx + 14 * sc), int(cy - 8 * sc)), c_g, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 28 * sc)), int(11 * sc), c_g, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 36 * sc), int(cy + 18 * sc)), (int(cx + 36 * sc), int(cy + 18 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy + 12 * sc)), (int(34 * sc), int(14 * sc)), 0, 180, 360, c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 22 * sc), int(cy + 20 * sc)), int(7 * sc), c_m, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx + 22 * sc), int(cy + 20 * sc)), int(7 * sc), c_m, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "weapon_wheel":
            # Radial 8-slot weapon wheel
            cv2.circle(target, (cx, cy), int(34 * sc), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(12 * sc), c_c, int(3 * sc), lineType=cv2.LINE_AA)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = int(cx + 12 * sc * math.cos(rad))
                y1 = int(cy + 12 * sc * math.sin(rad))
                x2 = int(cx + 34 * sc * math.cos(rad))
                y2 = int(cy + 34 * sc * math.sin(rad))
                cv2.line(target, (x1, y1), (x2, y2), c_m, int(3 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "pistol_sidearm":
            # Heavy Handgun silhouette
            pts = np.array([
                [int(cx - 30 * sc), int(cy - 18 * sc)],
                [int(cx + 26 * sc), int(cy - 18 * sc)],
                [int(cx + 26 * sc), int(cy - 4 * sc)],
                [int(cx + 8 * sc), int(cy)],
                [int(cx - 2 * sc), int(cy + 30 * sc)],
                [int(cx - 20 * sc), int(cy + 30 * sc)],
                [int(cx - 12 * sc), int(cy)],
                [int(cx - 30 * sc), int(cy - 4 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 4 * sc), cy), (int(cx + 12 * sc), int(cy + 12 * sc)), c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "assault_rifle":
            # Tactical Carbine Rifle
            cv2.line(target, (int(cx - 40 * sc), int(cy - 6 * sc)), (int(cx + 40 * sc), int(cy - 6 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 30 * sc), int(cy - 6 * sc)), (int(cx - 42 * sc), int(cy + 18 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 8 * sc), int(cy - 6 * sc)), (int(cx - 14 * sc), int(cy + 22 * sc)), c_m, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx + 10 * sc), int(cy - 6 * sc)), (int(cx + 4 * sc), int(cy + 16 * sc)), c_w, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 2 * sc), int(cy - 16 * sc)), (int(cx + 18 * sc), int(cy - 16 * sc)), c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "sniper_scope":
            # Precision Crosshair
            cv2.circle(target, (cx, cy), int(32 * sc), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(16 * sc), c_m, int(3 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 38 * sc), cy), (int(cx + 38 * sc), cy), c_c, int(3 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (cx, int(cy - 38 * sc)), (cx, int(cy + 38 * sc)), c_c, int(3 * sc), lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(4 * sc), c_w, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "sticky_c4":
            # C4 Brick with digital timer
            cv2.rectangle(target, (int(cx - 28 * sc), int(cy - 18 * sc)), (int(cx + 28 * sc), int(cy + 24 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 16 * sc), int(cy - 8 * sc)), (int(cx + 16 * sc), int(cy + 8 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.putText(target, "88", (int(cx - 12 * sc), int(cy + 6 * sc)), cv2.FONT_HERSHEY_DUPLEX, 0.55 * sc, c_w, 1, lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy - 24 * sc)), (int(18 * sc), int(12 * sc)), 0, 180, 360, c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "heavy_armor":
            # Heavy Tactical Ballistic Vest
            pts = np.array([
                [int(cx - 20 * sc), int(cy - 30 * sc)],
                [int(cx - 8 * sc), int(cy - 30 * sc)],
                [int(cx - 6 * sc), int(cy - 14 * sc)],
                [int(cx + 6 * sc), int(cy - 14 * sc)],
                [int(cx + 8 * sc), int(cy - 30 * sc)],
                [int(cx + 20 * sc), int(cy - 30 * sc)],
                [int(cx + 32 * sc), int(cy - 4 * sc)],
                [int(cx + 24 * sc), int(cy + 28 * sc)],
                [int(cx - 24 * sc), int(cy + 28 * sc)],
                [int(cx - 32 * sc), int(cy - 4 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 16 * sc), cy), (int(cx + 16 * sc), cy), c_c, int(4 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 16 * sc), int(cy + 12 * sc)), (int(cx + 16 * sc), int(cy + 12 * sc)), c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "snack_heal":
            # First Aid Cross
            cv2.rectangle(target, (int(cx - 12 * sc), int(cy - 32 * sc)), (int(cx + 12 * sc), int(cy + 22 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 28 * sc), int(cy - 16 * sc)), (int(cx + 28 * sc), int(cy + 6 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 12 * sc), int(cy - 32 * sc)), (int(cx + 12 * sc), int(cy + 22 * sc)), c_w, int(3 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 28 * sc), int(cy - 16 * sc)), (int(cx + 28 * sc), int(cy + 6 * sc)), c_w, int(3 * sc), lineType=cv2.LINE_AA)
            # Pulse
            pts = np.array([[int(cx - 36 * sc), int(cy + 28 * sc)], [int(cx - 18 * sc), int(cy + 28 * sc)], [int(cx - 9 * sc), int(cy + 14 * sc)], [cx, int(cy + 36 * sc)], [int(cx + 12 * sc), int(cy + 22 * sc)], [int(cx + 36 * sc), int(cy + 28 * sc)]], np.int32)
            cv2.polylines(target, [pts], False, c_g, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "clear_wanted":
            # 5-star police badge with slash
            pts = []
            for i in range(10):
                r = 32 * sc if i % 2 == 0 else 13 * sc
                angle = i * 36 - 90
                rad = math.radians(angle)
                pts.append([int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad))])
            cv2.fillPoly(target, [np.array(pts, np.int32)], c_g, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 30 * sc), int(cy + 30 * sc)), (int(cx + 30 * sc), int(cy - 30 * sc)), c_c, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "ifruit_phone":
            # Smartphone with app dots
            cv2.rectangle(target, (int(cx - 20 * sc), int(cy - 36 * sc)), (int(cx + 20 * sc), int(cy + 36 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 15 * sc), int(cy - 28 * sc)), (int(cx + 15 * sc), int(cy + 24 * sc)), c_m, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy + 30 * sc)), int(3 * sc), c_w, -1, lineType=cv2.LINE_AA)
            for dy in [-18, -6, 6]:
                for dx in [-7, 7]:
                    cv2.circle(target, (int((cx + dx) * sc), int((cy + dy) * sc)), int(2 * sc), c_c, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "interaction_menu":
            # Gear / 'M' Badge
            cv2.circle(target, (cx, cy), int(26 * sc), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = int(cx + 26 * sc * math.cos(rad))
                y1 = int(cy + 26 * sc * math.sin(rad))
                x2 = int(cx + 34 * sc * math.cos(rad))
                y2 = int(cy + 34 * sc * math.sin(rad))
                cv2.line(target, (x1, y1), (x2, y2), c_g, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.putText(target, "M", (int(cx - 12 * sc), int(cy + 10 * sc)), cv2.FONT_HERSHEY_DUPLEX, 1.0 * sc, c_c, 2, lineType=cv2.LINE_AA)

        elif symbol_id == "gps_waypoint":
            # Map Pin & Radar Ring
            cv2.circle(target, (cx, int(cy - 12 * sc)), int(18 * sc), c_m, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy - 12 * sc)), int(7 * sc), c_w, -1, lineType=cv2.LINE_AA)
            pts = np.array([[int(cx - 14 * sc), int(cy - 4 * sc)], [cx, int(cy + 24 * sc)], [int(cx + 14 * sc), int(cy - 4 * sc)]], np.int32)
            cv2.fillPoly(target, [pts], c_m, lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy + 28 * sc)), (int(28 * sc), int(9 * sc)), 0, 0, 360, c_c, int(4 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "heist_loot":
            # Heist duffel bag & cash mark
            cv2.rectangle(target, (int(cx - 30 * sc), int(cy - 12 * sc)), (int(cx + 30 * sc), int(cy + 24 * sc)), c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.ellipse(target, (cx, int(cy - 12 * sc)), (int(18 * sc), int(16 * sc)), 0, 180, 360, c_w, int(5 * sc), lineType=cv2.LINE_AA)
            cv2.putText(target, "$", (int(cx - 10 * sc), int(cy + 16 * sc)), cv2.FONT_HERSHEY_DUPLEX, 0.9 * sc, c_g, 2, lineType=cv2.LINE_AA)

        elif symbol_id == "cyber_hack":
            # Cyber skull
            cv2.circle(target, (cx, int(cy - 8 * sc)), int(22 * sc), c_c, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 8 * sc), int(cy - 8 * sc)), int(5 * sc), (20, 10, 24), -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx + 8 * sc), int(cy - 8 * sc)), int(5 * sc), (20, 10, 24), -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (int(cx - 12 * sc), int(cy + 8 * sc)), (int(cx + 12 * sc), int(cy + 24 * sc)), c_c, -1, lineType=cv2.LINE_AA)
            cv2.line(target, (int(cx - 4 * sc), int(cy + 8 * sc)), (int(cx - 4 * sc), int(cy + 24 * sc)), (20, 10, 24), 2)
            cv2.line(target, (int(cx + 4 * sc), int(cy + 8 * sc)), (int(cx + 4 * sc), int(cy + 24 * sc)), (20, 10, 24), 2)

        elif symbol_id == "hands_up_rp":
            # Figure with hands raised in air
            cv2.circle(target, (cx, int(cy - 20 * sc)), int(11 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.line(target, (cx, int(cy - 9 * sc)), (cx, int(cy + 26 * sc)), c_w, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (cx, cy), (int(cx - 26 * sc), int(cy - 26 * sc)), c_g, int(6 * sc), lineType=cv2.LINE_AA)
            cv2.line(target, (cx, cy), (int(cx + 26 * sc), int(cy - 26 * sc)), c_g, int(6 * sc), lineType=cv2.LINE_AA)

        elif symbol_id == "mask_bandana":
            # Heist bandana mask
            pts = np.array([[int(cx - 30 * sc), int(cy - 18 * sc)], [int(cx + 30 * sc), int(cy - 18 * sc)], [cx, int(cy + 28 * sc)]], np.int32)
            cv2.fillPoly(target, [pts], c_m, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx - 14 * sc), cy), int(3 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (int(cx + 14 * sc), cy), int(3 * sc), c_w, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, int(cy + 10 * sc)), int(3 * sc), c_w, -1, lineType=cv2.LINE_AA)

        elif symbol_id == "mod_shield":
            # Security shield
            pts = np.array([
                [cx, int(cy - 30 * sc)],
                [int(cx + 28 * sc), int(cy - 18 * sc)],
                [int(cx + 22 * sc), int(cy + 18 * sc)],
                [cx, int(cy + 34 * sc)],
                [int(cx - 22 * sc), int(cy + 18 * sc)],
                [int(cx - 28 * sc), int(cy - 18 * sc)]
            ], np.int32)
            cv2.fillPoly(target, [pts], c_w, lineType=cv2.LINE_AA)
            cv2.circle(target, (cx, cy), int(10 * sc), c_m, -1, lineType=cv2.LINE_AA)

    # 1. Render mask for soft neon bloom
    render_geometry(mask, is_mask=True)
    mask_blur = cv2.GaussianBlur(mask, (21, 21), 0) / 255.0
    
    # 2. Apply neon ambient bloom to canvas
    canvas[:, :, 0] = np.clip(canvas[:, :, 0].astype(np.float32) + mask_blur * 220, 0, 255).astype(np.uint8) # B
    canvas[:, :, 1] = np.clip(canvas[:, :, 1].astype(np.float32) + mask_blur * 140, 0, 255).astype(np.uint8) # G
    canvas[:, :, 2] = np.clip(canvas[:, :, 2].astype(np.float32) + mask_blur * 90, 0, 255).astype(np.uint8)  # R
    
    # 3. Draw final crisp geometry on top
    render_geometry(canvas, is_mask=False)
    
    return canvas

# ==============================================================================
# CATALOG: 48 BOLD ICONS
# ==============================================================================

ICONS_BOLD = [
    # --- STREAMING & OBS CONTROL (Matching Ulanzi & OBS References) ---
    {"id": "STRM-01", "name": "SCENE", "symbol": "scene_switch", "sub": "strm", "file": "01_scene_switch"},
    {"id": "STRM-02", "name": "RECORD", "symbol": "record", "sub": "strm", "file": "02_record_stream"},
    {"id": "STRM-03", "name": "STREAM", "symbol": "stream", "sub": "strm", "file": "03_start_stream"},
    {"id": "STRM-04", "name": "VIRTUAL CAM", "symbol": "virtual_cam", "sub": "strm", "file": "04_virtual_cam"},
    {"id": "STRM-05", "name": "STUDIO MODE", "symbol": "studio_mode", "sub": "strm", "file": "05_studio_mode"},
    {"id": "STRM-06", "name": "PLAY", "symbol": "play", "sub": "strm", "file": "06_play_media"},
    {"id": "STRM-07", "name": "PAUSE", "symbol": "pause", "sub": "strm", "file": "07_pause_media"},
    {"id": "STRM-08", "name": "PLAY NEXT", "symbol": "play_next", "sub": "strm", "file": "08_play_next"},
    {"id": "STRM-09", "name": "PLAY PREV", "symbol": "play_prev", "sub": "strm", "file": "09_play_prev"},
    {"id": "STRM-10", "name": "SKIP ALERT", "symbol": "skip_forward", "sub": "strm", "file": "10_skip_alert"},
    {"id": "STRM-11", "name": "ALERTS", "symbol": "alert_bell", "sub": "strm", "file": "11_alert_bell"},
    {"id": "STRM-12", "name": "MUTE ALERTS", "symbol": "alert_mute", "sub": "strm", "file": "12_mute_alerts"},
    {"id": "STRM-13", "name": "RELOAD OVERLAYS", "symbol": "reload_overlays", "sub": "strm", "file": "13_reload_overlays"},
    {"id": "STRM-14", "name": "VIEWER REQ", "symbol": "viewer_requests", "sub": "strm", "file": "14_viewer_requests"},
    {"id": "STRM-15", "name": "WIDGET ON", "symbol": "widget_toggle", "sub": "strm", "file": "15_widget_toggle"},
    {"id": "STRM-16", "name": "VIDEO ON", "symbol": "video_toggle", "sub": "strm", "file": "16_video_toggle"},
    {"id": "STRM-17", "name": "VOLUME UP", "symbol": "volume_up", "sub": "strm", "file": "17_volume_up"},
    {"id": "STRM-18", "name": "VOLUME DOWN", "symbol": "volume_down", "sub": "strm", "file": "18_volume_down"},
    {"id": "STRM-19", "name": "MUTE AUDIO", "symbol": "volume_mute", "sub": "strm", "file": "19_volume_mute"},
    {"id": "STRM-20", "name": "SET VOLUME", "symbol": "volume_levels", "sub": "strm", "file": "20_set_volume"},
    {"id": "STRM-21", "name": "MIC MUTE", "symbol": "mic_mute", "sub": "strm", "file": "21_mic_mute"},
    {"id": "STRM-22", "name": "DEAFEN", "symbol": "headphone_deafen", "sub": "strm", "file": "22_headphone_deafen"},
    {"id": "STRM-23", "name": "MOD SHIELD", "symbol": "mod_shield", "sub": "strm", "file": "23_mod_shield"},
    {"id": "STRM-24", "name": "REPLAY 30S", "symbol": "reload_overlays", "sub": "strm", "file": "24_replay_buffer"},

    # --- GTA VI GAMING & OPERATIONS ---
    {"id": "GAME-01", "name": "IGNITION", "symbol": "engine_ignition", "sub": "game", "file": "25_engine_ignition"},
    {"id": "GAME-02", "name": "HIGH BEAMS", "symbol": "headlights_highbeam", "sub": "game", "file": "26_headlights_highbeam"},
    {"id": "GAME-03", "name": "NITRO BOOST", "symbol": "nitro_boost", "sub": "game", "file": "27_nitro_boost"},
    {"id": "GAME-04", "name": "DRIFT BRAKE", "symbol": "handbrake_drift", "sub": "game", "file": "28_handbrake_drift"},
    {"id": "GAME-05", "name": "VICE RADIO", "symbol": "vice_radio", "sub": "game", "file": "29_vice_radio"},
    {"id": "GAME-06", "name": "CINEMATIC", "symbol": "cinematic_cam", "sub": "game", "file": "30_cinematic_cam"},
    {"id": "GAME-07", "name": "VTOL / GEAR", "symbol": "vtol_landing_gear", "sub": "game", "file": "31_vtol_landing_gear"},
    {"id": "GAME-08", "name": "CAR LOCK", "symbol": "vehicle_lock", "sub": "game", "file": "32_vehicle_lock"},
    {"id": "GAME-09", "name": "WEAPON WHEEL", "symbol": "weapon_wheel", "sub": "game", "file": "33_weapon_wheel"},
    {"id": "GAME-10", "name": "PISTOL", "symbol": "pistol_sidearm", "sub": "game", "file": "34_pistol_sidearm"},
    {"id": "GAME-11", "name": "RIFLE", "symbol": "assault_rifle", "sub": "game", "file": "35_assault_rifle"},
    {"id": "GAME-12", "name": "SNIPER", "symbol": "sniper_scope", "sub": "game", "file": "36_sniper_scope"},
    {"id": "GAME-13", "name": "STICKY C4", "symbol": "sticky_c4", "sub": "game", "file": "37_sticky_c4"},
    {"id": "GAME-14", "name": "ARMOR", "symbol": "heavy_armor", "sub": "game", "file": "38_heavy_armor"},
    {"id": "GAME-15", "name": "SNACK HEAL", "symbol": "snack_heal", "sub": "game", "file": "39_snack_heal"},
    {"id": "GAME-16", "name": "CLEAR WANTED", "symbol": "clear_wanted", "sub": "game", "file": "40_clear_wanted"},
    {"id": "GAME-17", "name": "iFRUIT PHONE", "symbol": "ifruit_phone", "sub": "game", "file": "41_ifruit_phone"},
    {"id": "GAME-18", "name": "MENU (M)", "symbol": "interaction_menu", "sub": "game", "file": "42_interaction_menu"},
    {"id": "GAME-19", "name": "GPS MAP", "symbol": "gps_waypoint", "sub": "game", "file": "43_gps_waypoint"},
    {"id": "GAME-20", "name": "HEIST LOOT", "symbol": "heist_loot", "sub": "game", "file": "44_heist_loot"},
    {"id": "GAME-21", "name": "CYBER HACK", "symbol": "cyber_hack", "sub": "game", "file": "45_cyber_hack"},
    {"id": "GAME-22", "name": "HANDS UP RP", "symbol": "hands_up_rp", "sub": "game", "file": "46_hands_up_rp"},
    {"id": "GAME-23", "name": "MASK ON/OFF", "symbol": "mask_bandana", "sub": "game", "file": "47_mask_bandana"},
    {"id": "GAME-24", "name": "HERO PLAY", "symbol": "play", "sub": "game", "file": "48_hero_play"},
]

def render_bold_keycap(icon_def):
    """Renders 186x186 keycap with large bold glyph and high-contrast label."""
    canvas = create_vice_gradient_keycap(KEY_SIZE, KEY_SIZE)
    
    # Check if hero icon or labeled icon
    is_hero = icon_def["name"] == "HERO PLAY"
    has_label = not is_hero
    
    center = (KEY_SIZE // 2, 72) if has_label else (KEY_SIZE // 2, KEY_SIZE // 2)
    draw_bold_symbol(canvas, icon_def["symbol"], center=center, has_label=has_label)
    
    if has_label:
        name = icon_def["name"]
        # Sleek dark label capsule
        cv2.rectangle(canvas, (12, KEY_SIZE - 36), (KEY_SIZE - 13, KEY_SIZE - 12), (16, 6, 22), -1)
        cv2.rectangle(canvas, (12, KEY_SIZE - 36), (KEY_SIZE - 13, KEY_SIZE - 12), (90, 20, 140), 1, lineType=cv2.LINE_AA)
        
        # High contrast font
        font_scale = 0.38 if len(name) <= 11 else 0.32
        (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)
        tx = (KEY_SIZE - tw) // 2
        ty = KEY_SIZE - 20
        
        cv2.putText(canvas, name, (tx + 1, ty + 1), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), 2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, C_WHITE, 1, lineType=cv2.LINE_AA)
        
    return canvas

def render_bold_transparent_glyph(icon_def):
    """Renders large isolated vector glyph on transparent 32-bit RGBA canvas."""
    rgba = np.zeros((KEY_SIZE, KEY_SIZE, 4), dtype=np.uint8)
    temp_rgb = np.zeros((KEY_SIZE, KEY_SIZE, 3), dtype=np.uint8)
    draw_bold_symbol(temp_rgb, icon_def["symbol"], center=(KEY_SIZE//2, KEY_SIZE//2), has_label=False)
    
    gray = cv2.cvtColor(temp_rgb, cv2.COLOR_BGR2GRAY)
    mask = (gray > 15).astype(np.uint8) * 255
    mask_blur = cv2.GaussianBlur(mask, (3, 3), 0.5)
    
    rgba[:, :, :3] = temp_rgb
    rgba[:, :, 3] = mask_blur
    return rgba

def main():
    print(f"Generating 48 Bold GTA VI / Vice City Pro Icons (Matching Ulanzi & OBS decks)...")
    
    for icon in ICONS_BOLD:
        sub = icon["sub"]
        file_prefix = icon["file"]
        
        if sub == "game":
            key_dir = DIRS["game_keys"]
            trans_dir = DIRS["game_trans"]
            hidpi_dir = DIRS["game_hidpi"]
        else:
            key_dir = DIRS["strm_keys"]
            trans_dir = DIRS["strm_trans"]
            hidpi_dir = DIRS["strm_hidpi"]
            
        # 1. Bold Keycap (186x186)
        keycap = render_bold_keycap(icon)
        cv2.imwrite(os.path.join(key_dir, f"{file_prefix}.png"), keycap)
        
        # 2. 2x Hi-DPI (372x372)
        keycap_2x = enhance_2x(keycap)
        cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), keycap_2x)
        
        # 3. Transparent Vector Glyph
        glyph = render_bold_transparent_glyph(icon)
        cv2.imwrite(os.path.join(trans_dir, f"glyph_{file_prefix}.png"), glyph)

    print("All 48 Bold GTA VI icons successfully generated with large proportions and neon bloom!")

if __name__ == "__main__":
    main()
