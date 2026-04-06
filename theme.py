"""
NeuroMentor Theme Configuration
Charcoal / Gold / Amber palette.
All colors are RGBA tuples (0-1 range) for Kivy.
"""


# ============================================================
# COLOR PALETTE
# ============================================================

# Primary accent - Gold Yellow
GOLD = (0.910, 0.753, 0.180, 1)          # #e8c02e

# Secondary accent - Lighter Gold
TEAL = (0.933, 0.800, 0.310, 1)          # #eecc4f

# Danger/Stress - Amber Orange
RED = (0.863, 0.608, 0.157, 1)           # #dc9b28

# Backgrounds
BG_DARK = (0.200, 0.180, 0.235, 1)       # #332e3c
PANEL_BG = (0.235, 0.216, 0.275, 1)      # #3c3746
CARD_BG = (0.275, 0.255, 0.318, 1)       # #464151

# Borders
BORDER_DARK = (0.310, 0.290, 0.357, 1)   # #4f4a5b
BORDER_LIGHT = (0.357, 0.337, 0.400, 1)  # #5b5666

# Text colors
TEXT_PRIMARY = (0.910, 0.902, 0.925, 1)   # #e8e6ec
TEXT_SECONDARY = (0.753, 0.737, 0.773, 1) # #c0bcc5
TEXT_MUTED = (0.475, 0.455, 0.502, 1)     # #797480

# Input
INPUT_BG = (0.173, 0.157, 0.208, 1)      # #2c2835
INPUT_BORDER = (0.357, 0.337, 0.400, 1)   # #5b5666

# Additional UI colors
SIDEBAR_BG = (0.180, 0.161, 0.212, 1)    # #2e2936
SIDEBAR_BORDER = (0.310, 0.290, 0.357, 1) # #4f4a5b
DARK_CARD = (0.157, 0.141, 0.188, 1)     # #282430
BUTTON_BG = (0.275, 0.255, 0.318, 1)     # #464151
DANGER_BUTTON_BG = (0.250, 0.200, 0.100, 1) # #40331a

# Transparent
TRANSPARENT = (0, 0, 0, 0)


# ============================================================
# FONT SIZES
# ============================================================

FONT_TITLE_LARGE = 28
FONT_TITLE_MEDIUM = 22
FONT_HEADING_LARGE = 24
FONT_HEADING_MEDIUM = 18
FONT_BODY_LARGE = 16
FONT_BODY_REGULAR = 14
FONT_BODY_SMALL = 12
FONT_DISPLAY_LARGE = 72
FONT_TIMER = 24


# ============================================================
# HELPERS
# ============================================================

def rgba_hex(hex_color, alpha=1.0):
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)


def with_alpha(color, alpha):
    """Return a color tuple with modified alpha."""
    return (color[0], color[1], color[2], alpha)
