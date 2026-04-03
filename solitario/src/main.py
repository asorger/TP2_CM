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

    def close_dialog(e=None):
        page.dialog.open = False
        page.update()

    def save_game(e):
        solitaire.save_to_storage()
        page.dialog = ft.AlertDialog(
            title=ft.Text("Jogo Guardado"),
            content=ft.Text("O jogo foi guardado com sucesso."),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
            open=True,
        )
        page.update()

    def load_game(e):
        ok = solitaire.load_from_storage()
        if not ok:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Erro"),
                content=ft.Text("Nenhum jogo guardado encontrado."),
                actions=[ft.TextButton("OK", on_click=close_dialog)],
                open=True,
            )
        else:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Jogo Carregado"),
                content=ft.Text("O jogo foi carregado com sucesso."),
                actions=[ft.TextButton("OK", on_click=close_dialog)],
                open=True,
            )
        page.update()

    save_button = ft.ElevatedButton("Guardar Jogo", on_click=save_game)
    load_button = ft.ElevatedButton("Carregar Jogo", on_click=load_game)

    page.add(
        restart_button,
        undo_button,
        card_back_selector,
        save_button,
        load_button,
        solitaire
    )


ft.app(target=main, assets_dir="assets")