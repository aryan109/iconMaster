"""
SimForge Fire Metal OBS Studio Record Pause Icon Suite
Renders:
1. SimForge Fire Metal Record Pause (State 2: Camera with vertical pause bars '||')
2. SimForge Fire Metal Record Active (State 1: Camera with glowing molten record dot)
3. Hero pure-symbol editions (without text label, enlarged 65% glyph)
4. Companion GTA VI Vice City editions for complete cross-theme parity
5. Standard 1x (186x186), 2x Hi-DPI (372x372), and Transparent 32-bit RGBA Glyphs
"""

import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SimForge Directories
SIM_BUTTONS_DIR = os.path.join(BASE_DIR, "output", "themes", "simforge", "buttons")
SIM_BUTTONS_ROOT = os.path.join(BASE_DIR, "output", "buttons")
SIM_HIDPI_DIR = os.path.join(SIM_BUTTONS_DIR, "high_dpi_2x")
SIM_ROOT_HIDPI = os.path.join(SIM_BUTTONS_ROOT, "high_dpi_2x")
SIM_TRANS_DIR = os.path.join(BASE_DIR, "output", "themes", "simforge", "icons_isolated", "transparent")
SIM_ROOT_TRANS = os.path.join(BASE_DIR, "output", "icons_isolated", "transparent")

# GTA VI Directories
GTA_KEY_DIR = os.path.join(BASE_DIR, "output", "themes", "gta6_vice", "streaming_icons", "keycaps")
GTA_HIDPI_DIR = os.path.join(BASE_DIR, "output", "themes", "gta6_vice", "streaming_icons", "high_dpi_2x")
GTA_TRANS_DIR = os.path.join(BASE_DIR, "output", "themes", "gta6_vice", "streaming_icons", "transparent_glyphs")

for d in [SIM_BUTTONS_DIR, SIM_BUTTONS_ROOT, SIM_HIDPI_DIR, SIM_ROOT_HIDPI, SIM_TRANS_DIR, SIM_ROOT_TRANS, GTA_KEY_DIR, GTA_HIDPI_DIR, GTA_TRANS_DIR]:
    os.makedirs(d, exist_ok=True)

KEY_SIZE = 186

# SimForge Colors (BGR)
SIM_ORANGE = (0, 140, 255)     # Glowing Amber / Orange #FF8C00
SIM_FIRE = (0, 69, 255)       # Molten Red-Orange #FF4500
SIM_HOT_YELLOW = (80, 210, 255)# White-hot core #FFD250
SIM_DARK_STEEL = (22, 24, 28)  # Brushed dark gunmetal

