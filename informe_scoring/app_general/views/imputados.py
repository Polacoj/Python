"""
views/imputados.py
==================
Vista Flet para Productividad Imputados.
"""

import threading
import flet as ft
from views.home import C_PANEL, C_BORDER, C_ACCENT, C_TEXT, C_MUTED, C_GREEN, C_RED, C_YELLOW


def build_imputados(page: ft.Page):
    archivo = {"path": None}
    lbl_archivo = ft.Text("📂 Ningún archivo seleccionado", size=13, color=C_MUTED, italic=True)
    lbl_estado = ft.Text("🟢 Listo para procesar", size=13, color=C_GREEN)
    progress = ft.ProgressBar(value=0, color="#4CAF82", bgcolor=C_BORDER, height=6, border_radius=3)
    log_view = ft.ListView(expand=True, spacing=2, auto_scroll=True, padding=10)

    btn_procesar = ft.ElevatedButton(
        text="▶  Procesar archivo",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor="#4CAF82",
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def log(msg: str):
        log_view.controls.append(ft.Text(msg, size=11, color="#C8D0E0", font_family="Consolas"))
        page.update()

    def on_file_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        archivo["path"] = e.files[0].path
        lbl_archivo.value = f"📂 {e.files[0].name}"
        lbl_archivo.color = C_TEXT
        lbl_archivo.italic = False
        btn_procesar.disabled = False
        lbl_estado.value = "📁 Archivo seleccionado"
        lbl_estado.color = C_YELLOW
        log(f"\n{'='*60}")
        log(f"📂 Archivo: {e.files[0].name}")
        page.update()

    def on_procesar(_):
        from core.imputados_logic import process_file
        btn_procesar.disabled = True
        lbl_estado.value = "🔄 Procesando..."
        lbl_estado.color = C_YELLOW
        progress.value = None
        page.update()

        def _run():
            ok, msg = process_file(archivo["path"], log)

            def _update():
                progress.value = 1 if ok else 0
                lbl_estado.value = "✅ Completado" if ok else "✗ Error"
                lbl_estado.color = C_GREEN if ok else C_RED
                btn_procesar.disabled = False
                dlg = ft.AlertDialog(
                    title=ft.Text("✅ Completado" if ok else "✗ Error",
                                  color=C_GREEN if ok else C_RED, weight=ft.FontWeight.BOLD),
                    content=ft.Container(ft.Text(msg, size=12, color=C_TEXT, selectable=True), width=500, max_height=300),
                    actions=[ft.TextButton("Cerrar", on_click=lambda _: page.close(dlg))],
                    bgcolor=C_PANEL,
                )
                page.open(dlg)
                page.update()

            _update()

        threading.Thread(target=_run, daemon=True).start()

    file_picker.on_result = on_file_picked
    btn_procesar.on_click = on_procesar

    return ft.Column(
        [
            ft.Column(
                [
                    ft.Row([ft.Icon(ft.Icons.PERSON_SEARCH_ROUNDED, color="#4CAF82", size=28),
                            ft.Text("Productividad Imputados", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT)], spacing=10),
                    ft.Text("Genera productividad_imputados.xlsx y productividad_imputados_sisep.xlsx en DATOS/",
                            size=13, color=C_MUTED),
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
                                        dialog_title="Seleccionar archivo Excel",
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
                content=ft.Column([ft.Row([lbl_estado], alignment=ft.MainAxisAlignment.CENTER), progress], spacing=8),
                padding=12, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            btn_procesar,
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📊 Archivos generados:", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
                        ft.Text(
                            "• DATOS/productividad_imputados.xlsx  —  eventos por OPERADOR\n"
                            "• DATOS/productividad_imputados_sisep.xlsx  —  eventos SISEP/ANILLO",
                            size=11, color=C_MUTED,
                        ),
                    ],
                    spacing=4,
                ),
                padding=12, border_radius=10, bgcolor=C_PANEL,
                border=ft.Border.all(1, C_BORDER),
            ),
            ft.Text("📝 Registro", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
            ft.Container(
                content=log_view, expand=True, border_radius=10, bgcolor="#0D0D1A",
                border=ft.Border.all(1, C_BORDER),
            ),
        ],
        spacing=12,
        expand=True,
    )
