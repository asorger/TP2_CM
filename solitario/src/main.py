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

    def show_leaderboard():
        scores = solitaire.get_leaderboard()

        if not scores:
            content = ft.Text("Ainda não há pontuações guardadas.")
        else:
            content = ft.Column(
                [
                    ft.Text(
                        f"{i+1}º lugar: {entry['score']} pontos — {entry['time']//60:02d}:{entry['time']%60:02d}"
                    )
                    for i, entry in enumerate(scores)
                ],
                spacing=5
            )

        page.dialog = ft.AlertDialog(
            title=ft.Text("Top 3 Pontuações"),
            content=content,
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog())],
            open=True
        )
        page.update()


    # -----------------------------
    # ESTILO DOS BOTÕES (alteração pedida)
    # -----------------------------
    button_style = ft.ButtonStyle(
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
        shape=ft.RoundedRectangleBorder(radius=8)
    )

    restart_button = ft.ElevatedButton(
        "Reiniciar",
        icon=ft.Icons.RESTART_ALT,
        on_click=lambda e: solitaire.reset_game()
    )

    undo_button = ft.ElevatedButton(
        "Undo",
        icon=ft.Icons.UNDO,
        on_click=lambda e: solitaire.undo()
    )

    save_button = ft.ElevatedButton(
        "Guardar Jogo",
        icon=ft.Icons.SAVE,
        on_click=save_game
    )

    load_button = ft.ElevatedButton(
        "Carregar Jogo",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=load_game
    )

    leaderboard_button = ft.ElevatedButton(
        "Pontuações",
        icon=ft.Icons.LEADERBOARD,
        on_click=lambda e: show_leaderboard()
    )
    restart_button.style = button_style
    undo_button.style = button_style
    save_button.style = button_style
    load_button.style = button_style
    leaderboard_button.style = button_style


    card_back_selector = ft.Dropdown(
        label="Traseira das cartas",
        options=[
            ft.dropdown.Option("card_back.png"),
            ft.dropdown.Option("card_back2.png"),
            ft.dropdown.Option("card_back3.png"),
            ft.dropdown.Option("card_back4.png"),
        ],
        value="card_back.png",
        on_change=lambda e: solitaire.set_card_back(e.control.value),
        width=180,
    )

    controls_bar = ft.Container(
        padding=10,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.20, ft.Colors.BLACK),
        content=ft.Row(
            [
                restart_button,
                undo_button,
                save_button,
                load_button,
                leaderboard_button,
                card_back_selector,
            ],
            spacing=10,
            alignment="start"
        )
    )

    # -----------------------------
    # FUNDO DA PÁGINA INTEIRA
    # -----------------------------
    page.add(
        ft.Container(
            expand=True,
            image_src="/images/table_green.png",
            image_fit=ft.ImageFit.COVER,
            content=ft.Column(
                [
                    controls_bar,
                    ft.Container(
                        content=solitaire,
                        padding=ft.padding.only(top=10) 
                    )
                ]
            )

        )
    )


ft.app(target=main, assets_dir="assets")