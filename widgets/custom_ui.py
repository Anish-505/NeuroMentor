"""
Custom UI Elements with shadows and gradients.
"""
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
import theme

class ShadowButton(ButtonBehavior, Label):
    """A button with a soft drop-shadow and rounded corners."""
    
    def __init__(self, **kwargs):
        self.bg_color = kwargs.pop('bg_color', kwargs.pop('background_color', theme.BUTTON_BG))
        self.radius = kwargs.pop('radius', 12)
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, state=self.update_canvas)
        self.update_canvas()
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Soft shadow effect
            shadow_steps = 4
            base_offset = 1 if self.state == 'down' else 4
            
            for i in range(shadow_steps):
                alpha = 0.25 * (1.0 - i/shadow_steps)
                r_exp = self.radius + i
                Color(0, 0, 0, alpha)
                RoundedRectangle(
                    pos=(self.x - i + 2, self.y - base_offset - i),
                    size=(self.width + i*2, self.height + i*2),
                    radius=[r_exp]
                )
            
            # Main button background
            if self.state == 'down':
                # Dim the color slightly
                Color(self.bg_color[0]*0.8, self.bg_color[1]*0.8, self.bg_color[2]*0.8, 1)
            else:
                Color(*self.bg_color)
            
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

from kivy.uix.widget import Widget
from kivy.graphics import Line

class MenuBurgerButton(ButtonBehavior, Widget):
    """A perfect hamburger menu icon that transitions to an X."""
    def __init__(self, **kwargs):
        self.color = kwargs.pop('color', theme.GOLD)
        self.is_open = False
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def set_open(self, is_open):
        self.is_open = is_open
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color)
            w = self.width * 0.5
            h = max(2, self.height * 0.08)
            cx, cy = self.center_x, self.center_y
            
            if not self.is_open:
                # Hamburger: 3 lines
                spacing = self.height * 0.22
                RoundedRectangle(pos=(cx - w/2, cy + spacing - h/2), size=(w, h), radius=[h/2])
                RoundedRectangle(pos=(cx - w/2, cy - h/2), size=(w, h), radius=[h/2])
                RoundedRectangle(pos=(cx - w/2, cy - spacing - h/2), size=(w, h), radius=[h/2])
            else:
                # X shape
                Line(points=[cx - w/2, cy - w/2, cx + w/2, cy + w/2], width=h/2, cap='round')
                Line(points=[cx - w/2, cy + w/2, cx + w/2, cy - w/2], width=h/2, cap='round')

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle

from kivy.graphics.texture import Texture

class GradientCard(BoxLayout):
    """A card with a soft gradient background, rounded corners, and a drop shadow."""
    def __init__(self, accent_color=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', 15)
        kwargs.setdefault('spacing', 8)
        self.accent_color = accent_color
        self.radius = kwargs.pop('radius', 12)
        super().__init__(**kwargs)
        
        # Create a basic 1x2 vertical gradient texture mapping top #202020 to bottom #0E0E0E
        self.texture = Texture.create(size=(1, 2), colorfmt='rgba')
        self.texture.mag_filter = 'linear'
        self.texture.min_filter = 'linear'
        
        # Bottom color, Top color (charcoal tones)
        buf = bytes([
            51, 46, 60, 255,   # bottom (darker charcoal #332e3c)
            70, 65, 81, 255,   # top (lighter charcoal #464151)
        ])
        self.texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Soft dark drop shadow effect
            shadow_steps = 4
            for i in range(shadow_steps):
                alpha = 0.2 * (1.0 - i/shadow_steps)
                r_exp = self.radius + i
                Color(0, 0, 0, alpha)
                RoundedRectangle(
                    pos=(self.x - i + 2, self.y - 2 - i),
                    size=(self.width + i*2, self.height + i*2),
                    radius=[r_exp]
                )
            
            # Gradient rounded background
            Color(1, 1, 1, 1)  # White to allow natural texture colors
            RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius], texture=self.texture
            )

            # Optional accent color indicator strip
            if self.accent_color:
                Color(*self.accent_color)
                RoundedRectangle(
                    pos=(self.x + 8, self.y + self.height - 4), 
                    size=(self.width - 16, 3), 
                    radius=[1.5]
                )
