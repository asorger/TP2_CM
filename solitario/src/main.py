import flet as ft
import json
from solitaire import Solitaire


def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)

    # Favicon simples
    page.favicon = "/favicon.png"

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
        if page.overlay:
            dlg = page.overlay[-1]
            dlg.open = False
            page.update()

    def save_game(e):
        def confirm_save(ev):
            name = name_field.value.strip()
            if name == "":
                return

            saves = page.client_storage.get("solitaire_saves") or []
            saves = json.loads(saves) if isinstance(saves, str) else saves

            state = solitaire.export_state()
            saves.append({"name": name, "data": state})

            page.client_storage.set("solitaire_saves", json.dumps(saves))

            dialog.open = False
            page.update()

        name_field = ft.TextField(label="Nome do save", width=250)

        dialog = ft.AlertDialog(
            title=ft.Text("Guardar Jogo"),
            content=name_field,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog()),
                ft.TextButton("Guardar", on_click=confirm_save),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()


    def load_game(e):
        saves = page.client_storage.get("solitaire_saves") or []
        saves = json.loads(saves) if isinstance(saves, str) else saves

        if not saves:
            dialog = ft.AlertDialog(
                title=ft.Text("Carregar Jogo"),
                content=ft.Text("Não existem saves."),
                actions=[ft.TextButton("OK", on_click=close_dialog)],
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            return

        save_rows = []

        for idx, save in enumerate(saves):
            def load_closure(s=save):
                def _load(ev):
                    solitaire.import_state(s["data"])
                    close_dialog()
                return _load

            def delete_closure(i=idx):
                def _delete(ev):
                    saves.pop(i)
                    page.client_storage.set("solitaire_saves", json.dumps(saves))
                    close_dialog()
                return _delete

            save_rows.append(
                ft.Row(
                    [
                        ft.Text(save["name"], expand=True),
                        ft.TextButton("Carregar", on_click=load_closure()),
                        ft.TextButton("Apagar", on_click=delete_closure()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Carregar Jogo"),
            content=ft.Column(save_rows, scroll=ft.ScrollMode.AUTO, height=300),
            actions=[ft.TextButton("Fechar", on_click=close_dialog)],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()


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

        dialog = ft.AlertDialog(
            title=ft.Text("Top 3 Pontuações"),
            content=content,
            actions=[ft.TextButton("OK", on_click=close_dialog)],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # -----------------------------
    # ESTILO DOS BOTÕES
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

    # Criar o painel lateral de desafios
    solitaire.challenge_panel = solitaire.get_challenge_panel()

    # -----------------------------
    # LAYOUT FINAL COM BARRA LATERAL DE DESAFIOS
    # -----------------------------
    page.add(
        ft.Container(
            expand=True,
            image_src="/images/table_green.png",
            image_fit=ft.ImageFit.COVER,
            content=ft.Column(
                [
                    controls_bar,
                    ft.Row(
                        [
                            ft.Container(
                                content=solitaire,
                                expand=True,
                                padding=ft.padding.only(top=10)
                            ),
                            solitaire.challenge_panel
                        ],
                        expand=True
                    )
                ]
            )
        )
    )


ft.app(target=main, assets_dir="assets")