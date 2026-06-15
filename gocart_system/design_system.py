"""
GoCart Design System - Modern UI Constants and Components
"""

import flet as ft

# Color Palette
class Colors:
    # Primary Colors
    PRIMARY = "#6366f1"        # Indigo
    PRIMARY_LIGHT = "#818cf8"
    PRIMARY_DARK = "#4f46e5"

    # Secondary Colors
    SECONDARY = "#06b6d4"      # Cyan
    SECONDARY_LIGHT = "#22d3ee"
    SECONDARY_DARK = "#0891b2"

    # Accent Colors
    ACCENT = "#f43f5e"         # Rose
    ACCENT_LIGHT = "#fb7185"
    ACCENT_DARK = "#e11d48"

    # Status Colors
    SUCCESS = "#22c55e"        # Green
    SUCCESS_LIGHT = "#4ade80"
    SUCCESS_DARK = "#16a34a"

    WARNING = "#f59e0b"        # Amber
    WARNING_LIGHT = "#fbbf24"
    WARNING_DARK = "#d97706"

    ERROR = "#ef4444"          # Red
    ERROR_LIGHT = "#f87171"
    ERROR_DARK = "#dc2626"

    # Neutral Colors
    BACKGROUND = "#0a0e27"     # Dark navy
    SURFACE = "#141b34"        # Darker navy
    SURFACE_LIGHT = "#1c2548"  # Medium navy
    CARD = "#1e293b"           # Slate

    # Text Colors
    TEXT_PRIMARY = "#f8fafc"   # Almost white
    TEXT_SECONDARY = "#cbd5e1" # Light gray
    TEXT_MUTED = "#64748b"     # Medium gray

    # Border Colors
    BORDER = "#334155"         # Dark gray
    BORDER_LIGHT = "#475569"   # Medium gray

# Typography
class Typography:
    H1 = ft.TextStyle(size=32, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY)
    H2 = ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY)
    H3 = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY)
    H4 = ft.TextStyle(size=18, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY)
    BODY_LARGE = ft.TextStyle(size=16, color=Colors.TEXT_SECONDARY)
    BODY = ft.TextStyle(size=14, color=Colors.TEXT_SECONDARY)
    BODY_SMALL = ft.TextStyle(size=12, color=Colors.TEXT_MUTED)
    CAPTION = ft.TextStyle(size=11, color=Colors.TEXT_MUTED, weight=ft.FontWeight.W_500)

# Spacing System (8px grid)
class Spacing:
    XS = 4   # 4px
    SM = 8   # 8px
    MD = 16  # 16px
    LG = 24  # 24px
    XL = 32  # 32px
    XXL = 48 # 48px

# Border Radius
class BorderRadius:
    SM = 8
    MD = 12
    LG = 16
    XL = 24

# Shadows
class Shadows:
    SM = ft.BoxShadow(
        spread_radius=1,
        blur_radius=4,
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        offset=ft.Offset(0, 2)
    )
    MD = ft.BoxShadow(
        spread_radius=2,
        blur_radius=8,
        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        offset=ft.Offset(0, 4)
    )
    LG = ft.BoxShadow(
        spread_radius=4,
        blur_radius=16,
        color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
        offset=ft.Offset(0, 8)
    )

# Common Styles
class Styles:
    @staticmethod
    def card_style():
        return ft.Container(
            border_radius=BorderRadius.LG,
            bgcolor=Colors.CARD,
            shadow=Shadows.MD,
            padding=Spacing.LG
        )

    @staticmethod
    def button_primary():
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: Colors.PRIMARY,
                ft.ControlState.HOVERED: Colors.PRIMARY_LIGHT,
                ft.ControlState.DISABLED: Colors.BORDER,
            },
            color={
                ft.ControlState.DEFAULT: Colors.TEXT_PRIMARY,
                ft.ControlState.DISABLED: Colors.TEXT_MUTED,
            },
            elevation={
                ft.ControlState.DEFAULT: 4,
                ft.ControlState.HOVERED: 8,
            },
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
        )

    @staticmethod
    def button_secondary():
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.with_opacity(0.1, Colors.SECONDARY),
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.2, Colors.SECONDARY),
            },
            color={
                ft.ControlState.DEFAULT: Colors.SECONDARY,
            },
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
        )

    @staticmethod
    def text_field_style():
        return ft.TextField(
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
        )

# Modern Components
class ModernComponents:
    @staticmethod
    def gradient_background():
        return ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[
                    Colors.BACKGROUND,
                    ft.Colors.with_opacity(0.8, Colors.SURFACE),
                    Colors.BACKGROUND,
                ]
            ),
            expand=True
        )

    @staticmethod
    def animated_card(content, on_hover=None):
        def hover_handler(e):
            if on_hover:
                on_hover(e)
            e.control.shadow = Shadows.LG if e.data == "true" else Shadows.MD
            e.control.update()

        return ft.Container(
            content=content,
            border_radius=BorderRadius.LG,
            bgcolor=Colors.CARD,
            shadow=Shadows.MD,
            padding=Spacing.LG,
            on_hover=hover_handler,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    @staticmethod
    def icon_button(icon, on_click=None, color=Colors.TEXT_SECONDARY, tooltip=""):
        return ft.IconButton(
            icon,
            on_click=on_click,
            icon_color=color,
            tooltip=tooltip,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, color),
                },
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
        )

    @staticmethod
    def status_badge(text, color=Colors.SUCCESS, icon=None):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=14, color=color) if icon else None,
                    ft.Text(text, size=12, weight=ft.FontWeight.W_600, color=color),
                ],
                spacing=Spacing.XS,
                tight=True,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border_radius=BorderRadius.SM,
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS),
        )