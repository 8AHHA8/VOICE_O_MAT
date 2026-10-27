import os
import time
import wave
import numpy as np
import torch
from Audio.utils import read_text_from_file, split_text, load_audio_as_wav_temp
import config
import config

class GeneratorMixin:
    def generate(self, text_path, voice_paths, language="pl", speed=1.0, pitch=1.0, pause_event=None, output_filename="generated_audio.wav"):
        self.cancel_requested = False
        self.is_preview = False
        self.pause_event = pause_event
        actual_voice_paths = []
        
        try:
            text = read_text_from_file(text_path)
            if not text.strip():
                raise RuntimeError("File is empty.")

            segments = split_text(text)
            if not segments:
                raise RuntimeError("No text to read.")

            actual_voice_paths = load_audio_as_wav_temp(voice_paths, self.log_cb)

            device = self.load_model()
            self.log_cb(f"Recording started ({len(segments)} segments).")
            all_audio = []
            total_segments = len(segments)

            for idx, segment in enumerate(segments):
                if self.cancel_requested:
                    self.log_cb("Cancelled by user.")
                    for path in actual_voice_paths:
                        if path not in voice_paths and os.path.exists(path): os.remove(path)
                    return

                if self.pause_event and self.pause_event.is_set():
                    self.status_cb("[PAUSED] Waiting...")
                    while self.pause_event.is_set():
                        if self.cancel_requested: return
                        time.sleep(0.2)
                    self.status_cb("[RESUMED] Processing...")

                percent = idx / total_segments
                self.progress_cb(percent)
                self.log_cb(f"Reading: {segment[:50]}...")
                
                if device == "GPU": self.clear_vram()

                try:
                    wav = self.tts.tts(text=segment, speaker_wav=actual_voice_paths, language=language, speed=speed)
                except RuntimeError as e:
                    if "out of memory" in str(e).lower() and device == "GPU":
                        self.log_cb("Out of VRAM! Switching to CPU.")
                        self.clear_vram()
                        self.tts = None
                        self.use_gpu = False
                        device = self.load_model()
                        wav = self.tts.tts(text=segment, speaker_wav=actual_voice_paths, language=language, speed=speed)
                    else:
                        raise

                if isinstance(wav, list): wav = np.array(wav)
                wav = np.asarray(wav)
                if wav.ndim > 1: wav = wav.flatten()

                if wav.size > 0:
                    if wav.dtype != np.int16: wav = (wav * 32767).astype(np.int16)
                    all_audio.append(wav)

                self.sample_rate = self.tts.synthesizer.output_sample_rate
                if device == "GPU":
                    torch.cuda.synchronize()
                    time.sleep(0.5)

            for path in actual_voice_paths:
                if path not in voice_paths and os.path.exists(path): os.remove(path)

            if self.cancel_requested: return
            if not all_audio: raise RuntimeError("Recording yielded empty audio.")

            self.progress_cb(1.0)
            full_path = os.path.join(config.OUTPUT_DIR, output_filename)
            self.log_cb(f"Saving to file: {full_path}...")
            
            final_audio = np.concatenate(all_audio)
            
            with wave.open(full_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) 
                wf.setframerate(int(self.sample_rate * pitch))
                wf.writeframes(final_audio.tobytes())

            duration = len(final_audio) / int(self.sample_rate * pitch)
            self.finish_cb((full_path, duration))

        except Exception as e:
            self.error_cb(str(e))
            for path in actual_voice_paths:
                if path not in voice_paths and os.path.exists(path): os.remove(path)