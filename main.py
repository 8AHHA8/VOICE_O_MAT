import os

ffmpeg_shared_bin = r"C:\ffmpeg-shared\bin"
if os.path.exists(ffmpeg_shared_bin):
    os.add_dll_directory(ffmpeg_shared_bin)

from GUI.app import XTTSReaderApp

if __name__ == "__main__":
    app = XTTSReaderApp()
    app.mainloop()