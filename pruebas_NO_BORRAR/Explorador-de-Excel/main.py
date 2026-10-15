import flet as ft

from views.excel_reader import create_excel_reader


async def main(page: ft.Page):
    page.title = "Explorador de Excel"
    page.add(create_excel_reader(page))


ft.run(main)
