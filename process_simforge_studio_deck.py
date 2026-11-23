"""
SimForge Studio 15-Key Stream Deck Panel Processor
Detects, marks, extracts, and renders high-quality assets:
- Marked/annotated master images with coordinate callouts and HUD legend
- Individual buttons and keycaps (standard, 2x High-DPI, and true-square 186x186/372x372 Stream Deck format)
- Isolated icon glyphs with alpha transparency (bezel-free, molten glow preserved)
- Circular Anvil Emblem with anti-aliased circular alpha transparency
- Telemetry display screen and individual CPU, RAM, and GPU sub-meters
- Industrial chassis faceplates, spotless modular empty template, hazard vents, hex bolts, and textures
"""

import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "SimForge Stream Deck Studio 15-Key.jpg")
SIMFORGE_THEME_DIR = os.path.join(BASE_DIR, "output", "themes", "simforge")
GENERAL_OUTPUT_DIR = os.path.join(BASE_DIR, "output")

DIRS = {
    # Theme specific directories
    "sim_annotated": os.path.join(SIMFORGE_THEME_DIR, "annotated"),
    "sim_buttons": os.path.join(SIMFORGE_THEME_DIR, "buttons"),
    "sim_buttons_hidpi": os.path.join(SIMFORGE_THEME_DIR, "buttons", "high_dpi_2x"),
    "sim_buttons_sq": os.path.join(SIMFORGE_THEME_DIR, "buttons", "square_deck_format"),
    "sim_icons_trans": os.path.join(SIMFORGE_THEME_DIR, "icons_isolated", "transparent"),
    "sim_icons_slate": os.path.join(SIMFORGE_THEME_DIR, "icons_isolated", "dark_slate"),
    "sim_icons_hidpi": os.path.join(SIMFORGE_THEME_DIR, "icons_isolated", "high_dpi_2x"),
    "sim_display": os.path.join(SIMFORGE_THEME_DIR, "display_panel"),
    "sim_display_hidpi": os.path.join(SIMFORGE_THEME_DIR, "display_panel", "high_dpi_2x"),
    "sim_branding": os.path.join(SIMFORGE_THEME_DIR, "branding"),
    "sim_branding_hidpi": os.path.join(SIMFORGE_THEME_DIR, "branding", "high_dpi_2x"),
    "sim_bkg": os.path.join(SIMFORGE_THEME_DIR, "backgrounds_and_chassis"),
    "sim_bkg_hidpi": os.path.join(SIMFORGE_THEME_DIR, "backgrounds_and_chassis", "high_dpi_2x"),
    # General output mirroring
    "gen_annotated": os.path.join(GENERAL_OUTPUT_DIR, "annotated"),
    "gen_buttons": os.path.join(GENERAL_OUTPUT_DIR, "buttons"),
    "gen_buttons_hidpi": os.path.join(GENERAL_OUTPUT_DIR, "buttons", "high_dpi_2x"),
    "gen_icons_trans": os.path.join(GENERAL_OUTPUT_DIR, "icons_isolated", "transparent"),
    "gen_display": os.path.join(GENERAL_OUTPUT_DIR, "display_panel"),
    "gen_branding": os.path.join(GENERAL_OUTPUT_DIR, "branding"),
    "gen_bkg": os.path.join(GENERAL_OUTPUT_DIR, "backgrounds_and_chassis"),
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Category styling: (Box Color BGR, Fill Color BGRA, Label Tag)
CATEGORY_STYLES = {
    "Button": {"box": (255, 191, 0), "fill": (255, 191, 0, 35), "tag": "BTN"},        # Deep Sky Blue
    "Display": {"box": (50, 205, 50), "fill": (50, 205, 50, 35), "tag": "DSP"},         # Lime Green
    "Telemetry": {"box": (128, 255, 0), "fill": (128, 255, 0, 35), "tag": "MET"},       # Chartreuse
    "Control": {"box": (203, 192, 255), "fill": (203, 192, 255, 40), "tag": "CTL"},     # Orchid / Magenta
    "Branding": {"box": (0, 215, 255), "fill": (0, 215, 255, 40), "tag": "LOGO"},       # Gold / Amber
    "Chassis": {"box": (190, 190, 190), "fill": (190, 190, 190, 20), "tag": "CHAS"},    # Steel Silver
    "Accent": {"box": (0, 128, 255), "fill": (0, 128, 255, 45), "tag": "VENT"},         # Orange Accent
    "Hardware": {"box": (230, 230, 230), "fill": (230, 230, 230, 45), "tag": "BOLT"},  # Pure Silver
    "Texture": {"box": (160, 210, 100), "fill": (160, 210, 100, 35), "tag": "TEX"},    # Aqua Slate
}

# Individually pixel-verified element bounding boxes for 1024x616 panel
ELEMENTS = [
    # Row 1 Buttons (y=38..182)
    {"id": "BTN-16", "name": "Tab Navigation", "cat": "Button", "box": [73, 38, 227, 182], "type": "rect", "file": "16_btn_tab"},
    {"id": "BTN-17", "name": "TrackIR / Sensor Nodes", "cat": "Button", "box": [262, 38, 416, 182], "type": "rect", "file": "17_btn_tracking_nodes"},
    {"id": "BTN-18", "name": "Scene Dual Window", "cat": "Button", "box": [446, 38, 595, 182], "type": "rect", "file": "18_btn_scene_dual_window"},
    {"id": "BTN-19", "name": "Studio Mode Chart", "cat": "Button", "box": [625, 38, 776, 182], "type": "rect", "file": "19_btn_studio_mode_chart"},
    {"id": "BTN-20", "name": "Video Cam Toggle", "cat": "Button", "box": [809, 38, 960, 182], "type": "rect", "file": "20_btn_video_cam"},

    # Row 2 Buttons (y=200..343)
    {"id": "BTN-21", "name": "OBS Studio Logo", "cat": "Button", "box": [73, 200, 228, 343], "type": "rect", "file": "21_btn_obs_studio"},
    {"id": "BTN-22", "name": "Backspace", "cat": "Button", "box": [262, 200, 416, 343], "type": "rect", "file": "22_btn_backspace"},
    {"id": "BTN-23", "name": "Media Play", "cat": "Button", "box": [446, 200, 596, 343], "type": "rect", "file": "23_btn_media_play"},
    {"id": "BTN-24", "name": "Media Pause", "cat": "Button", "box": [625, 200, 777, 343], "type": "rect", "file": "24_btn_media_pause"},
    {"id": "BTN-25", "name": "Replay Buffer", "cat": "Button", "box": [809, 200, 962, 343], "type": "rect", "file": "25_btn_replay_buffer"},

    # Row 3 Buttons (y=361..508)
    {"id": "BTN-26", "name": "Combat Flight Badge", "cat": "Button", "box": [73, 361, 229, 508], "type": "rect", "file": "26_btn_flight_sim_badge"},
    {"id": "BTN-27", "name": "Ctrl+Win Macro", "cat": "Button", "box": [262, 361, 414, 508], "type": "rect", "file": "27_btn_ctrl_win"},

    # Row 3 Central Emblem / Control
    {"id": "EMB-01", "name": "SimForge Anvil Plate", "cat": "Control", "box": [447, 363, 599, 511], "type": "rect", "file": "04_simforge_anvil_plate"},
    {"id": "EMB-02", "name": "SimForge Anvil Badge", "cat": "Control", "box": [455, 368, 591, 504], "center": [523, 436], "radius": 66, "type": "circle", "file": "05_simforge_anvil_badge_circular"},

    # Row 3 Telemetry Display Unit & Meters (vertical dividers at x=748 and x=854)
    {"id": "DSP-05", "name": "Studio Telemetry Unit", "cat": "Display", "box": [624, 364, 972, 510], "type": "rect", "file": "05_studio_telemetry_unit"},
    {"id": "MET-04", "name": "CPU Meter (5%)", "cat": "Telemetry", "box": [640, 381, 746, 493], "type": "rect", "file": "06_telemetry_cpu_5pct"},
    {"id": "MET-05", "name": "RAM Meter (54%)", "cat": "Telemetry", "box": [750, 381, 852, 493], "type": "rect", "file": "07_telemetry_ram_54pct"},
    {"id": "MET-06", "name": "GPU Meter (7%)", "cat": "Telemetry", "box": [856, 381, 958, 493], "type": "rect", "file": "08_telemetry_gpu_7pct"},

    # Branding & Bottom Bevel
    {"id": "BRD-04", "name": "SimForge Chiseled Wordmark", "cat": "Branding", "box": [416, 536, 612, 584], "type": "rect", "file": "06_simforge_chiseled_wordmark"},
    {"id": "BRD-05", "name": "Bottom Deck Control Strip", "cat": "Branding", "box": [215, 532, 815, 594], "type": "rect", "file": "07_bottom_deck_control_strip"},

    # Backgrounds & Chassis Elements
    {"id": "BKG-10", "name": "Studio Chassis Full Faceplate", "cat": "Chassis", "box": [4, 4, 1020, 612], "type": "rect", "file": "10_studio_chassis_full_faceplate"},
    {"id": "BKG-11", "name": "Clean Modular Deck Template", "cat": "Chassis", "box": [4, 4, 1020, 612], "type": "rect", "file": "11_studio_modular_empty_chassis"},
    {"id": "BKG-12", "name": "Top-Left Hazard Chevrons", "cat": "Accent", "box": [155, 8, 265, 36], "type": "rect", "file": "12_top_left_hazard_chevrons"},
    {"id": "BKG-13", "name": "Top-Right Hazard Chevrons", "cat": "Accent", "box": [746, 8, 852, 36], "type": "rect", "file": "13_top_right_hazard_chevrons"},
    {"id": "BKG-14", "name": "Left Hazard Side Vent", "cat": "Accent", "box": [4, 100, 36, 300], "type": "rect", "file": "14_left_hazard_side_vent"},
    {"id": "BKG-15", "name": "Right Hazard Side Vent", "cat": "Accent", "box": [992, 215, 1020, 405], "type": "rect", "file": "15_right_hazard_side_vent"},
    {"id": "BKG-16", "name": "Top-Left Corner Bolt", "cat": "Hardware", "box": [24, 43, 54, 73], "center": [39, 58], "radius": 15, "type": "circle", "file": "16_bolt_top_left"},
    {"id": "BKG-17", "name": "Top-Right Corner Bolt", "cat": "Hardware", "box": [970, 43, 1000, 73], "center": [985, 58], "radius": 15, "type": "circle", "file": "17_bolt_top_right"},
    {"id": "BKG-18", "name": "Bottom-Left Corner Bolt", "cat": "Hardware", "box": [24, 505, 54, 535], "center": [39, 520], "radius": 15, "type": "circle", "file": "18_bolt_bottom_left"},
    {"id": "BKG-19", "name": "Bottom-Right Corner Bolt", "cat": "Hardware", "box": [970, 505, 1000, 535], "center": [985, 520], "radius": 15, "type": "circle", "file": "19_bolt_bottom_right"},
    {"id": "BKG-20", "name": "Industrial Brushed Metal Tile", "cat": "Texture", "box": [34, 195, 66, 345], "type": "rect", "file": "20_studio_forged_metal_tile"},
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
    Takes an undistorted square crop centered on the button directly from full_img
    (preserving true 1:1 circles without black letterbox bars) and resizes with Lanczos4.
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


SIMFORGE_GLYPH_OVERRIDES = {
    "BTN-26": {"fill_holes": True},
    "BTN-27": {"ix": 10, "it": 18, "ib": 30, "r_top": 12, "r_bot": 16, "prune_border": False},
}


def extract_isolated_glyph(crop, el_id=""):
    """
    Extracts the glowing icon and keycap label onto a clean 32-bit transparent RGBA canvas.
    Uses an asymmetric rounded mask, border-connected flare pruning, outer-corner speck
    filtering, and optional hole filling to remove outer bezels while preserving full glyphs.
    """
    h, w = crop.shape[:2]
    cfg = {
        "ix": 11,
        "it": 10,
        "ib": 13,
        "r_top": 20,
        "r_bot": 42,
        "th": 46.0,
        "prune_border": True,
        "fill_holes": False,
    }
    cfg.update(SIMFORGE_GLYPH_OVERRIDES.get(el_id, {}))

    mask = build_asymmetric_rounded_mask(
        h, w, cfg["ix"], cfg["it"], cfg["ib"], cfg["r_top"], cfg["r_bot"]
    )
    bg_bgr = np.percentile(crop[mask > 200], 15, axis=0).astype(np.float32)
    dist = np.linalg.norm(crop.astype(np.float32) - bg_bgr, axis=2)

    th = cfg["th"]
    fg = ((dist > th) & (mask > 128)).astype(np.uint8)

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


def extract_circular_badge(crop, center_rel, radius):
    """Extracts a circular element with smooth anti-aliased alpha transparency."""
    h, w = crop.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center_rel, radius, 255, -1, lineType=cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (3, 3), 0.5)

    b, g, r = cv2.split(crop)
    rgba = cv2.merge([b, g, r, mask])

    cx, cy = center_rel
    x1 = max(0, cx - radius - 2)
    x2 = min(w, cx + radius + 2)
    y1 = max(0, cy - radius - 2)
    y2 = min(h, cy + radius + 2)
    return rgba[y1:y2, x1:x2]


def _place_pill(canvas, tag_text, x1, y1, color):
    """Draws a crisp dark ID pill clamped inside image bounds."""
    img_h, img_w = canvas.shape[:2]
    (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
    pw = tw + 10
    ph = th + 8
    px1 = max(2, min(x1, img_w - pw - 2))
    py1 = max(2, min(y1, img_h - ph - 2))
    px2 = px1 + pw
    py2 = py1 + ph

    cv2.rectangle(canvas, (px1, py1), (px2, py2), (16, 18, 22), -1)
    cv2.rectangle(canvas, (px1, py1), (px2, py2), color, 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, tag_text, (px1 + 5, py2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, lineType=cv2.LINE_AA)


def generate_marked_overview(img):
    """Generates the marked overview master image with non-overlapping boxes and clamped ID pills."""
    img_h, img_w = img.shape[:2]
    annotated = img.copy()
    overlay = annotated.copy()

    overview_elements = [
        el for el in ELEMENTS
        if el["cat"] not in ["Texture", "Hardware"] and el["id"] != "BKG-11"
    ]

    for el in overview_elements:
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        x1, y1, x2, y2 = el["box"]
        if el.get("type") == "circle":
            cx, cy = el["center"]
            cv2.circle(overlay, (cx, cy), el["radius"], style["box"], -1, lineType=cv2.LINE_AA)
            cv2.circle(annotated, (cx, cy), el["radius"], style["box"], 2, lineType=cv2.LINE_AA)
        else:
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
            px, py = x1 + (x2 - x1 - pw) // 2, 512
        elif el["id"] == "EMB-02":
            cx, cy = el["center"]
            px, py = cx - pw // 2, cy + el["radius"] + 3
        elif el["id"] == "BRD-05":
            px, py = x1 + 4, y1 + 3
        elif el["id"] in ("BKG-10", "BKG-12", "BKG-13") or y1 < ph + 4:
            px, py = x1 + 3, y1 + 3
        elif el["id"] == "BKG-15":
            px, py = x2 - 64, y1 - ph - 2
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
    cat_y = header_y + 60
    cat_x = pw + 25
    legend_w = 780
    total_w = pw + legend_w
    for cat_name in CATEGORY_STYLES:
        if cat_name in ["Texture", "Hardware"]:
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
    canvas[:] = (14, 16, 20)

    canvas[0:ph, 0:pw] = annotated_panel
    cv2.line(canvas, (pw, 0), (pw, total_h), (45, 50, 62), 2)

    header_x = pw + 25
    cv2.putText(canvas, "SIMFORGE STUDIO 15-KEY ASSET MAPPING", (header_x, header_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 165, 0), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, f"Total Elements Mapped: {len(ELEMENTS)} | Master Resolution: {pw}x{ph}px", (header_x, header_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 160, 175), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, header_y + 36), (total_w - 25, header_y + 36), (50, 58, 72), 1)

    cat_y_draw = header_y + 60
    cat_x_draw = header_x
    for cat_name, style in CATEGORY_STYLES.items():
        if cat_name in ["Texture", "Hardware"]:
            continue
        cv2.rectangle(canvas, (cat_x_draw, cat_y_draw - 12), (cat_x_draw + 14, cat_y_draw + 2), style["box"], -1)
        cv2.putText(canvas, cat_name, (cat_x_draw + 20, cat_y_draw), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 225, 230), 1, lineType=cv2.LINE_AA)
        cat_x_draw += 108
        if cat_x_draw > total_w - 110:
            cat_x_draw = header_x
            cat_y_draw += 22

    cv2.line(canvas, (header_x, cat_y_draw + 15), (total_w - 25, cat_y_draw + 15), (50, 58, 72), 1)

    cv2.putText(canvas, "ID", (header_x + 5, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ELEMENT NAME", (header_x + 85, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "CATEGORY", (header_x + 335, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "BOUNDS (X, Y, WxH)", (header_x + 470, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, table_top + 10), (total_w - 25, table_top + 10), (45, 52, 65), 1)

    row_y = table_top + 30
    for el in ELEMENTS:
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        box = el["box"]
        w = box[2] - box[0]
        h = box[3] - box[1]
        coords_str = f"[{box[0]}, {box[1]}, {w}x{h}]"

        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), (25, 28, 35), -1)
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), style["box"], 1)
        cv2.putText(canvas, el["id"], (header_x + 8, row_y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.40, style["box"], 1, lineType=cv2.LINE_AA)

        cv2.putText(canvas, el["name"], (header_x + 85, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (240, 242, 245), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, el["cat"], (header_x + 335, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.39, (175, 185, 195), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, coords_str, (header_x + 470, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130, 215, 255), 1, lineType=cv2.LINE_AA)

        row_y += row_step

    return canvas


def generate_clean_modular_chassis(img):
    """
    Generates a spotless industrial stream deck chassis background plate by replacing each button's
    interior rounded face with a forged charcoal gradient and brushed metal grain while keeping
    100% of the outer glowing metallic bevels intact.
    """
    clean = img.copy()
    rng = np.random.default_rng(42)

    for el in ELEMENTS:
        if el["cat"] != "Button":
            continue
        x1, y1, x2, y2 = el["box"]
        bw, bh = x2 - x1, y2 - y1

        mask = build_rounded_rect_mask(bh, bw, inset_x=9, inset_top=12, inset_bot=12, radius=22)
        alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (7, 7), 1.8)[:, :, np.newaxis]

        # Vertical gradient from cool dark charcoal steel at top to subtle warm anvil bounce at bottom
        t = np.linspace(0.0, 1.0, bh, dtype=np.float32)[:, np.newaxis, np.newaxis]
        top_bgr = np.array([[[16.0, 18.0, 22.0]]], dtype=np.float32)
        mid_bgr = np.array([[[11.0, 14.0, 24.0]]], dtype=np.float32)
        warm_bounce = np.clip((t - 0.72) / 0.28, 0.0, 1.0) ** 1.6
        base_grad = top_bgr * (1.0 - t) + mid_bgr * t + warm_bounce * np.array([[[2.0, 10.0, 24.0]]], dtype=np.float32)
        synth = np.broadcast_to(base_grad, (bh, bw, 3)).copy()

        # Subtle brushed steel noise matching the panel chassis grain
        synth += rng.normal(0.0, 2.2, (bh, bw, 3)).astype(np.float32)
        synth = np.clip(synth, 0, 255)

        orig = clean[y1:y2, x1:x2].astype(np.float32)
        blended = orig * (1.0 - alpha) + synth * alpha
        clean[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)

    return clean


def main():
    print(f"Loading SimForge Stream Deck Studio 15-Key panel: {IMAGE_PATH}")
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {IMAGE_PATH}")

    print(f"Image dimensions: {img.shape[1]}x{img.shape[0]} px")

    # 1. Annotated Master Images
    print("Generating Annotated Master Images...")
    marked_overview = generate_marked_overview(img)
    cv2.imwrite(os.path.join(DIRS["sim_annotated"], "marked_panel_overview.png"), marked_overview)
    cv2.imwrite(os.path.join(DIRS["gen_annotated"], "marked_panel_overview_studio.png"), marked_overview)

    marked_legend = generate_marked_with_legend(img)
    cv2.imwrite(os.path.join(DIRS["sim_annotated"], "marked_panel_with_legend.png"), marked_legend)
    cv2.imwrite(os.path.join(DIRS["gen_annotated"], "marked_panel_with_legend_studio.png"), marked_legend)
    print("Annotated Master Images rendered successfully.")

    # 2. Extract and Render All Elements
    print("Extracting individual assets and generating high-DPI renders...")
    for el in ELEMENTS:
        box = el["box"]
        x1, y1, x2, y2 = box
        crop = img[y1:y2, x1:x2]
        file_stem = el["file"]
        cat = el["cat"]

        crop_2x = render_high_dpi(crop, scale=2)

        if cat == "Button":
            # Save 1x and 2x keycap
            cv2.imwrite(os.path.join(DIRS["sim_buttons"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_buttons"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            cv2.imwrite(os.path.join(DIRS["gen_buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)

            # True-square Stream Deck keycap format (186x186 and 372x372 2x)
            crop_sq = make_square_streamdeck_keycap(img, box, target_size=186)
            crop_sq_2x = make_square_streamdeck_keycap(img, box, target_size=372)
            cv2.imwrite(os.path.join(DIRS["sim_buttons_sq"], f"{file_stem}_sq186.png"), crop_sq)
            cv2.imwrite(os.path.join(DIRS["sim_buttons_sq"], f"{file_stem}_sq372.png"), crop_sq_2x)

            # Isolated Transparent Glyphs (bezel-free)
            glyph_rgba = extract_isolated_glyph(crop, el["id"])
            cv2.imwrite(os.path.join(DIRS["sim_icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)
            cv2.imwrite(os.path.join(DIRS["gen_icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)

            # High-DPI 2x Glyph
            glyph_2x = render_high_dpi(glyph_rgba, scale=2)
            cv2.imwrite(os.path.join(DIRS["sim_icons_hidpi"], f"icon_{file_stem}_2x.png"), glyph_2x)

            # Dark slate backing
            slate_bg = np.full((crop.shape[0], crop.shape[1], 3), (24, 20, 18), dtype=np.uint8)
            alpha = (glyph_rgba[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]
            slate_composite = (glyph_rgba[:, :, :3].astype(np.float32) * alpha + slate_bg.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
            cv2.imwrite(os.path.join(DIRS["sim_icons_slate"], f"slate_{file_stem}.png"), slate_composite)

        elif cat in ["Display", "Telemetry"]:
            cv2.imwrite(os.path.join(DIRS["sim_display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_display_hidpi"], f"{file_stem}_2x.png"), crop_2x)

        elif cat == "Control":
            if el.get("type") == "circle":
                cx, cy = el["center"]
                rad = el["radius"]
                rel_center = (cx - x1, cy - y1)
                circular_rgba = extract_circular_badge(crop, rel_center, rad)
                cv2.imwrite(os.path.join(DIRS["sim_branding"], f"{file_stem}.png"), circular_rgba)
                cv2.imwrite(os.path.join(DIRS["gen_branding"], f"{file_stem}.png"), circular_rgba)
                circ_2x = render_high_dpi(circular_rgba, scale=2)
                cv2.imwrite(os.path.join(DIRS["sim_branding_hidpi"], f"{file_stem}_2x.png"), circ_2x)
            else:
                cv2.imwrite(os.path.join(DIRS["sim_branding"], f"{file_stem}.png"), crop)
                cv2.imwrite(os.path.join(DIRS["gen_branding"], f"{file_stem}.png"), crop)
                cv2.imwrite(os.path.join(DIRS["sim_branding_hidpi"], f"{file_stem}_2x.png"), crop_2x)

        elif cat == "Branding":
            cv2.imwrite(os.path.join(DIRS["sim_branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_branding_hidpi"], f"{file_stem}_2x.png"), crop_2x)

        elif cat in ["Chassis", "Accent", "Hardware", "Texture"]:
            if el["id"] == "BKG-11":
                continue
            cv2.imwrite(os.path.join(DIRS["sim_bkg"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_bkg"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_bkg_hidpi"], f"{file_stem}_2x.png"), crop_2x)

    # 3. Clean Modular Chassis Template
    print("Generating Clean Modular Deck Template...")
    clean_chassis = generate_clean_modular_chassis(img)
    cv2.imwrite(os.path.join(DIRS["sim_bkg"], "11_studio_modular_empty_chassis.png"), clean_chassis)
    cv2.imwrite(os.path.join(DIRS["gen_bkg"], "11_studio_modular_empty_chassis.png"), clean_chassis)
    clean_2x = render_high_dpi(clean_chassis, scale=2)
    cv2.imwrite(os.path.join(DIRS["sim_bkg_hidpi"], "11_studio_modular_empty_chassis_2x.png"), clean_2x)

    print("All SimForge Studio Deck assets processed and exported successfully!")


if __name__ == "__main__":
    main()
