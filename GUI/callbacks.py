import time
import os
import threading
import pygame
from GUI.theme import *

class CallbacksMixin:
    def _on_playback_started(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.Sound.stop(self.reel_sound)
        except pygame.error:
            pass

    def _on_progress(self, percent): 
        self.reel_progress = percent

    def _on_finish(self, result):
        if isinstance(result, tuple):
            filename, duration = result
            if self.audio_gen.is_preview: 
                return
            
            self._refresh_playlist(select_file=os.path.basename(filename))
            self._log(f"SUCCESS: File saved as {filename}")
            
            self.is_generating = False
            self.is_paused = False
            self._stop_animation()
            self._stop_timer()
            self._stop_led_blinking()
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.Sound.stop(self.reel_sound)
            except pygame.error:
                pass
            
            elapsed = int(time.time() - self.start_time)
            self.reel_center_label.configure(text=f"[DONE]\n{elapsed//60:02d}:{elapsed%60:02d}")
            
            self.btn_preview.configure(state="normal")
            self.btn_play_last.configure(state="normal")
            
            self._reset_buttons()
            
        elif isinstance(result, (int, float)):
            self.playback_duration = result
            self._log(f"Playback started: {result:.1f}s")
            
            # Inkrementujemy ID sesji i przekazujemy do wątku
            self.playback_session_id += 1
            current_session = self.playback_session_id
            
            threading.Thread(target=self._wait_for_playback_end, args=(current_session,), daemon=True).start()

    def _wait_for_playback_end(self, session_id):
        while True:
            # Jeśli w międzyczasie kliknięto Abort lub nowy Play, przerywamy ten wątek
            if session_id != self.playback_session_id:
                return

            try:
                if not pygame.mixer.get_init():
                    break
                if not self.is_paused and not pygame.mixer.music.get_busy():
                    break
            except pygame.error:
                break
            time.sleep(0.1)

        # Upewniamy się, że ID sesji jest nadal aktualne (zapobiega ucięciu nowego audio)
        if session_id != self.playback_session_id:
            return

        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except pygame.error:
            pass

        try:
            self.after(0, self._on_playback_finished)
        except Exception:
            pass

    def _on_playback_finished(self):
        self.is_playing = False
        self.is_paused = False
        self._stop_animation()
        self._stop_led_blinking()
        
        self.btn_preview.configure(state="normal")
        self.btn_play_last.configure(state="normal")
        
        self._reset_buttons()
        self._log("Playback finished.")

    def _on_error(self, error_msg):
        self._log(f"CRITICAL ERROR: {error_msg}")
        self.is_generating = False
        self.is_paused = False
        self.is_playing = False
        self._stop_animation()
        self._stop_timer()
        self._stop_led_blinking()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.Sound.stop(self.reel_sound)
        except pygame.error:
            pass
        
        self.btn_preview.configure(state="normal")
        self.btn_play_last.configure(state="normal")
        
        self._reset_buttons()

    def _set_status(self, text, is_error=False): 
        self._log(text)

    def _on_window_resize(self, event):
        if event.widget == self:
            new_w, new_h = event.width, event.height
            if abs(new_w - self.last_width) > 20 or abs(new_h - self.last_height) > 20:
                self.last_width = new_w; self.last_height = new_h
                self.bg_label.configure(image=generate_wood_texture(new_w + 100, new_h + 100))