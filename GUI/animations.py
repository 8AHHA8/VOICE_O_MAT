import time
import pygame
import customtkinter as ctk
from GUI.theme import COLOR_RED, COLOR_AMBER, COLOR_BUTTON, COLOR_TEXT, COLOR_TEXT_DIM
from GUI.widgets import draw_reel

class AnimationsMixin:
    def _blink_led(self):
        if not self.led_blinking: return
        self.led_state = not self.led_state
        self.led.configure(text_color="#ff3333" if self.led_state else "#550000")
        self.led_job = self.after(800, self._blink_led)

    def _start_led_blinking(self):
        self.led_blinking = True
        self.led_state = True
        self._blink_led()

    def _stop_led_blinking(self):
        self.led_blinking = False
        if self.led_job: self.after_cancel(self.led_job); self.led_job = None
        self.led.configure(text_color=COLOR_RED)

    def _update_reels(self, angle, progress):
        self.reel_angle = angle; self.reel_progress = progress
        img = draw_reel(angle, size=110)
        self.reel_left_img = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))
        self.reel_left_label.configure(image=self.reel_left_img)
        self.reel_right_img = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))
        self.reel_right_label.configure(image=self.reel_right_img)

    def _animate_reels(self):
        if not self.animation_running: return
        self.reel_angle = (self.reel_angle + 15) % 360
        self._update_reels(self.reel_angle, self.reel_progress)
        self.animation_job = self.after(50, self._animate_reels)

    def _start_animation(self):
        self.animation_running = True
        self._animate_reels()

    def _stop_animation(self):
        self.animation_running = False
        if self.animation_job: self.after_cancel(self.animation_job); self.animation_job = None

    def _update_timer(self):
        if not self.timer_running or self.is_paused: return
        if self.is_playing:
            elapsed = time.time() - self.playback_start_time
            if self.playback_duration > 0 and elapsed > self.playback_duration: elapsed = self.playback_duration
            self.reel_center_label.configure(text=f"[PLAY]\n{int(elapsed)//60:02d}:{int(elapsed)%60:02d}")
            if self.playback_duration > 0 and elapsed >= self.playback_duration:
                self.is_playing = False; self._stop_animation(); self._stop_led_blinking()
                self.reel_center_label.configure(text=f"[END]\n{int(elapsed)//60:02d}:{int(elapsed)%60:02d}")
                self.timer_running = False
                if self.sound_enabled and self.is_generating: pygame.mixer.Sound.play(self.reel_sound, loops=-1)
                return
        else:
            elapsed = int(time.time() - self.start_time)
            self.reel_center_label.configure(text=f"[REC]\n{int(self.reel_progress*100)}%\n{elapsed//60:02d}:{elapsed%60:02d}")
        self.timer_job = self.after(200, self._update_timer)

    def _start_timer(self):
        if not self.timer_running: 
            self.start_time = time.time(); self.timer_running = True; self._update_timer()

    def _stop_timer(self):
        self.timer_running = False
        if self.timer_job: self.after_cancel(self.timer_job); self.timer_job = None