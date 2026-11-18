"""
SimForge Industrial Stream Deck Panel Processor
Detects, marks, extracts, and renders high-quality assets:
- Marked/annotated master images with coordinate callouts and legend
- Individual buttons and keycaps (standard and 2x High-DPI)
- Isolated icon glyphs with alpha transparency
- Hardware knobs, dials, and push buttons with circular alpha masks
- Telemetry display screen and individual CPU/RAM/GPU sub-meters
- Industrial chassis faceplates, hazard vents, hex bolts, and textures
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "SimForge Industrial Stream Deck Panel.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

DIRS = {
    "annotated": os.path.join(OUTPUT_DIR, "annotated"),
    "buttons": os.path.join(OUTPUT_DIR, "buttons"),
    "buttons_hidpi": os.path.join(OUTPUT_DIR, "buttons", "high_dpi_2x"),
    "icons_trans": os.path.join(OUTPUT_DIR, "icons_isolated", "transparent"),
    "icons_slate": os.path.join(OUTPUT_DIR, "icons_isolated", "dark_slate"),
    "icons_hidpi": os.path.join(OUTPUT_DIR, "icons_isolated", "high_dpi_2x"),
    "display": os.path.join(OUTPUT_DIR, "display_panel"),
    "display_hidpi": os.path.join(OUTPUT_DIR, "display_panel", "high_dpi_2x"),
    "controls": os.path.join(OUTPUT_DIR, "controls_and_knobs"),
    "controls_hidpi": os.path.join(OUTPUT_DIR, "controls_and_knobs", "high_dpi_2x"),
    "branding": os.path.join(OUTPUT_DIR, "branding"),
    "branding_hidpi": os.path.join(OUTPUT_DIR, "branding", "high_dpi_2x"),
    "backgrounds": os.path.join(OUTPUT_DIR, "backgrounds_and_chassis"),
    "backgrounds_hidpi": os.path.join(OUTPUT_DIR, "backgrounds_and_chassis", "high_dpi_2x"),
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Category styling: (Box Color BGR, Fill Color BGRA, Label Color BGR)
CATEGORY_STYLES = {
    "Button": {"box": (255, 191, 0), "fill": (255, 191, 0, 35), "tag": "BTN"},        # Deep Sky Blue
    "Empty Slot": {"box": (0, 165, 255), "fill": (0, 165, 255, 35), "tag": "SLOT"},     # Orange
    "Display": {"box": (50, 205, 50), "fill": (50, 205, 50, 35), "tag": "DSP"},         # Lime Green
    "Telemetry": {"box": (128, 255, 0), "fill": (128, 255, 0, 35), "tag": "MET"},       # Chartreuse
    "Control": {"box": (203, 192, 255), "fill": (203, 192, 255, 40), "tag": "CTL"},     # Orchid / Magenta
    "Control Deck": {"box": (180, 105, 255), "fill": (180, 105, 255, 25), "tag": "DECK"},# Neon Pink
    "Branding": {"box": (0, 215, 255), "fill": (0, 215, 255, 40), "tag": "LOGO"},       # Gold / Amber
    "Chassis": {"box": (190, 190, 190), "fill": (190, 190, 190, 20), "tag": "CHAS"},    # Steel Silver
    "Accent": {"box": (0, 128, 255), "fill": (0, 128, 255, 45), "tag": "VENT"},         # Orange Accent
    "Hardware": {"box": (230, 230, 230), "fill": (230, 230, 230, 45), "tag": "BOLT"},  # Pure Silver
    "Texture": {"box": (160, 210, 100), "fill": (160, 210, 100, 35), "tag": "TEX"},    # Aqua Slate
}

ELEMENTS = [
    # Action Buttons
    {"id": "BTN-01", "name": "ESC", "cat": "Button", "box": [179, 145, 365, 331], "type": "rect", "file": "01_btn_esc"},
    {"id": "BTN-02", "name": "CCRP OFF", "cat": "Button", "box": [402, 145, 588, 331], "type": "rect", "file": "02_btn_ccrp_off"},
    {"id": "BTN-03", "name": "X WEAPON", "cat": "Button", "box": [625, 145, 811, 331], "type": "rect", "file": "03_btn_x_weapon"},
    {"id": "BTN-04", "name": "EMPTY SLOT 1", "cat": "Empty Slot", "box": [848, 145, 1034, 331], "type": "rect", "file": "04_btn_empty_slot_1"},
    {"id": "BTN-05", "name": "EMPTY SLOT 2", "cat": "Empty Slot", "box": [1071, 145, 1257, 331], "type": "rect", "file": "05_btn_empty_slot_2"},
    {"id": "BTN-06", "name": "COVER ME", "cat": "Button", "box": [179, 351, 365, 537], "type": "rect", "file": "06_btn_cover_me"},
    {"id": "BTN-07", "name": "ATTACK HIM", "cat": "Button", "box": [402, 351, 588, 537], "type": "rect", "file": "07_btn_attack_him"},
    {"id": "BTN-08", "name": "THANK", "cat": "Button", "box": [625, 351, 811, 537], "type": "rect", "file": "08_btn_thank"},
    {"id": "BTN-09", "name": "SMOKE", "cat": "Button", "box": [848, 351, 1034, 537], "type": "rect", "file": "09_btn_smoke"},
    {"id": "BTN-10", "name": "JETISON", "cat": "Button", "box": [1071, 351, 1257, 537], "type": "rect", "file": "10_btn_jetison"},
    {"id": "BTN-11", "name": "YES", "cat": "Button", "box": [179, 557, 365, 743], "type": "rect", "file": "11_btn_yes"},
    {"id": "BTN-12", "name": "Ctrl+Win", "cat": "Button", "box": [402, 557, 588, 743], "type": "rect", "file": "12_btn_ctrl_win"},
    {"id": "BTN-13", "name": "NO", "cat": "Button", "box": [625, 557, 811, 743], "type": "rect", "file": "13_btn_no"},

    # Display Unit and Telemetry
    {"id": "DSP-01", "name": "System Display Unit", "cat": "Display", "box": [848, 557, 1258, 743], "type": "rect", "file": "01_system_display_unit"},
    {"id": "DSP-02", "name": "CPU Meter (4%)", "cat": "Telemetry", "box": [863, 572, 988, 728], "type": "rect", "file": "02_telemetry_cpu"},
    {"id": "DSP-03", "name": "RAM Meter (30%)", "cat": "Telemetry", "box": [990, 572, 1115, 728], "type": "rect", "file": "03_telemetry_ram"},
    {"id": "DSP-04", "name": "GPU Meter (4%)", "cat": "Telemetry", "box": [1118, 572, 1243, 728], "type": "rect", "file": "04_telemetry_gpu"},

    # Controls & Knobs
    {"id": "CTL-01", "name": "Push Button Left", "cat": "Control", "box": [198, 873, 308, 983], "center": [253, 928], "radius": 52, "type": "circle", "file": "01_push_button_left"},
    {"id": "CTL-02", "name": "Push Button Mid-Left", "cat": "Control", "box": [414, 873, 524, 983], "center": [469, 928], "radius": 52, "type": "circle", "file": "02_push_button_mid_left"},
    {"id": "CTL-03", "name": "Rotary Knob 1", "cat": "Control", "box": [615, 837, 795, 1017], "center": [705, 927], "radius": 88, "type": "circle", "file": "03_rotary_knob_1"},
    {"id": "CTL-04", "name": "Rotary Knob 2", "cat": "Control", "box": [850, 838, 1030, 1018], "center": [940, 928], "radius": 88, "type": "circle", "file": "04_rotary_knob_2"},
    {"id": "CTL-05", "name": "Rotary Knob 3", "cat": "Control", "box": [1085, 839, 1265, 1019], "center": [1175, 929], "radius": 88, "type": "circle", "file": "05_rotary_knob_3"},
    {"id": "CTL-06", "name": "Lower Control Deck Strip", "cat": "Control Deck", "box": [150, 800, 1300, 1055], "type": "rect", "file": "06_lower_control_deck_strip"},

    # Branding
    {"id": "BRD-01", "name": "SimForge Header Banner", "cat": "Branding", "box": [485, 15, 935, 135], "type": "rect", "file": "01_simforge_header_full"},
    {"id": "BRD-02", "name": "Anvil & Hammer Emblem", "cat": "Branding", "box": [495, 15, 620, 135], "center": [557, 75], "radius": 55, "type": "circle", "file": "02_simforge_anvil_badge"},
    {"id": "BRD-03", "name": "SimForge Wordmark", "cat": "Branding", "box": [625, 35, 930, 115], "type": "rect", "file": "03_simforge_wordmark"},

    # Backgrounds & Chassis Elements
    {"id": "BKG-01", "name": "Upper Chassis Faceplate", "cat": "Chassis", "box": [25, 20, 1392, 755], "type": "rect", "file": "01_chassis_upper_faceplate"},
    {"id": "BKG-02", "name": "Lower Deck Faceplate", "cat": "Chassis", "box": [25, 755, 1392, 1085], "type": "rect", "file": "02_chassis_lower_deck"},
    {"id": "BKG-03", "name": "Left Hazard Accent Vent", "cat": "Accent", "box": [18, 160, 65, 590], "type": "rect", "file": "03_left_hazard_vent"},
    {"id": "BKG-04", "name": "Right Hazard Accent Vent", "cat": "Accent", "box": [1352, 160, 1399, 590], "type": "rect", "file": "04_right_hazard_vent"},
    {"id": "BKG-05", "name": "Top-Left Hex Bolt", "cat": "Hardware", "box": [70, 70, 130, 130], "type": "circle", "center": [100, 100], "radius": 28, "file": "05_bolt_top_left"},
    {"id": "BKG-06", "name": "Top-Right Hex Bolt", "cat": "Hardware", "box": [1287, 70, 1347, 130], "type": "circle", "center": [1317, 100], "radius": 28, "file": "06_bolt_top_right"},
    {"id": "BKG-07", "name": "Bottom-Left Hex Bolt", "cat": "Hardware", "box": [70, 980, 130, 1040], "type": "circle", "center": [100, 1010], "radius": 28, "file": "07_bolt_bottom_left"},
    {"id": "BKG-08", "name": "Bottom-Right Hex Bolt", "cat": "Hardware", "box": [1287, 980, 1347, 1040], "type": "circle", "center": [1317, 1010], "radius": 28, "file": "08_bolt_bottom_right"},
    {"id": "BKG-09", "name": "Industrial Brushed Metal Tile", "cat": "Texture", "box": [65, 230, 155, 520], "type": "rect", "file": "09_industrial_metal_tile"},
]

def enhance_2x(crop_bgr):
    """Render high-fidelity 2x super-sampled image using Lanczos and unsharp mask."""
    h, w = crop_bgr.shape[:2]
    upscaled = cv2.resize(crop_bgr, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
    sharpened = cv2.addWeighted(upscaled, 1.25, gaussian, -0.25, 0)
    return sharpened

def create_circular_alpha(crop_bgr):
    """Create RGBA image with smooth circular alpha mask."""
    h, w = crop_bgr.shape[:2]
    rgba = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2BGRA)
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)
    radius = min(w, h) // 2 - 2
    cv2.circle(mask, center, radius, 255, -1, lineType=cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (3, 3), 0.5)
    rgba[:, :, 3] = mask
    return rgba

def extract_icon_glyph(button_crop):
    """
    Isolate glowing icon and text glyph on transparent background and dark slate.
    """
    h, w = button_crop.shape[:2]
    inner = button_crop[20:h-20, 20:w-20].copy()
    ih, iw = inner.shape[:2]
    
    hsv = cv2.cvtColor(inner, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
    val = hsv[:, :, 2]
    sat = hsv[:, :, 1]
    
    fg_mask = np.zeros((ih, iw), dtype=np.uint8)
    fg_mask[val > 75] = 255
    fg_mask[(sat > 90) & (val > 55)] = 255
    fg_mask = cv2.GaussianBlur(fg_mask, (3, 3), 0.8)
    
    rgba = cv2.cvtColor(inner, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = fg_mask
    
    slate_bg = np.full((ih, iw, 3), (23, 20, 18), dtype=np.uint8)
    alpha_norm = (fg_mask.astype(float) / 255.0)[:, :, np.newaxis]
    slate_comp = (inner.astype(float) * alpha_norm + slate_bg.astype(float) * (1.0 - alpha_norm)).astype(np.uint8)
    
    return rgba, slate_comp

def render_marked_overview(base_img):
    """
    Draw precise annotated overlays, colored bounding boxes, category badges, and labels.
    """
    img_h, img_w = base_img.shape[:2]
    # Create overlay plane for transparent color fills
    overlay = base_img.copy()
    
    # Priority elements to draw on master overview (focused on primary interactive and structural blocks)
    primary_cats = ["Button", "Empty Slot", "Display", "Control", "Branding", "Accent", "Chassis"]
    
    for el in ELEMENTS:
        if el["cat"] in ["Telemetry", "Hardware", "Texture", "Control Deck"]:
            continue # Covered in detailed views
            
        style = CATEGORY_STYLES[el["cat"]]
        box = el["box"]
        x1, y1, x2, y2 = box
        
        # Transparent tinted fill
        cv2.rectangle(overlay, (x1, y1), (x2, y2), style["box"], -1)
        
    alpha = 0.18
    marked = cv2.addWeighted(overlay, alpha, base_img, 1.0 - alpha, 0)
    
    # Draw crisp lines and badges
    for el in ELEMENTS:
        if el["cat"] in ["Telemetry", "Hardware", "Texture", "Control Deck"]:
            continue
            
        style = CATEGORY_STYLES[el["cat"]]
        box = el["box"]
        x1, y1, x2, y2 = box
        color = style["box"]
        
        # Solid border
        cv2.rectangle(marked, (x1, y1), (x2, y2), color, 2, lineType=cv2.LINE_AA)
        
        # Corner brackets for tech HUD look
        bl = 12
        cv2.line(marked, (x1, y1), (x1 + bl, y1), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x1, y1), (x1, y1 + bl), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x2, y1), (x2 - bl, y1), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x2, y1), (x2, y1 + bl), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x1, y2), (x1 + bl, y2), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x1, y2), (x1, y2 - bl), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x2, y2), (x2 - bl, y2), color, 3, lineType=cv2.LINE_AA)
        cv2.line(marked, (x2, y2), (x2, y2 - bl), color, 3, lineType=cv2.LINE_AA)
        
        # Header Badge
        badge_text = f"{el['id']}: {el['name']}"
        font_scale = 0.42
        thickness = 1
        (tw, th), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # Badge background
        bx1 = x1
        by1 = max(0, y1 - th - 10)
        bx2 = x1 + tw + 12
        by2 = y1
        cv2.rectangle(marked, (bx1, by1), (bx2, by2), (18, 18, 22), -1)
        cv2.rectangle(marked, (bx1, by1), (bx2, by2), color, 1, lineType=cv2.LINE_AA)
        cv2.putText(marked, badge_text, (bx1 + 6, by2 - 4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)
        
    return marked

def render_legend_panel(base_img, marked_img):
    """
    Renders an extended wide image featuring the marked image on the left and a structured HUD legend table on the right.
    """
    mh, mw = marked_img.shape[:2]
    legend_w = 680
    total_w = mw + legend_w
    total_h = mh
    
    canvas = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    # Background: dark metallic slate gradient
    canvas[:, :mw] = marked_img
    canvas[:, mw:] = (22, 24, 28)
    
    # Draw dividing line
    cv2.line(canvas, (mw, 0), (mw, total_h), (50, 55, 65), 2)
    
    # Legend Header
    header_y = 45
    cv2.putText(canvas, "SIMFORGE STREAM DECK: ELEMENT MAP", (mw + 30, header_y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 215, 255), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, f"Total Elements Mapped: {len(ELEMENTS)} | Resolution: {mw}x{mh}px", (mw + 30, header_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 170, 180), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (mw + 30, header_y + 40), (total_w - 30, header_y + 40), (60, 70, 85), 1)
    
    # Categories Bar
    cat_y = header_y + 65
    cat_x = mw + 30
    for cat_name, style in CATEGORY_STYLES.items():
        if cat_name in ["Texture", "Hardware"]:
            continue
        cv2.rectangle(canvas, (cat_x, cat_y - 12), (cat_x + 14, cat_y + 2), style["box"], -1)
        cv2.putText(canvas, cat_name, (cat_x + 20, cat_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, lineType=cv2.LINE_AA)
        cat_x += 105
        if cat_x > total_w - 110:
            cat_x = mw + 30
            cat_y += 20
            
    cv2.line(canvas, (mw + 30, cat_y + 15), (total_w - 30, cat_y + 15), (60, 70, 85), 1)
    
    # Table Column Headers
    table_top = cat_y + 35
    cv2.putText(canvas, "ID", (mw + 35, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 160), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ELEMENT NAME", (mw + 115, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 160), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "CATEGORY", (mw + 340, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 160), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "COORDINATES (X, Y, W, H)", (mw + 460, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 160), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (mw + 30, table_top + 10), (total_w - 30, table_top + 10), (50, 60, 75), 1)
    
    # List Elements
    row_y = table_top + 32
    for el in ELEMENTS:
        if row_y > total_h - 25:
            break
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        box = el["box"]
        w = box[2] - box[0]
        h = box[3] - box[1]
        coords_str = f"[{box[0]}, {box[1]}, {w}x{h}]"
        
        # ID badge
        cv2.rectangle(canvas, (mw + 32, row_y - 14), (mw + 98, row_y + 4), (32, 36, 44), -1)
        cv2.rectangle(canvas, (mw + 32, row_y - 14), (mw + 98, row_y + 4), style["box"], 1)
        cv2.putText(canvas, el["id"], (mw + 36, row_y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.40, style["box"], 1, lineType=cv2.LINE_AA)
        
        # Name
        cv2.putText(canvas, el["name"], (mw + 115, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (240, 240, 240), 1, lineType=cv2.LINE_AA)
        
        # Category
        cv2.putText(canvas, el["cat"], (mw + 340, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 190, 200), 1, lineType=cv2.LINE_AA)
        
        # Coordinates
        cv2.putText(canvas, coords_str, (mw + 460, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 210, 240), 1, lineType=cv2.LINE_AA)
        
        row_y += 24
        
    return canvas

def generate_clean_chassis_background(img):
    """
    Generates a pristine industrial stream deck chassis background plate with button faces removed,
    leaving the metallic casing, orange hazard vents, hex bolts, and branding ready for custom layouts.
    """
    clean_bkg = img.copy()
    
    # For each button slot, replace the button cap with the empty slot texture
    # Button 4 and 5 on Row 1 are blank/empty slots with industrial diagonal lines
    empty_slot_1 = img[145:331, 848:1034]
    
    # Paste empty slot texture into other button slots to create a pristine modular blank panel
    xs = [179, 402, 625, 848, 1071]
    ys = [145, 351, 557]
    
    for r in range(3):
        for c in range(5):
            if r == 2 and c >= 3:
                continue # Display panel
            x1 = xs[c]
            y1 = ys[r]
            x2 = x1 + 186
            y2 = y1 + 186
            clean_bkg[y1:y2, x1:x2] = empty_slot_1
            
    return clean_bkg

def main():
    print(f"Loading image from: {IMAGE_PATH}")
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {IMAGE_PATH}")
        
    h, w = img.shape[:2]
    print(f"Loaded image: {w}x{h} px")
    
    # 1. Generate Marked / Annotated Images
    print("Generating marked overview and HUD legend master images...")
    marked_overview = render_marked_overview(img)
    overview_path = os.path.join(DIRS["annotated"], "marked_panel_overview.png")
    cv2.imwrite(overview_path, marked_overview)
    print(f"Saved: {overview_path}")
    
    marked_with_legend = render_legend_panel(img, marked_overview)
    legend_path = os.path.join(DIRS["annotated"], "marked_panel_with_legend.png")
    cv2.imwrite(legend_path, marked_with_legend)
    print(f"Saved: {legend_path}")
    
    # 2. Extract and Render High-Quality Elements
    print("Rendering high quality individual assets...")
    
    for el in ELEMENTS:
        box = el["box"]
        x1, y1, x2, y2 = box
        crop = img[y1:y2, x1:x2]
        file_prefix = el["file"]
        cat = el["cat"]
        
        # Decide destination folder based on category
        if cat in ["Button", "Empty Slot"]:
            target_dir = DIRS["buttons"]
            hidpi_dir = DIRS["buttons_hidpi"]
            
            # Save standard button crop
            cv2.imwrite(os.path.join(target_dir, f"{file_prefix}.png"), crop)
            
            # Save 2x High-DPI enhanced render
            crop_2x = enhance_2x(crop)
            cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), crop_2x)
            
            # If active button, extract isolated icon glyph
            if cat == "Button":
                rgba_glyph, slate_glyph = extract_icon_glyph(crop)
                cv2.imwrite(os.path.join(DIRS["icons_trans"], f"icon_{file_prefix}.png"), rgba_glyph)
                cv2.imwrite(os.path.join(DIRS["icons_slate"], f"icon_{file_prefix}_slate.png"), slate_glyph)
                # 2x High-DPI icon
                rgba_2x = cv2.resize(rgba_glyph, (rgba_glyph.shape[1]*2, rgba_glyph.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)
                cv2.imwrite(os.path.join(DIRS["icons_hidpi"], f"icon_{file_prefix}_2x.png"), rgba_2x)

        elif cat in ["Display", "Telemetry"]:
            target_dir = DIRS["display"]
            hidpi_dir = DIRS["display_hidpi"]
            cv2.imwrite(os.path.join(target_dir, f"{file_prefix}.png"), crop)
            crop_2x = enhance_2x(crop)
            cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), crop_2x)
            
        elif cat in ["Control", "Control Deck"]:
            target_dir = DIRS["controls"]
            hidpi_dir = DIRS["controls_hidpi"]
            cv2.imwrite(os.path.join(target_dir, f"{file_prefix}.png"), crop)
            
            # For circular dials/knobs, also generate circular alpha mask
            if el.get("type") == "circle":
                circ_rgba = create_circular_alpha(crop)
                cv2.imwrite(os.path.join(target_dir, f"{file_prefix}_circular.png"), circ_rgba)
                
            crop_2x = enhance_2x(crop)
            cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), crop_2x)

        elif cat == "Branding":
            target_dir = DIRS["branding"]
            hidpi_dir = DIRS["branding_hidpi"]
            cv2.imwrite(os.path.join(target_dir, f"{file_prefix}.png"), crop)
            if el.get("type") == "circle":
                circ_rgba = create_circular_alpha(crop)
                cv2.imwrite(os.path.join(target_dir, f"{file_prefix}_circular.png"), circ_rgba)
            crop_2x = enhance_2x(crop)
            cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), crop_2x)

        elif cat in ["Chassis", "Accent", "Hardware", "Texture"]:
            target_dir = DIRS["backgrounds"]
            hidpi_dir = DIRS["backgrounds_hidpi"]
            cv2.imwrite(os.path.join(target_dir, f"{file_prefix}.png"), crop)
            if el.get("type") == "circle":
                circ_rgba = create_circular_alpha(crop)
                cv2.imwrite(os.path.join(target_dir, f"{file_prefix}_circular.png"), circ_rgba)
            crop_2x = enhance_2x(crop)
            cv2.imwrite(os.path.join(hidpi_dir, f"{file_prefix}_2x.png"), crop_2x)

    # 3. Extra Specialty Render: Clean Modular Chassis (All buttons turned into empty slots)
    print("Generating clean modular chassis background...")
    clean_chassis = generate_clean_chassis_background(img)
    clean_path = os.path.join(DIRS["backgrounds"], "10_clean_chassis_modular_template.png")
    cv2.imwrite(clean_path, clean_chassis)
    clean_2x = enhance_2x(clean_chassis)
    cv2.imwrite(os.path.join(DIRS["backgrounds_hidpi"], "10_clean_chassis_modular_template_2x.png"), clean_2x)
    print(f"Saved: {clean_path}")

    print("All image assets successfully rendered and saved!")

if __name__ == "__main__":
    main()
