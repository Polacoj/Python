import flet as ft


def main(page: ft.Page):
    page.title = "Contador ---Titulo de la ventana (PAGE)---"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    texto = ft.TextField(value='0', text_align='center', width=200)

    def menos_click(e):
        texto.value = int(texto.value) - 1
        page.update()

    def mas_click(e):
        texto.value = str(int(texto.value) + 1)
        page.update()

    page.add(ft.Row([ft.IconButton(ft.Icons.REMOVE_CIRCLE, on_click=menos_click), texto, ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=mas_click)], alignment=ft.MainAxisAlignment.CENTER
        )
    )


ft.app(target=main)
