"""
GTA VI / Vice City (GTX 6) Icon Pack & Telemetry Suite
Generates:
1. 24 Gaming Icons (Vehicles, Combat, Heists, Roleplay, Navigation)
2. 16 Streaming Icons (OBS Scenes, Audio Studio, Camera, Recording, Moderation)
3. 3 Custom 458x196 px System Telemetry Widget Backgrounds (CPU / RAM / GPU)
4. 2x Hi-DPI Renders & Transparent Glyphs
"""

import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "themes", "gta6_vice")

# Directories
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

# Color Palette (BGR for OpenCV, RGB for PIL)
PALETTE = {
    "vice_black": (20, 10, 24),        # Deepest night indigo
    "vice_purple": (77, 18, 45),       # Deep twilight purple #2D124D
    "neon_magenta": (118, 34, 216),    # Hot pink / magenta #D82276
    "sunset_peach": (68, 160, 255),    # Golden peach #FFA044
    "neon_cyan": (255, 240, 0),        # Electric cyan #00F0FF
    "neon_gold": (0, 184, 255),        # Sunset gold #FFB800
    "pure_white": (255, 255, 255),
}

def create_vice_gradient_keycap(w=186, h=186, style="sunset"):
    """Creates a Vice City aesthetic keycap base with neon beveled glow and silhouette palms."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # 1. Base dark plate with subtle dusk gradient
    for y in range(h):
        t = y / float(h)
        if style == "sunset":
            # Dark violet (#1A0A26) to dusky purple (#361245)
            b = int(38 * (1 - t) + 69 * t)
            g = int(10 * (1 - t) + 18 * t)
            r = int(26 * (1 - t) + 54 * t)
        else: # neon_night
            b = int(30 * (1 - t) + 45 * t)
            g = int(12 * (1 - t) + 20 * t)
            r = int(18 * (1 - t) + 28 * t)
        img[y, :] = (b, g, r)
        
    # 2. Add subtle horizon sunset glow band at bottom third
    glow_h = int(h * 0.35)
    horizon_glow = np.zeros((h, w, 3), dtype=np.float32)
    for y in range(h - glow_h, h):
        factor = (y - (h - glow_h)) / float(glow_h)
        # Peach / magenta glow
        horizon_glow[y, :, 0] += factor * 35   # B
        horizon_glow[y, :, 1] += factor * 70   # G
        horizon_glow[y, :, 2] += factor * 160  # R
    img = np.clip(img.astype(np.float32) + horizon_glow, 0, 255).astype(np.uint8)

    # 3. Add silhouette palm frond in corner for Vice City atmosphere
    # Gentle dark silhouette curved fronds
    cv2.ellipse(img, (w + 10, h - 20), (50, 80), 35, 180, 290, (12, 6, 16), 2, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (w + 15, h - 15), (40, 70), 30, 180, 290, (12, 6, 16), 2, lineType=cv2.LINE_AA)
    cv2.ellipse(img, (-10, h - 20), (50, 80), -35, 250, 360, (12, 6, 16), 2, lineType=cv2.LINE_AA)

    # 4. Multi-layered neon beveled frame (Magenta + Sunset Peach)
    # Outer dark chamfer
    cv2.rectangle(img, (3, 3), (w - 4, h - 4), (32, 14, 40), 2, lineType=cv2.LINE_AA)
    
    # Neon glow line (magenta top/sides, golden peach bottom)
    for y in range(8, h - 8):
        t = y / float(h)
        # Gradient color along border
        edge_b = int(118 * (1 - t) + 68 * t)
        edge_g = int(34 * (1 - t) + 160 * t)
        edge_r = int(216 * (1 - t) + 255 * t)
        color = (edge_b, edge_g, edge_r)
        
        if y == 8 or y == h - 9:
            cv2.line(img, (8, y), (w - 9, y), color, 2, lineType=cv2.LINE_AA)
        else:
            img[y, 8] = color
            img[y, 9] = color
            img[y, w - 9] = color
            img[y, w - 10] = color

    # Soft ambient neon glow around the inner rim
    glow_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(glow_mask, (8, 8), (w - 9, h - 9), 255, 3, lineType=cv2.LINE_AA)
    glow_blur = cv2.GaussianBlur(glow_mask, (9, 9), 0) / 255.0
    for c, val in enumerate([70, 40, 180]): # BGR magenta-pink glow
        img[:, :, c] = np.clip(img[:, :, c].astype(np.float32) + glow_blur * val, 0, 255).astype(np.uint8)

    return img

def enhance_2x(img):
    """Lanczos super-sampled 2x render."""
    h, w = img.shape[:2]
    upscaled = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.8)
    return cv2.addWeighted(upscaled, 1.25, gaussian, -0.25, 0)

# ==============================================================================
# SYMBOL DRAWING ENGINE (Clean neon vector glyphs)
# ==============================================================================

def draw_symbol_glyph(canvas, symbol_id, center=(93, 85), scale=1.0):
    """
    Renders clean, iconic vector symbols in crisp neon white with hot magenta/cyan glow.
    """
    cx, cy = center
    color_white = (255, 255, 255)
    color_cyan = (255, 240, 0)
    color_pink = (118, 34, 216)
    color_gold = (68, 160, 255)
    
    # --- GAMING ICONS ---
    if symbol_id == "engine_ignition":
        # Car Key / Ignition button
        cv2.circle(canvas, (cx, cy - 8), int(18 * scale), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - 24), (cx, cy - 10), color_cyan, 3, lineType=cv2.LINE_AA)
        # Power symbol arc
        cv2.ellipse(canvas, (cx, cy + 10), (int(16*scale), int(16*scale)), 0, 130, 410, color_gold, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy), (cx, cy + 12), color_white, 3, lineType=cv2.LINE_AA)

    elif symbol_id == "headlights_highbeam":
        # Headlight bulb with 4 forward beam rays
        cv2.ellipse(canvas, (cx - 10, cy), (int(16*scale), int(22*scale)), 0, 270, 90, color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy - 22), (cx - 10, cy + 22), color_white, 2, lineType=cv2.LINE_AA)
        # Horizontal parallel beam lines
        for offset in [-16, -6, 4, 14]:
            cv2.line(canvas, (cx + 6, cy + offset), (cx + 28, cy + offset), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "nitro_boost":
        # NOS bottle + nitrous flame blast
        cv2.rectangle(canvas, (cx - 16, cy - 18), (cx + 4, cy + 22), color_white, 2, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 10, cy - 26), (cx - 2, cy - 18), color_cyan, -1, lineType=cv2.LINE_AA)
        # Flame streaks
        pts = np.array([[cx + 6, cy - 10], [cx + 26, cy - 14], [cx + 18, cy + 2], [cx + 30, cy + 6], [cx + 8, cy + 18]], np.int32)
        cv2.polylines(canvas, [pts], False, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "handbrake_drift":
        # Brake disc (circle with exclamation point) + tire skid curves
        cv2.circle(canvas, (cx - 4, cy), int(20*scale), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 4, cy), int(12*scale), color_pink, 1, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 4, cy - 7), (cx - 4, cy + 2), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 4, cy + 6), 1, color_white, -1, lineType=cv2.LINE_AA)
        # Skid marks
        cv2.ellipse(canvas, (cx + 18, cy + 12), (16, 22), -25, 180, 290, color_gold, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx + 24, cy + 16), (16, 22), -25, 180, 290, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "radio_next":
        # Musical Eighth note + forward arrows (>>)
        cv2.circle(canvas, (cx - 16, cy + 14), 6, color_white, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 2, cy + 10), 6, color_white, -1, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy + 14), (cx - 10, cy - 16), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx + 4, cy + 10), (cx + 4, cy - 20), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy - 16), (cx + 4, cy - 20), color_cyan, 3, lineType=cv2.LINE_AA)
        # >> arrows
        for off in [12, 22]:
            pts = np.array([[cx + off, cy - 10], [cx + off + 8, cy], [cx + off, cy + 10]], np.int32)
            cv2.polylines(canvas, [pts], False, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "cinematic_cam":
        # Retro 35mm movie camera
        cv2.rectangle(canvas, (cx - 18, cy - 10), (cx + 10, cy + 16), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 10, cy - 18), 8, color_pink, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 2, cy - 18), 8, color_pink, 2, lineType=cv2.LINE_AA)
        # Trapezoid lens
        pts = np.array([[cx + 10, cy - 2], [cx + 26, cy - 12], [cx + 26, cy + 18], [cx + 10, cy + 8]], np.int32)
        cv2.polylines(canvas, [pts], True, color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "vtol_landing_gear":
        # Jet airplane silhouette with landing gear wheels down
        cv2.line(canvas, (cx, cy - 24), (cx, cy + 16), color_white, 3, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 24, cy - 4), (cx + 24, cy - 4), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 12, cy + 14), (cx + 12, cy + 14), color_white, 2, lineType=cv2.LINE_AA)
        # Landing gear wheels
        cv2.circle(canvas, (cx, cy + 22), 3, color_gold, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 14, cy + 6), 3, color_gold, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 14, cy + 6), 3, color_gold, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "vehicle_lock":
        # Sports car coupe silhouette with lock on top
        cv2.rectangle(canvas, (cx - 10, cy - 20), (cx + 10, cy - 6), color_gold, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 20), 7, color_gold, 2, lineType=cv2.LINE_AA)
        # Car body
        cv2.line(canvas, (cx - 26, cy + 12), (cx + 26, cy + 12), color_white, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy + 8), (24, 10), 0, 180, 360, color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 16, cy + 14), 5, color_pink, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 16, cy + 14), 5, color_pink, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "weapon_wheel":
        # Radial weapon wheel with 8 segments and central crosshair
        cv2.circle(canvas, (cx, cy), 24, color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 8, color_cyan, 1, lineType=cv2.LINE_AA)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = int(cx + 8 * math.cos(rad))
            y1 = int(cy + 8 * math.sin(rad))
            x2 = int(cx + 24 * math.cos(rad))
            y2 = int(cy + 24 * math.sin(rad))
            cv2.line(canvas, (x1, y1), (x2, y2), color_pink, 1, lineType=cv2.LINE_AA)

    elif symbol_id == "pistol_sidearm":
        # Handgun silhouette
        pts = np.array([
            [cx - 20, cy - 14], [cx + 16, cy - 14], [cx + 16, cy - 4],
            [cx + 4, cy - 2], [cx - 2, cy + 18], [cx - 14, cy + 18],
            [cx - 8, cy - 2], [cx - 20, cy - 4]
        ], np.int32)
        cv2.polylines(canvas, [pts], True, color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx + 2, cy - 2), (cx + 8, cy + 6), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "assault_rifle":
        # Tactical Assault rifle silhouette
        cv2.line(canvas, (cx - 26, cy - 4), (cx + 26, cy - 4), color_white, 3, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 20, cy - 4), (cx - 28, cy + 12), color_white, 2, lineType=cv2.LINE_AA) # Stock
        cv2.line(canvas, (cx - 6, cy - 4), (cx - 10, cy + 14), color_pink, 3, lineType=cv2.LINE_AA)   # Magazine
        cv2.line(canvas, (cx + 6, cy - 4), (cx + 2, cy + 10), color_white, 2, lineType=cv2.LINE_AA)   # Grip
        cv2.line(canvas, (cx - 2, cy - 10), (cx + 12, cy - 10), color_cyan, 2, lineType=cv2.LINE_AA) # Optic

    elif symbol_id == "sniper_scope":
        # Precision crosshair reticle
        cv2.circle(canvas, (cx, cy), 22, color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 12, color_pink, 1, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 26, cy), (cx + 26, cy), color_cyan, 1, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - 26), (cx, cy + 26), color_cyan, 1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 2, color_white, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "explosive_c4":
        # C4 Brick with digital timer and wires
        cv2.rectangle(canvas, (cx - 18, cy - 12), (cx + 18, cy + 16), color_white, 2, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 10, cy - 6), (cx + 10, cy + 4), color_pink, -1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "88", (cx - 8, cy + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color_white, 1, lineType=cv2.LINE_AA)
        # Wires
        cv2.ellipse(canvas, (cx, cy - 16), (12, 8), 0, 180, 360, color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "armor_vest":
        # Body Armor vest
        pts = np.array([
            [cx - 14, cy - 20], [cx - 6, cy - 20], [cx - 4, cy - 10], [cx + 4, cy - 10],
            [cx + 6, cy - 20], [cx + 14, cy - 20], [cx + 22, cy - 4], [cx + 16, cy + 18],
            [cx - 16, cy + 18], [cx - 22, cy - 4]
        ], np.int32)
        cv2.polylines(canvas, [pts], True, color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy), (cx + 10, cy), color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy + 8), (cx + 10, cy + 8), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "health_snack":
        # First Aid Cross & snack soda can
        # Cross
        cv2.rectangle(canvas, (cx - 7, cy - 20), (cx + 7, cy + 14), color_pink, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 17, cy - 10), (cx + 17, cy + 4), color_pink, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 7, cy - 20), (cx + 7, cy + 14), color_white, 1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 17, cy - 10), (cx + 17, cy + 4), color_white, 1, lineType=cv2.LINE_AA)
        # Heart pulse line
        pts = np.array([[cx - 24, cy + 18], [cx - 12, cy + 18], [cx - 6, cy + 8], [cx, cy + 24], [cx + 8, cy + 14], [cx + 24, cy + 18]], np.int32)
        cv2.polylines(canvas, [pts], False, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "wanted_stars":
        # 5-pointed star with police siren slash
        pts = []
        for i in range(10):
            r = 22 if i % 2 == 0 else 9
            angle = i * 36 - 90
            rad = math.radians(angle)
            pts.append([int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad))])
        cv2.polylines(canvas, [np.array(pts, np.int32)], True, color_gold, 2, lineType=cv2.LINE_AA)
        # Red/blue slash
        cv2.line(canvas, (cx - 20, cy + 20), (cx + 20, cy - 20), color_cyan, 3, lineType=cv2.LINE_AA)

    elif symbol_id == "ifruit_phone":
        # Smartphone with notch and apps
        cv2.rectangle(canvas, (cx - 14, cy - 24), (cx + 14, cy + 24), color_white, 2, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 10, cy - 18), (cx + 10, cy + 16), color_pink, 1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy + 20), 2, color_white, -1, lineType=cv2.LINE_AA)
        # App dots
        for dy in [-12, -4, 4]:
            for dx in [-5, 5]:
                cv2.circle(canvas, (cx + dx, cy + dy), 1, color_cyan, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "interaction_menu":
        # Radial gear / 'M' key badge
        cv2.circle(canvas, (cx, cy), 18, color_white, 2, lineType=cv2.LINE_AA)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = int(cx + 18 * math.cos(rad))
            y1 = int(cy + 18 * math.sin(rad))
            x2 = int(cx + 23 * math.cos(rad))
            y2 = int(cy + 23 * math.sin(rad))
            cv2.line(canvas, (x1, y1), (x2, y2), color_gold, 2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "M", (cx - 7, cy + 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, color_cyan, 1, lineType=cv2.LINE_AA)

    elif symbol_id == "map_gps_waypoint":
        # Location Pin with circular radar waves
        cv2.circle(canvas, (cx, cy - 8), 12, color_pink, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 8), 4, color_white, -1, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 8, cy - 2), (cx, cy + 16), color_pink, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx + 8, cy - 2), (cx, cy + 16), color_pink, 2, lineType=cv2.LINE_AA)
        # Radar ground ring
        cv2.ellipse(canvas, (cx, cy + 18), (20, 6), 0, 0, 360, color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "duffel_bag_loot":
        # Heist duffel bag with handles and dollar mark
        cv2.rectangle(canvas, (cx - 20, cy - 8), (cx + 20, cy + 16), color_white, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy - 8), (12, 10), 0, 180, 360, color_white, 2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "$", (cx - 6, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "hack_device":
        # Cyber skull / USB bypass device
        cv2.circle(canvas, (cx, cy - 6), 14, color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 5, cy - 6), 3, color_white, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 5, cy - 6), 3, color_white, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 8, cy + 4), (cx + 8, cy + 14), color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 3, cy + 4), (cx - 3, cy + 14), color_cyan, 1)
        cv2.line(canvas, (cx + 3, cy + 4), (cx + 3, cy + 14), color_cyan, 1)

    elif symbol_id == "hands_up_rp":
        # Figure with hands raised in air
        cv2.circle(canvas, (cx, cy - 14), 7, color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - 7), (cx, cy + 18), color_white, 2, lineType=cv2.LINE_AA)
        # Arms raised
        cv2.line(canvas, (cx, cy - 2), (cx - 18, cy - 18), color_gold, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - 2), (cx + 18, cy - 18), color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "mask_bandana":
        # Bandit bandana triangle
        pts = np.array([[cx - 20, cy - 12], [cx + 20, cy - 12], [cx, cy + 18]], np.int32)
        cv2.polylines(canvas, [pts], True, color_pink, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 10, cy - 2), 2, color_white, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 10, cy - 2), 2, color_white, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy + 6), 2, color_white, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "screenshot_snap":
        # Camera / Clapperboard snap
        cv2.rectangle(canvas, (cx - 20, cy - 12), (cx + 20, cy + 16), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy + 2), 9, color_cyan, 2, lineType=cv2.LINE_AA)
        # Top flash
        cv2.circle(canvas, (cx + 12, cy - 6), 3, color_gold, -1, lineType=cv2.LINE_AA)

    # --- STREAMING ICONS ---
    elif symbol_id == "scene_starting":
        # Rising neon sun over horizon with palm tree
        cv2.circle(canvas, (cx, cy), 18, color_gold, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 26, cy + 8), (cx + 26, cy + 8), color_pink, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 20, cy + 14), (cx + 20, cy + 14), color_pink, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "scene_gameplay":
        # Gamepad controller
        cv2.rectangle(canvas, (cx - 18, cy - 10), (cx + 18, cy + 12), color_white, 2, lineType=cv2.LINE_AA)
        # D-pad
        cv2.line(canvas, (cx - 10, cy - 5), (cx - 10, cy + 7), color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 16, cy + 1), (cx - 4, cy + 1), color_cyan, 2, lineType=cv2.LINE_AA)
        # Action buttons
        cv2.circle(canvas, (cx + 10, cy - 2), 2, color_pink, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 10, cy + 6), 2, color_gold, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "scene_chatting":
        # Dual chatting speech bubbles
        cv2.ellipse(canvas, (cx - 6, cy - 6), (16, 12), 0, 0, 360, color_white, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx + 10, cy + 8), (14, 10), 0, 0, 360, color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "scene_brb":
        # Neon tropical cocktail glass (Martini with straw)
        pts = np.array([[cx - 18, cy - 18], [cx + 18, cy - 18], [cx, cy + 4]], np.int32)
        cv2.polylines(canvas, [pts], True, color_pink, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy + 4), (cx, cy + 18), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy + 18), (cx + 10, cy + 18), color_white, 2, lineType=cv2.LINE_AA)
        # Neon straw
        cv2.line(canvas, (cx - 4, cy), (cx + 16, cy - 26), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "scene_ending":
        # Vice City skyline with crescent moon
        # Buildings
        cv2.rectangle(canvas, (cx - 22, cy - 4), (cx - 10, cy + 20), color_pink, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 8, cy - 16), (cx + 4, cy + 20), color_cyan, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx + 6, cy - 8), (cx + 18, cy + 20), color_pink, -1, lineType=cv2.LINE_AA)
        # Moon
        cv2.circle(canvas, (cx - 10, cy - 18), 8, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "mic_toggle":
        # Broadcast condenser mic with toggle slash
        cv2.rectangle(canvas, (cx - 8, cy - 22), (cx + 8, cy + 2), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 22), 8, color_white, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy - 4), (14, 14), 0, 0, 180, color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy + 10), (cx, cy + 20), color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 8, cy + 20), (cx + 8, cy + 20), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "headphone_deafen":
        # DJ Headphones with slash
        cv2.ellipse(canvas, (cx, cy - 2), (20, 20), 0, 180, 360, color_white, 3, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 24, cy - 4), (cx - 16, cy + 16), color_pink, -1, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx + 16, cy - 4), (cx + 24, cy + 16), color_pink, -1, lineType=cv2.LINE_AA)
        # Deafen red slash
        cv2.line(canvas, (cx - 18, cy + 18), (cx + 18, cy - 18), color_gold, 3, lineType=cv2.LINE_AA)

    elif symbol_id == "discord_ptt":
        # Discord controller mask
        cv2.ellipse(canvas, (cx, cy), (22, 14), 0, 0, 360, color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 8, cy), 4, color_white, -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx + 8, cy), 4, color_white, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "music_spotify":
        # Vinyl record with music audio wave
        cv2.circle(canvas, (cx, cy), 22, color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 8, color_gold, -1, lineType=cv2.LINE_AA)
        for h_off in [-14, -8, 8, 14]:
            cv2.ellipse(canvas, (cx, cy), (int(abs(h_off)*1.3), int(abs(h_off)*1.3)), 0, 0, 360, color_pink, 1, lineType=cv2.LINE_AA)

    elif symbol_id == "soundboard_sfx":
        # Megaphone / Airhorn burst
        pts = np.array([[cx - 18, cy - 4], [cx, cy - 14], [cx, cy + 14], [cx - 18, cy + 4]], np.int32)
        cv2.polylines(canvas, [pts], True, color_white, 2, lineType=cv2.LINE_AA)
        cv2.rectangle(canvas, (cx - 22, cy - 4), (cx - 18, cy + 4), color_pink, -1, lineType=cv2.LINE_AA)
        # Audio burst arcs
        cv2.ellipse(canvas, (cx + 4, cy), (10, 16), 0, -45, 45, color_cyan, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx + 12, cy), (14, 22), 0, -45, 45, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "voice_changer":
        # Radio audio waves / Cyber mask
        cv2.circle(canvas, (cx, cy), 18, color_white, 2, lineType=cv2.LINE_AA)
        # Soundwave frequency bars
        for dx, h_bar in [(-12, 6), (-6, 12), (0, 18), (6, 12), (12, 6)]:
            cv2.line(canvas, (cx + dx, cy - h_bar), (cx + dx, cy + h_bar), color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "start_stop_stream":
        # Satellite antenna tower with ON AIR rings
        cv2.line(canvas, (cx, cy - 14), (cx - 16, cy + 20), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - 14), (cx + 16, cy + 20), color_white, 2, lineType=cv2.LINE_AA)
        cv2.line(canvas, (cx - 10, cy + 6), (cx + 10, cy + 6), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 14), 5, color_pink, -1, lineType=cv2.LINE_AA)
        # Broadcast waves
        cv2.ellipse(canvas, (cx, cy - 14), (14, 14), 0, 200, 340, color_gold, 2, lineType=cv2.LINE_AA)
        cv2.ellipse(canvas, (cx, cy - 14), (22, 22), 0, 200, 340, color_gold, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "record_replay":
        # Instant Replay (circular rewind arrow + 30s)
        cv2.ellipse(canvas, (cx, cy), (20, 20), 0, 45, 315, color_cyan, 2, lineType=cv2.LINE_AA)
        # Arrowhead
        pts = np.array([[cx + 10, cy - 20], [cx + 20, cy - 14], [cx + 16, cy - 26]], np.int32)
        cv2.fillPoly(canvas, [pts], color_cyan, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "30s", (cx - 14, cy + 5), cv2.FONT_HERSHEY_DUPLEX, 0.45, color_white, 1, lineType=cv2.LINE_AA)

    elif symbol_id == "facecam_toggle":
        # Video Camera lens with aperture iris
        cv2.rectangle(canvas, (cx - 16, cy - 12), (cx + 8, cy + 14), color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx - 4, cy + 1), 7, color_pink, 2, lineType=cv2.LINE_AA)
        pts = np.array([[cx + 8, cy - 6], [cx + 22, cy - 14], [cx + 22, cy + 16], [cx + 8, cy + 8]], np.int32)
        cv2.polylines(canvas, [pts], True, color_cyan, 2, lineType=cv2.LINE_AA)

    elif symbol_id == "stream_marker":
        # Flag bookmark with highlight star
        pts = np.array([[cx - 12, cy - 20], [cx + 12, cy - 20], [cx + 12, cy + 16], [cx, cy + 6], [cx - 12, cy + 16]], np.int32)
        cv2.polylines(canvas, [pts], True, color_gold, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 4), 4, color_white, -1, lineType=cv2.LINE_AA)

    elif symbol_id == "chat_moderation":
        # Security shield with neon chat bubble
        pts = np.array([[cx, cy - 20], [cx + 18, cy - 12], [cx + 14, cy + 12], [cx, cy + 22], [cx - 14, cy + 12], [cx - 18, cy - 12]], np.int32)
        cv2.polylines(canvas, [pts], True, color_white, 2, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy - 2), 6, color_pink, -1, lineType=cv2.LINE_AA)
        
    return canvas

# ==============================================================================
# ICON CATALOG DEFINITIONS (40 Icons)
# ==============================================================================

ICONS = [
    # 24 GAMING ICONS
    {"id": "GTA-GAME-01", "name": "ENGINE IGNITION", "symbol": "engine_ignition", "cat": "Vehicle", "sub": "game", "file": "01_engine_ignition"},
    {"id": "GTA-GAME-02", "name": "HIGH BEAMS", "symbol": "headlights_highbeam", "cat": "Vehicle", "sub": "game", "file": "02_headlights_highbeam"},
    {"id": "GTA-GAME-03", "name": "NITRO BOOST", "symbol": "nitro_boost", "cat": "Vehicle", "sub": "game", "file": "03_nitro_boost"},
    {"id": "GTA-GAME-04", "name": "HANDBRAKE DRIFT", "symbol": "handbrake_drift", "cat": "Vehicle", "sub": "game", "file": "04_handbrake_drift"},
    {"id": "GTA-GAME-05", "name": "VICE RADIO", "symbol": "radio_next", "cat": "Vehicle", "sub": "game", "file": "05_vice_radio"},
    {"id": "GTA-GAME-06", "name": "CINEMATIC CAM", "symbol": "cinematic_cam", "cat": "Vehicle", "sub": "game", "file": "06_cinematic_cam"},
    {"id": "GTA-GAME-07", "name": "VTOL / GEAR", "symbol": "vtol_landing_gear", "cat": "Vehicle", "sub": "game", "file": "07_vtol_landing_gear"},
    {"id": "GTA-GAME-08", "name": "DOOR LOCK", "symbol": "vehicle_lock", "cat": "Vehicle", "sub": "game", "file": "08_vehicle_lock"},
    {"id": "GTA-GAME-09", "name": "WEAPON WHEEL", "symbol": "weapon_wheel", "cat": "Combat", "sub": "game", "file": "09_weapon_wheel"},
    {"id": "GTA-GAME-10", "name": "PISTOL SIDEARM", "symbol": "pistol_sidearm", "cat": "Combat", "sub": "game", "file": "10_pistol_sidearm"},
    {"id": "GTA-GAME-11", "name": "ASSAULT RIFLE", "symbol": "assault_rifle", "cat": "Combat", "sub": "game", "file": "11_assault_rifle"},
    {"id": "GTA-GAME-12", "name": "SNIPER SCOPE", "symbol": "sniper_scope", "cat": "Combat", "sub": "game", "file": "12_sniper_scope"},
    {"id": "GTA-GAME-13", "name": "STICKY C4", "symbol": "explosive_c4", "cat": "Combat", "sub": "game", "file": "13_sticky_c4"},
    {"id": "GTA-GAME-14", "name": "HEAVY ARMOR", "symbol": "armor_vest", "cat": "Combat", "sub": "game", "file": "14_heavy_armor"},
    {"id": "GTA-GAME-15", "name": "SNACK HEAL", "symbol": "health_snack", "cat": "Combat", "sub": "game", "file": "15_snack_heal"},
    {"id": "GTA-GAME-16", "name": "CLEAR WANTED", "symbol": "wanted_stars", "cat": "Combat", "sub": "game", "file": "16_clear_wanted"},
    {"id": "GTA-GAME-17", "name": "iFRUIT PHONE", "symbol": "ifruit_phone", "cat": "Heist & RP", "sub": "game", "file": "17_ifruit_phone"},
    {"id": "GTA-GAME-18", "name": "MENU (M)", "symbol": "interaction_menu", "cat": "Heist & RP", "sub": "game", "file": "18_interaction_menu"},
    {"id": "GTA-GAME-19", "name": "GPS WAYPOINT", "symbol": "map_gps_waypoint", "cat": "Heist & RP", "sub": "game", "file": "19_gps_waypoint"},
    {"id": "GTA-GAME-20", "name": "HEIST LOOT", "symbol": "duffel_bag_loot", "cat": "Heist & RP", "sub": "game", "file": "20_heist_loot"},
    {"id": "GTA-GAME-21", "name": "CYBER HACK", "symbol": "hack_device", "cat": "Heist & RP", "sub": "game", "file": "21_cyber_hack"},
    {"id": "GTA-GAME-22", "name": "HANDS UP RP", "symbol": "hands_up_rp", "cat": "Heist & RP", "sub": "game", "file": "22_hands_up_rp"},
    {"id": "GTA-GAME-23", "name": "MASK ON/OFF", "symbol": "mask_bandana", "cat": "Heist & RP", "sub": "game", "file": "23_mask_bandana"},
    {"id": "GTA-GAME-24", "name": "CLIP SNAPSHOT", "symbol": "screenshot_snap", "cat": "Heist & RP", "sub": "game", "file": "24_clip_snapshot"},

    # 16 STREAMING ICONS
    {"id": "GTA-STRM-01", "name": "SCENE STARTING", "symbol": "scene_starting", "cat": "Scenes", "sub": "strm", "file": "25_scene_starting"},
    {"id": "GTA-STRM-02", "name": "SCENE GAMEPLAY", "symbol": "scene_gameplay", "cat": "Scenes", "sub": "strm", "file": "26_scene_gameplay"},
    {"id": "GTA-STRM-03", "name": "SCENE CHATTING", "symbol": "scene_chatting", "cat": "Scenes", "sub": "strm", "file": "27_scene_chatting"},
    {"id": "GTA-STRM-04", "name": "SCENE BRB", "symbol": "scene_brb", "cat": "Scenes", "sub": "strm", "file": "28_scene_brb"},
    {"id": "GTA-STRM-05", "name": "SCENE ENDING", "symbol": "scene_ending", "cat": "Scenes", "sub": "strm", "file": "29_scene_ending"},
    {"id": "GTA-STRM-06", "name": "MIC MUTE", "symbol": "mic_toggle", "cat": "Audio", "sub": "strm", "file": "30_mic_mute"},
    {"id": "GTA-STRM-07", "name": "DEAFEN HEADPHONES", "symbol": "headphone_deafen", "cat": "Audio", "sub": "strm", "file": "31_headphone_deafen"},
    {"id": "GTA-STRM-08", "name": "DISCORD VOICE", "symbol": "discord_ptt", "cat": "Audio", "sub": "strm", "file": "32_discord_voice"},
    {"id": "GTA-STRM-09", "name": "MUSIC TRACK", "symbol": "music_spotify", "cat": "Audio", "sub": "strm", "file": "33_music_track"},
    {"id": "GTA-STRM-10", "name": "SOUNDBOARD", "symbol": "soundboard_sfx", "cat": "Audio", "sub": "strm", "file": "34_soundboard"},
    {"id": "GTA-STRM-11", "name": "VOICE FX", "symbol": "voice_changer", "cat": "Audio", "sub": "strm", "file": "35_voice_fx"},
    {"id": "GTA-STRM-12", "name": "GO LIVE / END", "symbol": "start_stop_stream", "cat": "Production", "sub": "strm", "file": "36_go_live"},
    {"id": "GTA-STRM-13", "name": "REPLAY 30S", "symbol": "record_replay", "cat": "Production", "sub": "strm", "file": "37_replay_30s"},
    {"id": "GTA-STRM-14", "name": "FACECAM TOGGLE", "symbol": "facecam_toggle", "cat": "Production", "sub": "strm", "file": "38_facecam_toggle"},
    {"id": "GTA-STRM-15", "name": "HIGHLIGHT MARKER", "symbol": "stream_marker", "cat": "Production", "sub": "strm", "file": "39_highlight_marker"},
    {"id": "GTA-STRM-16", "name": "MOD SHIELD", "symbol": "chat_moderation", "cat": "Production", "sub": "strm", "file": "40_mod_shield"},
]

def render_keycap_with_label(icon_def):
    """Renders full 186x186 keycap with neon glyph and bottom text badge."""
    canvas = create_vice_gradient_keycap(KEY_SIZE, KEY_SIZE)
    
    # Draw Symbol in center
    draw_symbol_glyph(canvas, icon_def["symbol"], center=(KEY_SIZE//2, 80), scale=1.0)
    
    # Label Banner at bottom
    name = icon_def["name"]
    # Pill background for label
    cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 14), (16, 8, 22), -1)
    cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 14), (80, 24, 140), 1, lineType=cv2.LINE_AA)
    
    # Text calculation
    font_scale = 0.36
    if len(name) > 13:
        font_scale = 0.31
    (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)
    tx = (KEY_SIZE - tw) // 2
    ty = KEY_SIZE - 22
    
    # Text shadow & bright text
    cv2.putText(canvas, name, (tx + 1, ty + 1), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 1, lineType=cv2.LINE_AA)
    
    return canvas

def render_transparent_glyph(icon_def):
    """Renders isolated vector glyph on transparent RGBA canvas."""
    rgba = np.zeros((KEY_SIZE, KEY_SIZE, 4), dtype=np.uint8)
    
    # Draw on temporary RGB
    temp_rgb = np.zeros((KEY_SIZE, KEY_SIZE, 3), dtype=np.uint8)
    draw_symbol_glyph(temp_rgb, icon_def["symbol"], center=(KEY_SIZE//2, KEY_SIZE//2), scale=1.15)
    
    # Calculate mask
    gray = cv2.cvtColor(temp_rgb, cv2.COLOR_BGR2GRAY)
    mask = (gray > 15).astype(np.uint8) * 255
    mask_blur = cv2.GaussianBlur(mask, (3, 3), 0.5)
    
    rgba[:, :, :3] = temp_rgb
    rgba[:, :, 3] = mask_blur
    return rgba

# ==============================================================================
# GTA VI 458x196 WIDGET BACKGROUNDS
# ==============================================================================

def generate_gta6_telemetry_backgrounds():
    """Renders 458x196 px system telemetry widget backgrounds in Vice City aesthetic."""
    w, h = 458, 196
    bg1 = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Vice Sunset Gradient Plate
    for y in range(h):
        t = y / float(h)
        # Indigo -> Magenta -> Sunset Peach
        if t < 0.55:
            st = t / 0.55
            b = int(77 * (1 - st) + 118 * st)
            g = int(18 * (1 - st) + 34 * st)
            r = int(45 * (1 - st) + 216 * st)
        else:
            st = (t - 0.55) / 0.45
            b = int(118 * (1 - st) + 68 * st)
            g = int(34 * (1 - st) + 160 * st)
            r = int(216 * (1 - st) + 255 * st)
        bg1[y, :] = (b, g, r)
        
    # Darken inner display area so dynamic white text is completely legible
    inner_mask = np.zeros((h, w), dtype=np.float32)
    cv2.rectangle(inner_mask, (16, 16), (w - 17, h - 17), 0.82, -1)
    inner_mask = cv2.GaussianBlur(inner_mask, (7, 7), 0)
    bg1 = (bg1.astype(np.float32) * (1.0 - inner_mask[:, :, np.newaxis])).astype(np.uint8)
    
    # Silhouette palm tree on left & right
    cv2.ellipse(bg1, (24, h - 10), (35, 75), 25, 180, 300, (14, 6, 18), 3, lineType=cv2.LINE_AA)
    cv2.ellipse(bg1, (w - 24, h - 10), (35, 75), -25, 240, 360, (14, 6, 18), 3, lineType=cv2.LINE_AA)
    
    # Neon Beveled Border
    cv2.rectangle(bg1, (16, 16), (w - 17, h - 17), (216, 34, 118), 2, lineType=cv2.LINE_AA)
    cv2.rectangle(bg1, (18, 18), (w - 19, h - 19), (68, 160, 255), 1, lineType=cv2.LINE_AA)
    
    # Vertical Dividers between CPU, RAM, GPU
    for x in [152, 305]:
        cv2.line(bg1, (x, 32), (x, h - 32), (30, 10, 36), 3, lineType=cv2.LINE_AA)
        cv2.line(bg1, (x, 36), (x, h - 36), (216, 34, 118), 1, lineType=cv2.LINE_AA)
        cv2.circle(bg1, (x, 36), 2, (68, 160, 255), -1, lineType=cv2.LINE_AA)
        cv2.circle(bg1, (x, h - 36), 2, (68, 160, 255), -1, lineType=cv2.LINE_AA)
        
    # Top Header: Glowing "VI" Monogram with Vice City lettering
    cv2.putText(bg1, "VI", (w//2 - 14, 18), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1, lineType=cv2.LINE_AA)
    cv2.putText(bg1, "VICE CITY TELEMETRY", (w//2 - 68, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (68, 160, 255), 1, lineType=cv2.LINE_AA)
    
    return bg1

def render_simulated_widget_preview(bg):
    """Simulates active numbers over background."""
    sim = bg.copy()
    cols = [
        {"val": "8%", "label": "CPU", "cx": 82},
        {"val": "55%", "label": "RAM", "cx": 229},
        {"val": "8%", "label": "GPU", "cx": 376}
    ]
    for c in cols:
        cx = c["cx"]
        cv2.putText(sim, c["val"], (cx - 32, 108), cv2.FONT_HERSHEY_DUPLEX, 1.25, (0, 0, 0), 4, lineType=cv2.LINE_AA)
        cv2.putText(sim, c["val"], (cx - 32, 108), cv2.FONT_HERSHEY_DUPLEX, 1.25, (255, 255, 255), 2, lineType=cv2.LINE_AA)
        cv2.putText(sim, c["label"], (cx - 22, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 3, lineType=cv2.LINE_AA)
        cv2.putText(sim, c["label"], (cx - 22, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 240, 255), 1, lineType=cv2.LINE_AA)
    return sim

def main():
    print(f"Generating GTA VI / Vice City Icon Pack ({len(ICONS)} icons)...")
    
    for icon in ICONS:
        sub = icon["sub"]
        file_prefix = icon["file"]
        
        # Determine directories
        if sub == "game":
            key_dir = DIRS["game_keys"]
            trans_dir = DIRS["game_trans"]
            hidpi_dir = DIRS["game_hidpi"]
        else:
            key_dir = DIRS["strm_keys"]
            trans_dir = DIRS["strm_trans"]
            hidpi_dir = DIRS["strm_hidpi"]
            
        # 1. Full Keycap Render (186 x 186 px)
        keycap = render_keycap_with_label(icon)
        cv2.imwrite(os.path.join(key_dir, f"{file_prefix}.png"), keycap)
        
        # 2. 2x Hi-DPI Render (372 x 372 px)
        keycap_2x = enhance_2x(keycap)
        cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), keycap_2x)
        
        # 3. Transparent Glyph
        glyph = render_transparent_glyph(icon)
        cv2.imwrite(os.path.join(trans_dir, f"glyph_{file_prefix}.png"), glyph)

    print("All 40 GTA VI icons successfully rendered at 1x, 2x Hi-DPI, and transparent formats.")
    
    # 4. Generate GTA VI 458x196 Telemetry Background
    print("Generating GTA VI 458x196 System Telemetry Background...")
    gt6_bg = generate_gta6_telemetry_backgrounds()
    bg_path = os.path.join(DIRS["widgets"], "01_gta6_vice_sunset_telemetry_458x196.png")
    cv2.imwrite(bg_path, gt6_bg)
    
    # 2x Hi-DPI
    bg_2x = enhance_2x(gt6_bg)
    cv2.imwrite(os.path.join(DIRS["widgets_hidpi"], "01_gta6_vice_sunset_telemetry_458x196_2x.png"), bg_2x)
    
    # Simulated Preview
    prev = render_simulated_widget_preview(gt6_bg)
    cv2.imwrite(os.path.join(DIRS["widgets_prev"], "preview_01_gta6_vice_sunset_telemetry.png"), prev)
    print("GTA VI widget backgrounds successfully rendered!")

if __name__ == "__main__":
    main()
