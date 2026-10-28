import math
import time
import random
import pygame
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from GUI.theme import COLOR_TERMINAL_TEXT

COLOR_FACE = "#000000"

class AvatarMixin:
    def _current_sentiment(self):
        if getattr(self.audio_gen, 'is_preview', False):
            return getattr(self.audio_gen, 'preview_sentiment', 0.0)

        sentiments = getattr(self.audio_gen, 'segment_sentiments', None)
        durations = getattr(self.audio_gen, 'segment_durations', None)
        start = getattr(self.audio_gen, 'rms_start_time', 0.0)

        if not sentiments or not durations or start <= 0:
            return 0.0

        elapsed = time.time() - start
        acc = 0.0
        for dur, sent in zip(durations, sentiments):
            if elapsed <= acc:
                return sent
            acc += dur
        return sentiments[-1] if sentiments else 0.0

    def _draw_brow(self, draw, cx, cy, length, thickness, slope, inner_left):
        half = length / 2

        if inner_left:
            x_inner = cx + half
            x_outer = cx - half
        else:
            x_inner = cx - half
            x_outer = cx + half

        y_inner = cy + slope
        y_outer = cy

        t_inner = thickness * 1.0
        t_mid = thickness * 0.75
        t_outer = thickness * 0.25

        arch = thickness * 0.4
        x_mid = (x_inner + x_outer) / 2
        y_mid = (y_inner + y_outer) / 2 - arch

        top_inner = y_inner - t_inner / 2
        top_mid = y_mid - t_mid / 2
        top_outer = y_outer - t_outer / 2

        bot_outer = y_outer + t_outer / 2
        bot_mid = y_mid + t_mid / 2
        bot_inner = y_inner + t_inner / 2

        x_q1 = x_inner + (x_mid - x_inner) * 0.5
        x_q3 = x_mid + (x_outer - x_mid) * 0.5

        pts = [
            (x_inner, top_inner),
            (x_q1, top_inner + (top_mid - top_inner) * 0.6),
            (x_mid, top_mid),
            (x_q3, top_mid + (top_outer - top_mid) * 0.5),
            (x_outer, top_outer),
            (x_outer, bot_outer),
            (x_q3, bot_mid + (bot_outer - bot_mid) * 0.5),
            (x_mid, bot_mid),
            (x_q1, bot_inner + (bot_mid - bot_inner) * 0.6),
            (x_inner, bot_inner),
        ]

        draw.polygon(pts, fill=COLOR_FACE)

    def _draw_eye(self, draw, cx, cy, width, height, pupil_dx, pupil_dy, closed=False):
        half_w = width / 2
        half_h = height / 2

        if closed:
            draw.line(
                [(cx - half_w, cy), (cx + half_w, cy)],
                fill=COLOR_FACE,
                width=2,
            )
            return

        pupil_r_x = max(1, int(half_w * 0.35))
        pupil_r_y = max(1, int(half_h * 0.6))
        pcx = cx + pupil_dx
        pcy = cy + pupil_dy
        
        draw.ellipse(
            [pcx - pupil_r_x, pcy - pupil_r_y, pcx + pupil_r_x, pcy + pupil_r_y],
            fill=COLOR_FACE,
        )

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

    def _update_avatar(self):
        if not hasattr(self, 'avatar_label'):
            return

        width = self.avatar_label.winfo_width()
        height = self.avatar_label.winfo_height()

        if width <= 1 or height <= 1:
            width, height = 400, 700

        offset_y = round(math.sin(self.avatar_frame * 0.05) * 4)

        render_width = width
        render_height = height + 200

        img = Image.new("RGBA", (render_width, render_height), (5, 15, 5, 255))
        draw = ImageDraw.Draw(img)

        center_x = render_width // 2
        center_y = (render_height // 2) + offset_y - 90

        head_w = int(render_width * 0.60 * 1.1)
        head_h = int(render_height * 0.22 * 1.1)

        now = time.time()
        
        # --- LOGIKA OBROTU ---
        if getattr(self, 'eye_tracking_mode', False) and getattr(self, 'mouse_x', None) is not None:
            # Śledzenie myszką
            target_x = self.mouse_x - self.avatar_label.winfo_rootx()
            dx = target_x - (width // 2)
            target_yaw = max(-0.08, min(0.08, dx / 1000.0))
            
            current_yaw = getattr(self, 'avatar_yaw', 0.0)
            self.avatar_yaw = current_yaw + (target_yaw - current_yaw) * 0.05
            
        elif getattr(self, 'manual_rotation', False):
            # Ręczny obrót ze strzałek
            current_yaw = getattr(self, 'avatar_yaw', 0.0)
            target_yaw = getattr(self, '_avatar_yaw_target', 0.0)
            
            # Szybsza interpolacja
            self.avatar_yaw = current_yaw + (target_yaw - current_yaw) * 0.12
            
            # Zatrzymanie po dotarciu do celu
            if abs(self.avatar_yaw - target_yaw) < 0.01:
                self.avatar_yaw = target_yaw
                self.manual_rotation = False
                
        else:
            # Automatyczne błądzenie (Wander)
            if now > getattr(self, '_avatar_yaw_until', 0):
                self._avatar_yaw_target = random.uniform(-0.35, 0.35)
                self._avatar_yaw_until = now + random.uniform(1.5, 3.0)

            current_yaw = getattr(self, 'avatar_yaw', 0.0)
            target_yaw = getattr(self, '_avatar_yaw_target', 0.0)
            self.avatar_yaw = current_yaw + (target_yaw - current_yaw) * 0.08

        face_shift_x = self.avatar_yaw * head_w * 0.3
        
        target_squint = (abs(self.avatar_yaw) / 0.35) ** 3
        target_squint = min(1.0, max(0.0, target_squint))
        current_squint = getattr(self, 'avatar_squint', 0.0)
        self.avatar_squint = current_squint + (target_squint - current_squint) * 0.1
        pull_in = int(self.avatar_squint * 8)

        eyes_y = center_y - int(head_h * 0.15)
        mouth_y = center_y + int(head_h * 0.18)

        base_eye_offset = int(head_w * 0.22)
        current_eye_offset = max(0, base_eye_offset - pull_in)
        
        left_eye_x = center_x - current_eye_offset + face_shift_x
        right_eye_x = center_x + current_eye_offset + face_shift_x

        audio_busy = False
        try:
            if pygame.mixer.get_init():
                audio_busy = pygame.mixer.music.get_busy()
        except pygame.error:
            audio_busy = False

        if audio_busy:
            avatar_state = "TALKING"
        elif self.is_generating or self.is_playing:
            avatar_state = "PROCESSING"
        else:
            avatar_state = "IDLE"

        eyes_closed = (avatar_state == "PROCESSING")

        sentiment = 0.0
        if avatar_state == "TALKING":
            sentiment = self._current_sentiment()

        head_pts = self._draw_head_outline(img, draw, center_x + face_shift_x * 0.2, center_y, head_w, head_h)
        self._draw_balloon_details(draw, head_pts, center_x + face_shift_x * 0.2, center_y, head_w, head_h)

        eye_w = int(head_w * 0.22)
        eye_h = int(head_h * 0.22)

        if eyes_closed:
            self._draw_eye(draw, left_eye_x, eyes_y, eye_w, eye_h, 0, 0, closed=True)
            self._draw_eye(draw, right_eye_x, eyes_y, eye_w, eye_h, 0, 0, closed=True)
            self._avatar_current_look_until = 0
            look_dx, look_dy = 0, 0
        else:
            if getattr(self, 'eye_tracking_mode', False) and getattr(self, 'mouse_x', None) is not None:
                target_x = self.mouse_x - self.avatar_label.winfo_rootx()
                target_y = self.mouse_y - self.avatar_label.winfo_rooty()
                
                dx = target_x - (width // 2)
                dy = target_y - (height // 2) 
                
                dist = math.hypot(dx, dy)
                if dist > 0:
                    max_pupil_shift = int(eye_w * 0.3)
                    factor = min(1.0, dist / 300.0) 
                    look_dx = int((dx / dist) * max_pupil_shift * factor)
                    look_dy = int((dy / dist) * max_pupil_shift * factor)
            else:
                if now > getattr(self, '_avatar_current_look_until', 0):
                    step = max(1, int(eye_w * 0.15))
                    directions = [
                        (0, 0), (step, 0), (-step, 0), (0, step), (0, -step),
                        (max(1, step - 1), max(1, step - 1)),
                        (-max(1, step - 1), -max(1, step - 1)),
                        (max(1, step - 1), -max(1, step - 1)),
                        (-max(1, step - 1), max(1, step - 1)),
                    ]
                    look_dx, look_dy = random.choice(directions)
                    self._avatar_current_look = (look_dx, look_dy)
                    self._avatar_current_look_until = now + random.uniform(1.0, 3.0)
                else:
                    look_dx, look_dy = getattr(self, '_avatar_current_look', (0, 0))

            pupil_shift_x = self.avatar_yaw * 3

            self._draw_eye(draw, left_eye_x, eyes_y, eye_w, eye_h, look_dx + pupil_shift_x, look_dy)
            self._draw_eye(draw, right_eye_x, eyes_y, eye_w, eye_h, look_dx + pupil_shift_x, look_dy)

        brow_y = eyes_y - int(eye_h * 0.5)
        brow_len = int(eye_w * 1.2)
        brow_thickness = int(eye_h * 0.2)

        if sentiment > 0.1:
            brow_slope = -int(brow_thickness * 0.6)
        elif sentiment < -0.1:
            brow_slope = int(brow_thickness * 0.6)
        else:
            brow_slope = 0

        brow_shift_x = look_dx * 0.4
        brow_shift_y = look_dy * 0.3
        brow_extra_tilt = look_dx * 0.2

        self._draw_brow(
            draw,
            cx=left_eye_x + brow_shift_x,
            cy=brow_y + brow_shift_y,
            length=brow_len,
            thickness=brow_thickness,
            slope=brow_slope + brow_extra_tilt,
            inner_left=True,
        )
        self._draw_brow(
            draw,
            cx=right_eye_x + brow_shift_x,
            cy=brow_y + brow_shift_y,
            length=brow_len,
            thickness=brow_thickness,
            slope=brow_slope + brow_extra_tilt,
            inner_left=False,
        )

        half_w = int(head_w * 0.20)
        max_h = int(head_h * 0.25)
        mouth_center_x = center_x + face_shift_x

        prev_openness = getattr(self, 'mouth_openness', 0.0)
        target_openness = 0.0

        if avatar_state == "TALKING":
            envelope = getattr(self.audio_gen, 'rms_envelope', None)
            rms_start = getattr(self.audio_gen, 'rms_start_time', 0.0)
            rms_duration = getattr(self.audio_gen, 'rms_duration', 0.0)

            synced = False
            if envelope is not None and len(envelope) > 0 and rms_start > 0:
                elapsed = time.time() - rms_start
                if 0 <= elapsed <= rms_duration:
                    idx = int(elapsed / max(rms_duration, 0.001) * len(envelope))
                    idx = max(0, min(len(envelope) - 1, idx))
                    rms_val = float(envelope[idx])
                    target_openness = 0.10 + 0.90 * rms_val
                    synced = True

            if not synced:
                self.mouth_phase += 0.35
                syllable = abs(math.sin(self.mouth_phase))
                target_openness = 0.10 + 0.55 * syllable

        elif avatar_state == "PROCESSING":
            self.mouth_phase += 0.15
            target_openness = 0.15 + 0.25 * (0.5 + 0.5 * math.sin(self.mouth_phase))
        else:
            self.mouth_phase = 0.0
            target_openness = 0.0

        self.mouth_openness = prev_openness + (target_openness - prev_openness) * 0.35

        if avatar_state == "IDLE":
            now_t = time.time()
            if now_t > getattr(self, '_mouth_current_shift_until', 0):
                self._mouth_shift = (
                    random.choice([-1, 0, 1]),
                    random.choice([-1, 0, 1]),
                )
                self._mouth_current_shift_until = now_t + random.uniform(2.0, 4.0)

            shift_x, shift_y = getattr(self, '_mouth_shift', (0, 0))

            sway_x = math.sin(self.avatar_frame * 0.05) * 0.5
            sway_y = math.cos(self.avatar_frame * 0.07) * 0.3

            idle_center_x = mouth_center_x + shift_x + sway_x
            idle_center_y = mouth_y + shift_y + sway_y

            n = 30
            still_curve = max_h * 0.05
            points = []
            for k in range(n):
                t = k / (n - 1)
                px = idle_center_x - half_w + t * (2 * half_w)
                arc = 4 * t * (1 - t)
                py = idle_center_y + still_curve * arc
                points.append((px, py))

            draw.line(points, fill=COLOR_FACE, width=2)

            lips_top = [(px, py - 1) for (px, py) in points]
            lips_bottom = [(px, py + 1) for (px, py) in points]
            draw.line(lips_top, fill=COLOR_FACE, width=1)
            draw.line(lips_bottom, fill=COLOR_FACE, width=1)

        elif avatar_state == "PROCESSING":
            points = []
            n_points = 48
            wave_amp = 2.5 + 1.5 * abs(math.sin(self.mouth_phase * 0.5))
            flow = self.mouth_phase * 1.5

            for k in range(n_points):
                t = k / (n_points - 1)
                px = mouth_center_x - half_w + t * (2 * half_w)
                py = mouth_y + math.sin(flow - t * 4 * math.pi) * wave_amp
                points.append((px, py))

            draw.line(points, fill=COLOR_FACE, width=2)

        elif avatar_state == "TALKING":
            o = self.mouth_openness

            if sentiment > 0.1:
                top_curve = max_h * 0.4 * o
                bottom_curve = max_h * 0.4 * o
                top_sign, bottom_sign = +1, -1
            elif sentiment < -0.1:
                top_curve = max_h * 0.4 * o
                bottom_curve = max_h * 0.4 * o
                top_sign, bottom_sign = -1, +1
            else:
                top_curve = max_h * 0.4 * o
                bottom_curve = max_h * 0.4 * o
                top_sign, bottom_sign = +1, -1

            top_points = []
            bottom_points = []
            n = 40
            for k in range(n):
                t = k / (n - 1)
                px = mouth_center_x - half_w + t * (2 * half_w)
                arc = 4 * t * (1 - t)

                py_top = mouth_y + top_sign * top_curve * arc
                py_bottom = mouth_y + bottom_sign * bottom_curve * arc

                top_points.append((px, py_top))
                bottom_points.append((px, py_bottom))

            fill_polygon = top_points + list(reversed(bottom_points))
            draw.polygon(fill_polygon, fill=COLOR_FACE)

        squashed_height = int(render_height * 0.9)
        img = img.resize((render_width, squashed_height), Image.NEAREST)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(render_width, squashed_height))

        self.avatar_label.configure(image=ctk_img, text="")

        self.avatar_frame += 1

        self.avatar_job = self.after(10, self._update_avatar)