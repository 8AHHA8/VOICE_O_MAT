import os
import wave
import uuid
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
    def preview(self, text, voice_paths, language="pl", speed=1.0, pitch=1.0):
        self.cancel_requested = False
        self.is_preview = True
        actual_voice_paths = []
        
        try:
            if not text.strip():
                raise RuntimeError("Preview text is empty.")

            actual_voice_paths = load_audio_as_wav_temp(voice_paths, self.log_cb)

            device = self.load_model()
            self.status_cb("[TEST] Generating...")
            
            wav = self.tts.tts(
                text=text, speaker_wav=actual_voice_paths, language=language, speed=speed
            )

            if isinstance(wav, list): wav = np.array(wav)
            wav = np.asarray(wav)
            if wav.ndim > 1: wav = wav.flatten()

            if wav.size > 0:
                self.status_cb("[TEST] Playing...")
                sr = int(self.tts.synthesizer.output_sample_rate * pitch)
                
                # Generujemy unikalną nazwę pliku, żeby uniknąć blokady
                temp_preview = os.path.join(config.TEMP_DIR, f"temp_preview_{uuid.uuid4().hex}.wav")
                
                with wave.open(temp_preview, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    wf.writeframes((wav * 32767).astype(np.int16).tobytes())

                duration = len(wav) / sr
                
                self.playback_started_cb()
                pygame.mixer.music.load(temp_preview)
                pygame.mixer.music.play()
                
                # Próbujemy usunąć plik od razu po załadowaniu do pygame
                try:
                    os.remove(temp_preview)
                except:
                    pass

                self.finish_cb(duration)
                
            else:
                self.error_cb("Test generated empty audio.")

            for path in actual_voice_paths:
                if path not in voice_paths and os.path.exists(path): os.remove(path)
                
        except Exception as e:
            self.error_cb(str(e))
            for path in actual_voice_paths:
                if path not in voice_paths and os.path.exists(path): os.remove(path)

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
            
            self.playback_started_cb()
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.finish_cb(duration)
            
            # Próba usunięcia pliku tymczasowego z dysku
            if "temp_play_" in file_path:
                try:
                    os.remove(file_path)
                except:
                    pass

        except Exception as e:
            self.error_cb(f"Playback error: {str(e)}")