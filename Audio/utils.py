import os
import re
import config

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
try:
    from pyxtxt import xtxt
    PYXTXT_AVAILABLE = True
except ImportError:
    PYXTXT_AVAILABLE = False
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


def read_text_from_file(path):
    ext = os.path.splitext(path)[1].lower()
    
    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
            
    elif ext == ".pdf":
        if not PDF_AVAILABLE:
            raise RuntimeError("pypdf missing. Install: pip install pypdf")
        reader = PdfReader(path)
        return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
        
    elif ext == ".docx":
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx missing. Install: pip install python-docx")
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
        
    else:
        if not PYXTXT_AVAILABLE:
            raise RuntimeError(f"Format {ext} wymaga biblioteki pyxtxt. Zainstaluj: pip install pyxtxt")
        
        try:
            text = xtxt(path)
            if text is None or not text.strip():
                raise RuntimeError(f"Nie udało się wyciągnąć tekstu z pliku {os.path.basename(path)}")
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas czytania pliku {os.path.basename(path)}: {str(e)}")


def split_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    segments, current = [], ""
    for s in sentences:
        if len(s) > config.MAX_SEGMENT_CHARS:
            if current:
                segments.append(current.strip())
                current = ""
            for i in range(0, len(s), config.MAX_SEGMENT_CHARS):
                segments.append(s[i:i + config.MAX_SEGMENT_CHARS].strip())
            continue
        if len(current) + len(s) + 1 <= config.MAX_SEGMENT_CHARS:
            current = f"{current} {s}".strip()
        else:
            if current:
                segments.append(current.strip())
            current = s
    if current:
        segments.append(current.strip())
    return [s for s in segments if s]


def load_audio_as_wav_temp(file_paths, log_cb):
    if not PYDUB_AVAILABLE:
        raise RuntimeError("pydub missing. Install: pip install pydub (requires FFmpeg)")
        
    processed_paths = []
    for i, file_path in enumerate(file_paths):
        if file_path.lower().endswith(".wav"):
            processed_paths.append(file_path)
        else:
            log_cb(f"Decoding {os.path.basename(file_path)} to WAV...")
            try:
                audio = AudioSegment.from_file(file_path)
                temp_path = os.path.join(config.TEMP_DIR, f"temp_voice_sample_{i}.wav")
                audio.export(temp_path, format="wav")
                processed_paths.append(temp_path)
            except Exception as e:
                raise RuntimeError(f"Failed to decode audio file. Make sure FFmpeg is installed. Error: {e}")
    return processed_paths