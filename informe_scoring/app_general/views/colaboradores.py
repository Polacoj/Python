"""
views/colaboradores.py
======================
Vista Flet para Cruzar Colaboradores.
"""

import flet as ft
from views.home import C_PANEL, C_BORDER, C_ACCENT, C_TEXT, C_MUTED, C_GREEN, C_RED, C_YELLOW


def build_colaboradores(page: ft.Page):
    rutas = {"arch1": None, "arch2": None, "salida": None, "hoja": None}

    def make_file_row(label: str, key: str):
        lbl = ft.Text("Sin seleccionar", size=12, color=C_MUTED, italic=True, expand=True)
        picker = ft.FilePicker()

        def on_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            rutas[key] = e.files[0].path
            lbl.value = f"📂 {e.files[0].name}"
            lbl.color = C_TEXT
            lbl.italic = False
            if key == "arch1" and not rutas["salida"]:
                from pathlib import Path
                rutas["salida"] = str(Path(e.files[0].path).parent / "resultado_colaboradores.xlsx")
                salida_field.value = rutas["salida"]
            _check_ready()
            page.update()

        picker.on_result = on_picked
        page.overlay.append(picker)

        row = ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=11, color=C_MUTED, weight=ft.FontWeight.W_600),
                    ft.Row(
                        [
                            lbl,
                            ft.IconButton(
                                ft.Icons.FOLDER_OPEN_ROUNDED,
                                icon_color=C_MUTED,
                                on_click=lambda _, p=picker: p.pick_files(
                                    dialog_title=f"Seleccionar {label}",
                                    allowed_extensions=["xlsx", "xls", "xlsm"],
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=4,
            ),
            padding=12, border_radius=8, bgcolor=C_PANEL,
            border=ft.Border.all(1, C_BORDER),
        )
        return row, lbl

    (row_arch1, lbl_arch1) = make_file_row("Archivo 1 — Eventos diarios (contiene SAE)", "arch1")
    (row_arch2, lbl_arch2) = make_file_row("Archivo 2 — Colaboradores (SAE + COLABORADORES 1-5)", "arch2")

    salida_field = ft.TextField(
        hint_text="Ruta del archivo de salida (.xlsx)",
        hint_style=ft.TextStyle(color=C_MUTED),
        bgcolor=C_PANEL, border_color=C_BORDER, focused_border_color=C_ACCENT,
        color=C_TEXT, text_size=12, border_radius=8,
        on_change=lambda e: rutas.update({"salida": e.control.value}),
    )
    save_picker = ft.FilePicker()

    def on_save_picked(e: ft.FilePickerResultEvent):
        if e.path:
            path = e.path if e.path.endswith(".xlsx") else e.path + ".xlsx"
            rutas["salida"] = path
            salida_field.value = path
            _check_ready()
            page.update()

    save_picker.on_result = on_save_picked
    page.overlay.append(save_picker)

    progress = ft.ProgressBar(value=0, color=C_ACCENT, bgcolor=C_BORDER, height=6, border_radius=3)
    lbl_estado = ft.Text("En espera", size=12, color=C_MUTED, text_align=ft.TextAlign.CENTER)
    btn_procesar = ft.ElevatedButton(
        text="▶  Procesar archivos",
        icon=ft.Icons.COMPARE_ARROWS_ROUNDED,
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=C_ACCENT, color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    hoja_dd = ft.Dropdown(
        label="Hoja del Archivo 2",
        hint_text="Seleccioná la hoja",
        bgcolor=C_PANEL, border_color=C_BORDER, focused_border_color=C_ACCENT,
        color=C_TEXT, label_style=ft.TextStyle(color=C_MUTED),
        border_radius=8,
        on_change=lambda e: (rutas.update({"hoja": e.control.value}), _check_ready(), page.update()),
        visible=False,
    )

    def _check_ready():
        btn_procesar.disabled = not all([rutas["arch1"], rutas["arch2"], rutas["salida"]])
        page.update()

    def _cargar_hojas(_):
        if not rutas["arch2"]:
            return
        from core.colaboradores_logic import get_sheet_names
        try:
            hojas = get_sheet_names(rutas["arch2"])
            hoja_dd.options = [ft.dropdown.Option(h) for h in hojas]
            if len(hojas) == 1:
                rutas["hoja"] = hojas[0]
                hoja_dd.value = hojas[0]
                hoja_dd.visible = False
            else:
                hoja_dd.visible = True
            page.update()
        except Exception as e:
            lbl_estado.value = f"✗ Error al leer hojas: {e}"
            lbl_estado.color = C_RED
            page.update()

    def on_procesar(_):
        from core.colaboradores_logic import procesar_cruce, get_sheet_names

        if not rutas["hoja"]:
            try:
                rutas["hoja"] = get_sheet_names(rutas["arch2"])[0]
            except Exception as e:
                lbl_estado.value = f"✗ {e}"
                lbl_estado.color = C_RED
                page.update()
                return

        btn_procesar.disabled = True
        progress.value = None
        lbl_estado.value = f"Usando hoja: {rutas['hoja']}"
        lbl_estado.color = C_MUTED
        page.update()

        def _on_progress(valor: int, mensaje: str):
            progress.value = valor / 100
            lbl_estado.value = mensaje
            lbl_estado.color = C_MUTED
            page.update()

        def _on_done(stats: dict):
            progress.value = 1
            lbl_estado.value = f"✅ Guardado en: {stats['salida']}"
            lbl_estado.color = C_GREEN
            btn_procesar.disabled = False
            dlg = ft.AlertDialog(
                title=ft.Text("✅ Proceso completado", color=C_GREEN, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    ft.Column([
                        ft.Text(f"Total filas: {stats['total']}", size=13, color=C_TEXT),
                        ft.Text(f"SAEs con coincidencia: {stats['encontrados']}", size=13, color=C_GREEN),
                        ft.Text(f"SAEs sin coincidencia: {stats['no_encontrados']}", size=13, color=C_YELLOW),
                        ft.Divider(color=C_BORDER),
                        ft.Text(f"Guardado en:\n{stats['salida']}", size=11, color=C_MUTED, selectable=True),
                    ], spacing=6),
                    width=480,
                ),
                actions=[ft.TextButton("Cerrar", on_click=lambda _: page.close(dlg))],
                bgcolor=C_PANEL,
            )
            page.open(dlg)
            page.update()

        def _on_error(msg: str):
            progress.value = 0
            lbl_estado.value = "✗ Error"
            lbl_estado.color = C_RED
            btn_procesar.disabled = False
            dlg = ft.AlertDialog(
                title=ft.Text("✗ Error", color=C_RED, weight=ft.FontWeight.BOLD),
                content=ft.Container(ft.Text(msg, size=12, color=C_TEXT, selectable=True), width=500, max_height=300),
                actions=[ft.TextButton("Cerrar", on_click=lambda _: page.close(dlg))],
                bgcolor=C_PANEL,
            )
            page.open(dlg)
            page.update()

        procesar_cruce(
            rutas["arch1"], rutas["arch2"], rutas["salida"], rutas["hoja"],
            lambda msg: None, _on_progress, _on_done, _on_error,
        )

    btn_procesar.on_click = on_procesar

    return ft.Column(
        [
            ft.Column(
                [
                    ft.Row([ft.Icon(ft.Icons.COMPARE_ARROWS_ROUNDED, color=C_YELLOW, size=28),
                            ft.Text("Cruzar Colaboradores", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT)], spacing=10),
                    ft.Text("Inserta COLABORADOR 1 al 5 entre columnas 7 y 8, cruzando por SAE", size=13, color=C_MUTED),
                    ft.Divider(color=C_BORDER, height=20),
                ],
                spacing=4,
            ),
            row_arch1,
            row_arch2,
            ft.ElevatedButton(
                "🔍 Cargar hojas del Archivo 2",
                on_click=_cargar_hojas,
                style=ft.ButtonStyle(
                    bgcolor=C_PANEL, color=C_TEXT,
                    side=ft.BorderSide(1, C_BORDER),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
            hoja_dd,
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Archivo de salida", size=11, color=C_MUTED, weight=ft.FontWeight.W_600),
                        ft.Row([
                            ft.Container(salida_field, expand=True),
                            ft.IconButton(
                                ft.Icons.SAVE_ROUNDED, icon_color=C_MUTED,
                                on_click=lambda _: save_picker.save_file(
                                    dialog_title="Guardar resultado como",
                                    file_name="resultado_colaboradores.xlsx",
                                    allowed_extensions=["xlsx"],
                                ),
                            ),
                        ]),
                    ],
                    spacing=4,
                ),
                padding=12, border_radius=8, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Container(
                content=ft.Column([ft.Row([lbl_estado], alignment=ft.MainAxisAlignment.CENTER), progress], spacing=8),
                padding=12, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Row([btn_procesar], alignment=ft.MainAxisAlignment.CENTER),
        ],
        spacing=12,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
