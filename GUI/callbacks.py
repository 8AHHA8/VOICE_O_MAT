import time
import os
import threading
import pygame
from GUI.theme import *

class CallbacksMixin:
    def _on_playback_started(self): 
        pygame.mixer.Sound.stop(self.reel_sound)

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
            pygame.mixer.Sound.stop(self.reel_sound)
            
            elapsed = int(time.time() - self.start_time)
            self.reel_center_label.configure(text=f"[DONE]\n{elapsed//60:02d}:{elapsed%60:02d}")
            self._reset_buttons()
            
        elif isinstance(result, (int, float)):
            self.playback_duration = result
            self._log(f"Playback started: {result:.1f}s")
            
            # Uruchamiamy wątek, który poczeka dokładnie tyle, ile trwa nagranie
            threading.Thread(target=self._wait_for_playback_end, args=(result,), daemon=True).start()

    def _wait_for_playback_end(self, duration):
        # Czekamy określony czas (plus mały bufor bezpieczeństwa)
        time.sleep(duration + 0.5)
            
        # Resetujemy przyciski dopiero po zakończeniu odtwarzania
        self.after(0, self._on_playback_finished)
        
    def _on_playback_finished(self):
        self.is_playing = False
        self._stop_animation()
        self._stop_led_blinking()
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
        pygame.mixer.Sound.stop(self.reel_sound)
        self._reset_buttons()

    def _set_status(self, text, is_error=False): 
        self._log(text)

    def _on_window_resize(self, event):
        if event.widget == self:
            new_w, new_h = event.width, event.height
            if abs(new_w - self.last_width) > 20 or abs(new_h - self.last_height) > 20:
                self.last_width = new_w; self.last_height = new_h
                self.bg_label.configure(image=generate_wood_texture(new_w + 100, new_h + 100))