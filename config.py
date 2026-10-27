import os

COLOR_TEXT = "#e0e0e0"         
COLOR_TEXT_DIM = "#999999"     
COLOR_AMBER = "#ffb000"        
COLOR_RED = "#b80000"          
COLOR_RED_HOVER = "#d10000"    
COLOR_BUTTON = "#2a2a2a"       
COLOR_BUTTON_HOVER = "#3a3a3a"

MAX_SEGMENT_CHARS = 180
WINDOW_WIDTH = 820
WINDOW_HEIGHT = 680

TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Audio")

OUTPUT_DIR = os.path.join(AUDIO_DIR, "output_audio")
TEMP_DIR = os.path.join(AUDIO_DIR, "temp_audio")