"""
Tech Impact Stream Deck Panel Processor
Detects, marks, extracts, and renders high-quality assets:
- Marked/annotated master images with coordinate callouts and HUD legend
- Individual buttons and keycaps (standard, 2x High-DPI, and true-square 186x186/372x372 Stream Deck format)
- Isolated icon glyphs with alpha transparency (bezel-free, preserving cosmic neon blue, violet, magenta, and amber glow)
- System telemetry display unit and individual CPU, RAM, and GPU sub-meters
- Tech Impact branding: stylized 'T' axe emblem, futuristic wordmark, and 1024x1024 hero battle-axe assets
- Cosmic nebula chassis faceplates, spotless modular empty template, glowing neon frame, and space textures
"""

import os
import shutil
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PANEL_IMAGE_PATH = os.path.join(BASE_DIR, "Tech Impact Stream Deck Panel.jpg")
HERO_IMAGE_PATH = os.path.join(BASE_DIR, "Tech Impact Hero Emblem.jpg")

THEME_DIR = os.path.join(BASE_DIR, "output", "themes", "tech_impact")
THEME_ALT_DIR = os.path.join(BASE_DIR, "output", "themes", "Tech Impact")

DIRS = {
    "annotated": os.path.join(THEME_DIR, "annotated"),
    "buttons": os.path.join(THEME_DIR, "buttons"),
    "buttons_hidpi": os.path.join(THEME_DIR, "buttons", "high_dpi_2x"),
    "buttons_sq": os.path.join(THEME_DIR, "buttons", "square_deck_format"),
    "icons_trans": os.path.join(THEME_DIR, "icons_isolated", "transparent"),
    "icons_slate": os.path.join(THEME_DIR, "icons_isolated", "dark_slate"),
    "icons_hidpi": os.path.join(THEME_DIR, "icons_isolated", "high_dpi_2x"),
    "display": os.path.join(THEME_DIR, "display_panel"),
    "display_hidpi": os.path.join(THEME_DIR, "display_panel", "high_dpi_2x"),
    "branding": os.path.join(THEME_DIR, "branding"),
    "branding_hidpi": os.path.join(THEME_DIR, "branding", "high_dpi_2x"),
    "backgrounds": os.path.join(THEME_DIR, "backgrounds_and_chassis"),
    "backgrounds_hidpi": os.path.join(THEME_DIR, "backgrounds_and_chassis", "high_dpi_2x"),
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Category styling: (Box Color BGR, Fill Color BGRA, Label Tag)
CATEGORY_STYLES = {
    "Button": {"box": (255, 185, 0), "fill": (255, 185, 0, 35), "tag": "BTN"},        # Electric Cyan / Sky Blue
    "Display": {"box": (50, 215, 60), "fill": (50, 215, 60, 35), "tag": "DSP"},         # Lime Green
    "Telemetry": {"box": (120, 255, 0), "fill": (120, 255, 0, 35), "tag": "MET"},       # Chartreuse
    "Branding": {"box": (0, 215, 255), "fill": (0, 215, 255, 40), "tag": "LOGO"},       # Amber Gold
    "Chassis": {"box": (230, 130, 180), "fill": (230, 130, 180, 25), "tag": "CHAS"},    # Violet / Indigo
    "Accent": {"box": (0, 140, 255), "fill": (0, 140, 255, 45), "tag": "NEON"},         # Plasma Orange
    "Texture": {"box": (220, 180, 80), "fill": (220, 180, 80, 35), "tag": "TEX"},      # Cosmic Slate
}

# Individually pixel-verified element bounding boxes for 1024x630 Tech Impact panel
ELEMENTS = [
    # Row 1 Buttons (y=101..233)
    {"id": "BTN-01", "name": "Save Keycap", "cat": "Button", "box": [105, 101, 250, 233], "type": "rect", "file": "01_btn_save"},
    {"id": "BTN-02", "name": "Save As Keycap", "cat": "Button", "box": [273, 101, 418, 233], "type": "rect", "file": "02_btn_save_as"},
    {"id": "BTN-03", "name": "Radial Starburst / Particle Spark", "cat": "Button", "box": [442, 101, 586, 233], "type": "rect", "file": "03_btn_starburst_spark"},
    {"id": "BTN-04", "name": "Chromatic AI Sparkle (Gemini)", "cat": "Button", "box": [610, 101, 754, 233], "type": "rect", "file": "04_btn_chromatic_sparkle"},
    {"id": "BTN-05", "name": "Gradient Sine Wave / Arc", "cat": "Button", "box": [777, 101, 922, 233], "type": "rect", "file": "05_btn_gradient_wave_arc"},

    # Row 2 Buttons (y=249..382)
    {"id": "BTN-06", "name": "Tab Navigation", "cat": "Button", "box": [107, 249, 252, 382], "type": "rect", "file": "06_btn_tab"},
    {"id": "BTN-07", "name": "Backspace Keycap", "cat": "Button", "box": [275, 249, 419, 382], "type": "rect", "file": "07_btn_backspace"},
    {"id": "BTN-08", "name": "ChatGPT / AI Swirl", "cat": "Button", "box": [443, 249, 586, 382], "type": "rect", "file": "08_btn_chatgpt_swirl"},
    {"id": "BTN-09", "name": "Copilot / AI Robot Avatar", "cat": "Button", "box": [610, 249, 754, 382], "type": "rect", "file": "09_btn_copilot_avatar"},
    {"id": "BTN-10", "name": "Crystal Isometric Cube", "cat": "Button", "box": [778, 249, 922, 382], "type": "rect", "file": "10_btn_crystal_cube"},

    # Row 3 Buttons (y=398..531)
    {"id": "BTN-11", "name": "Num Enter Keycap", "cat": "Button", "box": [107, 398, 252, 531], "type": "rect", "file": "11_btn_num_enter"},
    {"id": "BTN-12", "name": "Ctrl+Win Macro", "cat": "Button", "box": [275, 398, 420, 531], "type": "rect", "file": "12_btn_ctrl_win"},
    {"id": "BTN-13", "name": "Windows Key", "cat": "Button", "box": [442, 398, 587, 531], "type": "rect", "file": "13_btn_win"},

    # Row 3 Telemetry Display Unit & Meters (vertical dividers at x=714 and x=816)
    {"id": "DSP-01", "name": "System Telemetry Display Unit", "cat": "Display", "box": [604, 396, 926, 532], "type": "rect", "file": "01_telemetry_display_unit"},
    {"id": "MET-01", "name": "CPU Meter (9%)", "cat": "Telemetry", "box": [618, 411, 712, 517], "type": "rect", "file": "02_telemetry_cpu_9pct"},
    {"id": "MET-02", "name": "RAM Meter (56%)", "cat": "Telemetry", "box": [716, 411, 814, 517], "type": "rect", "file": "03_telemetry_ram_56pct"},
    {"id": "MET-03", "name": "GPU Meter (23%)", "cat": "Telemetry", "box": [818, 411, 912, 517], "type": "rect", "file": "04_telemetry_gpu_23pct"},

    # Branding
    {"id": "BRD-01", "name": "Tech Impact Header Banner", "cat": "Branding", "box": [328, 6, 700, 78], "type": "rect", "file": "01_tech_impact_header_banner"},
    {"id": "BRD-02", "name": "Tech Impact Header 'T' Emblem", "cat": "Branding", "box": [330, 6, 408, 76], "type": "rect", "file": "02_tech_impact_header_emblem"},
    {"id": "BRD-03", "name": "Tech Impact Futuristic Wordmark", "cat": "Branding", "box": [410, 22, 698, 74], "type": "rect", "file": "03_tech_impact_wordmark"},

    # Backgrounds & Chassis Elements
    {"id": "BKG-01", "name": "Tech Impact Full Chassis Master", "cat": "Chassis", "box": [0, 0, 1024, 630], "type": "rect", "file": "01_tech_impact_full_chassis"},
    {"id": "BKG-02", "name": "Clean Modular Deck Template", "cat": "Chassis", "box": [0, 0, 1024, 630], "type": "rect", "file": "02_tech_impact_modular_template"},
    {"id": "BKG-03", "name": "Outer Glowing Neon Frame", "cat": "Accent", "box": [8, 78, 1016, 603], "type": "rect", "file": "03_outer_glowing_neon_frame"},
    {"id": "BKG-04", "name": "Cosmic Nebula Texture Top-Left", "cat": "Texture", "box": [0, 0, 240, 110], "type": "rect", "file": "04_cosmic_nebula_texture_tl"},
    {"id": "BKG-05", "name": "Deep Space Blue Gas Cloud", "cat": "Texture", "box": [780, 0, 1024, 110], "type": "rect", "file": "05_deep_space_blue_nebula_tr"},
    {"id": "BKG-06", "name": "Cosmic Amber Plasma Flurry", "cat": "Texture", "box": [0, 490, 95, 625], "type": "rect", "file": "06_cosmic_amber_plasma_bl"},
]


def render_high_dpi(crop, scale=2):
    """Super-samples an image using Lanczos interpolation and subtle unsharp masking."""
    h, w = crop.shape[:2]
    up = cv2.resize(crop, (w * scale, h * scale), interpolation=cv2.INTER_LANCZOS4)
    if crop.ndim == 3 and crop.shape[2] == 4:
        rgb = up[:, :, :3]
        blurred = cv2.GaussianBlur(rgb, (0, 0), 1.0)
        sharpened_rgb = cv2.addWeighted(rgb, 1.22, blurred, -0.22, 0)
        return np.dstack([sharpened_rgb, up[:, :, 3]])
    blurred = cv2.GaussianBlur(up, (0, 0), 1.0)
    return cv2.addWeighted(up, 1.22, blurred, -0.22, 0)


def build_rounded_rect_mask(height, width, inset_x, inset_top, inset_bot, radius):
    """Builds an anti-aliased binary mask (0..255) for an inset rounded rectangle."""
    mask = np.zeros((height, width), dtype=np.uint8)
    x1 = inset_x
    y1 = inset_top
    x2 = max(x1 + 2, width - inset_x - 1)
    y2 = max(y1 + 2, height - inset_bot - 1)
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    cv2.rectangle(mask, (x1 + r, y1), (x2 - r, y2), 255, -1)
    cv2.rectangle(mask, (x1, y1 + r), (x2, y2 - r), 255, -1)
    for cx, cy in [(x1 + r, y1 + r), (x2 - r, y1 + r), (x1 + r, y2 - r), (x2 - r, y2 - r)]:
        cv2.circle(mask, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
    return mask


def make_square_streamdeck_keycap(full_img, box, target_size=186):
    """
    Extracts an undistorted square crop centered on box directly from full_img
    (preserving 1:1 proportions with zero black letterbox bars) and Lanczos4-resizes to target_size.
    """
    H, W = full_img.shape[:2]
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    side = max(x2 - x1, y2 - y1)
    half = side // 2

    sx1 = max(0, cx - half)
    sy1 = max(0, cy - half)
    sx2 = sx1 + side
    sy2 = sy1 + side
    if sx2 > W:
        sx2 = W
        sx1 = max(0, W - side)
    if sy2 > H:
        sy2 = H
        sy1 = max(0, H - side)

    sq = full_img[sy1:sy2, sx1:sx2]
    up = cv2.resize(sq, (target_size, target_size), interpolation=cv2.INTER_LANCZOS4)
    blurred = cv2.GaussianBlur(up, (0, 0), 1.0)
    return cv2.addWeighted(up, 1.18, blurred, -0.18, 0)


def build_asymmetric_rounded_mask(height, width, ix, it, ib, r_top, r_bot):
    """Builds a binary interior mask with independent top and bottom corner radii."""
    mask = np.zeros((height, width), dtype=np.uint8)
    x1, y1 = ix, it
    x2 = max(x1 + 2, width - ix - 1)
    y2 = max(y1 + 2, height - ib - 1)
    rt = min(r_top, (x2 - x1) // 2, (y2 - y1) // 2)
    rb = min(r_bot, (x2 - x1) // 2, (y2 - y1) // 2)
    mid_y = (y1 + y2) // 2

    cv2.rectangle(mask, (x1 + rt, y1), (x2 - rt, mid_y), 255, -1)
    cv2.rectangle(mask, (x1, y1 + rt), (x2, mid_y), 255, -1)
    for cx, cy in [(x1 + rt, y1 + rt), (x2 - rt, y1 + rt)]:
        cv2.circle(mask, (cx, cy), rt, 255, -1, lineType=cv2.LINE_AA)

    cv2.rectangle(mask, (x1 + rb, mid_y), (x2 - rb, y2), 255, -1)
    cv2.rectangle(mask, (x1, mid_y), (x2, y2 - rb), 255, -1)
    for cx, cy in [(x1 + rb, y2 - rb), (x2 - rb, y2 - rb)]:
        cv2.circle(mask, (cx, cy), rb, 255, -1, lineType=cv2.LINE_AA)
    return mask


TECH_GLYPH_OVERRIDES = {
    "BTN-03": {"th": 72.0},
    "BTN-05": {"th": 72.0, "ib": 16, "r_bot": 48, "drop_amber_br": True},
    "BTN-07": {"th": 82.0},
    "BTN-09": {"th": 90.0, "it": 31, "r_top": 36, "fill_holes": True},
    "BTN-10": {"fill_holes": True},
}


def extract_isolated_glyph(crop, el_id=""):
    """
    Extracts the glowing icon and keycap label onto a clean 32-bit transparent RGBA canvas.
    Uses an asymmetric rounded mask, optional amber corner plasma filtering, border-connected
    flare pruning, outer-corner speck removal, and optional hole filling.
    """
    h, w = crop.shape[:2]
    cfg = {
        "ix": 13,
        "it": 12,
        "ib": 14,
        "r_top": 20,
        "r_bot": 44,
        "th": 48.0,
        "prune_border": True,
        "fill_holes": False,
        "drop_amber_br": False,
    }
    cfg.update(TECH_GLYPH_OVERRIDES.get(el_id, {}))

    mask = build_asymmetric_rounded_mask(
        h, w, cfg["ix"], cfg["it"], cfg["ib"], cfg["r_top"], cfg["r_bot"]
    )
    bg_bgr = np.percentile(crop[mask > 200], 15, axis=0).astype(np.float32)
    dist = np.linalg.norm(crop.astype(np.float32) - bg_bgr, axis=2)

    th = cfg["th"]
    fg = ((dist > th) & (mask > 128)).astype(np.uint8)

    if cfg["drop_amber_br"]:
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        y_cut, x_cut = int(h * 0.60), int(w * 0.50)
        amber_br = hsv[y_cut:, x_cut:, 0] <= 42
        fg[y_cut:, x_cut:][amber_br] = 0

    keep = np.zeros_like(fg)
    num, labels, stats, centroids = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if cfg["prune_border"]:
        ring = mask - cv2.erode(mask, np.ones((5, 5), np.uint8), iterations=1)
        for i in range(1, num):
            area = stats[i, cv2.CC_STAT_AREA]
            if area < 6:
                continue
            comp = labels == i
            touches_border = np.any(comp & (ring > 0))
            cx_c, cy_c = centroids[i]
            truly_centered = (w * 0.35 < cx_c < w * 0.65) and (h * 0.35 < cy_c < h * 0.65)
            if touches_border and not truly_centered:
                continue
            in_outer_corner = (cx_c < w * 0.28 or cx_c > w * 0.72) and (cy_c < h * 0.28 or cy_c > h * 0.72)
            if area < 45 and in_outer_corner:
                continue
            keep[comp] = 1
    else:
        for i in range(1, num):
            if stats[i, cv2.CC_STAT_AREA] >= 6:
                keep[labels == i] = 1

    if cfg["fill_holes"]:
        closed = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        inv = (1 - closed).astype(np.uint8) * 255
        ff = inv.copy()
        ff_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        cv2.floodFill(ff, ff_mask, (0, 0), 128)
        holes = (ff == 255).astype(np.uint8)
        keep = np.maximum(keep, holes)

    dil = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    support = cv2.GaussianBlur(dil.astype(np.float32), (5, 5), 1.2)

    low_t = th - 6.0
    high_t = th + 45.0
    soft = np.clip((dist - low_t) / (high_t - low_t), 0.0, 1.0)
    alpha_f = np.clip(np.maximum(soft * support, keep.astype(np.float32)), 0.0, 1.0)
    alpha = cv2.GaussianBlur((alpha_f * 255.0).astype(np.uint8), (3, 3), 0.5)

    b, g, r = cv2.split(crop)
    return cv2.merge([b, g, r, alpha])


def extract_hero_axe_assets(hero_img):
    """Processes the 1024x1024 Tech Impact hero battle-axe emblem."""
    master_path = os.path.join(DIRS["branding"], "04_tech_impact_hero_axe_1024x1024.png")
    cv2.imwrite(master_path, hero_img)

    hsv = cv2.cvtColor(hero_img, cv2.COLOR_BGR2HSV)
    val = hsv[:, :, 2].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    signal = (val * 0.75) + (sat * 0.25)

    alpha = np.clip((signal - 22.0) / (85.0 - 22.0), 0.0, 1.0) * 255.0
    alpha = cv2.GaussianBlur(alpha.astype(np.uint8), (3, 3), 0)

    b, g, r = cv2.split(hero_img)
    rgba = cv2.merge([b, g, r, alpha])
    trans_path = os.path.join(DIRS["branding"], "05_tech_impact_hero_axe_transparent.png")
    cv2.imwrite(trans_path, rgba)

    h, w = hero_img.shape[:2]
    cx, cy = w // 2, h // 2
    rad = int(min(cx, cy) * 0.92)
    circ_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(circ_mask, (cx, cy), rad, 255, -1, lineType=cv2.LINE_AA)
    final_circ_alpha = cv2.bitwise_and(alpha, circ_mask)
    circ_rgba = cv2.merge([b, g, r, final_circ_alpha])
    circ_path = os.path.join(DIRS["branding"], "06_tech_impact_circular_emblem.png")
    cv2.imwrite(circ_path, circ_rgba)

    hero_box = [0, 0, w, h]
    keycap = make_square_streamdeck_keycap(hero_img, hero_box, target_size=186)
    cv2.imwrite(os.path.join(DIRS["buttons"], "00_btn_tech_impact_hero_keycap.png"), keycap)
    keycap_2x = make_square_streamdeck_keycap(hero_img, hero_box, target_size=372)
    cv2.imwrite(os.path.join(DIRS["buttons_hidpi"], "00_btn_tech_impact_hero_keycap_2x.png"), keycap_2x)
    print("Hero battle-axe assets extracted and rendered.")


def _place_pill(canvas, tag_text, x1, y1, color):
    """Draws a crisp dark ID pill clamped strictly inside image bounds."""
    img_h, img_w = canvas.shape[:2]
    (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
    pw = tw + 10
    ph = th + 8
    px1 = max(2, min(x1, img_w - pw - 2))
    py1 = max(2, min(y1, img_h - ph - 2))
    px2 = px1 + pw
    py2 = py1 + ph

    cv2.rectangle(canvas, (px1, py1), (px2, py2), (12, 10, 18), -1)
    cv2.rectangle(canvas, (px1, py1), (px2, py2), color, 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, tag_text, (px1 + 5, py2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, lineType=cv2.LINE_AA)


def generate_marked_overview(img):
    """Generates the marked overview master image with non-overlapping boxes and clamped ID pills."""
    annotated = img.copy()
    overlay = annotated.copy()

    overview_elements = [
        el for el in ELEMENTS
        if el["cat"] != "Texture" and el["id"] not in ("BKG-01", "BKG-02")
    ]

    for el in overview_elements:
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        x1, y1, x2, y2 = el["box"]
        cv2.rectangle(overlay, (x1, y1), (x2, y2), style["box"], -1)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), style["box"], 2, lineType=cv2.LINE_AA)

    cv2.addWeighted(overlay, 0.20, annotated, 0.80, 0, annotated)

    for el in overview_elements:
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        x1, y1, x2, y2 = el["box"]
        tag_text = el["id"]
        (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        pw = tw + 10
        ph = th + 8

        if el["cat"] == "Telemetry":
            px, py = x1 + (x2 - x1 - pw) // 2, 535
        elif el["id"] == "BRD-01":
            px, py = x1 + 2, y2 - ph - 2
        elif el["id"] == "BRD-02":
            px, py = x1 + 2, 2
        elif el["id"] == "BRD-03":
            px, py = x2 - pw - 2, 2
        elif el["id"] == "BKG-03":
            px, py = x1 + 4, y1 - ph - 2
        else:
            px, py = x1, y1 - ph - 2

        _place_pill(annotated, tag_text, px, py, style["box"])

    return annotated


def generate_marked_with_legend(img):
    """
    Creates an expanded telemetry overview canvas featuring the annotated panel on the left
    and a full unclipped industrial HUD coordinate telemetry legend on the right.
    """
    annotated_panel = generate_marked_overview(img)
    ph, pw = annotated_panel.shape[:2]

    header_y = 35
    legend_w = 780
    total_w = pw + legend_w
    cat_y = header_y + 60
    cat_x = pw + 25
    for cat_name in CATEGORY_STYLES:
        if cat_name == "Texture":
            continue
        cat_x += 108
        if cat_x > total_w - 110:
            cat_x = pw + 25
            cat_y += 22

    table_top = cat_y + 36
    row_step = 23
    needed_h = table_top + 32 + len(ELEMENTS) * row_step + 24
    total_h = max(ph, needed_h)

    canvas = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    canvas[:] = (10, 8, 14)

    canvas[0:ph, 0:pw] = annotated_panel
    cv2.line(canvas, (pw, 0), (pw, total_h), (55, 45, 75), 2)

    header_x = pw + 25
    cv2.putText(canvas, "TECH IMPACT COSMIC SUITE MAPPING", (header_x, header_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 215, 255), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, f"Total Elements Mapped: {len(ELEMENTS)} | Master Resolution: {pw}x{ph}px", (header_x, header_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 170, 195), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, header_y + 36), (total_w - 25, header_y + 36), (65, 55, 85), 1)

    cat_y_draw = header_y + 60
    cat_x_draw = header_x
    for cat_name, style in CATEGORY_STYLES.items():
        if cat_name == "Texture":
            continue
        cv2.rectangle(canvas, (cat_x_draw, cat_y_draw - 12), (cat_x_draw + 14, cat_y_draw + 2), style["box"], -1)
        cv2.putText(canvas, cat_name, (cat_x_draw + 20, cat_y_draw), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (225, 230, 240), 1, lineType=cv2.LINE_AA)
        cat_x_draw += 108
        if cat_x_draw > total_w - 110:
            cat_x_draw = header_x
            cat_y_draw += 22

    cv2.line(canvas, (header_x, cat_y_draw + 15), (total_w - 25, cat_y_draw + 15), (65, 55, 85), 1)

    cv2.putText(canvas, "ID", (header_x + 5, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ELEMENT NAME", (header_x + 85, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "CATEGORY", (header_x + 335, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "BOUNDS (X, Y, WxH)", (header_x + 470, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, table_top + 10), (total_w - 25, table_top + 10), (55, 45, 75), 1)

    row_y = table_top + 30
    for el in ELEMENTS:
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        box = el["box"]
        w = box[2] - box[0]
        h = box[3] - box[1]
        coords_str = f"[{box[0]}, {box[1]}, {w}x{h}]"

        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), (22, 18, 30), -1)
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), style["box"], 1)
        cv2.putText(canvas, el["id"], (header_x + 8, row_y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.40, style["box"], 1, lineType=cv2.LINE_AA)

        cv2.putText(canvas, el["name"], (header_x + 85, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (245, 245, 250), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, el["cat"], (header_x + 335, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.39, (185, 195, 210), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, coords_str, (header_x + 470, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 225, 255), 1, lineType=cv2.LINE_AA)

        row_y += row_step

    return canvas


def generate_clean_modular_chassis(img):
    """
    Generates a spotless cosmic stream deck chassis background plate by replacing each button's
    interior rounded face with a deep cosmic navy-indigo gradient while preserving 100% of
    the glowing blue, purple, and gold outer keycap bezels.
    """
    clean = img.copy()
    rng = np.random.default_rng(42)

    tl_bgr = np.array([[[28.0, 10.0, 8.0]]], dtype=np.float32)
    mid_bgr = np.array([[[20.0, 8.0, 14.0]]], dtype=np.float32)
    br_bgr = np.array([[[14.0, 12.0, 24.0]]], dtype=np.float32)

    for el in ELEMENTS:
        if el["cat"] != "Button":
            continue
        x1, y1, x2, y2 = el["box"]
        bw, bh = x2 - x1, y2 - y1

        mask = build_rounded_rect_mask(bh, bw, inset_x=14, inset_top=14, inset_bot=16, radius=20)
        alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (11, 11), 3.0)[:, :, np.newaxis]

        ty = np.linspace(0.0, 1.0, bh, dtype=np.float32)[:, np.newaxis, np.newaxis]
        tx = np.linspace(0.0, 1.0, bw, dtype=np.float32)[np.newaxis, :, np.newaxis]
        diag = 0.55 * ty + 0.45 * tx
        synth = np.where(
            diag < 0.5,
            tl_bgr * (1.0 - diag * 2.0) + mid_bgr * (diag * 2.0),
            mid_bgr * (1.0 - (diag - 0.5) * 2.0) + br_bgr * ((diag - 0.5) * 2.0),
        )
        synth += rng.normal(0.0, 1.6, (bh, bw, 3)).astype(np.float32)
        synth = np.clip(synth, 0, 255)

        orig = clean[y1:y2, x1:x2].astype(np.float32)
        blended = orig * (1.0 - alpha) + synth * alpha
        clean[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)

    return clean


def sync_to_alt_theme_dir():
    """Synchronizes output/themes/tech_impact to output/themes/Tech Impact cleanly."""
    if os.path.exists(THEME_ALT_DIR):
        for item in os.listdir(THEME_DIR):
            s = os.path.join(THEME_DIR, item)
            d = os.path.join(THEME_ALT_DIR, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print("Synchronized assets to Tech Impact directory.")


def main():
    print(f"Loading Tech Impact Stream Deck Panel: {PANEL_IMAGE_PATH}")
    img = cv2.imread(PANEL_IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {PANEL_IMAGE_PATH}")

    hero_img = cv2.imread(HERO_IMAGE_PATH)
    if hero_img is None:
        raise FileNotFoundError(f"Could not load hero emblem at {HERO_IMAGE_PATH}")

    print(f"Panel dimensions: {img.shape[1]}x{img.shape[0]} px")
    print(f"Hero logo dimensions: {hero_img.shape[1]}x{hero_img.shape[0]} px")

    # 1. Annotated Master Images
    print("Generating Annotated Master Images...")
    marked_overview = generate_marked_overview(img)
    cv2.imwrite(os.path.join(DIRS["annotated"], "marked_panel_overview.png"), marked_overview)

    marked_legend = generate_marked_with_legend(img)
    cv2.imwrite(os.path.join(DIRS["annotated"], "marked_panel_with_legend.png"), marked_legend)
    print("Annotated Master Images rendered successfully.")

    # 2. Extract Hero Battle-Axe Assets
    print("Extracting Hero Battle-Axe Assets...")
    extract_hero_axe_assets(hero_img)

    # 3. Extract and Render All Elements
    print("Extracting individual assets and generating high-DPI renders...")
    for el in ELEMENTS:
        box = el["box"]
        x1, y1, x2, y2 = box
        crop = img[y1:y2, x1:x2]
        file_stem = el["file"]
        cat = el["cat"]

        crop_2x = render_high_dpi(crop, scale=2)

        if cat == "Button":
            # 1x and 2x keycaps
            cv2.imwrite(os.path.join(DIRS["buttons"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)

            # True-square Stream Deck keycap format (186x186 and 372x372 2x)
            crop_sq = make_square_streamdeck_keycap(img, box, target_size=186)
            crop_sq_2x = make_square_streamdeck_keycap(img, box, target_size=372)
            cv2.imwrite(os.path.join(DIRS["buttons_sq"], f"{file_stem}_sq186.png"), crop_sq)
            cv2.imwrite(os.path.join(DIRS["buttons_sq"], f"{file_stem}_sq372.png"), crop_sq_2x)

            # Isolated Transparent Glyphs (bezel-free)
            glyph_rgba = extract_isolated_glyph(crop, el["id"])
            cv2.imwrite(os.path.join(DIRS["icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)
            glyph_2x = render_high_dpi(glyph_rgba, scale=2)
            cv2.imwrite(os.path.join(DIRS["icons_hidpi"], f"icon_{file_stem}_2x.png"), glyph_2x)

            # Dark slate backing
            slate_bg = np.full((crop.shape[0], crop.shape[1], 3), (20, 16, 24), dtype=np.uint8)
            alpha = (glyph_rgba[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]
            slate_composite = (glyph_rgba[:, :, :3].astype(np.float32) * alpha + slate_bg.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
            cv2.imwrite(os.path.join(DIRS["icons_slate"], f"slate_{file_stem}.png"), slate_composite)

        elif cat in ["Display", "Telemetry"]:
            cv2.imwrite(os.path.join(DIRS["display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["display_hidpi"], f"{file_stem}_2x.png"), crop_2x)

        elif cat == "Branding":
            cv2.imwrite(os.path.join(DIRS["branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["branding_hidpi"], f"{file_stem}_2x.png"), crop_2x)

        elif cat in ["Chassis", "Accent", "Texture"]:
            if el["id"] == "BKG-02":
                continue
            cv2.imwrite(os.path.join(DIRS["backgrounds"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["backgrounds_hidpi"], f"{file_stem}_2x.png"), crop_2x)

    # 4. Clean Modular Deck Template
    print("Generating Clean Modular Deck Template...")
    clean_chassis = generate_clean_modular_chassis(img)
    cv2.imwrite(os.path.join(DIRS["backgrounds"], "02_tech_impact_modular_template.png"), clean_chassis)
    clean_2x = render_high_dpi(clean_chassis, scale=2)
    cv2.imwrite(os.path.join(DIRS["backgrounds_hidpi"], "02_tech_impact_modular_template_2x.png"), clean_2x)

    # 5. Mirror to Tech Impact alt directory
    sync_to_alt_theme_dir()

    print("All Tech Impact assets processed, extracted, and rendered successfully!")


if __name__ == "__main__":
    main()