def create_simforge_keycap_base(w=186, h=186):
    """
    Renders authentic SimForge industrial stream deck button face:
    Dark brushed steel plate, socket chamfer, and radiant incandescent molten orange perimeter glow.
    """
    canvas = np.full((h, w, 3), (18, 20, 24), dtype=np.uint8)
    
    # Brushed metal micro-texture
    noise = np.random.normal(0, 3.5, (h, w)).astype(np.float32)
    noise_brushed = cv2.GaussianBlur(noise, (15, 1), 0)
    for c in range(3):
        canvas[:, :, c] = np.clip(canvas[:, :, c].astype(np.float32) + noise_brushed, 10, 40).astype(np.uint8)
        
    # Beveled outer socket rim
    cv2.rectangle(canvas, (3, 3), (w - 4, h - 4), (40, 44, 52), 2, lineType=cv2.LINE_AA)
    cv2.rectangle(canvas, (6, 6), (w - 7, h - 7), (12, 13, 16), 3, lineType=cv2.LINE_AA)

    # Glowing Molten Fire Metal Socket Glow
    glow_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(glow_mask, (7, 7), (w - 8, h - 8), 255, 3, lineType=cv2.LINE_AA)
    
    # Red furnace bloom
    red_blur = cv2.GaussianBlur(glow_mask, (25, 25), 0) / 255.0
    canvas[:, :, 0] = np.clip(canvas[:, :, 0] + red_blur * 10, 0, 255).astype(np.uint8)
    canvas[:, :, 1] = np.clip(canvas[:, :, 1] + red_blur * 50, 0, 255).astype(np.uint8)
    canvas[:, :, 2] = np.clip(canvas[:, :, 2] + red_blur * 210, 0, 255).astype(np.uint8)
    
    # Orange molten radiance
    orange_blur = cv2.GaussianBlur(glow_mask, (11, 11), 0) / 255.0
    canvas[:, :, 0] = np.clip(canvas[:, :, 0] + orange_blur * 20, 0, 255).astype(np.uint8)
    canvas[:, :, 1] = np.clip(canvas[:, :, 1] + orange_blur * 130, 0, 255).astype(np.uint8)
    canvas[:, :, 2] = np.clip(canvas[:, :, 2] + orange_blur * 255, 0, 255).astype(np.uint8)
    
    # White-hot inner rim line
    cv2.rectangle(canvas, (8, 8), (w - 9, h - 9), SIM_HOT_YELLOW, 1, lineType=cv2.LINE_AA)
    
    # Corner hex bolts
    for bx, by in [(13, 13), (w - 14, 13), (13, h - 14), (w - 14, h - 14)]:
        cv2.circle(canvas, (bx, by), 3, (120, 130, 145), -1, lineType=cv2.LINE_AA)
        cv2.circle(canvas, (bx, by), 1, (10, 10, 15), -1, lineType=cv2.LINE_AA)

    return canvas

def create_gta_keycap_base(w=186, h=186):
    """Vice City neon gradient keycap base."""
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / float(h)
        b = int(36 * (1 - t) + 60 * t)
        g = int(8 * (1 - t) + 12 * t)
        r = int(22 * (1 - t) + 43 * t)
        canvas[y, :] = (b, g, r)
    cv2.rectangle(canvas, (2, 2), (w - 3, h - 3), (28, 10, 36), 3, lineType=cv2.LINE_AA)
    cv2.rectangle(canvas, (5, 5), (w - 6, h - 6), (216, 34, 118), 2, lineType=cv2.LINE_AA)
    cv2.rectangle(canvas, (7, 7), (w - 8, h - 8), (108, 17, 59), 1, lineType=cv2.LINE_AA)
    return canvas

