# ui/components.py - Custom UI widgets
import tkinter as tk
from config import Config

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = kwargs.get('bg', Config.GUI_ACCENT)
        self.default_fg = kwargs.get('fg', Config.GUI_TEXT)
        self.config(
            relief='flat',
            border=0,
            padx=20,
            pady=10,
            font=(Config.GUI_FONT_PRIMARY, 10, 'bold'),
            cursor='hand2'
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, e):
        self.config(bg=Config.GUI_ACCENT_DARK)
        
    def on_leave(self, e):
        self.config(bg=self.default_bg)

class ModernCard(tk.Frame):
    def __init__(self, master=None, title="", **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=Config.GUI_CARD_BG,
            relief='flat',
            border=1,
            highlightbackground='#333355',
            highlightthickness=1
        )
        if title:
            title_label = tk.Label(
                self, 
                text=title, 
                bg=Config.GUI_CARD_BG,
                fg=Config.GUI_ACCENT,
                font=(Config.GUI_FONT_PRIMARY, 12, 'bold')
            )
            title_label.pack(pady=(10, 5))

class DigitalDisplay(tk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=Config.GUI_BG,
            fg=Config.GUI_SUCCESS,
            font=(Config.GUI_FONT_SECONDARY, 24, 'bold'),
            justify='center'
        )