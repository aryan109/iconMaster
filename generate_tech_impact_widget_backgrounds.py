import os
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TARGET_W = 458
TARGET_H = 196

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_DIR = os.path.join(BASE_DIR, "output", "themes", "tech_impact")
MIRROR_THEME_DIR = os.path.join(BASE_DIR, "output", "themes", "Tech Impact")

OUTPUT_DIR = os.path.join(THEME_DIR, "widget_backgrounds")
HIDPI_DIR = os.path.join(OUTPUT_DIR, "high_dpi_2x")
PREVIEW_DIR = os.path.join(OUTPUT_DIR, "simulated_previews")
MIRROR_OUTPUT_DIR = os.path.join(MIRROR_THEME_DIR, "widget_backgrounds")

DISPLAY_PATH = os.path.join(THEME_DIR, "display_panel", "01_telemetry_display_unit.png")
HEADER_BANNER_PATH = os.path.join(THEME_DIR, "branding", "01_tech_impact_header_banner.png")
HEADER_EMBLEM_PATH = os.path.join(THEME_DIR, "branding", "02_tech_impact_header_emblem.png")
NEBULA_TL_PATH = os.path.join(THEME_DIR, "backgrounds_and_chassis", "04_cosmic_nebula_texture_tl.png")
NEBULA_TR_PATH = os.path.join(THEME_DIR, "backgrounds_and_chassis", "05_deep_space_blue_nebula_tr.png")
NEBULA_BL_PATH = os.path.join(THEME_DIR, "backgrounds_and_chassis", "06_cosmic_amber_plasma_bl.png")

COL_CENTERS = [95, 229, 362]
DIVIDER_XS = [156, 302]


