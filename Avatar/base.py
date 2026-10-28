import math
import time
import random
import pygame
import customtkinter as ctk
from PIL import Image, ImageDraw
from GUI.theme import COLOR_TERMINAL_TEXT
from Avatar.face import COLOR_FACE

class BaseMixin:
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
            target_x = self.mouse_x - self.avatar_label.winfo_rootx()
            dx = target_x - (width // 2)
            target_yaw = max(-0.08, min(0.08, dx / 1000.0))
            
            current_yaw = getattr(self, 'avatar_yaw', 0.0)
            self.avatar_yaw = current_yaw + (target_yaw - current_yaw) * 0.05
            
        elif getattr(self, 'manual_rotation', False):
            current_yaw = getattr(self, 'avatar_yaw', 0.0)
            target_yaw = getattr(self, '_avatar_yaw_target', 0.0)
            
            self.avatar_yaw = current_yaw + (target_yaw - current_yaw) * 0.12
            
            if abs(self.avatar_yaw - target_yaw) < 0.01:
                self.avatar_yaw = target_yaw
                self.manual_rotation = False
                
        else:
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