def draw_camera_geometry(canvas, center=(93, 72), is_paused=True, theme="simforge", has_label=True):
    """
    Renders the exact video camera geometry from the user's screenshot:
    - Rounded rectangular video camera housing
    - Angled trapezoid lens cone on the right
    - Inside camera body:
      - If is_paused: Two bold vertical pause bars '||'
      - If active: Solid glowing record indicator circle
    """
    cx, cy = center
    sc = 0.95 if has_label else 1.25
    
    # Palette selection based on theme
    if theme == "simforge":
        c_body = (245, 248, 255)      # Metallic warm white
        c_glow = SIM_ORANGE            # Molten amber glow
        c_inner = SIM_HOT_YELLOW if is_paused else (30, 40, 255) # Yellow pause or Red active
        c_lens = SIM_FIRE
    else: # gta6_vice
        c_body = (255, 255, 255)
        c_glow = (255, 240, 0)         # Cyan glow
        c_inner = (216, 34, 118) if is_paused else (40, 40, 255) # Magenta pause or Red active
        c_lens = (255, 240, 0)
        
    mask = np.zeros(canvas.shape[:2], dtype=np.uint8)
    
    def draw_elements(target, is_mask=False):
        c_w = 255 if is_mask else c_body
        c_g_color = 255 if is_mask else c_glow
        c_in = 255 if is_mask else c_inner
        c_ln = 255 if is_mask else c_lens
        
        # Dimensions matching the screenshot
        bw = int(58 * sc)  # Camera body width
        bh = int(48 * sc)  # Camera body height
        bx = int(cx - 38 * sc)
        by = int(cy - bh // 2)
        
        # 1. Camera Body (Rounded rectangle)
        cv2.rectangle(target, (bx, by), (bx + bw, by + bh), c_w, int(6 * sc), lineType=cv2.LINE_AA)
        
        # 2. Lens Cone (Trapezoid on the right)
        lx1 = bx + bw
        lx2 = int(cx + 40 * sc)
        pts_lens = np.array([
            [lx1, int(cy - 12 * sc)],
            [lx2, int(cy - 26 * sc)],
            [lx2, int(cy + 26 * sc)],
            [lx1, int(cy + 12 * sc)]
        ], np.int32)
        cv2.fillPoly(target, [pts_lens], c_ln, lineType=cv2.LINE_AA)
        cv2.polylines(target, [pts_lens], True, c_w, int(3 * sc), lineType=cv2.LINE_AA)
        
        # 3. Inside the Camera Body:
        body_cx = bx + bw // 2
        body_cy = cy
        
        if is_paused:
            # Two vertical pause bars '||' (Exact match to screenshot!)
            bar_w = int(6 * sc)
            bar_h = int(22 * sc)
            gap = int(7 * sc)
            b1_x = body_cx - gap//2 - bar_w
            b2_x = body_cx + gap//2
            cv2.rectangle(target, (b1_x, int(body_cy - bar_h//2)), (b1_x + bar_w, int(body_cy + bar_h//2)), c_in, -1, lineType=cv2.LINE_AA)
            cv2.rectangle(target, (b2_x, int(body_cy - bar_h//2)), (b2_x + bar_w, int(body_cy + bar_h//2)), c_in, -1, lineType=cv2.LINE_AA)
        else:
            # Active Recording Dot (Glowing Record Tally)
            cv2.circle(target, (body_cx, body_cy), int(10 * sc), c_in, -1, lineType=cv2.LINE_AA)
            cv2.circle(target, (body_cx, body_cy), int(4 * sc), (255, 255, 255), -1, lineType=cv2.LINE_AA)

    # Render soft luminous glow
    draw_elements(mask, is_mask=True)
    mask_blur = cv2.GaussianBlur(mask, (19, 19), 0) / 255.0
    
    if theme == "simforge":
        canvas[:, :, 0] = np.clip(canvas[:, :, 0] + mask_blur * 20, 0, 255).astype(np.uint8)
        canvas[:, :, 1] = np.clip(canvas[:, :, 1] + mask_blur * 120, 0, 255).astype(np.uint8)
        canvas[:, :, 2] = np.clip(canvas[:, :, 2] + mask_blur * 255, 0, 255).astype(np.uint8)
    else:
        canvas[:, :, 0] = np.clip(canvas[:, :, 0] + mask_blur * 230, 0, 255).astype(np.uint8)
        canvas[:, :, 1] = np.clip(canvas[:, :, 1] + mask_blur * 150, 0, 255).astype(np.uint8)
        canvas[:, :, 2] = np.clip(canvas[:, :, 2] + mask_blur * 80, 0, 255).astype(np.uint8)

    # Render crisp vector lines
    draw_elements(canvas, is_mask=False)
    return canvas

def render_simforge_record_keycap(name, is_paused=True, has_label=True):
    """Renders complete SimForge Fire Metal keycap."""
    canvas = create_simforge_keycap_base(KEY_SIZE, KEY_SIZE)
    center = (KEY_SIZE // 2, 70) if has_label else (KEY_SIZE // 2, KEY_SIZE // 2)
    draw_camera_geometry(canvas, center=center, is_paused=is_paused, theme="simforge", has_label=has_label)
    
    if has_label:
        # Sleek dark industrial badge capsule
        cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 12), (12, 13, 16), -1)
        cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 12), (0, 110, 220), 1, lineType=cv2.LINE_AA)
        
        font_scale = 0.38 if len(name) <= 10 else 0.32
        (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)
        tx = (KEY_SIZE - tw) // 2
        ty = KEY_SIZE - 20
        cv2.putText(canvas, name, (tx + 1, ty + 1), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), 2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 1, lineType=cv2.LINE_AA)
        
    return canvas

def render_gta_record_keycap(name, is_paused=True, has_label=True):
    """Renders complete GTA VI Vice City keycap."""
    canvas = create_gta_keycap_base(KEY_SIZE, KEY_SIZE)
    center = (KEY_SIZE // 2, 70) if has_label else (KEY_SIZE // 2, KEY_SIZE // 2)
    draw_camera_geometry(canvas, center=center, is_paused=is_paused, theme="gta6_vice", has_label=has_label)
    
    if has_label:
        cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 12), (16, 6, 22), -1)
        cv2.rectangle(canvas, (14, KEY_SIZE - 36), (KEY_SIZE - 15, KEY_SIZE - 12), (90, 20, 140), 1, lineType=cv2.LINE_AA)
        
        font_scale = 0.38 if len(name) <= 10 else 0.32
        (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)
        tx = (KEY_SIZE - tw) // 2
        ty = KEY_SIZE - 20
        cv2.putText(canvas, name, (tx + 1, ty + 1), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), 2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, name, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 1, lineType=cv2.LINE_AA)
        
    return canvas

def render_transparent_record_glyph(is_paused=True, theme="simforge"):
    """Renders isolated vector glyph on 32-bit RGBA canvas."""
    rgba = np.zeros((KEY_SIZE, KEY_SIZE, 4), dtype=np.uint8)
    temp_rgb = np.zeros((KEY_SIZE, KEY_SIZE, 3), dtype=np.uint8)
    draw_camera_geometry(temp_rgb, center=(KEY_SIZE//2, KEY_SIZE//2), is_paused=is_paused, theme=theme, has_label=False)
    
    gray = cv2.cvtColor(temp_rgb, cv2.COLOR_BGR2GRAY)
    mask = (gray > 15).astype(np.uint8) * 255
    mask_blur = cv2.GaussianBlur(mask, (3, 3), 0.5)
    
    rgba[:, :, :3] = temp_rgb
    rgba[:, :, 3] = mask_blur
    return rgba

def enhance_2x(img):
    """Lanczos 2x super-sampling with unsharp masking."""
    h, w = img.shape[:2]
    upscaled = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 1.8)
    return cv2.addWeighted(upscaled, 1.25, gaussian, -0.25, 0)

def main():
    print("Generating SimForge Fire Metal Record Pause Icon Suite...")
    
    # 1. SimForge Record Pause (State 2: Paused '||')
    sim_pause = render_simforge_record_keycap("REC PAUSE", is_paused=True, has_label=True)
    cv2.imwrite(os.path.join(SIM_BUTTONS_DIR, "14_obs_record_pause.png"), sim_pause)
    cv2.imwrite(os.path.join(SIM_BUTTONS_ROOT, "14_obs_record_pause.png"), sim_pause)
    
    sim_pause_2x = enhance_2x(sim_pause)
    cv2.imwrite(os.path.join(SIM_HIDPI_DIR, "14_obs_record_pause_2x.png"), sim_pause_2x)
    cv2.imwrite(os.path.join(SIM_ROOT_HIDPI, "14_obs_record_pause_2x.png"), sim_pause_2x)
    
    sim_pause_glyph = render_transparent_record_glyph(is_paused=True, theme="simforge")
    cv2.imwrite(os.path.join(SIM_TRANS_DIR, "icon_14_obs_record_pause.png"), sim_pause_glyph)
    cv2.imwrite(os.path.join(SIM_ROOT_TRANS, "icon_14_obs_record_pause.png"), sim_pause_glyph)
    
    # Hero unlabelled version
    sim_pause_hero = render_simforge_record_keycap("REC PAUSE", is_paused=True, has_label=False)
    cv2.imwrite(os.path.join(SIM_BUTTONS_DIR, "14_obs_record_pause_hero.png"), sim_pause_hero)
    cv2.imwrite(os.path.join(SIM_BUTTONS_ROOT, "14_obs_record_pause_hero.png"), sim_pause_hero)
    cv2.imwrite(os.path.join(SIM_HIDPI_DIR, "14_obs_record_pause_hero_2x.png"), enhance_2x(sim_pause_hero))
    cv2.imwrite(os.path.join(SIM_ROOT_HIDPI, "14_obs_record_pause_hero_2x.png"), enhance_2x(sim_pause_hero))
    
    # 2. SimForge Record Active (State 1: Active recording)
    sim_active = render_simforge_record_keycap("RECORDING", is_paused=False, has_label=True)
    cv2.imwrite(os.path.join(SIM_BUTTONS_DIR, "15_obs_record_active.png"), sim_active)
    cv2.imwrite(os.path.join(SIM_BUTTONS_ROOT, "15_obs_record_active.png"), sim_active)
    
    sim_active_2x = enhance_2x(sim_active)
    cv2.imwrite(os.path.join(SIM_HIDPI_DIR, "15_obs_record_active_2x.png"), sim_active_2x)
    cv2.imwrite(os.path.join(SIM_ROOT_HIDPI, "15_obs_record_active_2x.png"), sim_active_2x)
    
    sim_active_glyph = render_transparent_record_glyph(is_paused=False, theme="simforge")
    cv2.imwrite(os.path.join(SIM_TRANS_DIR, "icon_15_obs_record_active.png"), sim_active_glyph)
    cv2.imwrite(os.path.join(SIM_ROOT_TRANS, "icon_15_obs_record_active.png"), sim_active_glyph)

    sim_active_hero = render_simforge_record_keycap("RECORDING", is_paused=False, has_label=False)
    cv2.imwrite(os.path.join(SIM_BUTTONS_DIR, "15_obs_record_active_hero.png"), sim_active_hero)
    cv2.imwrite(os.path.join(SIM_BUTTONS_ROOT, "15_obs_record_active_hero.png"), sim_active_hero)
    cv2.imwrite(os.path.join(SIM_HIDPI_DIR, "15_obs_record_active_hero_2x.png"), enhance_2x(sim_active_hero))
    cv2.imwrite(os.path.join(SIM_ROOT_HIDPI, "15_obs_record_active_hero_2x.png"), enhance_2x(sim_active_hero))
    
    print("SimForge Record Pause icons rendered successfully.")
    
    # 3. Companion GTA VI Vice City Record Pause & Active editions
    gta_pause = render_gta_record_keycap("REC PAUSE", is_paused=True, has_label=True)
    cv2.imwrite(os.path.join(GTA_KEY_DIR, "49_obs_record_pause.png"), gta_pause)
    cv2.imwrite(os.path.join(GTA_HIDPI_DIR, "49_obs_record_pause_2x.png"), enhance_2x(gta_pause))
    cv2.imwrite(os.path.join(GTA_TRANS_DIR, "glyph_49_obs_record_pause.png"), render_transparent_record_glyph(is_paused=True, theme="gta6_vice"))
    
    gta_active = render_gta_record_keycap("RECORDING", is_paused=False, has_label=True)
    cv2.imwrite(os.path.join(GTA_KEY_DIR, "50_obs_record_active.png"), gta_active)
    cv2.imwrite(os.path.join(GTA_HIDPI_DIR, "50_obs_record_active_2x.png"), enhance_2x(gta_active))
    cv2.imwrite(os.path.join(GTA_TRANS_DIR, "glyph_50_obs_record_active.png"), render_transparent_record_glyph(is_paused=False, theme="gta6_vice"))
    
    print("GTA VI Record Pause icons rendered successfully.")

if __name__ == "__main__":
    main()
