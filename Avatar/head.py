import math
from PIL import Image, ImageDraw, ImageFilter
from GUI.theme import COLOR_TERMINAL_TEXT

class HeadMixin:
    def _draw_head_outline(self, img, draw, cx, cy, width, height):
        half_w = width / 2
        half_h = height / 2

        head_pts = []
        n = 200
        for k in range(n):
            t = k / n
            angle = t * 2 * math.pi

            px = math.cos(angle)
            py = math.sin(angle)

            weight = (math.sin(angle) + 1) / 2

            top_px_mult = 1.15
            top_py_mult = 1.10
            bot_px_mult = 0.80
            bot_py_mult = 1.05

            ease = weight * weight * (3 - 2 * weight)

            px_mult = top_px_mult * (1 - ease) + bot_px_mult * ease
            py_mult = top_py_mult * (1 - ease) + bot_py_mult * ease

            px *= px_mult
            py *= py_mult

            side_factor = abs(math.cos(angle))
            if side_factor > 0.7:
                shrink = 1.0 - (side_factor - 0.7) / 0.3 * 0.06
                px *= shrink

            head_pts.append((cx + px * half_w, cy + py * half_h))

        yaw = getattr(self, 'avatar_yaw', 0.0)
        
        left_weight = 0.5 + yaw * 2.5  
        left_weight = max(0.02, min(0.98, left_weight))

        draw.polygon(head_pts, fill=(100, 255, 100, 255))

        shade_mask = Image.new("L", img.size, 0)
        mask_draw = ImageDraw.Draw(shade_mask)
        
        gradient_steps = 100
        for i in range(gradient_steps):
            t = i / (gradient_steps - 1)
            x_pos = cx - half_w + t * (2 * half_w)
            
            val = left_weight * (1 - t) + (1.0 - left_weight) * t
            val = int(val * 255)
            
            next_x = cx - half_w + ((i + 1) / (gradient_steps - 1)) * (2 * half_w)
            mask_draw.rectangle([x_pos, cy - half_h - 10, next_x, cy + half_h + 10], fill=val)
            
        shade_mask = shade_mask.filter(ImageFilter.GaussianBlur(radius=15))

        shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.polygon(head_pts, fill=COLOR_TERMINAL_TEXT)
        
        shadow_layer.putalpha(190) 
        
        img.paste(shadow_layer, (0, 0), shade_mask)

        return head_pts

    def _draw_balloon_details(self, draw, head_pts, center_x, center_y, head_w, head_h):
        bottom_point = max(head_pts, key=lambda p: p[1])
        knot_x = bottom_point[0]
        knot_y = bottom_point[1]

        knot_size = 8
        knot_pts = [
            (knot_x - knot_size, knot_y),
            (knot_x + knot_size, knot_y),
            (knot_x, knot_y + knot_size * 1.5)
        ]
        draw.polygon(knot_pts, fill=COLOR_TERMINAL_TEXT)

        string_start_y = knot_y + knot_size * 1.5
        string_length = 220
        points = []
        
        wave_amp = 2.5
        wave_speed = 0.08

        n_string_pts = 30
        for i in range(n_string_pts):
            t = i / (n_string_pts - 1)
            py = string_start_y + t * string_length
            wave_env = t
            px = knot_x + math.sin(self.avatar_frame * wave_speed + t * 10) * wave_amp * wave_env
            points.append((px, py))

        draw.line(points, fill=COLOR_TERMINAL_TEXT, width=2)