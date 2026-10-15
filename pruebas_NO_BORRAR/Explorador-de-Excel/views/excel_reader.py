import flet as ft

from models import WorkbookInfo, read_workbook_info


def create_excel_reader(page: ft.Page):
    results = ft.Column()
    status = ft.Text("Elige un archivo XLSX para consultar sus hojas y encabezados.")

    def show_workbook(workbook: WorkbookInfo) -> None:
        results.controls = [
            ft.Text(f"Archivo: {workbook.file_name}"),
            ft.Text(f"Cantidad de hojas: {len(workbook.sheets)}"),
        ]
        for sheet in workbook.sheets:
            headers = ", ".join(sheet.headers) if sheet.headers else "No se encontraron encabezados."
            results.controls.append(
                ft.Column(
                    controls=[
                        ft.Text(f"Hoja: {sheet.name}"),
                        ft.Text(f"Encabezados: {headers}"),
                    ]
                )
            )

    async def choose_file(_event) -> None:
        files = await picker.pick_files(
            dialog_title="Selecciona un archivo Excel",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
            allow_multiple=False,
        )
        if not files:
            status.value = "No se seleccionó ningún archivo."
            results.controls = []
            page.update()
            return

        selected_file = files[0]
        if not selected_file.path:
            status.value = "No fue posible acceder a la ruta del archivo seleccionado."
            results.controls = []
            page.update()
            return

        try:
            workbook = read_workbook_info(selected_file.path)
        except Exception as error:
            status.value = f"No se pudo leer el archivo: {error}"
            results.controls = []
        else:
            status.value = "Archivo leído correctamente."
            show_workbook(workbook)
        page.update()

    picker = ft.FilePicker()
    page.services.append(picker)

    return ft.Column(
        controls=[
            ft.Text("Explorador de Excel"),
            ft.Button(
                content="Seleccionar archivo XLSX",
                icon=ft.Icons.BACKUP_TABLE,
                on_click=choose_file,
            ),
            status,
            results,
        ]
    )
