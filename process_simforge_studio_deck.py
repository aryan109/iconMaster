"""
SimForge Studio 15-Key Stream Deck Panel Processor
Detects, marks, extracts, and renders high-quality assets:
- Marked/annotated master images with coordinate callouts and HUD legend
- Individual buttons and keycaps (standard, 2x High-DPI, and square Stream Deck format)
- Isolated icon glyphs with alpha transparency (molten glow preserved)
- Circular Anvil Emblem with anti-aliased circular alpha transparency
- Telemetry display screen and individual CPU, RAM, and GPU sub-meters
- Industrial chassis faceplates, modular empty template, hazard vents, hex bolts, and textures
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

ELEMENTS = [
    # Row 1 Buttons
    {"id": "BTN-16", "name": "Tab Navigation", "cat": "Button", "box": [80, 64, 220, 184], "type": "rect", "file": "16_btn_tab"},
    {"id": "BTN-17", "name": "TrackIR / Sensor Nodes", "cat": "Button", "box": [261, 64, 401, 184], "type": "rect", "file": "17_btn_tracking_nodes"},
    {"id": "BTN-18", "name": "Scene Dual Window", "cat": "Button", "box": [442, 64, 582, 184], "type": "rect", "file": "18_btn_scene_dual_window"},
    {"id": "BTN-19", "name": "Studio Mode Chart", "cat": "Button", "box": [623, 64, 763, 184], "type": "rect", "file": "19_btn_studio_mode_chart"},
    {"id": "BTN-20", "name": "Video Cam Toggle", "cat": "Button", "box": [804, 64, 944, 184], "type": "rect", "file": "20_btn_video_cam"},

    # Row 2 Buttons
    {"id": "BTN-21", "name": "OBS Studio Logo", "cat": "Button", "box": [80, 216, 220, 336], "type": "rect", "file": "21_btn_obs_studio"},
    {"id": "BTN-22", "name": "Backspace", "cat": "Button", "box": [261, 216, 401, 336], "type": "rect", "file": "22_btn_backspace"},
    {"id": "BTN-23", "name": "Media Play", "cat": "Button", "box": [442, 216, 582, 336], "type": "rect", "file": "23_btn_media_play"},
    {"id": "BTN-24", "name": "Media Pause", "cat": "Button", "box": [623, 216, 763, 336], "type": "rect", "file": "24_btn_media_pause"},
    {"id": "BTN-25", "name": "Replay Buffer", "cat": "Button", "box": [804, 216, 944, 336], "type": "rect", "file": "25_btn_replay_buffer"},

    # Row 3 Buttons
    {"id": "BTN-26", "name": "Combat Flight Badge", "cat": "Button", "box": [80, 368, 220, 488], "type": "rect", "file": "26_btn_flight_sim_badge"},
    {"id": "BTN-27", "name": "Ctrl+Win Macro", "cat": "Button", "box": [261, 368, 401, 488], "type": "rect", "file": "27_btn_ctrl_win"},

    # Row 3 Central Emblem / Control
    {"id": "EMB-01", "name": "SimForge Anvil Plate", "cat": "Control", "box": [442, 368, 582, 488], "type": "rect", "file": "04_simforge_anvil_plate"},
    {"id": "EMB-02", "name": "SimForge Anvil Badge", "cat": "Control", "box": [457, 373, 567, 483], "center": [512, 428], "radius": 54, "type": "circle", "file": "05_simforge_anvil_badge_circular"},

    # Row 3 Telemetry Display Unit & Meters
    {"id": "DSP-05", "name": "Studio Telemetry Unit", "cat": "Display", "box": [623, 368, 944, 488], "type": "rect", "file": "05_studio_telemetry_unit"},
    {"id": "MET-04", "name": "CPU Meter (5%)", "cat": "Telemetry", "box": [635, 378, 730, 478], "type": "rect", "file": "06_telemetry_cpu_5pct"},
    {"id": "MET-05", "name": "RAM Meter (54%)", "cat": "Telemetry", "box": [735, 378, 832, 478], "type": "rect", "file": "07_telemetry_ram_54pct"},
    {"id": "MET-06", "name": "GPU Meter (7%)", "cat": "Telemetry", "box": [837, 378, 932, 478], "type": "rect", "file": "08_telemetry_gpu_7pct"},

    # Branding & Bottom Bevel
    {"id": "BRD-04", "name": "SimForge Chiseled Wordmark", "cat": "Branding", "box": [415, 532, 609, 574], "type": "rect", "file": "06_simforge_chiseled_wordmark"},
    {"id": "BRD-05", "name": "Bottom Deck Control Strip", "cat": "Branding", "box": [150, 520, 874, 590], "type": "rect", "file": "07_bottom_deck_control_strip"},

    # Backgrounds & Chassis Elements
    {"id": "BKG-10", "name": "Studio Chassis Full Faceplate", "cat": "Chassis", "box": [10, 10, 1014, 606], "type": "rect", "file": "10_studio_chassis_full_faceplate"},
    {"id": "BKG-11", "name": "Clean Modular Deck Template", "cat": "Chassis", "box": [10, 10, 1014, 606], "type": "rect", "file": "11_studio_modular_empty_chassis"},
    {"id": "BKG-12", "name": "Top-Left Hazard Chevrons", "cat": "Accent", "box": [155, 20, 275, 52], "type": "rect", "file": "12_top_left_hazard_chevrons"},
    {"id": "BKG-13", "name": "Top-Right Hazard Chevrons", "cat": "Accent", "box": [750, 20, 870, 52], "type": "rect", "file": "13_top_right_hazard_chevrons"},
    {"id": "BKG-14", "name": "Left Hazard Side Vent", "cat": "Accent", "box": [8, 165, 45, 455], "type": "rect", "file": "14_left_hazard_side_vent"},
    {"id": "BKG-15", "name": "Right Hazard Side Vent", "cat": "Accent", "box": [979, 165, 1016, 455], "type": "rect", "file": "15_right_hazard_side_vent"},
    {"id": "BKG-16", "name": "Top-Left Corner Bolt", "cat": "Hardware", "box": [22, 26, 54, 58], "center": [38, 42], "radius": 16, "type": "circle", "file": "16_bolt_top_left"},
    {"id": "BKG-17", "name": "Top-Right Corner Bolt", "cat": "Hardware", "box": [970, 26, 1002, 58], "center": [986, 42], "radius": 16, "type": "circle", "file": "17_bolt_top_right"},
    {"id": "BKG-18", "name": "Bottom-Left Corner Bolt", "cat": "Hardware", "box": [22, 504, 54, 536], "center": [38, 520], "radius": 16, "type": "circle", "file": "18_bolt_bottom_left"},
    {"id": "BKG-19", "name": "Bottom-Right Corner Bolt", "cat": "Hardware", "box": [970, 504, 1002, 536], "center": [986, 520], "radius": 16, "type": "circle", "file": "19_bolt_bottom_right"},
    {"id": "BKG-20", "name": "Industrial Brushed Metal Tile", "cat": "Texture", "box": [40, 200, 75, 350], "type": "rect", "file": "20_studio_forged_metal_tile"},
]

def render_high_dpi(crop, scale=2):
    """Super-samples an image using Lanczos interpolation and subtle unsharp masking."""
    h, w = crop.shape[:2]
    up = cv2.resize(crop, (w * scale, h * scale), interpolation=cv2.INTER_LANCZOS4)
    blurred = cv2.GaussianBlur(up, (0, 0), 1.0)
    sharpened = cv2.addWeighted(up, 1.25, blurred, -0.25, 0)
    return sharpened

def make_square_streamdeck_keycap(crop, target_size=186):
    """
    Places the 140x120 button centered on a standard square 186x186 Stream Deck keycap canvas
    with realistic forged metallic dark border padding.
    """
    h, w = crop.shape[:2]
    # Create dark metallic backing
    canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    canvas[:] = (18, 20, 24)
    # Scale proportionally to fit within 90% of target
    fit_scale = min((target_size * 0.94) / w, (target_size * 0.94) / h)
    nw, nh = int(w * fit_scale), int(h * fit_scale)
    scaled = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    
    ox = (target_size - nw) // 2
    oy = (target_size - nh) // 2
    canvas[oy:oy+nh, ox:ox+nw] = scaled
    return canvas

def extract_isolated_glyph(crop):
    """
    Extracts the glowing icon glyph onto a clean 32-bit transparent RGBA canvas.
    Retains molten glow, amber radiance, and vibrant colors while making dark metal background transparent.
    """
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    # Glow / icon signal: high value OR high saturation in orange/green/red
    val = hsv[:, :, 2].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    
    # Baseline dark metal threshold
    # Metal interior is typically gray < 55 and low sat
    alpha = np.zeros_like(gray, dtype=np.float32)
    
    # Signal mask
    signal = (val * 0.7) + (sat * 0.3)
    thresh_low = 55.0
    thresh_high = 140.0
    
    alpha = np.clip((signal - thresh_low) / (thresh_high - thresh_low), 0.0, 1.0) * 255.0
    alpha = alpha.astype(np.uint8)
    
    # Smooth alpha slightly
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    # Build RGBA
    b, g, r = cv2.split(crop)
    rgba = cv2.merge([b, g, r, alpha])
    return rgba

def extract_circular_badge(crop, center_rel, radius):
    """Extracts a circular element with anti-aliased alpha transparency."""
    h, w = crop.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center_rel, radius, 255, -1, lineType=cv2.LINE_AA)
    
    b, g, r = cv2.split(crop)
    rgba = cv2.merge([b, g, r, mask])
    
    # Crop to circle bounding square
    cx, cy = center_rel
    x1 = max(0, cx - radius - 2)
    x2 = min(w, cx + radius + 2)
    y1 = max(0, cy - radius - 2)
    y2 = min(h, cy + radius + 2)
    return rgba[y1:y2, x1:x2]

def generate_marked_overview(img):
    """Generates the marked overview master image with colored bounding boxes and ID tags."""
    annotated = img.copy()
    overlay = annotated.copy()
    
    for el in ELEMENTS:
        if el["cat"] in ["Texture", "Hardware"]:
            continue
            
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200), "fill": (200, 200, 200, 30)})
        box = el["box"]
        x1, y1, x2, y2 = box
        
        # Semi-transparent fill
        cv2.rectangle(overlay, (x1, y1), (x2, y2), style["box"], -1)
        # Bounding box stroke
        cv2.rectangle(annotated, (x1, y1), (x2, y2), style["box"], 2, lineType=cv2.LINE_AA)
        
        # ID tag pill
        tag_text = el["id"]
        (tw, th), baseline = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        tag_x1 = x1
        tag_y1 = max(0, y1 - th - 8)
        tag_x2 = tag_x1 + tw + 10
        tag_y2 = y1
        
        cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), (18, 20, 24), -1)
        cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), style["box"], 1, lineType=cv2.LINE_AA)
        cv2.putText(annotated, tag_text, (tag_x1 + 5, tag_y2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, lineType=cv2.LINE_AA)
        
    # Blend fill overlay at 22% opacity
    cv2.addWeighted(overlay, 0.22, annotated, 0.78, 0, annotated)
    return annotated

def generate_marked_with_legend(img):
    """
    Creates an expanded telemetry overview canvas featuring the annotated panel on the left
    and an industrial HUD coordinate telemetry legend on the right.
    """
    annotated_panel = generate_marked_overview(img)
    ph, pw = annotated_panel.shape[:2]
    
    legend_w = 780
    total_w = pw + legend_w
    total_h = max(ph, 780)
    
    canvas = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    canvas[:] = (14, 16, 20) # Slate carbon
    
    # Place annotated panel
    canvas[0:ph, 0:pw] = annotated_panel
    
    # Border divider between panel and legend
    cv2.line(canvas, (pw, 0), (pw, total_h), (45, 50, 62), 2)
    
    # Legend Header
    header_x = pw + 25
    header_y = 35
    cv2.putText(canvas, "SIMFORGE STUDIO 15-KEY ASSET MAPPING", (header_x, header_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 165, 0), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "Hardware Coordinate & Geometry Telemetry Matrix", (header_x, header_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 160, 175), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, header_y + 36), (total_w - 25, header_y + 36), (50, 58, 72), 1)
    
    # Category Legend Badges
    cat_y = header_y + 60
    cat_x = header_x
    for cat_name, style in CATEGORY_STYLES.items():
        if cat_name in ["Texture", "Hardware"]:
            continue
        cv2.rectangle(canvas, (cat_x, cat_y - 12), (cat_x + 14, cat_y + 2), style["box"], -1)
        cv2.putText(canvas, cat_name, (cat_x + 20, cat_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 225, 230), 1, lineType=cv2.LINE_AA)
        cat_x += 108
        if cat_x > total_w - 110:
            cat_x = header_x
            cat_y += 22
            
    cv2.line(canvas, (header_x, cat_y + 15), (total_w - 25, cat_y + 15), (50, 58, 72), 1)
    
    # Table Column Headers
    table_top = cat_y + 36
    cv2.putText(canvas, "ID", (header_x + 5, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ELEMENT NAME", (header_x + 85, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "CATEGORY", (header_x + 330, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "BOUNDS (X, Y, W, H)", (header_x + 470, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 150, 165), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, table_top + 10), (total_w - 25, table_top + 10), (45, 52, 65), 1)
    
    # Populate Rows
    row_y = table_top + 30
    for el in ELEMENTS:
        if row_y > total_h - 20:
            break
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        box = el["box"]
        w = box[2] - box[0]
        h = box[3] - box[1]
        coords_str = f"[{box[0]}, {box[1]}, {w}x{h}]"
        
        # ID pill
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), (25, 28, 35), -1)
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), style["box"], 1)
        cv2.putText(canvas, el["id"], (header_x + 8, row_y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.40, style["box"], 1, lineType=cv2.LINE_AA)
        
        # Element Name
        cv2.putText(canvas, el["name"], (header_x + 85, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (240, 242, 245), 1, lineType=cv2.LINE_AA)
        
        # Category
        cv2.putText(canvas, el["cat"], (header_x + 330, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.39, (175, 185, 195), 1, lineType=cv2.LINE_AA)
        
        # Coordinates
        cv2.putText(canvas, coords_str, (header_x + 470, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130, 215, 255), 1, lineType=cv2.LINE_AA)
        
        row_y += 24
        
    return canvas

def generate_clean_modular_chassis(img):
    """
    Generates a pristine industrial stream deck chassis background plate with button faces cleared,
    leaving the metallic casing, orange hazard vents, hex bolts, and branding ready for custom layouts.
    """
    clean = img.copy()
    
    # Inpaint or clear button inner faceplates
    for el in ELEMENTS:
        if el["cat"] == "Button":
            x1, y1, x2, y2 = el["box"]
            # Inner button face is within 12px margin
            ix1, iy1 = x1 + 12, y1 + 12
            ix2, iy2 = x2 - 12, y2 - 12
            # Create dark brushed metal fill
            sub = clean[iy1:iy2, ix1:ix2]
            gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
            mask = (gray > 115).astype(np.uint8) * 255
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            cleaned_sub = cv2.inpaint(sub, mask, 5, cv2.INPAINT_TELEA)
            clean[iy1:iy2, ix1:ix2] = cleaned_sub
            
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
        
        # High-DPI 2x render
        crop_2x = render_high_dpi(crop, scale=2)
        
        if cat == "Button":
            # Save 1x keycap
            cv2.imwrite(os.path.join(DIRS["sim_buttons"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_buttons"], f"{file_stem}.png"), crop)
            # Save 2x keycap
            cv2.imwrite(os.path.join(DIRS["sim_buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            cv2.imwrite(os.path.join(DIRS["gen_buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            # Standardized 186x186 square Stream Deck keycap format
            crop_sq = make_square_streamdeck_keycap(crop, target_size=186)
            cv2.imwrite(os.path.join(DIRS["sim_buttons_sq"], f"{file_stem}_sq186.png"), crop_sq)
            
            # Isolated Transparent Glyphs
            glyph_rgba = extract_isolated_glyph(crop)
            cv2.imwrite(os.path.join(DIRS["sim_icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)
            cv2.imwrite(os.path.join(DIRS["gen_icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)
            
            # High-DPI 2x Glyph
            glyph_2x = render_high_dpi(glyph_rgba, scale=2)
            cv2.imwrite(os.path.join(DIRS["sim_icons_hidpi"], f"icon_{file_stem}_2x.png"), glyph_2x)
            
            # Dark slate backing
            slate_bg = np.zeros((crop.shape[0], crop.shape[1], 3), dtype=np.uint8)
            slate_bg[:] = (27, 21, 18) # BGR for dark slate #12151b
            alpha = glyph_rgba[:, :, 3].astype(np.float32) / 255.0
            alpha = np.expand_dims(alpha, axis=-1)
            slate_composite = (glyph_rgba[:, :, :3] * alpha + slate_bg * (1 - alpha)).astype(np.uint8)
            cv2.imwrite(os.path.join(DIRS["sim_icons_slate"], f"slate_{file_stem}.png"), slate_composite)
            
        elif cat in ["Display", "Telemetry"]:
            # Display & Telemetry gauges
            cv2.imwrite(os.path.join(DIRS["sim_display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_display_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            
        elif cat == "Control":
            # Circular Anvil Badge vs Rectangular Plate
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
            # Wordmarks and Deck strips
            cv2.imwrite(os.path.join(DIRS["sim_branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_branding_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            
        elif cat in ["Chassis", "Accent", "Hardware", "Texture"]:
            # Backgrounds, Vents, Bolts
            cv2.imwrite(os.path.join(DIRS["sim_bkg"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["gen_bkg"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["sim_bkg_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            
    # 3. Modular Clean Chassis Template
    print("Generating Clean Modular Deck Template...")
    clean_chassis = generate_clean_modular_chassis(img)
    cv2.imwrite(os.path.join(DIRS["sim_bkg"], "11_studio_modular_empty_chassis.png"), clean_chassis)
    cv2.imwrite(os.path.join(DIRS["gen_bkg"], "11_studio_modular_empty_chassis.png"), clean_chassis)
    clean_2x = render_high_dpi(clean_chassis, scale=2)
    cv2.imwrite(os.path.join(DIRS["sim_bkg_hidpi"], "11_studio_modular_empty_chassis_2x.png"), clean_2x)
    
    print("All SimForge Studio Deck assets processed and exported successfully!")

if __name__ == "__main__":
    main()
