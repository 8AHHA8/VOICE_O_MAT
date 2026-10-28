import customtkinter as ctk
import tkinter as tk
from GUI.theme import *

class SectionsMixin:
    def _build_ui(self):
        self.bg_label = ctk.CTkLabel(self, text="", anchor="center")
        self.bg_label.pack(fill="both", expand=True, padx=0, pady=0)
        self.bg_label.configure(image=generate_wood_texture(self.last_width + 100, self.last_height + 100))

        self.main_container = ctk.CTkFrame(self.bg_label, fg_color="transparent")
        self.main_container.place(relx=0.02, rely=0.5, anchor="w", relwidth=0.62, relheight=0.94)

        self.dark_overlay = ctk.CTkFrame(self.main_container, fg_color="#222222", corner_radius=20, border_width=4, border_color=COLOR_SHADOW)
        self.dark_overlay.pack(fill="both", expand=True)
        
        self.metal_panel = ctk.CTkFrame(self.dark_overlay, fg_color="#1c1c1c", corner_radius=15, border_width=2, border_color=COLOR_HIGHLIGHT)
        self.metal_panel.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_top_panel()
        self._build_input_frame()
        self._build_reel_frame()
        self._build_controls_frame()
        self._build_terminal_frame()

        self.monitor_outer = ctk.CTkFrame(self.bg_label, fg_color="#222222", corner_radius=20, border_width=4, border_color=COLOR_SHADOW)
        self.monitor_outer.place(relx=0.98, rely=0.5, anchor="e", relwidth=0.34, relheight=0.94)

        self.monitor_inner = ctk.CTkFrame(self.monitor_outer, fg_color="#1c1c1c", corner_radius=15, border_width=2, border_color=COLOR_HIGHLIGHT)
        self.monitor_inner.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.monitor_inner.grid_rowconfigure(0, weight=1)
        self.monitor_inner.grid_rowconfigure(1, weight=0)
        self.monitor_inner.grid_rowconfigure(2, weight=0)
        self.monitor_inner.grid_columnconfigure(0, weight=1)

        self.monitor_screen = ctk.CTkFrame(
            self.monitor_inner, fg_color=COLOR_SHADOW, corner_radius=12, border_width=2, border_color="#333333"
        )
        self.monitor_screen.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        self.monitor_glass = ctk.CTkFrame(
            self.monitor_screen, fg_color="#051405", corner_radius=8, border_width=2, border_color=COLOR_HIGHLIGHT
        )
        self.monitor_glass.pack(expand=True, fill="both", padx=3, pady=3)
        
        self.avatar_label = ctk.CTkLabel(
            self.monitor_glass, text="", font=("Courier New", 6, "bold"), 
            text_color=COLOR_TERMINAL_TEXT, justify="left", anchor="center"
        )
        self.avatar_label.pack(expand=True, fill="both", padx=2, pady=2)
        
        self._update_avatar()

        arrows_frame = ctk.CTkFrame(self.monitor_inner, fg_color="transparent")
        arrows_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        self.btn_arrow_left = ctk.CTkButton(
            arrows_frame, text="◀", width=45, height=28, 
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, 
            text_color=COLOR_BUTTON_TEXT, font=("Courier New", 14, "bold"), 
            corner_radius=6, border_width=1, border_color=COLOR_HIGHLIGHT,
            command=lambda: [self._play_click(), self._manual_rotate(-1)]
        )
        self.btn_arrow_left.pack(side="left", expand=True, padx=(0, 5))

        self.btn_arrow_right = ctk.CTkButton(
            arrows_frame, text="▶", width=45, height=28, 
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, 
            text_color=COLOR_BUTTON_TEXT, font=("Courier New", 14, "bold"), 
            corner_radius=6, border_width=1, border_color=COLOR_HIGHLIGHT,
            command=lambda: [self._play_click(), self._manual_rotate(1)]
        )
        self.btn_arrow_right.pack(side="left", expand=True, padx=(5, 0))

        tracking_frame = ctk.CTkFrame(self.monitor_inner, fg_color="transparent")
        tracking_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.btn_wander = ctk.CTkButton(
            tracking_frame, text="WANDER", width=100, height=32, 
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON, 
            text_color="#888888", font=("Courier New", 12, "bold"), 
            corner_radius=8, border_width=1, border_color=COLOR_HIGHLIGHT,
            command=lambda: [self._play_click(), self._set_eye_mode(False)]
        )
        self.btn_wander.pack(side="left", expand=True, padx=(0, 5))

        self.btn_track = ctk.CTkButton(
            tracking_frame, text="TRACK MOUSE", width=100, height=32, 
            fg_color=COLOR_BUTTON_HOVER, hover_color=COLOR_BUTTON_HOVER, 
            text_color=COLOR_BUTTON_TEXT, font=("Courier New", 12, "bold"), 
            corner_radius=8, border_width=1, border_color=COLOR_HIGHLIGHT,
            command=lambda: [self._play_click(), self._set_eye_mode(True)]
        )
        self.btn_track.pack(side="left", expand=True, padx=(5, 0))

    def _build_top_panel(self):
        top_panel = ctk.CTkFrame(self.metal_panel, fg_color="transparent")
        top_panel.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(top_panel, text="VOICE-O-MAT", font=ctk.CTkFont(family="Courier New", size=24, weight="bold"), text_color=COLOR_AMBER).pack(side="left")
        
        self.btn_sound = ctk.CTkButton(
            top_panel, text="SOUND: ON", width=110, height=30, 
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, 
            font=("Courier New", 12, "bold"), 
            corner_radius=8, border_width=1, border_color=COLOR_HIGHLIGHT,
            command=lambda: [self._play_click(), self._toggle_sound()]
        )
        self.btn_sound.pack(side="right", padx=(15, 0))
        
        self.led = ctk.CTkLabel(top_panel, text="●", text_color=COLOR_RED, font=("Arial", 22))
        self.led.pack(side="right")

    def _build_input_frame(self):
        panel_outer = ctk.CTkFrame(self.metal_panel, fg_color=COLOR_SHADOW, corner_radius=12)
        panel_outer.pack(fill="x", padx=15, pady=5)
        
        panel_inner = ctk.CTkFrame(panel_outer, fg_color=COLOR_PANEL_3D, corner_radius=10, border_width=1, border_color=COLOR_HIGHLIGHT)
        panel_inner.pack(fill="x", padx=2, pady=2)
        
        input_frame = ctk.CTkFrame(panel_inner, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="SOURCE TEXT:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        file_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        file_row.pack(fill="x", pady=(0, 10))
        self.entry_file = ctk.CTkEntry(file_row, fg_color="#0d0d0d", border_color=COLOR_SHADOW, border_width=2, text_color=COLOR_AMBER, font=("Courier New", 11))
        self.entry_file.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(file_row, text="LOAD", command=lambda: [self._play_click(), self._select_file()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, font=("Courier New", 11, "bold"), width=80, corner_radius=8, border_width=1, border_color=COLOR_HIGHLIGHT).pack(side="left")

        ctk.CTkLabel(input_frame, text="VOICE SAMPLE/SAMPLES:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        voice_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        voice_row.pack(fill="x", pady=(0, 10))
        self.entry_voice = ctk.CTkEntry(voice_row, fg_color="#0d0d0d", border_color=COLOR_SHADOW, border_width=2, text_color=COLOR_AMBER, font=("Courier New", 11))
        self.entry_voice.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(voice_row, text="LOAD", command=lambda: [self._play_click(), self._select_voice()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, font=("Courier New", 11, "bold"), width=80, corner_radius=8, border_width=1, border_color=COLOR_HIGHLIGHT).pack(side="left")

        grid_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 10))
        grid_frame.columnconfigure(0, weight=1, uniform="group1")
        grid_frame.columnconfigure(1, weight=1, uniform="group1")
        grid_frame.columnconfigure(2, weight=1, uniform="group1")

        lang_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        lang_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(lang_col, text="LANGUAGE:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        self.lang_var = ctk.StringVar(value="Polish (pl)")
        self.lang_menu = ctk.CTkOptionMenu(
            lang_col, variable=self.lang_var, 
            values=["Polish (pl)", "English (en)", "German (de)", "Spanish (es)", "French (fr)", "Italian (it)"], 
            fg_color="#0d0d0d", button_color=COLOR_BUTTON, button_hover_color=COLOR_HIGHLIGHT, 
            text_color=COLOR_AMBER, font=("Courier New", 11), dropdown_fg_color=COLOR_PANEL_3D, 
            dropdown_text_color=COLOR_AMBER, corner_radius=8, height=28, command=lambda _: self._play_click()
        )
        self.lang_menu.pack(fill="x")

        speed_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        speed_col.grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(speed_col, text="SPEED:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        speed_inner = ctk.CTkFrame(speed_col, fg_color="transparent")
        speed_inner.pack(fill="x")
        self.speed_slider = ctk.CTkSlider(speed_inner, from_=0.1, to=2.0, number_of_steps=19, button_color=COLOR_AMBER, progress_color=COLOR_SHADOW, command=self._update_speed_label)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.speed_slider.set(1.0)
        self.speed_label = ctk.CTkLabel(speed_inner, text="1.0x", text_color=COLOR_AMBER, font=("Courier New", 11, "bold"), width=40)
        self.speed_label.pack(side="left")

        pitch_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        pitch_col.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(pitch_col, text="PITCH:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        pitch_inner = ctk.CTkFrame(pitch_col, fg_color="transparent")
        pitch_inner.pack(fill="x")
        self.pitch_slider = ctk.CTkSlider(pitch_inner, from_=0.5, to=1.5, number_of_steps=10, button_color=COLOR_AMBER, progress_color=COLOR_SHADOW, command=self._update_pitch_label)
        self.pitch_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.pitch_slider.set(1.0)
        self.pitch_label = ctk.CTkLabel(pitch_inner, text="1.0", text_color=COLOR_AMBER, font=("Courier New", 11, "bold"), width=40)
        self.pitch_label.pack(side="left")

        out_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        out_col.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(10, 0))
        ctk.CTkLabel(out_col, text="OUTPUT FILE NAME:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        self.entry_output_name = ctk.CTkEntry(out_col, fg_color="#0d0d0d", border_color=COLOR_SHADOW, border_width=2, text_color=COLOR_AMBER, font=("Courier New", 11))
        self.entry_output_name.pack(fill="x")
        self.entry_output_name.insert(0, "generated_audio")

        preview_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        preview_col.grid(row=1, column=1, sticky="ew", padx=10, pady=(10, 0))
        ctk.CTkLabel(preview_col, text="PREVIEW TEXT:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        preview_inner = ctk.CTkFrame(preview_col, fg_color="transparent")
        preview_inner.pack(fill="x")
        self.entry_preview = ctk.CTkEntry(preview_inner, fg_color="#0d0d0d", border_color=COLOR_SHADOW, border_width=2, text_color=COLOR_AMBER, font=("Courier New", 11))
        self.entry_preview.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_preview.insert(0, "Hello world.")
        self.btn_preview = ctk.CTkButton(preview_inner, text="TEST", command=lambda: [self._play_click(), self._start_preview()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, font=("Courier New", 11, "bold"), width=50, corner_radius=6, border_width=1, border_color=COLOR_HIGHLIGHT)
        self.btn_preview.pack(side="left")

        play_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        play_col.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(10, 0))
        ctk.CTkLabel(play_col, text="PLAY LAST:", text_color=COLOR_TEXT, font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 2))
        play_inner = ctk.CTkFrame(play_col, fg_color="transparent")
        play_inner.pack(fill="x")
        self.playlist_var = ctk.StringVar()
        self.playlist_combo = ctk.CTkComboBox(
            play_inner, variable=self.playlist_var, values=[""], fg_color="#0d0d0d", 
            button_color=COLOR_BUTTON, button_hover_color=COLOR_HIGHLIGHT, 
            text_color=COLOR_AMBER, font=("Courier New", 11), dropdown_fg_color=COLOR_PANEL_3D, 
            dropdown_text_color=COLOR_AMBER, corner_radius=8, height=28, border_width=0,  
            command=lambda _: self._play_click()
        )
        self.playlist_combo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_play_last = ctk.CTkButton(play_inner, text="▶", command=lambda: [self._play_click(), self._play_last()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, font=("Courier New", 11, "bold"), width=30, corner_radius=6, border_width=1, border_color=COLOR_HIGHLIGHT)
        self.btn_play_last.pack(side="left")

    def _build_reel_frame(self):
        reel_frame_outer = ctk.CTkFrame(self.metal_panel, fg_color=COLOR_SHADOW, corner_radius=12)
        reel_frame_outer.pack(fill="x", padx=15, pady=15)
        
        reel_frame = ctk.CTkFrame(reel_frame_outer, fg_color="#000000", corner_radius=10, border_width=1, border_color="#333333")
        reel_frame.pack(fill="x", padx=2, pady=2)
        
        self.reel_left_label = ctk.CTkLabel(reel_frame, text="")
        self.reel_left_label.pack(side="left", expand=True, pady=10)
        self.reel_center_label = ctk.CTkLabel(reel_frame, text="[READY]\n00:00", font=("Courier New", 14, "bold"), text_color=COLOR_AMBER)
        self.reel_center_label.pack(side="left", expand=True, pady=10)
        self.reel_right_label = ctk.CTkLabel(reel_frame, text="")
        self.reel_right_label.pack(side="left", expand=True, pady=10)
        self._update_reels(0, 0.0)

    def _build_controls_frame(self):
        controls_frame = ctk.CTkFrame(self.metal_panel, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_start = ctk.CTkButton(controls_frame, text="▶ START", command=lambda: [self._play_click(), self._start_resume()], fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, font=("Courier New", 14, "bold"), corner_radius=10, height=45, border_width=2, border_color=COLOR_HIGHLIGHT)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_pause = ctk.CTkButton(controls_frame, text="|| PAUSE", command=lambda: [self._play_click(), self._pause()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT_DIM, font=("Courier New", 14, "bold"), corner_radius=10, height=45, state="disabled", border_width=2, border_color=COLOR_HIGHLIGHT)
        self.btn_pause.pack(side="left", expand=True, fill="x", padx=(5, 5))
        
        self.btn_abort = ctk.CTkButton(controls_frame, text="⏹ ABORT", command=lambda: [self._play_click(), self._abort()], fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER, text_color=COLOR_TEXT_DIM, font=("Courier New", 14, "bold"), corner_radius=10, height=45, state="disabled", border_width=2, border_color=COLOR_HIGHLIGHT)
        self.btn_abort.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _build_terminal_frame(self):
        terminal_outer = ctk.CTkFrame(self.metal_panel, fg_color=COLOR_SHADOW, corner_radius=12)
        terminal_outer.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        
        terminal_frame = ctk.CTkFrame(terminal_outer, fg_color=COLOR_TERMINAL_BG, corner_radius=10, border_width=2, border_color=COLOR_HIGHLIGHT)
        terminal_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.terminal_text = ctk.CTkTextbox(terminal_frame, fg_color="transparent", text_color=COLOR_TERMINAL_TEXT, font=("Courier New", 12), activate_scrollbars=True, wrap="word")
        self.terminal_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.terminal_text.insert("end", "[READY] Awaiting input...\n")
        self.terminal_text.configure(state="disabled")