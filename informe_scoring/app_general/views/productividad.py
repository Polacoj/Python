"""
views/productividad.py
======================
Vista Flet para Productividad General.
"""

import threading
import flet as ft
from views.home import C_PANEL, C_BORDER, C_ACCENT, C_TEXT, C_MUTED, C_GREEN, C_RED, C_YELLOW


def build_productividad(page: ft.Page):
    archivo_principal = {"path": None, "name": None}
    ruta_unificado = {"path": None}

    lbl_archivo = ft.Text("📂 Ningún archivo seleccionado", size=13, color=C_MUTED, italic=True)
    lbl_estado = ft.Text("🟢 Listo para procesar", size=13, color=C_GREEN)
    log_view = ft.ListView(expand=True, spacing=2, auto_scroll=True, padding=10)
    progress = ft.ProgressBar(value=0, color=C_ACCENT, bgcolor=C_BORDER, height=6, border_radius=3)

    btn_procesar = ft.ElevatedButton(
        text="▶  Procesar archivo",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=C_ACCENT,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    btn_narracion = ft.OutlinedButton(
        text="📝  Agregar Narración",
        icon=ft.Icons.ADD_COMMENT_ROUNDED,
        disabled=True,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1, C_ACCENT),
            color=C_ACCENT,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    file_picker = ft.FilePicker()
    narr_picker = ft.FilePicker()
    page.overlay.extend([file_picker, narr_picker])

    def log(msg: str):
        log_view.controls.append(ft.Text(msg, size=11, color="#C8D0E0", font_family="Consolas"))
        page.update()

    def on_file_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        f = e.files[0]
        archivo_principal["path"] = f.path
        archivo_principal["name"] = f.name
        lbl_archivo.value = f"📂 {f.name}"
        lbl_archivo.color = C_TEXT
        lbl_archivo.italic = False
        btn_procesar.disabled = False
        lbl_estado.value = "📁 Archivo seleccionado — listo para procesar"
        lbl_estado.color = C_YELLOW
        log(f"\n{'='*60}")
        log(f"📂 Archivo: {f.name}")
        page.update()

    def on_procesar_click(_):
        from core.productividad_logic import procesar_excel
        btn_procesar.disabled = True
        btn_narracion.disabled = True
        lbl_estado.value = "🔄 Procesando..."
        lbl_estado.color = C_YELLOW
        progress.value = None
        page.update()

        def _run():
            ok, msg, ruta = procesar_excel(archivo_principal["path"], log)
            ruta_unificado["path"] = ruta

            def _update():
                progress.value = 1 if ok else 0
                lbl_estado.value = "✅ Completado" if ok else "✗ Error"
                lbl_estado.color = C_GREEN if ok else C_RED
                if ok:
                    btn_narracion.disabled = False
                btn_procesar.disabled = False
                _dlg("✅ Proceso completado" if ok else "✗ Error", msg, error=not ok)
                page.update()

            _update()

        threading.Thread(target=_run, daemon=True).start()

    def on_narracion_click(_):
        narr_picker.pick_files(
            dialog_title="Seleccionar archivo de Narración",
            allowed_extensions=["xlsx", "xls"],
        )

    def on_narracion_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        from core.productividad_logic import procesar_narracion
        ruta_narr = e.files[0].path
        lbl_estado.value = "🔄 Procesando narración..."
        lbl_estado.color = C_YELLOW
        progress.value = None
        page.update()

        def _run():
            ok, msg = procesar_narracion(ruta_narr, ruta_unificado["path"], archivo_principal["name"], log)

            def _update():
                progress.value = 1 if ok else 0
                lbl_estado.value = "✅ Narración agregada" if ok else "✗ Error en narración"
                lbl_estado.color = C_GREEN if ok else C_RED
                _dlg("✅ Narración procesada" if ok else "✗ Error", msg, error=not ok)
                page.update()

            _update()

        threading.Thread(target=_run, daemon=True).start()

    def _dlg(titulo: str, mensaje: str, error: bool = False):
        dlg = ft.AlertDialog(
            title=ft.Text(titulo, color=C_RED if error else C_GREEN, weight=ft.FontWeight.BOLD),
            content=ft.Container(ft.Text(mensaje, size=12, color=C_TEXT, selectable=True), width=500, max_height=300),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: page.close(dlg))],
            bgcolor=C_PANEL,
        )
        page.open(dlg)

    file_picker.on_result = on_file_picked
    narr_picker.on_result = on_narracion_picked
    btn_procesar.on_click = on_procesar_click
    btn_narracion.on_click = on_narracion_click

    return ft.Column(
        [
            ft.Column(
                [
                    ft.Row([ft.Icon(ft.Icons.BAR_CHART_ROUNDED, color=C_ACCENT, size=28),
                            ft.Text("Productividad General", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT)], spacing=10),
                    ft.Text("Procesa el archivo CMU Excel y genera eventos_unificados.xlsx", size=13, color=C_MUTED),
                    ft.Divider(color=C_BORDER, height=20),
                ],
                spacing=4,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Archivo de entrada", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
                        ft.Row(
                            [
                                ft.Container(lbl_archivo, expand=True),
                                ft.ElevatedButton(
                                    "Seleccionar…",
                                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                    on_click=lambda _: file_picker.pick_files(
                                        dialog_title="Seleccionar archivo Excel CMU",
                                        allowed_extensions=["xlsx", "xls"],
                                    ),
                                    style=ft.ButtonStyle(
                                        bgcolor=C_PANEL, color=C_TEXT,
                                        side=ft.BorderSide(1, C_BORDER),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=8,
                ),
                padding=16, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Container(
                content=ft.Column(
                    [ft.Row([lbl_estado], alignment=ft.MainAxisAlignment.CENTER), progress],
                    spacing=8,
                ),
                padding=12, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Row([btn_procesar, btn_narracion], spacing=12),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📊 Columnas procesadas:", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
                        ft.Text(
                            "Col 1: FECHA  •  Col 2: HORA  •  Col 7: OPERADOR  •  Col 16: TIPIFICACION\n"
                            "Col 20: BARRIO  •  Col 32: ORIGEN  •  Col 13: GAP  •  Col 14: SAE",
                            size=11, color=C_MUTED,
                        ),
                    ],
                    spacing=4,
                ),
                padding=12, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Text("📝 Registro de proceso", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
            ft.Container(
                content=log_view,
                expand=True, border_radius=10, bgcolor="#0D0D1A",
                border=ft.Border.all(1, C_BORDER),
            ),
        ],
        spacing=12,
        expand=True,
    )
