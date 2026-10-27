import gc
import torch
from TTS.api import TTS
import config
import config

class ModelMixin:
    def clear_vram(self):
        try:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        except Exception:
            pass

    def load_model(self):
        if self.tts is not None:
            return "GPU" if self.use_gpu else "CPU"

        if self.use_gpu:
            self.clear_vram()
            self.log_cb("Initializing GPU (VRAM)...")
            try:
                self.tts = TTS(config.TTS_MODEL, gpu=True)
                for p in self.tts.synthesizer.tts_model.parameters():
                    p.data = p.data.float() 
                torch.zeros(1, device="cuda", dtype=torch.float32)
                return "GPU"
            except Exception as e:
                self.log_cb(f"GPU error: {e}. Falling back to CPU.")
                self.tts = None
                self.clear_vram()
                self.use_gpu = False

        self.log_cb("Initializing CPU...")
        self.tts = TTS(config.TTS_MODEL, gpu=False)
        return "CPU"