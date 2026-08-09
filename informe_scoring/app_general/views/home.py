"""
views/home.py
=============
Pantalla de bienvenida / dashboard de la app unificada.
"""

import flet as ft

C_BG = "#1E1E2E"
C_PANEL = "#2A2A3E"
C_BORDER = "#3D3D5C"
C_ACCENT = "#7C6AF7"
C_ACCENT2 = "#9B8FFB"
C_TEXT = "#E0E0F0"
C_MUTED = "#9090B0"
C_GREEN = "#4CAF82"
C_RED = "#F7706A"
C_YELLOW = "#F7C26A"

APPS = [
    {
        "id": "productividad",
        "icon": ft.Icons.BAR_CHART_ROUNDED,
        "title": "Productividad General",
        "desc": "Procesa el archivo CMU y genera\nevento_unificados.xlsx + narración.",
        "color": "#7C6AF7",
    },
    {
        "id": "imputados",
        "icon": ft.Icons.PERSON_SEARCH_ROUNDED,
        "title": "Imputados",
        "desc": "Extrae contraventores, detenidos\ne integrados por operador y SISEP.",
        "color": "#4CAF82",
    },
    {
        "id": "colaboradores",
        "icon": ft.Icons.COMPARE_ARROWS_ROUNDED,
        "title": "Cruzar Colaboradores",
        "desc": "Cruza 2 Excel por SAE e inserta\nCOLABORADOR 1–5 entre columnas 7 y 8.",
        "color": "#F7C26A",
    },
    {
        "id": "diccionario",
        "icon": ft.Icons.BOOK_ROUNDED,
        "title": "Diccionario CIVILES",
        "desc": "Reconcilia nombres con el Diccionario\nMaestro y convierte a LP/DNI.",
        "color": "#F7706A",
    },
]


def build_home(on_navigate):
    """Construye la vista Home y devuelve un ft.Column."""

    def card(app):
        def on_hover(e):
            card_container.border = ft.Border.all(
                2, ft.Colors.with_opacity(0.8, app["color"])
            ) if e.data == "true" else ft.Border.all(1, C_BORDER)
            card_container.shadow = (
                ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, app["color"]))
                if e.data == "true"
                else None
            )
            card_container.update()

        card_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(app["icon"], size=38, color=app["color"]),
                        padding=ft.Padding(left=0, right=0, top=0, bottom=10),
                    ),
                    ft.Text(app["title"], size=16, weight=ft.FontWeight.BOLD, color=C_TEXT),
                    ft.Text(app["desc"], size=12, color=C_MUTED, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        text="Abrir",
                        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                        on_click=lambda _, aid=app["id"]: on_navigate(aid),
                        style=ft.ButtonStyle(
                            bgcolor=app["color"],
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=24,
            border_radius=14,
            bgcolor=C_PANEL,
            border=ft.Border.all(1, C_BORDER),
            on_hover=on_hover,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            expand=True,
        )
        return card_container

    header = ft.Column(
        [
            ft.Text("🏠  Panel de Control", size=28, weight=ft.FontWeight.BOLD, color=C_TEXT),
            ft.Text("Seleccioná la herramienta que querés usar", size=14, color=C_MUTED),
            ft.Divider(color=C_BORDER, height=30),
        ],
        spacing=4,
    )

    grid = ft.Row([card(a) for a in APPS], spacing=16, wrap=True, expand=True)

    footer = ft.Container(
        content=ft.Text(
            "Informe Scoring — Sistema Unificado  |  v1.0.0",
            size=11,
            color=C_MUTED,
            text_align=ft.TextAlign.CENTER,
        ),
        padding=ft.Padding(left=0, right=0, top=24, bottom=0),
    )

    return ft.Column([header, grid, footer], spacing=0, expand=True)
