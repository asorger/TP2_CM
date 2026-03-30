import flet as ft
from solitaire import Solitaire


def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)

    solitaire = Solitaire()

    restart_button = ft.ElevatedButton(
        "Reiniciar",
        on_click=lambda e: solitaire.reset_game()
    )

    undo_button = ft.ElevatedButton(
        "Undo",
        on_click=lambda e: solitaire.undo()
    )

    page.add(restart_button, undo_button, solitaire)


ft.app(target=main, assets_dir="assets")