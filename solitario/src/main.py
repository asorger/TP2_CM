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

    card_back_selector = ft.Dropdown(
        label="Traseira das cartas",
        options=[
            ft.dropdown.Option("card_back.png"),
            ft.dropdown.Option("card_back2.png"),
            ft.dropdown.Option("card_back3.png"),
            ft.dropdown.Option("card_back4.png"),
        ],
        value="card_back.png",
        on_change=lambda e: solitaire.set_card_back(e.control.value)
    )

    page.add(restart_button, undo_button, card_back_selector, solitaire)


ft.app(target=main, assets_dir="assets")