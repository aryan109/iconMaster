"""
SimForge Fire Metal Stream Deck Widget Background Generator
Target Resolution: 458 x 196 px (and 916 x 392 px 2x Hi-DPI)
Designed specifically for dynamic CPU / RAM / GPU system telemetry widgets.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "simforge_widget_backgrounds")
PREVIEW_DIR = os.path.join(OUTPUT_DIR, "simulated_previews")
HIDPI_DIR = os.path.join(OUTPUT_DIR, "high_dpi_2x")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(HIDPI_DIR, exist_ok=True)

# Assets from earlier extraction
ANVIL_PATH = os.path.join(BASE_DIR, "output", "branding", "02_simforge_anvil_badge.png")
HEADER_PATH = os.path.join(BASE_DIR, "output", "branding", "01_simforge_header_full.png")
WORDMARK_PATH = os.path.join(BASE_DIR, "output", "branding", "03_simforge_wordmark.png")
BOLT_PATH = os.path.join(BASE_DIR, "output", "backgrounds_and_chassis", "05_bolt_top_left.png")
ORIGINAL_DISP_PATH = os.path.join(BASE_DIR, "output", "display_panel", "01_system_display_unit.png")

TARGET_W = 458
TARGET_H = 196

def create_metallic_plate(w, h, base_color=(20, 22, 26)):
    """Generates brushed industrial dark forged steel plate texture with subtle micro-grain."""
    plate = np.full((h, w, 3), base_color, dtype=np.uint8)
    # Add horizontal brushing texture
    noise = np.random.normal(0, 4.0, (h, w)).astype(np.float32)
    noise_brushed = cv2.GaussianBlur(noise, (15, 1), 0)
    for c in range(3):
        channel = plate[:, :, c].astype(np.float32) + noise_brushed
        plate[:, :, c] = np.clip(channel, 8, 45).astype(np.uint8)
    return plate

def add_fire_metal_glow(base_img, rect, corner_radius=16, intensity=1.0):
    """
    Applies multi-layered incandescent molten fire metal glow around a rounded rectangle boundary.
    Layers: Inner yellow heat -> Vibrant fire orange -> Deep furnace red ambient bloom.
    """
    h, w = base_img.shape[:2]
    x1, y1, x2, y2 = rect
    
    # Glow mask canvas
    glow_canvas = np.zeros((h, w, 3), dtype=np.float32)
    
    # 1. Outer Deep Red/Furnace Glow (broad bloom)
    mask_red = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask_red, (x1, y1), (x2, y2), 255, 10, lineType=cv2.LINE_AA)
    mask_red_blur = cv2.GaussianBlur(mask_red, (29, 29), 0) / 255.0
    glow_canvas[:, :, 0] += mask_red_blur * (15 * intensity)   # B
    glow_canvas[:, :, 1] += mask_red_blur * (55 * intensity)   # G
    glow_canvas[:, :, 2] += mask_red_blur * (210 * intensity)  # R
    
    # 2. Mid Vibrant Fire Orange (intense molten flame)
    mask_orange = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask_orange, (x1, y1), (x2, y2), 255, 4, lineType=cv2.LINE_AA)
    mask_orange_blur = cv2.GaussianBlur(mask_orange, (13, 13), 0) / 255.0
    glow_canvas[:, :, 0] += mask_orange_blur * (20 * intensity)
    glow_canvas[:, :, 1] += mask_orange_blur * (120 * intensity)
    glow_canvas[:, :, 2] += mask_orange_blur * (255 * intensity)
    
    # 3. Inner White-Hot / Yellow Molten Core
    mask_yellow = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask_yellow, (x1, y1), (x2, y2), 255, 2, lineType=cv2.LINE_AA)
    mask_yellow_blur = cv2.GaussianBlur(mask_yellow, (5, 5), 0) / 255.0
    glow_canvas[:, :, 0] += mask_yellow_blur * (80 * intensity)
    glow_canvas[:, :, 1] += mask_yellow_blur * (210 * intensity)
    glow_canvas[:, :, 2] += mask_yellow_blur * (255 * intensity)
    
    # Composite additively
    result = base_img.astype(np.float32) + glow_canvas
    return np.clip(result, 0, 255).astype(np.uint8)

def draw_corner_hex_bolts(img, bolt_crop, margin=14, bolt_size=20):
    """Draws 4 industrial corner mounting screws/bolts."""
    h, w = img.shape[:2]
    resized_bolt = cv2.resize(bolt_crop, (bolt_size, bolt_size), interpolation=cv2.INTER_LANCZOS4)
    bh, bw = resized_bolt.shape[:2]
    
    # Coordinates for the 4 corners
    coords = [
        (margin, margin),                       # Top-Left
        (w - margin - bw, margin),              # Top-Right
        (margin, h - margin - bh),              # Bottom-Left
        (w - margin - bw, h - margin - bh)      # Bottom-Right
    ]
    
    for x, y in coords:
        # Create subtle circular shadow
        shadow = np.zeros((bh + 4, bw + 4), dtype=np.float32)
        cv2.circle(shadow, (bw//2 + 2, bh//2 + 2), bw//2, 0.7, -1)
        shadow = cv2.GaussianBlur(shadow, (5, 5), 0)
        
        # Alpha blend bolt with subtle ambient glow
        roi = img[y:y+bh, x:x+bw]
        # Circular mask for bolt
        mask = np.zeros((bh, bw), dtype=np.float32)
        cv2.circle(mask, (bw//2, bh//2), bw//2 - 1, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        
        blended = roi.astype(np.float32) * (1.0 - mask[:, :, np.newaxis]) + resized_bolt.astype(np.float32) * mask[:, :, np.newaxis]
        img[y:y+bh, x:x+bw] = np.clip(blended, 0, 255).astype(np.uint8)
        
    return img

def draw_vertical_dividers(img, x_positions=[152, 305], y1=36, y2=164):
    """Draws sleek fiery vertical dividers separating the CPU, RAM, and GPU columns."""
    h, w = img.shape[:2]
    for x in x_positions:
        # Subtle dark groove line
        cv2.line(img, (x, y1), (x, y2), (12, 14, 16), 3, lineType=cv2.LINE_AA)
        # Glowing molten orange core line
        cv2.line(img, (x, y1 + 6), (x, y2 - 6), (20, 110, 230), 1, lineType=cv2.LINE_AA)
        # End dots/pins with molten glow
        cv2.circle(img, (x, y1 + 5), 2, (30, 160, 255), -1, lineType=cv2.LINE_AA)
        cv2.circle(img, (x, y2 - 5), 2, (30, 160, 255), -1, lineType=cv2.LINE_AA)
    return img

def render_simulated_preview(bg_img, title="Preview"):
    """
    Renders a simulation of the widget with dynamic system stats (e.g. 8% CPU, 55% RAM, 8% GPU)
    overlaid exactly as the Stream Deck software displays it, so the user can see it in action.
    """
    sim = bg_img.copy()
    h, w = sim.shape[:2]
    
    # Positions of the 3 columns
    cols = [
        {"val": "8%", "label": "CPU", "cx": 82},
        {"val": "55%", "label": "RAM", "cx": 229},
        {"val": "8%", "label": "GPU", "cx": 376}
    ]
    
    for c in cols:
        cx = c["cx"]
        # Drop shadow for dynamic numbers
        cv2.putText(sim, c["val"], (cx - 32, 108), cv2.FONT_HERSHEY_DUPLEX, 1.25, (0, 0, 0), 4, lineType=cv2.LINE_AA)
        # Crisp white dynamic number
        cv2.putText(sim, c["val"], (cx - 32, 108), cv2.FONT_HERSHEY_DUPLEX, 1.25, (250, 252, 255), 2, lineType=cv2.LINE_AA)
        
        # Sub-label shadow
        cv2.putText(sim, c["label"], (cx - 22, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 3, lineType=cv2.LINE_AA)
        # Sub-label light text
        cv2.putText(sim, c["label"], (cx - 22, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 225, 230), 1, lineType=cv2.LINE_AA)
        
    return sim

def enhance_2x(img):
    """Generates 2x Hi-DPI render (916 x 392 px)."""
    h, w = img.shape[:2]
    upscaled = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
    return cv2.addWeighted(upscaled, 1.25, gaussian, -0.25, 0)

# ==============================================================================
# VARIANT GENERATORS
# ==============================================================================

def generate_variant_1_molten_forge(bolt_crop, anvil_crop):
    """
    Variant 1: SimForge Fire Metal - Molten Forge Edition (Featured Masterpiece)
    Heavy beveled forged steel frame, intense molten fiery edge glow,
    prominent top-centered SimForge glowing anvil emblem, corner bolts,
    and sleek fiery vertical dividers.
    """
    img = create_metallic_plate(TARGET_W, TARGET_H, (18, 20, 24))
    
    # Outer beveled dark steel frame
    cv2.rectangle(img, (4, 4), (TARGET_W - 5, TARGET_H - 5), (38, 42, 48), 3, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (7, 7), (TARGET_W - 8, TARGET_H - 8), (14, 15, 18), 2, lineType=cv2.LINE_AA)
    
    # Inner display recess plate
    cv2.rectangle(img, (18, 18), (TARGET_W - 19, TARGET_H - 19), (12, 13, 16), -1)
    # Subtle inner metallic texture
    inner_noise = np.random.normal(0, 2.5, (TARGET_H - 38, TARGET_W - 38)).astype(np.float32)
    inner_noise = cv2.GaussianBlur(inner_noise, (9, 1), 0)
    for c in range(3):
        roi = img[19:TARGET_H-19, 19:TARGET_W-19, c].astype(np.float32) + inner_noise
        img[19:TARGET_H-19, 19:TARGET_W-19, c] = np.clip(roi, 10, 32).astype(np.uint8)
        
    # Apply incandescent molten fire metal glow around the inner bezel
    img = add_fire_metal_glow(img, (17, 17, TARGET_W - 18, TARGET_H - 18), intensity=1.1)
    
    # Also add fiery glow accent on outer chamfer corners
    img = add_fire_metal_glow(img, (5, 5, TARGET_W - 6, TARGET_H - 6), intensity=0.6)
    
    # Vertical Dividers
    img = draw_vertical_dividers(img, [152, 305], y1=32, y2=164)
    
    # Top Center: SimForge Anvil & Hammer Glowing Emblem
    # Resize anvil emblem to fit gracefully in the top center bar
    badge_size = 42
    anvil_resized = cv2.resize(anvil_crop, (badge_size, badge_size), interpolation=cv2.INTER_LANCZOS4)
    
    # Circular alpha mask for badge
    mask = np.zeros((badge_size, badge_size), dtype=np.float32)
    cv2.circle(mask, (badge_size//2, badge_size//2), badge_size//2 - 1, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    
    bx = (TARGET_W - badge_size) // 2
    by = 4
    
    # Glow backing behind badge
    cv2.circle(img, (TARGET_W//2, by + badge_size//2), 24, (10, 60, 180), -1, lineType=cv2.LINE_AA)
    
    roi = img[by:by+badge_size, bx:bx+badge_size]
    blended = roi.astype(np.float32) * (1.0 - mask[:, :, np.newaxis]) + anvil_resized.astype(np.float32) * mask[:, :, np.newaxis]
    img[by:by+badge_size, bx:bx+badge_size] = np.clip(blended, 0, 255).astype(np.uint8)
    
    # SimForge tiny stencil text next to badge or at bottom
    cv2.putText(img, "SIMFORGE", (TARGET_W//2 - 32, TARGET_H - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (30, 140, 255), 1, lineType=cv2.LINE_AA)
    
    # Corner hex bolts
    img = draw_corner_hex_bolts(img, bolt_crop, margin=11, bolt_size=18)
    
    return img

def generate_variant_2_branding_header(bolt_crop, header_crop):
    """
    Variant 2: SimForge Fire Metal - Full Brand Banner Edition
    Features the full glowing "SimForge" wordmark and anvil emblem integrated into the top bar,
    with an intense heated orange fire metal glow around the outer chassis.
    """
    img = create_metallic_plate(TARGET_W, TARGET_H, (16, 18, 22))
    
    # Inner display recess
    cv2.rectangle(img, (16, 16), (TARGET_W - 17, TARGET_H - 17), (10, 12, 14), -1)
    
    # Fire Metal Glow
    img = add_fire_metal_glow(img, (15, 15, TARGET_W - 16, TARGET_H - 16), intensity=1.2)
    
    # Vertical Dividers
    img = draw_vertical_dividers(img, [152, 305], y1=38, y2=164)
    
    # Top Bar Branding Header
    # Scale header crop to fit width ~180px, height ~42px
    hw = 190
    hh = int(hw * (header_crop.shape[0] / header_crop.shape[1]))
    header_resized = cv2.resize(header_crop, (hw, hh), interpolation=cv2.INTER_LANCZOS4)
    
    hx = (TARGET_W - hw) // 2
    hy = 3
    
    # Black/dark background behind header
    cv2.rectangle(img, (hx - 8, hy), (hx + hw + 8, hy + hh + 2), (8, 9, 11), -1)
    cv2.rectangle(img, (hx - 8, hy), (hx + hw + 8, hy + hh + 2), (20, 90, 200), 1, lineType=cv2.LINE_AA)
    
    # Blend header
    img[hy:hy+hh, hx:hx+hw] = cv2.addWeighted(img[hy:hy+hh, hx:hx+hw], 0.1, header_resized, 0.9, 0)
    
    # Corner bolts
    img = draw_corner_hex_bolts(img, bolt_crop, margin=10, bolt_size=18)
    
    return img

def generate_variant_3_hardware_icons(bolt_crop, anvil_crop):
    """
    Variant 3: SimForge Fire Metal - Hardware Icons Edition
    Subtle glowing molten-wireframe hardware icons (Microchip for CPU, RAM stick for RAM,
    GPU cooling fan for GPU) watermarked at the bottom of each column.
    """
    img = create_metallic_plate(TARGET_W, TARGET_H, (18, 20, 24))
    cv2.rectangle(img, (16, 16), (TARGET_W - 17, TARGET_H - 17), (11, 12, 15), -1)
    img = add_fire_metal_glow(img, (15, 15, TARGET_W - 16, TARGET_H - 16), intensity=1.0)
    img = draw_vertical_dividers(img, [152, 305], y1=30, y2=164)
    
    # Draw wireframe hardware icons at bottom of columns (y ~ 140-175)
    # 1. CPU Chip at x=82, y=156
    chip_x, chip_y = 82, 158
    cv2.rectangle(img, (chip_x - 12, chip_y - 12), (chip_x + 12, chip_y + 12), (25, 120, 230), 1, lineType=cv2.LINE_AA)
    cv2.rectangle(img, (chip_x - 7, chip_y - 7), (chip_x + 7, chip_y + 7), (35, 150, 255), 1, lineType=cv2.LINE_AA)
    for p in [-8, -3, 2, 7]:
        cv2.line(img, (chip_x + p, chip_y - 15), (chip_x + p, chip_y - 12), (30, 130, 240), 1)
        cv2.line(img, (chip_x + p, chip_y + 12), (chip_x + p, chip_y + 15), (30, 130, 240), 1)
        cv2.line(img, (chip_x - 15, chip_y + p), (chip_x - 12, chip_y + p), (30, 130, 240), 1)
        cv2.line(img, (chip_x + 12, chip_y + p), (chip_x + 15, chip_y + p), (30, 130, 240), 1)
        
    # 2. RAM Stick at x=229, y=158
    ram_x, ram_y = 229, 158
    cv2.rectangle(img, (ram_x - 18, ram_y - 8), (ram_x + 18, ram_y + 8), (25, 120, 230), 1, lineType=cv2.LINE_AA)
    for bx in [-13, -7, -1, 5, 11]:
        cv2.rectangle(img, (ram_x + bx, ram_y - 5), (ram_x + bx + 4, ram_y + 3), (35, 150, 255), 1, lineType=cv2.LINE_AA)
        
    # 3. GPU Fan at x=376, y=158
    fan_x, fan_y = 376, 158
    cv2.circle(img, (fan_x, fan_y), 13, (25, 120, 230), 1, lineType=cv2.LINE_AA)
    cv2.circle(img, (fan_x, fan_y), 4, (35, 150, 255), -1, lineType=cv2.LINE_AA)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = np.radians(angle)
        x2 = int(fan_x + 11 * np.cos(rad))
        y2 = int(fan_y + 11 * np.sin(rad))
        cv2.line(img, (fan_x, fan_y), (x2, y2), (30, 140, 245), 1, lineType=cv2.LINE_AA)
        
    # Top Anvil Badge
    badge_size = 38
    anvil_resized = cv2.resize(anvil_crop, (badge_size, badge_size), interpolation=cv2.INTER_LANCZOS4)
    bx = (TARGET_W - badge_size) // 2
    by = 4
    mask = np.zeros((badge_size, badge_size), dtype=np.float32)
    cv2.circle(mask, (badge_size//2, badge_size//2), badge_size//2 - 1, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    roi = img[by:by+badge_size, bx:bx+badge_size]
    img[by:by+badge_size, bx:bx+badge_size] = (roi.astype(np.float32)*(1-mask[:,:,None]) + anvil_resized.astype(np.float32)*mask[:,:,None]).astype(np.uint8)
    
    img = draw_corner_hex_bolts(img, bolt_crop, margin=11, bolt_size=18)
    return img

def generate_variant_4_clean_fire_bezel(bolt_crop):
    """
    Variant 4: SimForge Fire Metal - Clean Industrial Forge Edition
    Ultra-clean dark forged steel interior for maximum dynamic text readability,
    framed by an intense molten fire metal perimeter glow with industrial corner brackets.
    """
    img = create_metallic_plate(TARGET_W, TARGET_H, (16, 18, 22))
    cv2.rectangle(img, (14, 14), (TARGET_W - 15, TARGET_H - 15), (10, 11, 13), -1)
    
    # Dual Fire Metal Glow: Outer warm aura + inner incandescent seam
    img = add_fire_metal_glow(img, (14, 14, TARGET_W - 15, TARGET_H - 15), intensity=1.35)
    
    # Tech brackets on corners
    c_len = 16
    for (cx, cy, dx, dy) in [(18, 18, 1, 1), (TARGET_W-19, 18, -1, 1), (18, TARGET_H-19, 1, -1), (TARGET_W-19, TARGET_H-19, -1, -1)]:
        cv2.line(img, (cx, cy), (cx + dx * c_len, cy), (20, 180, 255), 2, lineType=cv2.LINE_AA)
        cv2.line(img, (cx, cy), (cx, cy + dy * c_len), (20, 180, 255), 2, lineType=cv2.LINE_AA)
        
    img = draw_vertical_dividers(img, [152, 305], y1=24, y2=172)
    
    # Tech Stencil Header
    cv2.putText(img, "SIMFORGE // THERMAL & LOGIC TELEMETRY", (TARGET_W//2 - 128, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (30, 150, 255), 1, lineType=cv2.LINE_AA)
    
    img = draw_corner_hex_bolts(img, bolt_crop, margin=8, bolt_size=16)
    return img

def generate_variant_5_original_panel_remaster(bolt_crop, original_disp_crop, anvil_crop):
    """
    Variant 5: SimForge Fire Metal - Original Hardware Remaster
    Directly sourced from the physical Stream Deck panel display unit,
    with original text seamlessly inpainted out, scaled to exact 458x196,
    and upgraded with molten fire metal edge lighting and top SimForge medallion.
    """
    h, w = original_disp_crop.shape[:2]
    # Inpaint text in original display unit
    gray = cv2.cvtColor(original_disp_crop, cv2.COLOR_BGR2GRAY)
    text_mask = (gray > 120).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    text_dilated = cv2.dilate(text_mask, kernel, iterations=2)
    inner_mask = np.zeros((h, w), dtype=np.uint8)
    inner_mask[22:h-22, 25:w-25] = 255
    clean_mask = cv2.bitwise_and(text_dilated, inner_mask)
    disp_clean = cv2.inpaint(original_disp_crop, clean_mask, 5, cv2.INPAINT_TELEA)
    
    # Resize to exact 458 x 196
    img = cv2.resize(disp_clean, (TARGET_W, TARGET_H), interpolation=cv2.INTER_LANCZOS4)
    
    # Enhance with fiery molten edge radiance
    img = add_fire_metal_glow(img, (18, 18, TARGET_W - 19, TARGET_H - 19), intensity=0.9)
    
    # Add top SimForge emblem
    badge_size = 38
    anvil_resized = cv2.resize(anvil_crop, (badge_size, badge_size), interpolation=cv2.INTER_LANCZOS4)
    bx = (TARGET_W - badge_size) // 2
    by = 4
    mask = np.zeros((badge_size, badge_size), dtype=np.float32)
    cv2.circle(mask, (badge_size//2, badge_size//2), badge_size//2 - 1, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    roi = img[by:by+badge_size, bx:bx+badge_size]
    img[by:by+badge_size, bx:bx+badge_size] = (roi.astype(np.float32)*(1-mask[:,:,None]) + anvil_resized.astype(np.float32)*mask[:,:,None]).astype(np.uint8)
    
    return img

def main():
    print(f"Loading base assets for 458x196 widget backgrounds...")
    bolt_crop = cv2.imread(BOLT_PATH)
    anvil_crop = cv2.imread(ANVIL_PATH)
    header_crop = cv2.imread(HEADER_PATH)
    orig_disp = cv2.imread(ORIGINAL_DISP_PATH)
    
    variants = [
        ("01_simforge_fire_metal_molten_forge_458x196", "Molten Forge Edition (Featured)", generate_variant_1_molten_forge(bolt_crop, anvil_crop)),
        ("02_simforge_fire_metal_brand_banner_458x196", "Full Brand Banner Edition", generate_variant_2_branding_header(bolt_crop, header_crop)),
        ("03_simforge_fire_metal_hardware_icons_458x196", "Hardware Icons Edition", generate_variant_3_hardware_icons(bolt_crop, anvil_crop)),
        ("04_simforge_fire_metal_clean_forge_458x196", "Clean Industrial Forge Edition", generate_variant_4_clean_fire_bezel(bolt_crop)),
        ("05_simforge_fire_metal_panel_remaster_458x196", "Original Panel Remaster Edition", generate_variant_5_original_panel_remaster(bolt_crop, orig_disp, anvil_crop)),
    ]
    
    print(f"Rendering {len(variants)} bespoke SimForge Fire Metal backgrounds at exact 458x196 px...")
    
    for filename, title, img_bgr in variants:
        # 1. Save standard 458x196 PNG
        out_path = os.path.join(OUTPUT_DIR, f"{filename}.png")
        cv2.imwrite(out_path, img_bgr)
        print(f"Saved: {out_path} ({img_bgr.shape[1]}x{img_bgr.shape[0]} px)")
        
        # 2. Save 2x Hi-DPI (916x392 px)
        hidpi_path = os.path.join(HIDPI_DIR, f"{filename}_2x.png")
        img_2x = enhance_2x(img_bgr)
        cv2.imwrite(hidpi_path, img_2x)
        
        # 3. Save simulated live preview with dynamic numbers overlaid
        prev_path = os.path.join(PREVIEW_DIR, f"preview_{filename}.png")
        sim_preview = render_simulated_preview(img_bgr, title)
        cv2.imwrite(prev_path, sim_preview)
        
    print("All 458x196 SimForge Fire Metal widget backgrounds successfully rendered!")

if __name__ == "__main__":
    main()