def ensure_dirs():
    for d in [OUTPUT_DIR, HIDPI_DIR, PREVIEW_DIR]:
        os.makedirs(d, exist_ok=True)


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def rounded_rect_mask(w, h, x1, y1, x2, y2, radius, supersample=4):
    """Render an anti-aliased rounded rectangle mask in float32 [0.0, 1.0]."""
    sw, sh = w * supersample, h * supersample
    sx1, sy1 = int(round(x1 * supersample)), int(round(y1 * supersample))
    sx2, sy2 = int(round(x2 * supersample)), int(round(y2 * supersample))
    r = int(round(radius * supersample))
    r = max(1, min(r, (sx2 - sx1) // 2, (sy2 - sy1) // 2))

    canvas = np.zeros((sh, sw), dtype=np.uint8)
    cv2.rectangle(canvas, (sx1 + r, sy1), (sx2 - r, sy2), 255, -1)
    cv2.rectangle(canvas, (sx1, sy1 + r), (sx2, sy2 - r), 255, -1)
    for cx, cy in [
        (sx1 + r, sy1 + r),
        (sx2 - r, sy1 + r),
        (sx1 + r, sy2 - r),
        (sx2 - r, sy2 - r),
    ]:
        cv2.circle(canvas, (cx, cy), r, 255, -1)

    mask = cv2.resize(canvas, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return np.clip(mask, 0.0, 1.0)


def create_cosmic_alloy_base(neb_tl, neb_tr, neb_bl, nebula_strength=0.38):
    """Create dark forged cosmic metal base with corner nebula accents and clean central cavity."""
    yy, xx = np.mgrid[0:TARGET_H, 0:TARGET_W].astype(np.float32)
    nx = (xx - TARGET_W * 0.5) / (TARGET_W * 0.5)
    ny = (yy - TARGET_H * 0.5) / (TARGET_H * 0.5)
    rad = np.sqrt(nx * nx * 0.65 + ny * ny)

    base = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    base[:, :, 0] = 18.0 - 7.0 * np.clip(1.0 - rad, 0.0, 1.0)
    base[:, :, 1] = 10.0 - 3.5 * np.clip(1.0 - rad, 0.0, 1.0)
    base[:, :, 2] = 7.0 - 2.0 * np.clip(1.0 - rad, 0.0, 1.0)

    # Subtle horizontal brushed alloy grain
    rng = np.random.RandomState(17)
    row_noise = rng.normal(0.0, 1.4, (TARGET_H, 1)).astype(np.float32)
    fine_noise = rng.normal(0.0, 0.9, (TARGET_H, TARGET_W)).astype(np.float32)
    grain = row_noise * 0.75 + cv2.GaussianBlur(fine_noise, (7, 1), 0)
    base += grain[:, :, None]

    # Corner-restricted nebula clouds preserving dark interior contrast
    cavity_suppress = rounded_rect_mask(TARGET_W, TARGET_H, 26, 48, TARGET_W - 27, TARGET_H - 22, 16)
    cavity_suppress = cv2.GaussianBlur(cavity_suppress, (21, 21), 0)
    corner_weight = 1.0 - 0.88 * cavity_suppress

    neb_canvas = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    if neb_tl is not None:
        tl_r = cv2.resize(neb_tl, (220, 100), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        fade = np.outer(np.linspace(1.0, 0.0, 100), np.linspace(1.0, 0.0, 220)).astype(np.float32)
        neb_canvas[0:100, 0:220] += tl_r * fade[:, :, None] * 0.75

    if neb_tr is not None:
        tr_r = cv2.resize(neb_tr, (220, 100), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        fade = np.outer(np.linspace(1.0, 0.0, 100), np.linspace(0.0, 1.0, 220)).astype(np.float32)
        neb_canvas[0:100, TARGET_W - 220:TARGET_W] += tr_r * fade[:, :, None] * 0.75

    if neb_bl is not None:
        bl_r = cv2.resize(neb_bl, (140, 110), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        fade = np.outer(np.linspace(0.0, 1.0, 110), np.linspace(1.0, 0.0, 140)).astype(np.float32)
        neb_canvas[TARGET_H - 110:TARGET_H, 0:140] += bl_r * fade[:, :, None] * 0.85

        br_r = cv2.flip(bl_r, 1)
        fade_r = np.outer(np.linspace(0.0, 1.0, 110), np.linspace(0.0, 1.0, 140)).astype(np.float32)
        neb_canvas[TARGET_H - 110:TARGET_H, TARGET_W - 140:TARGET_W] += br_r * fade_r[:, :, None] * 1.05

    neb_canvas *= corner_weight[:, :, None] * nebula_strength
    base = 255.0 * (1.0 - (1.0 - np.clip(base, 0, 255) / 255.0) * (1.0 - np.clip(neb_canvas, 0, 255) / 255.0))
    return np.clip(base, 0, 255).astype(np.uint8)


def draw_cosmic_fire_metal_bezel(img_bgr, fire_weight=1.0, blue_weight=1.0, include_sparks=True):
    """Apply rounded dual-tone electric blue, cosmic violet, and fiery fire-metal hardware bezel."""
    out = img_bgr.astype(np.float32)

    outer_m = rounded_rect_mask(TARGET_W, TARGET_H, 1, 1, TARGET_W - 2, TARGET_H - 2, 22)
    outer_bevel = rounded_rect_mask(TARGET_W, TARGET_H, 4, 4, TARGET_W - 5, TARGET_H - 5, 20)
    inner_bevel = rounded_rect_mask(TARGET_W, TARGET_H, 10, 10, TARGET_W - 11, TARGET_H - 11, 16)
    cavity_m = rounded_rect_mask(TARGET_W, TARGET_H, 13, 13, TARGET_W - 14, TARGET_H - 14, 14)

    # Dark outer vignette margin so rounded corners stay crisp
    out *= (0.28 + 0.72 * outer_m[:, :, None])

    # Metallic stepped housing ring
    housing_ring = np.clip(outer_m - cavity_m, 0.0, 1.0)
    metal_sheen = np.clip(outer_bevel - inner_bevel, 0.0, 1.0)
    inner_lip_line = np.clip(inner_bevel - rounded_rect_mask(TARGET_W, TARGET_H, 12, 12, TARGET_W - 13, TARGET_H - 13, 15), 0.0, 1.0)
    outer_rim_line = np.clip(outer_m - rounded_rect_mask(TARGET_W, TARGET_H, 4, 4, TARGET_W - 5, TARGET_H - 5, 20), 0.0, 1.0)

    # Spatial dual-tone color gradient: electric cyan-blue -> cosmic violet -> fiery molten amber/orange
    u = np.linspace(0.0, 1.0, TARGET_W, dtype=np.float32)[None, :]
    v = np.linspace(0.0, 1.0, TARGET_H, dtype=np.float32)[:, None]

    # Diagonal balance from top-left (cool electric blue) to bottom-right / bottom lip (fiery fire-metal)
    fire_factor = np.clip(0.55 * u + 0.55 * v - 0.15, 0.0, 1.0)
    # Enhance left-bottom corner violet transition and bottom rim fire streak
    bottom_fire_boost = np.clip((v - 0.72) / 0.28, 0.0, 1.0) * 0.35
    fire_t = np.clip(fire_factor + bottom_fire_boost, 0.0, 1.0)

    cyan_bgr = np.array([255.0, 185.0, 20.0], dtype=np.float32) * blue_weight
    violet_bgr = np.array([205.0, 50.0, 125.0], dtype=np.float32) * (0.5 * blue_weight + 0.5 * fire_weight)
    amber_bgr = np.array([18.0, 115.0, 255.0], dtype=np.float32) * fire_weight
    hot_core_bgr = np.array([110.0, 205.0, 255.0], dtype=np.float32) * fire_weight

    ring_color = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    low_band = (fire_t < 0.36)[:, :, None]
    t1 = np.clip(fire_t / 0.36, 0.0, 1.0)[:, :, None]
    t2 = np.clip((fire_t - 0.36) / 0.64, 0.0, 1.0)[:, :, None]

    cool_mix = cyan_bgr * (1.0 - t1) + violet_bgr * t1
    warm_mix = violet_bgr * (1.0 - t2) + amber_bgr * t2
    ring_color = np.where(low_band, cool_mix, warm_mix)

    # Subtle steel-brushed ring base inside bevel
    out += housing_ring[:, :, None] * np.array([34.0, 28.0, 26.0], dtype=np.float32)
    out += metal_sheen[:, :, None] * np.array([26.0, 22.0, 22.0], dtype=np.float32)

    # Neon perimeter trace lines + multi-scale bloom
    trace_energy = (outer_rim_line * 0.95 + inner_lip_line * 1.15)[:, :, None] * ring_color
    tight_glow = cv2.GaussianBlur(trace_energy, (0, 0), sigmaX=2.2, sigmaY=2.2)
    wide_glow = cv2.GaussianBlur(trace_energy, (0, 0), sigmaX=9.5, sigmaY=9.5)

    # Hot specular highlights on top-left cyan arc and bottom-right fiery rim
    hot_tl = np.exp(-(((u - 0.14) / 0.16) ** 2 + ((v - 0.08) / 0.14) ** 2))
    hot_br = np.exp(-(((u - 0.86) / 0.18) ** 2 + ((v - 0.92) / 0.16) ** 2))
    hot_highlight = (
        (outer_rim_line + inner_lip_line * 0.8)[:, :, None]
        * (hot_tl[:, :, None] * np.array([255.0, 240.0, 190.0], dtype=np.float32) * 0.85
           + hot_br[:, :, None] * hot_core_bgr * 0.95)
    )

    # Confine inner bloom slightly so telemetry interior stays dark and legible
    interior_bloom_damp = 1.0 - 0.72 * rounded_rect_mask(TARGET_W, TARGET_H, 24, 24, TARGET_W - 25, TARGET_H - 25, 12)
    out += trace_energy * 0.75 + tight_glow * 0.85 + wide_glow * 0.65 * interior_bloom_damp[:, :, None] + hot_highlight

    if include_sparks:
        rng = np.random.RandomState(42)
        sparks = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
        safe_zone_mask = np.ones((TARGET_H, TARGET_W), dtype=np.float32)
        safe_zone_mask[44:166, 26:TARGET_W - 26] = 0.0
        # Keep sparks off the bright neon tube centerlines so no white dots sit on the bezel strokes
        tube_exclusion = np.clip(outer_rim_line + inner_lip_line, 0.0, 1.0)
        for _ in range(70):
            sx = int(rng.randint(15, TARGET_W - 15))
            sy = int(rng.randint(14, TARGET_H - 14))
            if safe_zone_mask[sy, sx] < 0.5 or tube_exclusion[sy, sx] > 0.25:
                continue
            is_warm = (sx / float(TARGET_W) + sy / float(TARGET_H)) > 0.85 or rng.rand() < 0.55
            col = (45, 175, 255) if is_warm else (255, 210, 95)
            intensity = float(rng.uniform(0.25, 0.62))
            cv2.circle(sparks, (sx, sy), 1, (col[0] * intensity, col[1] * intensity, col[2] * intensity), -1, lineType=cv2.LINE_AA)
        sparks = cv2.GaussianBlur(sparks, (0, 0), sigmaX=0.8) + sparks * 0.55
        out += sparks * 0.55

    return np.clip(out, 0, 255).astype(np.uint8)


def composite_glowing_asset(canvas_bgr, asset_bgr, cx, top_y, target_h, edge_feather=7, boost=1.12):
    """Seamlessly blend dark-backed logo or banner onto canvas without visible rectangle borders."""
    h, w = asset_bgr.shape[:2]
    scale = float(target_h) / float(h)
    tw = max(1, int(round(w * scale)))
    th = max(1, target_h)
    resized = cv2.resize(asset_bgr, (tw, th), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)

    # Estimate dark background floor from asset perimeter pixels
    border_pixels = np.concatenate([resized[:2, :].reshape(-1, 3), resized[-2:, :].reshape(-1, 3)], axis=0)
    bg_floor = np.median(border_pixels, axis=0)
    clean_fg = np.clip(resized - bg_floor[None, None, :] * 1.15, 0.0, 255.0) * boost
    clean_fg = np.clip(clean_fg, 0.0, 255.0)

    # Soft elliptical/rectangular edge fade
    fx = np.ones(tw, dtype=np.float32)
    fy = np.ones(th, dtype=np.float32)
    ef_x = min(edge_feather, tw // 4)
    ef_y = min(edge_feather, th // 4)
    if ef_x > 0:
        ramp = np.linspace(0.0, 1.0, ef_x, dtype=np.float32)
        fx[:ef_x] = ramp
        fx[-ef_x:] = ramp[::-1]
    if ef_y > 0:
        ramp = np.linspace(0.0, 1.0, ef_y, dtype=np.float32)
        fy[:ef_y] = ramp
        fy[-ef_y:] = ramp[::-1]
    box_fade = np.outer(fy, fx)

    lum = clean_fg.max(axis=2)
    alpha = np.clip((lum - 8.0) / 48.0, 0.0, 1.0) * box_fade

    x1 = int(round(cx - tw * 0.5))
    y1 = int(round(top_y))
    x2 = x1 + tw
    y2 = y1 + th

    # Clip to canvas bounds safely
    cx1, cy1 = max(0, x1), max(0, y1)
    cx2, cy2 = min(TARGET_W, x2), min(TARGET_H, y2)
    if cx2 <= cx1 or cy2 <= cy1:
        return canvas_bgr

    ax1, ay1 = cx1 - x1, cy1 - y1
    ax2, ay2 = ax1 + (cx2 - cx1), ay1 + (cy2 - cy1)

    fg_patch = clean_fg[ay1:ay2, ax1:ax2]
    a_patch = alpha[ay1:ay2, ax1:ax2][:, :, None]
    out = canvas_bgr.astype(np.float32)
    roi = out[cy1:cy2, cx1:cx2]

    # Blend core with alpha + add subtle screen glow for luminescence
    blended = roi * (1.0 - a_patch * 0.85) + fg_patch * a_patch + (1.0 - roi / 255.0) * fg_patch * 0.25 * box_fade[ay1:ay2, ax1:ax2][:, :, None]
    out[cy1:cy2, cx1:cx2] = np.clip(blended, 0, 255)
    return out.astype(np.uint8)


def draw_cosmic_dividers(img_bgr, xs=DIVIDER_XS, y1=56, y2=162, intensity=0.85):
    """Draw smooth tapering vertical dividers between CPU, RAM, and GPU zones."""
    overlay = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    span = max(1, y2 - y1)
    for y in range(y1, y2 + 1):
        t = (y - y1) / float(span)
        taper = np.sin(np.pi * t) ** 0.75
        if t < 0.5:
            u = t * 2.0
            col = np.array([255.0 * (1 - u) + 210.0 * u, 185.0 * (1 - u) + 90.0 * u, 40.0 * (1 - u) + 180.0 * u], dtype=np.float32)
        else:
            u = (t - 0.5) * 2.0
            col = np.array([210.0 * (1 - u) + 45.0 * u, 90.0 * (1 - u) + 165.0 * u, 180.0 * (1 - u) + 255.0 * u], dtype=np.float32)
        for dx in xs:
            overlay[y, dx] = col * taper * intensity
            overlay[y, dx - 1] += col * taper * intensity * 0.28
            overlay[y, dx + 1] += col * taper * intensity * 0.28

    glow = cv2.GaussianBlur(overlay, (5, 3), 0)
    out = img_bgr.astype(np.float32) + overlay * 0.65 + glow * 0.55
    return np.clip(out, 0, 255).astype(np.uint8)


def draw_flanking_lines(img_bgr, center_x, y, inner_gap=26, outer_x=44, left_col=(255, 190, 40), right_col=(35, 155, 255)):
    """Draw sleek tapering horizontal accent hairlines flanking top emblem."""
    overlay = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    # Left line from outer_x to center_x - inner_gap
    lx1, lx2 = outer_x, center_x - inner_gap
    if lx2 > lx1:
        for x in range(lx1, lx2 + 1):
            t = (x - lx1) / float(lx2 - lx1)
            w = np.sin(np.pi * t) ** 0.6
            overlay[y, x] = np.array(left_col, dtype=np.float32) * w * 0.85
    # Right line from center_x + inner_gap to TARGET_W - outer_x
    rx1, rx2 = center_x + inner_gap, TARGET_W - outer_x
    if rx2 > rx1:
        for x in range(rx1, rx2 + 1):
            t = (x - rx1) / float(rx2 - rx1)
            w = np.sin(np.pi * t) ** 0.6
            overlay[y, x] = np.array(right_col, dtype=np.float32) * w * 0.85

    glow = cv2.GaussianBlur(overlay, (0, 0), sigmaX=1.6, sigmaY=1.2)
    out = img_bgr.astype(np.float32) + overlay * 0.7 + glow * 0.7
    return np.clip(out, 0, 255).astype(np.uint8)


def draw_neon_hardware_icons(img_bgr, cy=114):
    """Draw 4x supersampled neon CPU, RAM, and GPU icons inside y=105..123 gap."""
    ss = 4
    hi = np.zeros((TARGET_H * ss, TARGET_W * ss, 3), dtype=np.float32)
    core = np.zeros((TARGET_H * ss, TARGET_W * ss, 3), dtype=np.float32)

    def pt(x, y):
        return (int(round(x * ss)), int(round(y * ss)))

    lw = 2 * ss
    thin_lw = max(2, int(round(1.4 * ss)))

    # 1. CPU Microchip (Electric Cyan) centered at (95, cy)
    cx_cpu = COL_CENTERS[0]
    cyan = (255.0, 215.0, 20.0)
    white_cyan = (255.0, 245.0, 175.0)
    bw = 7.0
    cv2.rectangle(hi, pt(cx_cpu - bw, cy - bw), pt(cx_cpu + bw, cy + bw), cyan, lw, lineType=cv2.LINE_AA)
    cv2.rectangle(core, pt(cx_cpu - bw, cy - bw), pt(cx_cpu + bw, cy + bw), white_cyan, thin_lw, lineType=cv2.LINE_AA)
    # Inner die square
    di = 3.2
    cv2.rectangle(hi, pt(cx_cpu - di, cy - di), pt(cx_cpu + di, cy + di), cyan, thin_lw, lineType=cv2.LINE_AA)
    cv2.rectangle(core, pt(cx_cpu - di, cy - di), pt(cx_cpu + di, cy + di), white_cyan, max(1, ss // 2), lineType=cv2.LINE_AA)
    # 3 pins per side
    for d in [-3.8, 0.0, 3.8]:
        cv2.line(hi, pt(cx_cpu + d, cy - bw - 3.0), pt(cx_cpu + d, cy - bw), cyan, thin_lw, lineType=cv2.LINE_AA)
        cv2.line(hi, pt(cx_cpu + d, cy + bw), pt(cx_cpu + d, cy + bw + 3.0), cyan, thin_lw, lineType=cv2.LINE_AA)
        cv2.line(hi, pt(cx_cpu - bw - 3.0, cy + d), pt(cx_cpu - bw, cy + d), cyan, thin_lw, lineType=cv2.LINE_AA)
        cv2.line(hi, pt(cx_cpu + bw, cy + d), pt(cx_cpu + bw + 3.0, cy + d), cyan, thin_lw, lineType=cv2.LINE_AA)

    # 2. RAM DIMM Module (Cosmic Neon Violet) centered at (229, cy)
    cx_ram = COL_CENTERS[1]
    violet = (245.0, 110.0, 200.0)
    white_violet = (255.0, 210.0, 245.0)
    rw, rh = 12.5, 5.5
    cv2.rectangle(hi, pt(cx_ram - rw, cy - rh - 1.0), pt(cx_ram + rw, cy + rh - 1.0), violet, lw, lineType=cv2.LINE_AA)
    cv2.rectangle(core, pt(cx_ram - rw, cy - rh - 1.0), pt(cx_ram + rw, cy + rh - 1.0), white_violet, thin_lw, lineType=cv2.LINE_AA)
    # 3 DRAM chips inside
    for ox in [-7.0, 0.0, 7.0]:
        cv2.rectangle(hi, pt(cx_ram + ox - 2.2, cy - 3.4), pt(cx_ram + ox + 2.2, cy + 1.4), violet, thin_lw, lineType=cv2.LINE_AA)
        cv2.rectangle(core, pt(cx_ram + ox - 2.2, cy - 3.4), pt(cx_ram + ox + 2.2, cy + 1.4), white_violet, max(1, ss // 2), lineType=cv2.LINE_AA)
    # Bottom gold-finger contact notches
    for ox in [-8.5, -4.5, 2.5, 6.5, 10.0]:
        cv2.line(hi, pt(cx_ram + ox, cy + rh - 0.5), pt(cx_ram + ox, cy + rh + 2.2), violet, thin_lw, lineType=cv2.LINE_AA)

    # 3. GPU Card (Fiery Golden Amber) centered at (362, cy)
    cx_gpu = COL_CENTERS[2]
    amber = (35.0, 175.0, 255.0)
    white_amber = (165.0, 235.0, 255.0)
    gw, gh = 11.5, 6.2
    cv2.rectangle(hi, pt(cx_gpu - gw + 1.5, cy - gh), pt(cx_gpu + gw, cy + gh), amber, lw, lineType=cv2.LINE_AA)
    cv2.rectangle(core, pt(cx_gpu - gw + 1.5, cy - gh), pt(cx_gpu + gw, cy + gh), white_amber, thin_lw, lineType=cv2.LINE_AA)
    # Left I/O bracket spine
    cv2.line(hi, pt(cx_gpu - gw - 1.5, cy - gh - 2.2), pt(cx_gpu - gw - 1.5, cy + gh + 1.5), amber, thin_lw, lineType=cv2.LINE_AA)
    cv2.line(hi, pt(cx_gpu - gw - 3.2, cy - gh - 2.2), pt(cx_gpu - gw - 1.5, cy - gh - 2.2), amber, thin_lw, lineType=cv2.LINE_AA)
    # Right cooling fan + inner hub + spokes
    fcx, fcy, fr = cx_gpu + 4.2, cy, 4.2
    cv2.circle(hi, pt(fcx, fcy), int(round(fr * ss)), amber, thin_lw, lineType=cv2.LINE_AA)
    cv2.circle(core, pt(fcx, fcy), int(round(fr * ss)), white_amber, max(1, ss // 2), lineType=cv2.LINE_AA)
    cv2.circle(hi, pt(fcx, fcy), int(round(1.5 * ss)), amber, -1, lineType=cv2.LINE_AA)
    for ang in [0, 60, 120]:
        rad_a = np.deg2rad(ang)
        dx, dy = np.cos(rad_a) * fr, np.sin(rad_a) * fr
        cv2.line(hi, pt(fcx - dx, fcy - dy), pt(fcx + dx, fcy + dy), amber, max(1, ss // 2), lineType=cv2.LINE_AA)
    # Left auxiliary indicator / secondary rotor ring
    cv2.circle(hi, pt(cx_gpu - 4.8, cy), int(round(2.4 * ss)), amber, thin_lw, lineType=cv2.LINE_AA)

    hi_small = cv2.resize(hi, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)
    core_small = cv2.resize(core, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)
    bloom = cv2.GaussianBlur(hi_small, (0, 0), sigmaX=2.4, sigmaY=2.4)

    out = img_bgr.astype(np.float32) + bloom * 0.75 + hi_small * 0.72 + core_small * 0.42
    return np.clip(out, 0, 255).astype(np.uint8)


def draw_crisp_text_pil(img_bgr, text, center_x, center_y, font_size=10, color_rgb=(215, 225, 240), alpha=0.82, letter_spacing=0):
    """Draw crisp anti-aliased text via Pillow centered at (center_x, center_y)."""
    pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], font_size)

    a_val = int(round(255 * alpha))
    rgba = (color_rgb[0], color_rgb[1], color_rgb[2], a_val)

    if letter_spacing <= 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = int(round(center_x - tw * 0.5 - bbox[0]))
        ty = int(round(center_y - th * 0.5 - bbox[1]))
        draw.text((tx, ty), text, font=font, fill=rgba)
    else:
        widths = []
        max_h = 0
        min_top = 999
        for ch in text:
            bb = draw.textbbox((0, 0), ch, font=font)
            widths.append((bb[2] - bb[0], bb[0], bb[1], bb[3]))
            max_h = max(max_h, bb[3] - bb[1])
            min_top = min(min_top, bb[1])
        total_w = sum(w[0] for w in widths) + letter_spacing * max(0, len(text) - 1)
        cur_x = center_x - total_w * 0.5
        ty = center_y - max_h * 0.5 - min_top
        for idx, ch in enumerate(text):
            w_ch, ox, _, _ = widths[idx]
            draw.text((int(round(cur_x - ox)), int(round(ty))), ch, font=font, fill=rgba)
            cur_x += w_ch + letter_spacing

    composed = Image.alpha_composite(pil_img, overlay).convert("RGB")
    return cv2.cvtColor(np.array(composed), cv2.COLOR_RGB2BGR)


def generate_variant_1_cosmic_fire_metal(neb_tl, neb_tr, neb_bl, emblem_bgr):
    """Variant 1: Featured Cosmic Plasma & Fire-Metal Edition."""
    img = create_cosmic_alloy_base(neb_tl, neb_tr, neb_bl, nebula_strength=0.45)
    img = draw_cosmic_fire_metal_bezel(img, fire_weight=1.12, blue_weight=1.05, include_sparks=True)
    img = draw_flanking_lines(img, TARGET_W // 2, 31, inner_gap=26, outer_x=42)
    img = composite_glowing_asset(img, emblem_bgr, TARGET_W // 2, top_y=15, target_h=34, edge_feather=7, boost=1.18)
    img = draw_cosmic_dividers(img, DIVIDER_XS, y1=56, y2=156, intensity=0.88)
    img = draw_crisp_text_pil(img, "TECH IMPACT", TARGET_W // 2, 171, font_size=9, color_rgb=(255, 200, 125), alpha=0.85, letter_spacing=3)
    return img


def generate_variant_2_brand_banner(neb_tl, neb_tr, neb_bl, banner_bgr):
    """Variant 2: Full Brand Header Banner Edition."""
    img = create_cosmic_alloy_base(neb_tl, neb_tr, neb_bl, nebula_strength=0.38)
    img = draw_cosmic_fire_metal_bezel(img, fire_weight=1.10, blue_weight=1.05, include_sparks=True)
    img = composite_glowing_asset(img, banner_bgr, TARGET_W // 2, top_y=15, target_h=34, edge_feather=10, boost=1.18)
    # Subtle horizontal separator under banner (safe above y=70)
    overlay = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    for x in range(44, TARGET_W - 44):
        t = (x - 44) / float(TARGET_W - 88)
        fade = np.sin(np.pi * t) ** 0.7
        col = np.array([255.0 * (1 - t) + 35.0 * t, 185.0 * (1 - t) + 150.0 * t, 45.0 * (1 - t) + 255.0 * t], dtype=np.float32)
        overlay[54, x] = col * fade * 0.72
    img = np.clip(img.astype(np.float32) + cv2.GaussianBlur(overlay, (0, 0), sigmaX=1.2) + overlay * 0.5, 0, 255).astype(np.uint8)
    img = draw_cosmic_dividers(img, DIVIDER_XS, y1=60, y2=166, intensity=0.85)
    return img


def generate_variant_3_hardware_icons(neb_tl, neb_tr, neb_bl, emblem_bgr):
    """Variant 3: Neon Hardware Icons Edition (CPU/RAM/GPU glyphs cleanly between numbers & labels)."""
    img = create_cosmic_alloy_base(neb_tl, neb_tr, neb_bl, nebula_strength=0.34)
    img = draw_cosmic_fire_metal_bezel(img, fire_weight=1.05, blue_weight=1.05, include_sparks=False)
    img = draw_flanking_lines(img, TARGET_W // 2, 30, inner_gap=24, outer_x=52)
    img = composite_glowing_asset(img, emblem_bgr, TARGET_W // 2, top_y=15, target_h=32, edge_feather=7, boost=1.15)
    img = draw_cosmic_dividers(img, DIVIDER_XS, y1=52, y2=164, intensity=0.82)
    img = draw_neon_hardware_icons(img, cy=114)

    # Subtle color-coded bottom rim aura under CPU (cyan), RAM (violet), GPU (amber)
    aura = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:TARGET_H, 0:TARGET_W].astype(np.float32)
    rim_cols = [
        (COL_CENTERS[0], np.array([255.0, 195.0, 25.0], dtype=np.float32)),
        (COL_CENTERS[1], np.array([240.0, 90.0, 195.0], dtype=np.float32)),
        (COL_CENTERS[2], np.array([30.0, 165.0, 255.0], dtype=np.float32)),
    ]
    for cx, col in rim_cols:
        g = np.exp(-(((xx - cx) / 38.0) ** 2 + ((yy - 180.0) / 10.0) ** 2))
        aura += g[:, :, None] * col[None, None, :] * 0.28
    img = np.clip(img.astype(np.float32) + aura, 0, 255).astype(np.uint8)
    return img


def generate_variant_4_clean_fire_bezel(neb_tl, neb_tr, neb_bl):
    """Variant 4: Clean Max-Contrast Fire-Metal Bezel Edition."""
    img = create_cosmic_alloy_base(neb_tl, neb_tr, neb_bl, nebula_strength=0.14)
    # Darken central readout box extra deeply for peak number contrast
    center_dark = rounded_rect_mask(TARGET_W, TARGET_H, 24, 34, TARGET_W - 25, TARGET_H - 22, 14)
    img = np.clip(img.astype(np.float32) * (1.0 - 0.35 * center_dark[:, :, None]), 0, 255).astype(np.uint8)
    img = draw_cosmic_fire_metal_bezel(img, fire_weight=1.28, blue_weight=0.92, include_sparks=True)

    # Futuristic glowing HUD corner L-brackets
    brackets = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    bx1, by1, bx2, by2 = 24, 22, TARGET_W - 25, TARGET_H - 23
    blen = 16
    corners = [
        (bx1, by1, 1, 1, (255.0, 210.0, 50.0)),
        (bx2, by1, -1, 1, (45.0, 175.0, 255.0)),
        (bx1, by2, 1, -1, (220.0, 100.0, 210.0)),
        (bx2, by2, -1, -1, (45.0, 175.0, 255.0)),
    ]
    for x, y, dx, dy, col in corners:
        cv2.line(brackets, (x, y), (x + dx * blen, y), col, 2, lineType=cv2.LINE_AA)
        cv2.line(brackets, (x, y), (x, y + dy * blen), col, 2, lineType=cv2.LINE_AA)
    b_glow = cv2.GaussianBlur(brackets, (0, 0), sigmaX=2.2)
    img = np.clip(img.astype(np.float32) + brackets * 0.72 + b_glow * 0.65, 0, 255).astype(np.uint8)

    img = draw_cosmic_dividers(img, DIVIDER_XS, y1=52, y2=166, intensity=0.80)
    img = draw_crisp_text_pil(img, "TECH IMPACT // SYSTEM TELEMETRY", TARGET_W // 2, 24, font_size=10, color_rgb=(255, 200, 115), alpha=0.88, letter_spacing=1)
    return img


def generate_variant_5_panel_remaster(orig_disp_bgr, emblem_bgr):
    """Variant 5: Original Tech Impact Hardware Panel Remaster with clean feathered cavity replacement."""
    upscaled = cv2.resize(orig_disp_bgr, (TARGET_W, TARGET_H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)

    # Smooth rounded interior replacement mask clearing all original 9%/56%/23% numbers and icons cleanly
    inner_mask = rounded_rect_mask(TARGET_W, TARGET_H, 23, 19, TARGET_W - 24, TARGET_H - 22, 14)
    inner_mask = cv2.GaussianBlur(inner_mask, (0, 0), sigmaX=4.2, sigmaY=4.2)

    yy, xx = np.mgrid[0:TARGET_H, 0:TARGET_W].astype(np.float32)
    nx = (xx - TARGET_W * 0.5) / (TARGET_W * 0.5)
    ny = (yy - TARGET_H * 0.5) / (TARGET_H * 0.5)
    rad = np.sqrt(nx * nx * 0.6 + ny * ny)
    clean_cavity = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.float32)
    clean_cavity[:, :, 0] = 18.0 - 7.0 * np.clip(1.0 - rad, 0.0, 1.0)
    clean_cavity[:, :, 1] = 10.0 - 3.5 * np.clip(1.0 - rad, 0.0, 1.0)
    clean_cavity[:, :, 2] = 6.5 - 2.0 * np.clip(1.0 - rad, 0.0, 1.0)

    blended = upscaled * (1.0 - inner_mask[:, :, None]) + clean_cavity * inner_mask[:, :, None]

    # Reinforce authentic fiery fire-metal bottom-right glow + electric-blue top-left rim radiance
    outer_rim = rounded_rect_mask(TARGET_W, TARGET_H, 2, 2, TARGET_W - 3, TARGET_H - 3, 22) - rounded_rect_mask(TARGET_W, TARGET_H, 16, 15, TARGET_W - 17, TARGET_H - 17, 15)
    outer_rim = np.clip(outer_rim, 0.0, 1.0)
    u = xx / float(TARGET_W)
    v = yy / float(TARGET_H)
    fire_boost = np.exp(-(((u - 0.88) / 0.20) ** 2 + ((v - 0.85) / 0.25) ** 2))
    blue_boost = np.exp(-(((u - 0.14) / 0.22) ** 2 + ((v - 0.18) / 0.25) ** 2))
    rim_enhance = outer_rim[:, :, None] * (
        fire_boost[:, :, None] * np.array([25.0, 120.0, 240.0], dtype=np.float32) * 0.45
        + blue_boost[:, :, None] * np.array([240.0, 165.0, 20.0], dtype=np.float32) * 0.35
    )
    blended += cv2.GaussianBlur(rim_enhance, (0, 0), sigmaX=3.5) + rim_enhance * 0.45

    img = np.clip(blended, 0, 255).astype(np.uint8)
    img = draw_cosmic_dividers(img, DIVIDER_XS, y1=56, y2=158, intensity=0.82)
    img = composite_glowing_asset(img, emblem_bgr, TARGET_W // 2, top_y=20, target_h=30, edge_feather=6, boost=1.15)
    return img


def enhance_2x(img_bgr):
    """Upscale 458x196 -> 916x392 via Lanczos4 with crisp detail sharpening."""
    up = cv2.resize(img_bgr, (TARGET_W * 2, TARGET_H * 2), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    blur = cv2.GaussianBlur(up, (0, 0), sigmaX=1.0, sigmaY=1.0)
    sharp = up * 1.22 - blur * 0.22
    return np.clip(sharp, 0, 255).astype(np.uint8)


def render_simulated_preview(bg_bgr):
    """Render realistic preview simulating Stream Deck / Ulanzi dynamic white telemetry numbers."""
    pil_bg = Image.fromarray(cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    shadow_layer = Image.new("RGBA", pil_bg.size, (0, 0, 0, 0))
    text_layer = Image.new("RGBA", pil_bg.size, (0, 0, 0, 0))

    s_draw = ImageDraw.Draw(shadow_layer)
    t_draw = ImageDraw.Draw(text_layer)

    num_font = load_font(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], 29)
    lbl_font = load_font(["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"], 17)

    metrics = [
        (COL_CENTERS[0], "9%", "CPU"),
        (COL_CENTERS[1], "56%", "RAM"),
        (COL_CENTERS[2], "23%", "GPU"),
    ]

    for cx, pct, lbl in metrics:
        bb_n = t_draw.textbbox((0, 0), pct, font=num_font)
        nw = bb_n[2] - bb_n[0]
        nh = bb_n[3] - bb_n[1]
        nx = int(round(cx - nw * 0.5 - bb_n[0]))
        ny = int(round(85 - nh * 0.5 - bb_n[1]))
        s_draw.text((nx + 1, ny + 2), pct, font=num_font, fill=(0, 0, 0, 210))
        t_draw.text((nx, ny), pct, font=num_font, fill=(248, 251, 255, 255))

        bb_l = t_draw.textbbox((0, 0), lbl, font=lbl_font)
        lw = bb_l[2] - bb_l[0]
        lh = bb_l[3] - bb_l[1]
        lx = int(round(cx - lw * 0.5 - bb_l[0]))
        ly = int(round(138 - lh * 0.5 - bb_l[1]))
        s_draw.text((lx + 1, ly + 1), lbl, font=lbl_font, fill=(0, 0, 0, 200))
        t_draw.text((lx, ly), lbl, font=lbl_font, fill=(215, 222, 232, 255))

    composed = Image.alpha_composite(pil_bg, shadow_layer)
    composed = Image.alpha_composite(composed, text_layer).convert("RGB")
    return cv2.cvtColor(np.array(composed), cv2.COLOR_RGB2BGR)


def mirror_widget_folder():
    """Mirror generated widget_backgrounds into output/themes/Tech Impact cleanly."""
    os.makedirs(MIRROR_THEME_DIR, exist_ok=True)
    shutil.copytree(OUTPUT_DIR, MIRROR_OUTPUT_DIR, dirs_exist_ok=True)
    print(f"Mirrored widget_backgrounds to: {MIRROR_OUTPUT_DIR}")


def main():
    ensure_dirs()
    orig_disp = cv2.imread(DISPLAY_PATH)
    banner = cv2.imread(HEADER_BANNER_PATH)
    emblem = cv2.imread(HEADER_EMBLEM_PATH)
    neb_tl = cv2.imread(NEBULA_TL_PATH)
    neb_tr = cv2.imread(NEBULA_TR_PATH)
    neb_bl = cv2.imread(NEBULA_BL_PATH)

    missing = [
        name for name, arr in [
            (DISPLAY_PATH, orig_disp),
            (HEADER_BANNER_PATH, banner),
            (HEADER_EMBLEM_PATH, emblem),
            (NEBULA_TL_PATH, neb_tl),
            (NEBULA_TR_PATH, neb_tr),
            (NEBULA_BL_PATH, neb_bl),
        ] if arr is None
    ]
    if missing:
        raise FileNotFoundError(f"Missing required Tech Impact source assets: {missing}")

    variants = [
        ("01_tech_impact_cosmic_fire_metal_458x196", generate_variant_1_cosmic_fire_metal(neb_tl, neb_tr, neb_bl, emblem)),
        ("02_tech_impact_brand_banner_458x196", generate_variant_2_brand_banner(neb_tl, neb_tr, neb_bl, banner)),
        ("03_tech_impact_hardware_icons_458x196", generate_variant_3_hardware_icons(neb_tl, neb_tr, neb_bl, emblem)),
        ("04_tech_impact_clean_fire_bezel_458x196", generate_variant_4_clean_fire_bezel(neb_tl, neb_tr, neb_bl)),
        ("05_tech_impact_panel_remaster_458x196", generate_variant_5_panel_remaster(orig_disp, emblem)),
    ]

    for filename, img_bgr in variants:
        std_path = os.path.join(OUTPUT_DIR, f"{filename}.png")
        hidpi_path = os.path.join(HIDPI_DIR, f"{filename}_2x.png")
        prev_path = os.path.join(PREVIEW_DIR, f"preview_{filename}.png")

        cv2.imwrite(std_path, img_bgr)
        cv2.imwrite(hidpi_path, enhance_2x(img_bgr))
        cv2.imwrite(prev_path, render_simulated_preview(img_bgr))
        print(f"Generated {filename}.png ({img_bgr.shape[1]}x{img_bgr.shape[0]}) + 2x + simulated preview")

    mirror_widget_folder()
    print("Tech Impact 458x196 widget background generation complete.")


if __name__ == "__main__":
    main()
