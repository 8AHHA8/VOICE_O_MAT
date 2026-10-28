import tkinter as tk
from tkinter import filedialog
import os
import time
import pygame
import config
from GUI.theme import *
from Audio.utils import cleanup_temp_files

class HandlersMixin:
    def _play_click(self):
        if self.sound_enabled and self.audio_gen: 
            self.audio_gen.play_click()

    def _set_eye_mode(self, track_mode):
        self.eye_tracking_mode = track_mode
        self.manual_rotation = False
        
        if track_mode:
            self.btn_track.configure(fg_color=COLOR_BUTTON, text_color="#888888")
            self.btn_wander.configure(fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_BUTTON_TEXT)
            self._log("Eye tracking mode: ON")
        else:
            self.btn_wander.configure(fg_color=COLOR_BUTTON, text_color="#888888")
            self.btn_track.configure(fg_color=COLOR_BUTTON_HOVER, text_color=COLOR_BUTTON_TEXT)
            self._log("Eye tracking mode: OFF (Wander)")

    def _manual_rotate(self, direction):
        if getattr(self, 'eye_tracking_mode', False):
            self._set_eye_mode(False)
            
        self.manual_rotation = True
        
        if direction < 0:
            self._avatar_yaw_target = -0.35
        else:
            self._avatar_yaw_target = 0.35
            
        self._avatar_yaw_until = time.time() + 3.0

    def _on_mouse_move(self, event):
        self.mouse_x = event.x_root
        self.mouse_y = event.y_root

    def _log(self, text):
        def _do():
            self.terminal_text.configure(state="normal")
            self.terminal_text.insert("end", f"> {text}\n")
            self.terminal_text.see("end")
            self.terminal_text.configure(state="disabled")
        self.after(0, _do)

    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Dokumenty", "*.txt *.pdf *.docx *.doc *.odt *.rtf *.epub *.html *.md *.csv"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        if path: 
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, path)
            self._log(f"Loaded text: {path}")

    def _select_voice(self):
        paths = filedialog.askopenfilenames(
            title="Choose Voice Sample(s)", 
            filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.flac *.aac"), ("All Files", "*.*")]
        )
        if paths:
            self.selected_voice_paths = list(paths)
            self.entry_voice.delete(0, tk.END)
            self.entry_voice.insert(0, self.selected_voice_paths[0] if len(self.selected_voice_paths) == 1 else f"Selected {len(self.selected_voice_paths)} files")
            self._log(f"Loaded {len(self.selected_voice_paths)} voice sample(s).")

    def _toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.btn_sound.configure(text="SOUND: ON" if self.sound_enabled else "SOUND: OFF", text_color=COLOR_AMBER if self.sound_enabled else COLOR_TEXT_DIM)
        if not pygame.mixer.get_init():
            return
        try:
            if self.sound_enabled:
                if self.is_generating and not self.is_paused and not self.is_playing:
                    pygame.mixer.Sound.play(self.reel_sound, loops=-1)
            else:
                pygame.mixer.Sound.stop(self.reel_sound)
        except pygame.error:
            pass

    def _refresh_playlist(self, select_file=None):
        files = [f for f in os.listdir(config.OUTPUT_DIR) if f.lower().endswith(".wav")] if os.path.exists(config.OUTPUT_DIR) else []
        files.sort()
        self.playlist_combo.configure(values=files if files else [""])
        self.playlist_var.set(select_file if select_file else (files[-1] if files else ""))

    def _on_closing(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except pygame.error:
            pass
            
        cleanup_temp_files()
        
        self.destroy()

    def _update_speed_label(self, value): 
        self.speed_label.configure(text=f"{value:.1f}x")

    def _update_pitch_label(self, value): 
        self.pitch_label.configure(text=f"{value:.1f}")