import os
import threading
import time
import pygame
import config
from GUI.theme import *

class ControlsMixin:
    def _play_last(self):
        selected_file = self.playlist_var.get()
        if not selected_file: 
            return self._log("[ERROR] No file selected.")
            
        path = os.path.join(config.OUTPUT_DIR, selected_file)
        if not os.path.exists(path): 
            return self._log(f"[ERROR] File not found: {path}")
        
        self._log(f"Playing: {path}")
        self.is_playing = True
        self.is_paused = False
        self.playback_start_time = time.time()
        self.playback_duration = 0
        
        self.btn_start.configure(state="disabled", fg_color="#5a0000")
        self.btn_pause.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
        self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
        
        self.btn_preview.configure(state="disabled")
        self.btn_play_last.configure(state="disabled")

        self._start_led_blinking()
        self._start_animation()
        self._start_timer()
        
        threading.Thread(target=self.audio_gen.play_file, args=(path,), daemon=True).start()

    def _start_preview(self):
        if not self.selected_voice_paths: 
            return self._log("[ERROR] No voice sample selected.")
            
        lang_map = {"Polish (pl)": "pl", "English (en)": "en", "German (de)": "de", "Spanish (es)": "es", "French (fr)": "fr", "Italian (it)": "it"}
        
        self._log("Generating instant test...")
        self.is_playing = True
        self.is_paused = False
        self.playback_start_time = time.time()
        self.playback_duration = 0
        
        self.btn_start.configure(state="disabled", fg_color="#5a0000")
        self.btn_pause.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
        self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)

        self.btn_preview.configure(state="disabled")
        self.btn_play_last.configure(state="disabled")

        self._start_led_blinking()
        self._start_animation()
        self._start_timer()
        
        if self.sound_enabled:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.Sound.play(self.reel_sound, loops=-1)
            except pygame.error:
                pass
            
        def _run_preview():
            with self.tts_lock:
                self.audio_gen.preview(
                    self.entry_preview.get().strip(), 
                    self.selected_voice_paths, 
                    lang_map.get(self.lang_var.get(), "pl"), 
                    self.speed_slider.get(), self.pitch_slider.get()
                )
            
        threading.Thread(target=_run_preview, daemon=True).start()

    def _start_resume(self):
        if self.is_paused:
            self.is_paused = False
            
            if self.is_playing:
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.unpause()
                except pygame.error:
                    pass
                self._start_led_blinking()
                self._start_animation()
                
                self.btn_start.configure(text="▶ START", state="disabled", fg_color="#5a0000")
                self.btn_pause.configure(text="|| PAUSE", state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
                self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
                self._log("Playback resumed.")
            else:
                self.pause_event.clear()
                self.btn_start.configure(text="▶ START", state="disabled", fg_color="#5a0000")
                self.btn_pause.configure(text="|| PAUSE", state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
                self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
                
                if self.sound_enabled:
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.Sound.play(self.reel_sound, loops=-1)
                    except pygame.error:
                        pass
                self._start_animation()
                self._update_timer()
                self._log("Generation resumed.")
        else:
            text_path, output_name = self.entry_file.get().strip(), self.entry_output_name.get().strip()
            if not text_path or not os.path.exists(text_path): 
                return self._log("[ERROR] No text file selected.")
            if not self.selected_voice_paths: 
                return self._log("[ERROR] No voice sample selected.")
            if not output_name: 
                return self._log("[ERROR] No output file name provided.")
            if not output_name.lower().endswith(".wav"): 
                output_name += ".wav"
            
            lang_map = {"Polish (pl)": "pl", "English (en)": "en", "German (de)": "de", "Spanish (es)": "es", "French (fr)": "fr", "Italian (it)": "it"}
            
            self.is_generating = True
            self.is_paused = False
            self.pause_event.clear()
            
            self.btn_start.configure(state="disabled", fg_color="#5a0000")
            self.btn_pause.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
            self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
            
            self.reel_progress = 0.0
            self._start_animation()
            self._start_timer()
            self._start_led_blinking()
            
            if self.sound_enabled:
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.Sound.play(self.reel_sound, loops=-1)
                except pygame.error:
                    pass
                
            def _run_generation():
                with self.tts_lock:
                    self.audio_gen.generate(
                        text_path, self.selected_voice_paths, 
                        lang_map.get(self.lang_var.get(), "pl"), 
                        self.speed_slider.get(), self.pitch_slider.get(), 
                        self.pause_event, output_name
                    )
                    
            threading.Thread(target=_run_generation, daemon=True).start()

    def _pause(self):
        self.is_paused = True
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.pause()
        except pygame.error:
            pass
        self.pause_event.set()
        
        self._stop_animation()
        self._stop_led_blinking()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.Sound.stop(self.reel_sound)
        except pygame.error:
            pass
        
        self.btn_start.configure(text="▶ RESUME", state="normal", fg_color=COLOR_RED)
        self.btn_pause.configure(text="|| PAUSED", state="disabled", fg_color=COLOR_BUTTON)
        self.btn_abort.configure(state="normal", fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT)
        
        self.reel_center_label.configure(text="[PAUSED]\n--:--")
        self._log("Paused.")

    def _abort(self):
        # Inkrementacja ID sesji ucisza wiszące wątki odtwarzania
        self.playback_session_id += 1

        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except pygame.error:
            pass
        
        self.audio_gen.cancel()
        
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
        
        self.reel_center_label.configure(text="[ABORT]\n00:00")
        
        # --- BLOKADA PRZED KOLEJNYM URUCHOMIENIEM ---
        self.btn_start.configure(state="disabled", text="CLEANING...", fg_color=COLOR_BUTTON)
        self.btn_pause.configure(state="disabled", text="|| PAUSE", fg_color=COLOR_BUTTON, text_color=COLOR_TEXT_DIM)
        self.btn_abort.configure(state="disabled", fg_color=COLOR_BUTTON, text_color=COLOR_TEXT_DIM)
        self.btn_preview.configure(state="disabled")
        self.btn_play_last.configure(state="disabled")
        
        def _reenable():
            self.btn_start.configure(state="normal", text="▶ START", fg_color=COLOR_RED)
            self.btn_preview.configure(state="normal")
            self.btn_play_last.configure(state="normal")
            self._log("Ready.")
        
        self.after(3000, _reenable)
        self._log("Aborted. Cleaning up VRAM, please wait...")

    def _reset_buttons(self):
        def _do():
            self.btn_start.configure(state="normal", text="▶ START", fg_color=COLOR_RED)
            self.btn_pause.configure(state="disabled", text="|| PAUSE", fg_color=COLOR_BUTTON, text_color=COLOR_TEXT_DIM)
            self.btn_abort.configure(state="disabled", fg_color=COLOR_BUTTON, text_color=COLOR_TEXT_DIM)
        self.after(0, _do)