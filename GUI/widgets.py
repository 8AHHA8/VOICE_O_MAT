from PIL import Image, ImageDraw
import math

def draw_reel(angle, size=110):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2
    r_outer = center - 5
    r_inner = int(r_outer * 0.85)
    r_hub = int(r_outer * 0.3)

    draw.ellipse([center - r_outer, center - r_outer, center + r_outer, center + r_outer], fill="#1a1a1a", outline="#444", width=2)
    draw.ellipse([center - r_inner, center - r_inner, center + r_inner, center + r_inner], fill="#333333", outline="#222222", width=1)
    for step in range(r_hub, r_inner, 4):
        draw.ellipse([center - step, center - step, center + step, center + step], outline="#222222", width=1)
    draw.ellipse([center - r_hub, center - r_hub, center + r_hub, center + r_hub], fill="#111", outline="#555", width=1)
    
    for i in range(3):
        a = math.radians(angle + i * 120)
        hole_r = int(r_hub * 0.6)
        hx = center + math.cos(a) * (r_hub * 0.5)
        hy = center + math.sin(a) * (r_hub * 0.5)
        draw.ellipse([hx - hole_r/2, hy - hole_r/2, hx + hole_r/2, hy + hole_r/2], fill="#1a1a1a", outline="#555", width=1)
        tx = center + math.cos(a) * (r_hub * 0.8)
        ty = center + math.sin(a) * (r_hub * 0.8)
        draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill="#888")
        
    draw.arc([center - r_outer, center - r_outer, center + r_outer, center + r_outer], start=45, end=135, fill="#666", width=2)
    return img