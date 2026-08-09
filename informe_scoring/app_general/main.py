"""
main.py
=======
App General — Punto de entrada Flet unificado.

Agrupa:
  • Productividad General
  • Productividad Imputados
  • Cruzar Colaboradores
  • Diccionario CIVILES

Ejecutar con:
    uv run python app_general/main.py
"""

import sys
from pathlib import Path

import flet as ft

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_APP = Path(__file__).parent
if str(_APP) not in sys.path:
    sys.path.insert(0, str(_APP))


# ── Paleta ────────────────────────────────────────────────────────
C_BG = "#1E1E2E"
C_PANEL = "#2A2A3E"
C_SIDEBAR = "#16162A"
C_BORDER = "#3D3D5C"
C_ACCENT = "#7C6AF7"
C_TEXT = "#E0E0F0"
C_MUTED = "#9090B0"


# ── Módulos del sidebar ───────────────────────────────────────────
NAV_ITEMS = [
    {"id": "home",          "label": "Inicio",                "icon": ft.Icons.HOME_ROUNDED,            "color": C_ACCENT},
    {"id": "productividad", "label": "Productividad General", "icon": ft.Icons.BAR_CHART_ROUNDED,       "color": "#7C6AF7"},
    {"id": "imputados",     "label": "Imputados",             "icon": ft.Icons.PERSON_SEARCH_ROUNDED,   "color": "#4CAF82"},
    {"id": "colaboradores", "label": "Cruzar Colaboradores",  "icon": ft.Icons.COMPARE_ARROWS_ROUNDED,  "color": "#F7C26A"},
    {"id": "diccionario",   "label": "Diccionario CIVILES",   "icon": ft.Icons.BOOK_ROUNDED,            "color": "#F7706A"},
]


def main(page: ft.Page):
    page.title = "App General — Informe Scoring"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = C_BG
    page.window.width = 1100
    page.window.height = 780
    page.window.min_width = 900
    page.window.min_height = 600
    page.padding = 0

    current_view = {"id": "home"}
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    nav_buttons: dict[str, ft.Container] = {}

    # ── Cargar vista ──────────────────────────────────────────────
    def load_view(view_id: str):
        current_view["id"] = view_id

        for nid, btn in nav_buttons.items():
            is_active = nid == view_id
            item_data = next(i for i in NAV_ITEMS if i["id"] == nid)
            btn.bgcolor = ft.Colors.with_opacity(0.15, item_data["color"]) if is_active else "transparent"
            btn.border = ft.Border(
                left=ft.BorderSide(3, item_data["color"] if is_active else "transparent")
            )
            icon_ctrl = btn.content.controls[0]
            text_ctrl = btn.content.controls[1]
            icon_ctrl.color = item_data["color"] if is_active else C_MUTED
            text_ctrl.color = C_TEXT if is_active else C_MUTED
            text_ctrl.weight = ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL

        content_area.controls.clear()
        if view_id == "home":
            from views.home import build_home
            content_area.controls.append(build_home(load_view))
        elif view_id == "productividad":
            from views.productividad import build_productividad
            content_area.controls.append(build_productividad(page))
        elif view_id == "imputados":
            from views.imputados import build_imputados
            content_area.controls.append(build_imputados(page))
        elif view_id == "colaboradores":
            from views.colaboradores import build_colaboradores
            content_area.controls.append(build_colaboradores(page))
        elif view_id == "diccionario":
            from views.diccionario import build_diccionario
            content_area.controls.append(build_diccionario(page))

        page.update()

    # ── Botón de navegación ───────────────────────────────────────
    def make_nav_btn(item: dict) -> ft.Container:
        icon = ft.Icon(item["icon"], color=C_MUTED, size=20)
        label = ft.Text(item["label"], size=12, color=C_MUTED, no_wrap=True)

        def on_hover(e):
            if current_view["id"] != item["id"]:
                btn.bgcolor = (
                    ft.Colors.with_opacity(0.06, item["color"])
                    if e.data == "true"
                    else "transparent"
                )
                btn.update()

        btn = ft.Container(
            content=ft.Row(
                [icon, label],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            border_radius=8,
            on_click=lambda _, vid=item["id"]: load_view(vid),
            on_hover=on_hover,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            border=ft.Border(left=ft.BorderSide(3, "transparent")),
            margin=ft.Margin(left=4, right=4, top=2, bottom=2),
        )
        nav_buttons[item["id"]] = btn
        return btn

    # ── Sidebar ───────────────────────────────────────────────────
    sidebar = ft.Container(
        content=ft.Column(
            [
                # Header con logo
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.ANALYTICS_ROUNDED, color=ft.Colors.WHITE, size=22),
                                bgcolor=C_ACCENT,
                                width=40,
                                height=40,
                                border_radius=10,
                            ),
                            ft.Column(
                                [
                                    ft.Text("App General", size=14, weight=ft.FontWeight.BOLD, color=C_TEXT),
                                    ft.Text("Informe Scoring", size=10, color=C_MUTED),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    border=ft.Border(bottom=ft.BorderSide(1, C_BORDER)),
                ),

                # Botones de navegación
                ft.Container(
                    content=ft.Column(
                        [make_nav_btn(item) for item in NAV_ITEMS],
                        spacing=0,
                    ),
                    padding=ft.Padding(left=0, right=0, top=8, bottom=0),
                    expand=True,
                ),

                # Versión
                ft.Container(
                    content=ft.Text("v1.0.0", size=10, color=C_MUTED),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    border=ft.Border(top=ft.BorderSide(1, C_BORDER)),
                ),
            ],
            spacing=0,
            expand=True,
        ),
        width=200,
        bgcolor=C_SIDEBAR,
        border=ft.Border(right=ft.BorderSide(1, C_BORDER)),
    )

    # ── Layout principal ──────────────────────────────────────────
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(
                    content=ft.Column([content_area], expand=True, scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                    bgcolor=C_BG,
                ),
            ],
            spacing=0,
            expand=True,
        )
    )

    load_view("home")


if __name__ == "__main__":
    ft.run(main)
