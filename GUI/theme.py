import customtkinter as ctk
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random

COLOR_TEXT = "#e0e0e0"
COLOR_TEXT_DIM = "#999999"
COLOR_AMBER = "#ffb000"
COLOR_RED = "#b80000"
COLOR_RED_HOVER = "#d10000"
COLOR_BUTTON = "#3a3a3a"
COLOR_BUTTON_HOVER = "#4a4a4a"
COLOR_TERMINAL_BG = "#051405"
COLOR_TERMINAL_TEXT = "#33ff33"

COLOR_SHADOW = "#111111"
COLOR_HIGHLIGHT = "#555555"
COLOR_PANEL_3D = "#1a1a1a"

def generate_wood_texture(width, height):
    img = Image.new("RGB", (width, height), "#2a1d16")
    draw = ImageDraw.Draw(img)
    for y in range(0, height, 4):
        points = []
        for x in range(0, width, 10):
            offset = int(10 * np.sin(x / 100.0) + random.randint(-2, 2))
            points.append((x, y + offset))
        if len(points) > 1:
            color = random.choice(["#3b2619", "#452d1e", "#382316"])
            draw.line(points, fill=color, width=random.randint(1, 2))
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))