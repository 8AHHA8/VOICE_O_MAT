import os
import json
import wave
import uuid
import time
import numpy as np
import pygame
from Audio.utils import load_audio_as_wav_temp
import config

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class PreviewMixin:
    def _compute_rms_envelope(self, wav_path, window_ms=20):
        try:
            with wave.open(wav_path, 'rb') as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                raw = wf.readframes(n_frames)

            if sampwidth != 2:
                return None, 0.0

            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
            if n_channels > 1:
                samples = samples.reshape(-1, n_channels).mean(axis=1)

            window = max(1, int(framerate * window_ms / 1000.0))
            n_windows = len(samples) // window
            if n_windows < 1:
                return None, 0.0

            trimmed = samples[:n_windows * window].reshape(n_windows, window)
            rms = np.sqrt(np.mean(trimmed ** 2, axis=1))
            peak = np.max(rms)
            if peak > 0:
                rms = rms / peak
            if len(rms) > 2:
                rms = np.convolve(rms, np.ones(3) / 3, mode="same")

            return rms.astype(np.float32), len(samples) / framerate
        except Exception as e:
            self.log_cb(f"[RMS] envelope failed: {e}")
            return None, 0.0

    def preview(self, text, voice_paths, language="pl", speed=1.0, pitch=1.0):
        self.cancel_requested = False
        self.is_preview = True
        actual_voice_paths = []
        temp_preview = None
        
        try:
            if not text.strip():
                raise RuntimeError("Preview text is empty.")

            actual_voice_paths = load_audio_as_wav_temp(voice_paths, self.log_cb)

            device = self.load_model()
            self.status_cb("[TEST] Generating...")

            self.preview_sentiment = 0.0
            self.segment_sentiments = None
            self.segment_durations = None
            
            wav = self.tts.tts(
                text=text, speaker_wav=actual_voice_paths, language=language, speed=speed
            )

            if isinstance(wav, list): wav = np.array(wav)
            wav = np.asarray(wav)
            if wav.ndim > 1: wav = wav.flatten()

            if wav.size > 0:
                self.status_cb("[TEST] Playing...")
                sr = int(self.tts.synthesizer.output_sample_rate * pitch)
                
                temp_preview = os.path.join(config.TEMP_DIR, f"temp_preview_{uuid.uuid4().hex}.wav")
                
                with wave.open(temp_preview, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    wf.writeframes((wav * 32767).astype(np.int16).tobytes())

                duration = (len(wav) / sr) - 0.2 
                if duration < 0: duration = len(wav) / sr

                envelope, _ = self._compute_rms_envelope(temp_preview, window_ms=20)
                self.rms_envelope = envelope
                self.rms_start_time = time.time()
                self.rms_duration = duration
                
                self.playback_started_cb()
                pygame.mixer.music.load(temp_preview)
                pygame.mixer.music.play()

                self.finish_cb(duration)
                
            else:
                self.error_cb("Test generated empty audio.")

        except Exception as e:
            self.error_cb(str(e))
        finally:
            # Gwarantowane usunięcie pliku po załadowaniu do pamięci
            if temp_preview and os.path.exists(temp_preview):
                try: os.remove(temp_preview)
                except: pass
                
            for path in actual_voice_paths:
                if path not in voice_paths and os.path.exists(path): 
                    try: os.remove(path)
                    except: pass

    def play_file(self, file_path):
        try:
            if not file_path.lower().endswith(('.wav', '.mp3', '.ogg')):
                if PYDUB_AVAILABLE:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(file_path)
                    temp_play = os.path.join(config.TEMP_DIR, f"temp_play_{uuid.uuid4().hex}.wav")
                    audio.export(temp_play, format="wav")
                    file_path = temp_play
                else:
                    raise RuntimeError("Cannot play this format without FFmpeg/Pydub.")
            
            sound = pygame.mixer.Sound(file_path)
            duration = sound.get_length()

            self.segment_sentiments = None
            self.segment_durations = None
            if file_path.lower().endswith(".wav"):
                sentiment_path = file_path[:-4] + "_sentiment.json"
                if os.path.exists(sentiment_path):
                    try:
                        with open(sentiment_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        self.segment_sentiments = data.get("segments")
                        self.segment_durations = data.get("durations")
                        self.log_cb(f"Loaded sentiment for {len(self.segment_sentiments or [])} segments.")
                    except Exception as e:
                        self.log_cb(f"[SENTIMENT] read failed: {e}")

            envelope, _ = self._compute_rms_envelope(file_path, window_ms=20)
            self.rms_envelope = envelope
            self.rms_start_time = time.time()
            self.rms_duration = duration
            
            self.playback_started_cb()
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.finish_cb(duration)

        except Exception as e:
            self.error_cb(f"Playback error: {str(e)}")
        finally:
            if "temp_play_" in file_path and os.path.exists(file_path):
                try: os.remove(file_path)
                except: pass