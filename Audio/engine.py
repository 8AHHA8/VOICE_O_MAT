import os
import pygame
import torch
import config
from Audio.clicks import generate_click_sound
from Audio.model import ModelMixin
from Audio.preview import PreviewMixin
from Audio.generator import GeneratorMixin

class AudioGenerator(ModelMixin, PreviewMixin, GeneratorMixin):
    def __init__(self, status_callback, progress_callback, finish_callback, error_callback, log_callback, playback_started_callback):
        self.status_cb = status_callback
        self.progress_cb = progress_callback
        self.finish_cb = finish_callback
        self.error_cb = error_callback
        self.log_cb = log_callback
        self.playback_started_cb = playback_started_callback
        
        self.tts = None
        self.cancel_requested = False
        self.pause_event = None
        
        self.gpu_available = torch.cuda.is_available()
        self.gpu_name = torch.cuda.get_device_name(0) if self.gpu_available else "None"
        self.use_gpu = self.gpu_available
        self.sample_rate = 24000
        self.is_preview = False
        
        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR)
        if not os.path.exists(config.TEMP_DIR):
            os.makedirs(config.TEMP_DIR)
        
        self.click_sound = generate_click_sound()

    def play_click(self):
        if self.click_sound:
            self.click_sound.play()

    def cancel(self):
        self.cancel_requested = True
        if self.pause_event:
            self.pause_event.set()