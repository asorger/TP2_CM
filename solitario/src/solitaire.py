SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500
 
import random
import asyncio
import json
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
 
 
        self.card_back_src = "/images/card_back.png"
 
        self.score = 0
        self.seconds = 0
        self.timer_running = False
        self.first_move_done = False
        self.timer_task = None
 
        self.score_text = ft.Text("Pontuação: 0", size=18, weight="bold")
        self.time_text = ft.Text("Tempo: 00:00", size=18, weight="bold")
 
        self.top_bar = ft.Container(
            width=SOLITAIRE_WIDTH,
            height=40,
            padding=10,
            bgcolor=ft.colors.with_opacity(0.15, ft.colors.BLACK),
            border_radius=8,
            content=ft.Row(
                [
                    self.time_text,
                    ft.Container(expand=True),
                    self.score_text,
                ],
                alignment="start",
            )
        )
 
        # tornar o texto mais visível no fundo verde
        self.time_text.color = ft.colors.WHITE
        self.score_text.color = ft.colors.WHITE
 
 
        self.controls.append(self.top_bar)
 
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
 
            # cancelar timer antigo se existir
            if self.timer_task is not None:
                self.timer_task.cancel()
 
            # criar novo timer
            self.timer_task = self.page.run_task(self.timer_loop)
 
 
    def stop_timer(self):
        self.timer_running = False
        if self.timer_task is not None:
            self.timer_task.cancel()
            self.timer_task = None
 
 
    def add_score(self, value):
        self.score += value
        self.score_text.value = f"Pontuação: {self.score}"
        self.update()
 
    def set_card_back(self, filename):
        self.card_back_src = f"/images/{filename}"
 
        for card in self.cards:
            if not card.face_up:
                card.content.content.src = self.card_back_src
 
        self.update()
 
    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()
 
    # ---------------------------------------------------------
    #  EXPORTAR ESTADO DO JOGO (com proteção)
    # ---------------------------------------------------------
    def export_state(self):
        for card in self.cards:
            if card.slot is None:
                return None
 
        state = {
            "score": self.score,
            "seconds": self.seconds,
            "card_back_src": self.card_back_src,
            "cards": []
        }
 
        for card in self.cards:
            state["cards"].append({
                "id": card.id,
                "slot_id": card.slot.slot_id,
                "pile_index": card.slot.pile.index(card),
                "face_up": card.face_up,
                "top": card.top,
                "left": card.left,
                "z": self.controls.index(card)
            })
 
        return state
 
    # ---------------------------------------------------------
    #  SAVE / LOAD via SharedPreferences
    # ---------------------------------------------------------
    def save_to_storage(self, key="solitaire_state"):
        if not hasattr(self, "page") or self.page is None:
            return
 
        state = self.export_state()
        if state is None:
            return
 
        self.page.client_storage.set(key, json.dumps(state))
 
    def load_from_storage(self, key="solitaire_state"):
        if not hasattr(self, "page") or self.page is None:
            return False
 
        data = self.page.client_storage.get(key)
        if not data:
            return False
 
        state = json.loads(data)
 
        # -------------------------------------------------
        # LIMPAR TUDO ANTES DE CARREGAR O NOVO ESTADO
        # -------------------------------------------------
 
        # remover cartas antigas
        if hasattr(self, "cards"):
            for card in self.cards:
                if card in self.controls:
                    self.controls.remove(card)
 
        # remover slots antigos
        for group in ["tableau", "foundations"]:
            if hasattr(self, group):
                for slot in getattr(self, group):
                    if slot in self.controls:
                        self.controls.remove(slot)
 
        if hasattr(self, "stock") and self.stock in self.controls:
            self.controls.remove(self.stock)
 
        if hasattr(self, "waste") and self.waste in self.controls:
            self.controls.remove(self.waste)
 
        # limpar pilhas antigas
        if hasattr(self, "tableau"):
            for slot in self.tableau:
                slot.pile.clear()
 
        if hasattr(self, "foundations"):
            for slot in self.foundations:
                slot.pile.clear()
 
        if hasattr(self, "stock"):
            self.stock.pile.clear()
 
        if hasattr(self, "waste"):
            self.waste.pile.clear()
 
        # -------------------------------------------------
        # RECRIAR E CARREGAR
        # -------------------------------------------------
        self.create_card_deck()
        self.create_slots()
        self.import_state(state)
 
        return True
 
    # ---------------------------------------------------------
    #  IMPORTAR ESTADO DO JOGO (ordem lógica corrigida)
    # ---------------------------------------------------------
    def import_state(self, state):
        for slot in [self.stock, self.waste] + self.foundations + self.tableau:
            slot.pile.clear()
 
        self.score = state["score"]
        self.seconds = state["seconds"]
        self.card_back_src = state.get("card_back_src", self.card_back_src)
 
        self.score_text.value = f"Pontuação: {self.score}"
        mins = self.seconds // 60
        secs = self.seconds % 60
        self.time_text.value = f"Tempo: {mins:02d}:{secs:02d}"
 
        temp = {}
 
        for entry in state["cards"]:
            card = self.cards[entry["id"]]
 
            slot = next(s for s in [self.stock, self.waste] + self.foundations + self.tableau
                        if s.slot_id == entry["slot_id"])
 
            if slot not in temp:
                temp[slot] = {}
 
            temp[slot][entry["pile_index"]] = card
 
            card.top = entry["top"]
            card.left = entry["left"]
            card.set_face_up_silent(entry["face_up"])
 
        for slot, mapping in temp.items():
            slot.pile = [mapping[i] for i in sorted(mapping.keys())]
            for c in slot.pile:
                c.slot = slot
 
        for card in self.cards:
            if card in self.controls:
                self.controls.remove(card)
 
        ordered = sorted(state["cards"], key=lambda x: x["z"])
        for entry in ordered:
            self.controls.append(self.cards[entry["id"]])
 
        for card in self.cards:
            if not card.face_up:
                card.content.content.src = self.card_back_src
 
        self.update()
 
    # ---------------------------------------------------------
    #  RESTO DO TEU CÓDIGO (SEM ALTERAÇÕES)
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
                    "z": self.controls.index(card),
                }
            )
 
        self.history.append(state)
 
    def undo(self):
        if len(self.history) < 2:
            return
 
        self.add_score(-5)
 
        self.history.pop()
        state = self.history[-1]
 
        temp_piles = {
            self.stock: [],
            self.waste: [],
            **{slot: [] for slot in self.foundations},
            **{slot: [] for slot in self.tableau},
        }
 
        for entry in state:
            card = entry["card"]
            slot = entry["slot"]
 
            temp_piles[slot].append((card, entry["top"]))
 
            card.top = entry["top"]
            card.left = entry["left"]
 
            card.set_face_up_silent(entry["face_up"])
 
        for slot, items in temp_piles.items():
            items_sorted = sorted(items, key=lambda x: x[1])
            pile = [c for c, _ in items_sorted]
            slot.pile = pile
            for card in pile:
                card.slot = slot
 
        for card in self.cards:
            if card in self.controls:
                self.controls.remove(card)
 
        ordered_cards = sorted(state, key=lambda x: x["z"])
        for entry in ordered_cards:
            self.controls.append(entry["card"])
 
        self.update()
 
    def reset_game(self):
        self.score = 0
        self.seconds = 0
        self.first_move_done = False
 
        # parar o timer antigo
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
 
        # iniciar um novo timer (linha nova)
        self.timer_running = True
        self.start_timer()   # linha nova
 
 
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
 
        remaining_cards = self.cards.copy()
 
        first_slot = 0
 
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