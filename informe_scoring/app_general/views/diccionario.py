"""
views/diccionario.py
====================
Vista Flet para Diccionario CIVILES.
"""

import threading
from pathlib import Path
import flet as ft
from views.home import C_PANEL, C_BORDER, C_ACCENT, C_TEXT, C_MUTED, C_GREEN, C_RED, C_YELLOW


def build_diccionario(page: ft.Page):
    rutas = {
        "dict": None, "trabajo": None, "control": None,
        "trabajo_procesado": None, "control_procesado": None,
    }
    flags = {"incluir_trabajo": True, "incluir_control": True}

    log_view = ft.ListView(expand=True, spacing=2, auto_scroll=True, padding=10)

    def log(msg: str):
        log_view.controls.append(ft.Text(msg, size=11, color="#C8D0E0", font_family="Consolas"))
        page.update()

    def make_row(label, key):
        lbl = ft.Text("Sin seleccionar", size=12, color=C_MUTED, italic=True, expand=True)
        picker = ft.FilePicker()

        def on_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            rutas[key] = e.files[0].path
            lbl.value = f"📂 {e.files[0].name}"
            lbl.color = C_TEXT
            lbl.italic = False
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
                                ft.Icons.FOLDER_OPEN_ROUNDED, icon_color=C_MUTED,
                                on_click=lambda _, p=picker: p.pick_files(
                                    dialog_title=f"Seleccionar {label}",
                                    allowed_extensions=["xlsx", "xlsm"],
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

    (row_dict, _) = make_row("Diccionario Maestro", "dict")
    (row_trabajo, _) = make_row("Archivo Fiscalización Diaria/Mensual", "trabajo")
    (row_control, _) = make_row("Control Diario Mes", "control")

    chk_trabajo = ft.Checkbox(
        label="Incluir Fiscalización Diaria/Mensual", value=True,
        active_color=C_ACCENT, label_style=ft.TextStyle(color=C_TEXT),
    )
    chk_control = ft.Checkbox(
        label="Incluir Control Diario Mes", value=True,
        active_color=C_ACCENT, label_style=ft.TextStyle(color=C_TEXT),
    )

    trabajo_container = ft.Container(row_trabajo)
    control_container = ft.Container(row_control)

    def _warn(msg: str):
        dlg = ft.AlertDialog(
            title=ft.Text("⚠ Atención", color=C_YELLOW, weight=ft.FontWeight.BOLD),
            content=ft.Text(msg, color=C_TEXT),
            actions=[ft.TextButton("OK", on_click=lambda _: page.close(dlg))],
            bgcolor=C_PANEL,
        )
        page.open(dlg)

    def on_chk_trabajo(e):
        if not chk_trabajo.value and not chk_control.value:
            chk_trabajo.value = True
            _warn("Debe incluir al menos un archivo.")
        flags["incluir_trabajo"] = chk_trabajo.value
        trabajo_container.visible = chk_trabajo.value
        page.update()

    def on_chk_control(e):
        if not chk_control.value and not chk_trabajo.value:
            chk_control.value = True
            _warn("Debe incluir al menos un archivo.")
        flags["incluir_control"] = chk_control.value
        control_container.visible = chk_control.value
        page.update()

    chk_trabajo.on_change = on_chk_trabajo
    chk_control.on_change = on_chk_control

    btn_validar = ft.ElevatedButton(
        text="✔  Validar y reconciliar",
        icon=ft.Icons.VERIFIED_ROUNDED,
        style=ft.ButtonStyle(bgcolor=C_ACCENT, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)),
    )
    btn_revertir = ft.ElevatedButton(
        text="↩  Revertir IDs → Nombres",
        icon=ft.Icons.UNDO_ROUNDED,
        disabled=True,
        style=ft.ButtonStyle(bgcolor="#4CAF82", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)),
    )

    def on_validar(_):
        from core.diccionario_logic import (
            normalizar_columnas, leer_excel,
            reconciliar_trabajo_diario, reconciliar_control_diario,
        )
        if not rutas["dict"]:
            _warn("Seleccioná el Diccionario Maestro.")
            return
        if flags["incluir_trabajo"] and not rutas["trabajo"]:
            _warn("Seleccioná el archivo de Fiscalización.")
            return
        if flags["incluir_control"] and not rutas["control"]:
            _warn("Seleccioná el Control Diario.")
            return

        btn_validar.disabled = True
        btn_revertir.disabled = True
        log("\n" + "═" * 55)
        log("  VALIDACIÓN Y RECONCILIACIÓN")
        log("═" * 55)
        page.update()

        def _run():
            try:
                ruta_dict = Path(rutas["dict"])
                hojas_d = leer_excel(ruta_dict)
                hoja_d = next(iter(hojas_d))
                df_dict = normalizar_columnas(hojas_d[hoja_d])
                log(f"✔ Diccionario: {ruta_dict.name}  [{hoja_d}]")

                df_dict_vigente = df_dict
                ruta_t_proc = ruta_c_proc = None

                if flags["incluir_trabajo"]:
                    ruta_t = Path(rutas["trabajo"])
                    hojas_t = leer_excel(ruta_t)
                    hoja_t = next(iter(hojas_t))
                    df_t = normalizar_columnas(hojas_t[hoja_t])
                    log(f"✔ Fiscalización: {ruta_t.name}  [{hoja_t}]")
                    _, df_dict_vigente, _ = reconciliar_trabajo_diario(
                        df_t, df_dict_vigente, ruta_t, ruta_dict, log
                    )
                    ruta_t_proc = ruta_t.parent / (ruta_t.stem + "_PROCESADO" + ruta_t.suffix)

                if flags["incluir_control"]:
                    ruta_c = Path(rutas["control"])
                    hojas_c = leer_excel(ruta_c)
                    hoja_c = next(iter(hojas_c))
                    df_c = normalizar_columnas(hojas_c[hoja_c])
                    log(f"✔ Control Diario: {ruta_c.name}  [{hoja_c}]")
                    reconciliar_control_diario(df_c, df_dict_vigente, ruta_c, ruta_dict, log)
                    ruta_c_proc = ruta_c.parent / (ruta_c.stem + "_PROCESADO" + ruta_c.suffix)

                rutas["trabajo_procesado"] = str(ruta_t_proc) if ruta_t_proc else None
                rutas["control_procesado"] = str(ruta_c_proc) if ruta_c_proc else None

                btn_validar.disabled = False
                btn_revertir.disabled = False
                dlg = ft.AlertDialog(
                    title=ft.Text("✅ Proceso completado", color=C_GREEN, weight=ft.FontWeight.BOLD),
                    content=ft.Text("Reconciliación completada. Podés ejecutar el proceso inverso.", color=C_TEXT),
                    actions=[ft.TextButton("OK", on_click=lambda _: page.close(dlg))],
                    bgcolor=C_PANEL,
                )
                page.open(dlg)
                page.update()

            except RuntimeError as e:
                btn_validar.disabled = False
                dlg = ft.AlertDialog(
                    title=ft.Text("⚠ Atención", color=C_YELLOW, weight=ft.FontWeight.BOLD),
                    content=ft.Container(
                        ft.Text(str(e), size=12, color=C_TEXT, selectable=True),
                        width=500, max_height=300,
                    ),
                    actions=[ft.TextButton("OK", on_click=lambda _: page.close(dlg))],
                    bgcolor=C_PANEL,
                )
                page.open(dlg)
                page.update()
            except Exception as e:
                import traceback
                log(f"✗ ERROR: {e}")
                log(traceback.format_exc())
                btn_validar.disabled = False
                page.update()

        threading.Thread(target=_run, daemon=True).start()

    def on_revertir(_):
        from core.diccionario_logic import revertir_ids_a_nombres
        if not rutas["dict"]:
            _warn("No hay referencia al Diccionario Maestro.")
            return
        btn_revertir.disabled = True
        log("\n" + "═" * 55)
        page.update()

        def _run():
            try:
                revertir_ids_a_nombres(
                    Path(rutas["dict"]),
                    Path(rutas["trabajo_procesado"]) if rutas["trabajo_procesado"] else None,
                    Path(rutas["control_procesado"]) if rutas["control_procesado"] else None,
                    log,
                )
                btn_revertir.disabled = False
                dlg = ft.AlertDialog(
                    title=ft.Text("✅ Reversión completada", color=C_GREEN, weight=ft.FontWeight.BOLD),
                    content=ft.Text("Los archivos _REVERTIDO.xlsx fueron generados.", color=C_TEXT),
                    actions=[ft.TextButton("OK", on_click=lambda _: page.close(dlg))],
                    bgcolor=C_PANEL,
                )
                page.open(dlg)
                page.update()
            except Exception as e:
                log(f"✗ ERROR: {e}")
                btn_revertir.disabled = False
                page.update()

        threading.Thread(target=_run, daemon=True).start()

    btn_validar.on_click = on_validar
    btn_revertir.on_click = on_revertir

    return ft.Column(
        [
            ft.Column(
                [
                    ft.Row([ft.Icon(ft.Icons.BOOK_ROUNDED, color=C_RED, size=28),
                            ft.Text("Diccionario CIVILES", size=22, weight=ft.FontWeight.BOLD, color=C_TEXT)], spacing=10),
                    ft.Text("Reconcilia nombres con el Diccionario Maestro y convierte a LP/DNI", size=13, color=C_MUTED),
                    ft.Divider(color=C_BORDER, height=20),
                ],
                spacing=4,
            ),
            row_dict,
            chk_trabajo,
            trabajo_container,
            chk_control,
            control_container,
            ft.Row([btn_validar, btn_revertir], spacing=12),
            ft.Text("📝 Registro", size=12, color=C_MUTED, weight=ft.FontWeight.W_600),
            ft.Container(
                content=log_view, expand=True, border_radius=10, bgcolor="#0D0D1A",
                border=ft.Border.all(1, C_BORDER),
            ),
        ],
        spacing=12,
        expand=True,
    )
