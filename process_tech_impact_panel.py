"""
Tech Impact Stream Deck Panel Processor
Detects, marks, extracts, and renders high-quality assets:
- Marked/annotated master images with coordinate callouts and HUD legend
- Individual buttons and keycaps (standard, 2x High-DPI, and square Stream Deck format)
- Isolated icon glyphs with alpha transparency (preserving neon blue, violet, magenta, and amber cosmic glow)
- System telemetry display unit and individual CPU, RAM, and GPU sub-meters
- Tech Impact branding: stylized 'T' axe emblem, futuristic wordmark, and 1024x1024 hero battle-axe assets
- Cosmic nebula chassis faceplates, modular empty template, glowing neon frame, and space textures
"""

import os
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

ELEMENTS = [
    # Row 1 Buttons
    {"id": "BTN-01", "name": "Save Keycap", "cat": "Button", "box": [108, 158, 244, 286], "type": "rect", "file": "01_btn_save"},
    {"id": "BTN-02", "name": "Save As Keycap", "cat": "Button", "box": [276, 158, 412, 286], "type": "rect", "file": "02_btn_save_as"},
    {"id": "BTN-03", "name": "Radial Starburst / Particle Spark", "cat": "Button", "box": [444, 158, 580, 286], "type": "rect", "file": "03_btn_starburst_spark"},
    {"id": "BTN-04", "name": "Chromatic AI Sparkle (Gemini)", "cat": "Button", "box": [612, 158, 748, 286], "type": "rect", "file": "04_btn_chromatic_sparkle"},
    {"id": "BTN-05", "name": "Gradient Sine Wave / Arc", "cat": "Button", "box": [780, 158, 916, 286], "type": "rect", "file": "05_btn_gradient_wave_arc"},

    # Row 2 Buttons
    {"id": "BTN-06", "name": "Tab Navigation", "cat": "Button", "box": [108, 314, 244, 442], "type": "rect", "file": "06_btn_tab"},
    {"id": "BTN-07", "name": "Backspace Keycap", "cat": "Button", "box": [276, 314, 412, 442], "type": "rect", "file": "07_btn_backspace"},
    {"id": "BTN-08", "name": "ChatGPT / AI Swirl", "cat": "Button", "box": [444, 314, 580, 442], "type": "rect", "file": "08_btn_chatgpt_swirl"},
    {"id": "BTN-09", "name": "Copilot / AI Robot Avatar", "cat": "Button", "box": [612, 314, 748, 442], "type": "rect", "file": "09_btn_copilot_avatar"},
    {"id": "BTN-10", "name": "Crystal Isometric Cube", "cat": "Button", "box": [780, 314, 916, 442], "type": "rect", "file": "10_btn_crystal_cube"},

    # Row 3 Buttons
    {"id": "BTN-11", "name": "Num Enter Keycap", "cat": "Button", "box": [108, 470, 244, 598], "type": "rect", "file": "11_btn_num_enter"},
    {"id": "BTN-12", "name": "Ctrl+Win Macro", "cat": "Button", "box": [276, 470, 412, 598], "type": "rect", "file": "12_btn_ctrl_win"},
    {"id": "BTN-13", "name": "Windows Key", "cat": "Button", "box": [444, 470, 580, 598], "type": "rect", "file": "13_btn_win"},

    # Row 3 Telemetry Display Unit & Meters
    {"id": "DSP-01", "name": "System Telemetry Display Unit", "cat": "Display", "box": [612, 470, 916, 598], "type": "rect", "file": "01_telemetry_display_unit"},
    {"id": "MET-01", "name": "CPU Meter (9%)", "cat": "Telemetry", "box": [620, 480, 715, 590], "type": "rect", "file": "02_telemetry_cpu_9pct"},
    {"id": "MET-02", "name": "RAM Meter (56%)", "cat": "Telemetry", "box": [718, 480, 812, 590], "type": "rect", "file": "03_telemetry_ram_56pct"},
    {"id": "MET-03", "name": "GPU Meter (23%)", "cat": "Telemetry", "box": [815, 480, 910, 590], "type": "rect", "file": "04_telemetry_gpu_23pct"},

    # Branding
    {"id": "BRD-01", "name": "Tech Impact Header Banner", "cat": "Branding", "box": [315, 15, 690, 115], "type": "rect", "file": "01_tech_impact_header_banner"},
    {"id": "BRD-02", "name": "Tech Impact Header 'T' Emblem", "cat": "Branding", "box": [320, 15, 395, 115], "type": "rect", "file": "02_tech_impact_header_emblem"},
    {"id": "BRD-03", "name": "Tech Impact Futuristic Wordmark", "cat": "Branding", "box": [400, 35, 680, 95], "type": "rect", "file": "03_tech_impact_wordmark"},

    # Backgrounds & Chassis Elements
    {"id": "BKG-01", "name": "Tech Impact Full Chassis Master", "cat": "Chassis", "box": [5, 5, 1019, 625], "type": "rect", "file": "01_tech_impact_full_chassis"},
    {"id": "BKG-02", "name": "Clean Modular Deck Template", "cat": "Chassis", "box": [5, 5, 1019, 625], "type": "rect", "file": "02_tech_impact_modular_template"},
    {"id": "BKG-03", "name": "Outer Glowing Neon Frame", "cat": "Accent", "box": [12, 130, 1012, 622], "type": "rect", "file": "03_outer_glowing_neon_frame"},
    {"id": "BKG-04", "name": "Cosmic Nebula Texture Top-Left", "cat": "Texture", "box": [10, 10, 250, 140], "type": "rect", "file": "04_cosmic_nebula_texture_tl"},
    {"id": "BKG-05", "name": "Deep Space Blue Gas Cloud", "cat": "Texture", "box": [780, 10, 1014, 140], "type": "rect", "file": "05_deep_space_blue_nebula_tr"},
    {"id": "BKG-06", "name": "Cosmic Amber Plasma Flurry", "cat": "Texture", "box": [10, 500, 100, 620], "type": "rect", "file": "06_cosmic_amber_plasma_bl"},
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
    Places the 136x128 button centered on a standard square 186x186 Stream Deck keycap canvas
    with realistic cosmic dark slate border padding.
    """
    h, w = crop.shape[:2]
    canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    canvas[:] = (12, 8, 16) # Deep space cosmic slate
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
    Retains neon blue, violet, magenta, and celestial amber radiance.
    """
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    val = hsv[:, :, 2].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    
    # Metal backing threshold: deep cosmic slate is typically gray < 50
    signal = (val * 0.72) + (sat * 0.28)
    thresh_low = 45.0
    thresh_high = 130.0
    
    alpha = np.clip((signal - thresh_low) / (thresh_high - thresh_low), 0.0, 1.0) * 255.0
    alpha = alpha.astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    b, g, r = cv2.split(crop)
    rgba = cv2.merge([b, g, r, alpha])
    return rgba

def extract_hero_axe_assets(hero_img):
    """Processes the 1024x1024 Tech Impact hero battle-axe emblem."""
    # 1. High quality 1024x1024 master
    master_path = os.path.join(DIRS["branding"], "04_tech_impact_hero_axe_1024x1024.png")
    cv2.imwrite(master_path, hero_img)
    
    # 2. Transparent alpha cutout
    hsv = cv2.cvtColor(hero_img, cv2.COLOR_BGR2HSV)
    val = hsv[:, :, 2].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    signal = (val * 0.75) + (sat * 0.25)
    
    alpha = np.clip((signal - 22.0) / (85.0 - 22.0), 0.0, 1.0) * 255.0
    alpha = alpha.astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    b, g, r = cv2.split(hero_img)
    rgba = cv2.merge([b, g, r, alpha])
    trans_path = os.path.join(DIRS["branding"], "05_tech_impact_hero_axe_transparent.png")
    cv2.imwrite(trans_path, rgba)
    
    # 3. Circular emblem badge
    h, w = hero_img.shape[:2]
    cx, cy = w // 2, h // 2
    rad = int(min(cx, cy) * 0.92)
    circ_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(circ_mask, (cx, cy), rad, 255, -1, lineType=cv2.LINE_AA)
    final_circ_alpha = cv2.bitwise_and(alpha, circ_mask)
    circ_rgba = cv2.merge([b, g, r, final_circ_alpha])
    circ_path = os.path.join(DIRS["branding"], "06_tech_impact_circular_emblem.png")
    cv2.imwrite(circ_path, circ_rgba)
    
    # 4. Stream Deck keycap format (186x186)
    keycap = make_square_streamdeck_keycap(hero_img, target_size=186)
    keycap_path = os.path.join(DIRS["buttons"], "00_btn_tech_impact_hero_keycap.png")
    cv2.imwrite(keycap_path, keycap)
    keycap_2x = render_high_dpi(keycap, scale=2)
    cv2.imwrite(os.path.join(DIRS["buttons_hidpi"], "00_btn_tech_impact_hero_keycap_2x.png"), keycap_2x)
    print("Hero battle-axe assets extracted and rendered.")

def generate_marked_overview(img):
    """Generates the marked overview master image with colored bounding boxes and ID tags."""
    annotated = img.copy()
    overlay = annotated.copy()
    
    for el in ELEMENTS:
        if el["cat"] in ["Texture"]:
            continue
            
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200), "fill": (200, 200, 200, 30)})
        box = el["box"]
        x1, y1, x2, y2 = box
        
        cv2.rectangle(overlay, (x1, y1), (x2, y2), style["box"], -1)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), style["box"], 2, lineType=cv2.LINE_AA)
        
        tag_text = el["id"]
        (tw, th), baseline = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        tag_x1 = x1
        tag_y1 = max(0, y1 - th - 8)
        tag_x2 = tag_x1 + tw + 10
        tag_y2 = y1
        
        cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), (12, 10, 18), -1)
        cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), style["box"], 1, lineType=cv2.LINE_AA)
        cv2.putText(annotated, tag_text, (tag_x1 + 5, tag_y2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, lineType=cv2.LINE_AA)
        
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
    canvas[:] = (10, 8, 14) # Deep cosmic space slate
    
    canvas[0:ph, 0:pw] = annotated_panel
    cv2.line(canvas, (pw, 0), (pw, total_h), (55, 45, 75), 2)
    
    header_x = pw + 25
    header_y = 35
    cv2.putText(canvas, "TECH IMPACT COSMIC SUITE MAPPING", (header_x, header_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 215, 255), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "Hardware Coordinate & Geometry Telemetry Matrix", (header_x, header_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 170, 195), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, header_y + 36), (total_w - 25, header_y + 36), (65, 55, 85), 1)
    
    cat_y = header_y + 60
    cat_x = header_x
    for cat_name, style in CATEGORY_STYLES.items():
        if cat_name in ["Texture"]:
            continue
        cv2.rectangle(canvas, (cat_x, cat_y - 12), (cat_x + 14, cat_y + 2), style["box"], -1)
        cv2.putText(canvas, cat_name, (cat_x + 20, cat_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (225, 230, 240), 1, lineType=cv2.LINE_AA)
        cat_x += 108
        if cat_x > total_w - 110:
            cat_x = header_x
            cat_y += 22
            
    cv2.line(canvas, (header_x, cat_y + 15), (total_w - 25, cat_y + 15), (65, 55, 85), 1)
    
    table_top = cat_y + 36
    cv2.putText(canvas, "ID", (header_x + 5, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ELEMENT NAME", (header_x + 85, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "CATEGORY", (header_x + 330, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "BOUNDS (X, Y, W, H)", (header_x + 470, table_top), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (150, 160, 180), 1, lineType=cv2.LINE_AA)
    cv2.line(canvas, (header_x, table_top + 10), (total_w - 25, table_top + 10), (55, 45, 75), 1)
    
    row_y = table_top + 30
    for el in ELEMENTS:
        if row_y > total_h - 20:
            break
        style = CATEGORY_STYLES.get(el["cat"], {"box": (200, 200, 200)})
        box = el["box"]
        w = box[2] - box[0]
        h = box[3] - box[1]
        coords_str = f"[{box[0]}, {box[1]}, {w}x{h}]"
        
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), (22, 18, 30), -1)
        cv2.rectangle(canvas, (header_x + 4, row_y - 14), (header_x + 70, row_y + 3), style["box"], 1)
        cv2.putText(canvas, el["id"], (header_x + 8, row_y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.40, style["box"], 1, lineType=cv2.LINE_AA)
        
        cv2.putText(canvas, el["name"], (header_x + 85, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (245, 245, 250), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, el["cat"], (header_x + 330, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.39, (185, 195, 210), 1, lineType=cv2.LINE_AA)
        cv2.putText(canvas, coords_str, (header_x + 470, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 225, 255), 1, lineType=cv2.LINE_AA)
        
        row_y += 24
        
    return canvas

def generate_clean_modular_chassis(img):
    """
    Generates a pristine cosmic stream deck chassis background plate with button faces cleared,
    leaving the outer neon frame, cosmic nebula lighting, and Tech Impact header ready for custom layouts.
    """
    clean = img.copy()
    for el in ELEMENTS:
        if el["cat"] == "Button":
            x1, y1, x2, y2 = el["box"]
            ix1, iy1 = x1 + 14, y1 + 14
            ix2, iy2 = x2 - 14, y2 - 14
            sub = clean[iy1:iy2, ix1:ix2]
            gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
            mask = (gray > 95).astype(np.uint8) * 255
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            cleaned_sub = cv2.inpaint(sub, mask, 5, cv2.INPAINT_TELEA)
            clean[iy1:iy2, ix1:ix2] = cleaned_sub
            
    return clean

def sync_to_alt_theme_dir():
    """Synchronizes output/themes/tech_impact to output/themes/Tech Impact."""
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
            # 1x keycap
            cv2.imwrite(os.path.join(DIRS["buttons"], f"{file_stem}.png"), crop)
            # 2x keycap
            cv2.imwrite(os.path.join(DIRS["buttons_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            # Square Stream Deck format (186x186)
            crop_sq = make_square_streamdeck_keycap(crop, target_size=186)
            cv2.imwrite(os.path.join(DIRS["buttons_sq"], f"{file_stem}_sq186.png"), crop_sq)
            
            # Isolated Transparent Glyphs
            glyph_rgba = extract_isolated_glyph(crop)
            cv2.imwrite(os.path.join(DIRS["icons_trans"], f"icon_{file_stem}.png"), glyph_rgba)
            glyph_2x = render_high_dpi(glyph_rgba, scale=2)
            cv2.imwrite(os.path.join(DIRS["icons_hidpi"], f"icon_{file_stem}_2x.png"), glyph_2x)
            
            # Dark slate backing
            slate_bg = np.zeros((crop.shape[0], crop.shape[1], 3), dtype=np.uint8)
            slate_bg[:] = (20, 16, 24)
            alpha = glyph_rgba[:, :, 3].astype(np.float32) / 255.0
            alpha = np.expand_dims(alpha, axis=-1)
            slate_composite = (glyph_rgba[:, :, :3] * alpha + slate_bg * (1 - alpha)).astype(np.uint8)
            cv2.imwrite(os.path.join(DIRS["icons_slate"], f"slate_{file_stem}.png"), slate_composite)
            
        elif cat in ["Display", "Telemetry"]:
            cv2.imwrite(os.path.join(DIRS["display"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["display_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            
        elif cat == "Branding":
            cv2.imwrite(os.path.join(DIRS["branding"], f"{file_stem}.png"), crop)
            cv2.imwrite(os.path.join(DIRS["branding_hidpi"], f"{file_stem}_2x.png"), crop_2x)
            
        elif cat in ["Chassis", "Accent", "Texture"]:
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
