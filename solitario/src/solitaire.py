SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random
import asyncio
import flet as ft
from card import Card
from slot import Slot


class Suite:
    def __init__(self, suite_name, suite_color):
        self.name = suite_name
        self.color = suite_color


class Rank:
    def __init__(self, card_name, card_value):
        self.name = card_name
        self.value = card_value


class Solitaire(ft.Stack):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []

        # traseira atual das cartas
        self.card_back_src = "/images/card_back.png"

        # pontuação e tempo
        self.score = 0
        self.seconds = 0
        self.timer_running = False
        self.first_move_done = False

        # UI da barra superior
        self.score_text = ft.Text("Pontuação: 0", size=18, weight="bold")
        self.time_text = ft.Text("Tempo: 00:00", size=18, weight="bold")

        self.top_bar = ft.Container(
            width=SOLITAIRE_WIDTH,
            height=40,
            bgcolor="#DDDDDD",
            padding=10,
            content=ft.Row(
                [
                    self.time_text,
                    ft.Container(width=40),
                    self.score_text,
                ],
                alignment="start",
            ),
        )

        self.controls.append(self.top_bar)

    # ---------------------------------------------------------
    #  TIMER ASSÍNCRONO (compatível com Flet 0.25.1)
    # ---------------------------------------------------------
    async def timer_loop(self):
        while self.timer_running:
            await asyncio.sleep(1)
            self.seconds += 1
            mins = self.seconds // 60
            secs = self.seconds % 60
            self.time_text.value = f"Tempo: {mins:02d}:{secs:02d}"
            self.update()

    def start_timer(self):
        if not self.first_move_done:
            self.first_move_done = True
            self.timer_running = True
            self.page.run_task(self.timer_loop)

    def stop_timer(self):
        self.timer_running = False

    # ---------------------------------------------------------
    #  PONTUAÇÃO
    # ---------------------------------------------------------
    def add_score(self, value):
        self.score += value
        self.score_text.value = f"Pontuação: {self.score}"
        self.update()

    # ---------------------------------------------------------
    #  MUDAR TRASEIRA
    # ---------------------------------------------------------
    def set_card_back(self, filename):
        self.card_back_src = f"/images/{filename}"

        for card in self.cards:
            if not card.face_up:
                card.content.content.src = self.card_back_src

        self.update()

    # ---------------------------------------------------------
    #  INICIAR JOGO
    # ---------------------------------------------------------
    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

    # ---------------------------------------------------------
    #  UNDO
    # ---------------------------------------------------------
    def save_state(self):
        state = []

        for card in self.cards:
            state.append(
                {
                    "card": card,
                    "slot": card.slot,
                    "face_up": card.face_up,
                    "top": card.top,
                    "left": card.left,
                }
            )

        self.history.append(state)

    def undo(self):
        if len(self.history) < 2:
            return

        self.add_score(-5)

        self.history.pop()
        state = self.history[-1]

        new_piles = {
            self.stock: [],
            self.waste: [],
            **{slot: [] for slot in self.foundations},
            **{slot: [] for slot in self.tableau},
        }

        for entry in state:
            card = entry["card"]
            slot = entry["slot"]
            new_piles[slot].append(card)

            card.top = entry["top"]
            card.left = entry["left"]

            card.face_up = entry["face_up"]
            if card.face_up:
                card.turn_face_up()
            else:
                card.turn_face_down()

        for slot, pile in new_piles.items():
            slot.pile = pile
            for card in pile:
                card.slot = slot

        self.update()

    # ---------------------------------------------------------
    #  RESET TOTAL DO JOGO
    # ---------------------------------------------------------
    def reset_game(self):
        # reset pontuação e tempo
        self.score = 0
        self.seconds = 0
        self.first_move_done = False
        self.timer_running = False

        self.score_text.value = "Pontuação: 0"
        self.time_text.value = "Tempo: 00:00"

        for slot in [self.stock, self.waste] + self.foundations + self.tableau:
            slot.pile.clear()

        self.controls = [
            self.top_bar,
            self.stock,
            self.waste,
            *self.foundations,
            *self.tableau
        ]

        self.create_card_deck()
        self.deal_cards()

        self.history.clear()
        self.save_state()

        self.update()

    # ---------------------------------------------------------
    #  RESTO DO TEU CÓDIGO
    # ---------------------------------------------------------
    def create_card_deck(self):
        suites = [
            Suite("hearts", "RED"),
            Suite("diamonds", "RED"),
            Suite("clubs", "BLACK"),
            Suite("spades", "BLACK"),
        ]
        ranks = [
            Rank("Ace", 1),
            Rank("2", 2),
            Rank("3", 3),
            Rank("4", 4),
            Rank("5", 5),
            Rank("6", 6),
            Rank("7", 7),
            Rank("8", 8),
            Rank("9", 9),
            Rank("10", 10),
            Rank("Jack", 11),
            Rank("Queen", 12),
            Rank("King", 13),
        ]

        self.cards = []
        id_counter = 0

        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(self, suite, rank, id_counter))
                id_counter += 1

    def create_slots(self):
        self.stock = Slot(self, top=40, left=0, border=ft.border.all(1))
        self.waste = Slot(self, top=40, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(
                Slot(self, top=40, left=x, border=ft.border.all(1, "outline"))
            )
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(self, top=190, left=x, border=None))
            x += 100

        self.controls.append(self.stock)
        self.controls.append(self.waste)
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)
        self.update()

    def deal_cards(self):
        random.shuffle(self.cards)
        self.controls.extend(self.cards)

        first_slot = 0
        remaining_cards = self.cards

        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        for card in remaining_cards:
            card.place(self.stock)

        self.update()

        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        for card in self.cards:
            if not card.face_up:
                card.content.content.src = self.card_back_src

        self.update()

        self.history.clear()
        self.save_state()

    def check_foundations_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.name == top_card.suite.name
                and card.rank.value - top_card.rank.value == 1
            )
        else:
            return card.rank.name == "Ace"

    def check_tableau_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.color != top_card.suite.color
                and top_card.rank.value - card.rank.value == 1
                and top_card.face_up
            )
        else:
            return card.rank.name == "King"

    def restart_stock(self):
        self.add_score(-20)
        self.save_state()

        while len(self.waste.pile) > 0:
            card = self.waste.get_top_card()
            card.turn_face_down()
            card.move_on_top()
            card.place(self.stock)

    def check_win(self):
        cards_num = 0
        for slot in self.foundations:
            cards_num += len(slot.pile)
        return cards_num == 52

    def winning_sequence(self):
        self.stop_timer()

        mins = self.seconds // 60
        secs = self.seconds % 60

        dialog = ft.AlertDialog(
            title=ft.Text("Parabéns!"),
            content=ft.Text(
                f"Terminaste o jogo!\n\nTempo: {mins:02d}:{secs:02d}\nPontuação: {self.score}"
            ),
            open=True,
        )

        self.controls.append(dialog)
        self.update()