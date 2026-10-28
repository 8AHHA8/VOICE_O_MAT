import customtkinter as ctk
import threading
import os
import numpy as np
import pygame
import config
from Audio.engine import AudioGenerator
from Audio.utils import cleanup_temp_files

from GUI.theme import *
from GUI.sections import SectionsMixin
from GUI.animations import AnimationsMixin
from GUI.handlers import HandlersMixin
from GUI.controls import ControlsMixin
from GUI.callbacks import CallbacksMixin
from GUI.avatar import AvatarMixin

def generate_reel_sound(duration=1.2, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    motor_hum = 0.3 * np.sin(2 * np.pi * 25 * t) + 0.15 * np.sin(2 * np.pi * 15 * t)
    noise = np.random.uniform(-1, 1, len(t))
    clicks_envelope = np.zeros_like(t)
    for bt in [0.1, 0.4]:
        start_idx = int(bt * sample_rate)
        click_len = int(0.05 * sample_rate)
        if start_idx + click_len < len(t):
            envelope = np.exp(-np.linspace(0, 15, click_len))
            clicks_envelope[start_idx:start_idx+click_len] = envelope
    clicks = noise * clicks_envelope * 0.8
    audio = motor_hum + clicks
    smoothed_audio = np.convolve(audio, np.ones(80)/80, mode='same')
    max_val = np.max(np.abs(smoothed_audio))
    if max_val > 0:
        smoothed_audio = smoothed_audio / max_val
    audio_int16 = (smoothed_audio * 32767).astype(np.int16)
    stereo_audio = np.column_stack((audio_int16, audio_int16))
    return pygame.sndarray.make_sound(stereo_audio)

class XTTSReaderApp(SectionsMixin, AnimationsMixin, HandlersMixin, ControlsMixin, CallbacksMixin, AvatarMixin, ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("XTTS Studio Deck - Wood & Reels")
        
        window_width = config.WINDOW_WIDTH
        window_height = config.WINDOW_HEIGHT + 180
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.configure(fg_color="#2a1d16")
        ctk.set_appearance_mode("dark")

        apply_custom_button_theme()

        self.resizable(False, False)

        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[WARN] pygame.mixer.init() failed: {e}. Audio disabled.")

        self.is_generating = False
        self.is_paused = False
        self.is_playing = False
        self.playback_start_time = 0
        self.playback_duration = 0
        self.pause_event = threading.Event()
        self.selected_voice_paths = []
        self.reel_angle = 0
        self.reel_progress = 0.0
        self.animation_running = False
        self.animation_job = None
        self.start_time = 0
        self.timer_running = False
        self.timer_job = None
        self.led_blinking = False
        self.led_state = False
        self.led_job = None
        self.last_width = window_width
        self.last_height = window_height

        self.avatar_frame = 0
        self.avatar_job = None

        self.mouth_phase = 0.0
        self.mouth_openness = 0.0
        
        self.eye_tracking_mode = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.manual_rotation = False
        
        self.tts_lock = threading.Lock()

        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR)
            
        if not os.path.exists(config.TEMP_DIR):
            os.makedirs(config.TEMP_DIR)

        cleanup_temp_files()

        try:
            self.reel_sound = generate_reel_sound(duration=1.2)
            self.reel_sound.set_volume(0.80)
        except Exception as e:
            print(f"[WARN] reel_sound creation failed: {e}")
            self.reel_sound = None

        self.sound_enabled = True
        
        self.audio_gen = AudioGenerator(
            status_callback=self._set_status,
            progress_callback=self._on_progress,
            finish_callback=self._on_finish,
            error_callback=self._on_error,
            log_callback=self._log,
            playback_started_callback=self._on_playback_started
        )

        self._build_ui()
        self._refresh_playlist()
        self.bind("<Configure>", self._on_window_resize)
        
        self.bind("<Motion>", self._on_mouse_move)
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)