import flet as ft

CARD_WIDTH = 70
CARD_HEIGHT = 100
DROP_PROXIMITY = 30
CARD_OFFSET = 20


class Card(ft.GestureDetector):
    def __init__(self, solitaire, suite, rank, id):
        super().__init__()
        self.id = id
        self.mouse_cursor = ft.MouseCursor.MOVE
        self.drag_interval = 5
        self.on_pan_start = self.start_drag
        self.on_pan_update = self.drag
        self.on_pan_end = self.drop
        self.on_tap = self.click
        self.on_double_tap = self.doubleclick
        self.suite = suite
        self.rank = rank
        self.face_up = False
        self.top = None
        self.left = None
        self.solitaire = solitaire
        self.slot = None
        self.content = ft.Container(
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            border_radius=ft.border_radius.all(6),
            content=ft.Image(src=self.solitaire.card_back_src),
        )
        self.draggable_pile = [self]

    # -----------------------------
    # MÉTODOS DE VIRAR CARTA
    # -----------------------------
    def turn_face_up(self):
        self.face_up = True
        self.content.content.src = f"/images/{self.rank.name}_{self.suite.name}.svg"
        self.solitaire.add_score(5)
        self.solitaire.update()

    def turn_face_down(self):
        self.face_up = False
        self.content.content.src = self.solitaire.card_back_src
        self.solitaire.update()

    # usado por UNDO / LOAD: sem pontuação, sem update extra
    def set_face_up_silent(self, value: bool):
        self.face_up = value
        if self.face_up:
            self.content.content.src = f"/images/{self.rank.name}_{self.suite.name}.svg"
        else:
            self.content.content.src = self.solitaire.card_back_src

    # -----------------------------
    # RESTO DO TEU CÓDIGO
    # -----------------------------
    def move_on_top(self):
        for card in self.draggable_pile:
            if card in self.solitaire.controls:
                self.solitaire.controls.remove(card)
            self.solitaire.controls.append(card)
        self.solitaire.update()

    def bounce_back(self):
        for card in self.draggable_pile:
            if card.slot in self.solitaire.tableau:
                if card in card.slot.pile:
                    card.top = card.slot.top + card.slot.pile.index(card) * CARD_OFFSET
                else:
                    card.top = card.slot.top
            else:
                card.top = card.slot.top
            card.left = card.slot.left
        self.solitaire.update()

    def place(self, slot):
        self.solitaire.save_state()
        self.solitaire.start_timer()

        for card in self.draggable_pile:
            if slot in self.solitaire.tableau:
                card.top = slot.top + len(slot.pile) * CARD_OFFSET
                self.solitaire.add_score(3)
            else:
                card.top = slot.top

            card.left = slot.left

            if card.slot is not None and card in card.slot.pile:
                card.slot.pile.remove(card)

            card.slot = slot
            slot.pile.append(card)

        if slot in self.solitaire.foundations:
            self.solitaire.add_score(10)

        if self.solitaire.check_win():
            self.solitaire.winning_sequence()

        self.solitaire.update()

    def get_draggable_pile(self):
        if (
            self.slot is not None
            and self.slot != self.solitaire.stock
            and self.slot != self.solitaire.waste
            and self in self.slot.pile
        ):
            idx = self.slot.pile.index(self)
            self.draggable_pile = self.slot.pile[idx:]
        else:
            self.draggable_pile = [self]

    def start_drag(self, e: ft.DragStartEvent):
        if self.face_up:
            self.get_draggable_pile()
            self.move_on_top()

    def drag(self, e: ft.DragUpdateEvent):
        if self.face_up:
            for card in self.draggable_pile:
                offset = self.draggable_pile.index(card) * CARD_OFFSET
                card.top = max(0, self.top + e.delta_y) + offset
                card.left = max(0, self.left + e.delta_x)
            self.solitaire.update()

    def drop(self, e: ft.DragEndEvent):
        if self.face_up:
            for slot in self.solitaire.tableau:
                pile_len = len(slot.pile)
                if (
                    abs(self.top - (slot.top + pile_len * CARD_OFFSET)) < DROP_PROXIMITY
                    and abs(self.left - slot.left) < DROP_PROXIMITY
                    and self.solitaire.check_tableau_rules(self, slot)
                ):
                    self.place(slot)
                    return

            if len(self.draggable_pile) == 1:
                for slot in self.solitaire.foundations:
                    if (
                        abs(self.top - slot.top) < DROP_PROXIMITY
                        and abs(self.left - slot.left) < DROP_PROXIMITY
                        and self.solitaire.check_foundations_rules(self, slot)
                    ):
                        self.place(slot)
                        return

            self.bounce_back()

    def click(self, e):
        self.get_draggable_pile()

        if self.slot in self.solitaire.tableau:
            if not self.face_up and len(self.draggable_pile) == 1:
                self.solitaire.save_state()
                self.solitaire.start_timer()
                self.turn_face_up()

        elif self.slot == self.solitaire.stock:
            self.solitaire.save_state()
            self.solitaire.start_timer()
            self.move_on_top()
            self.place(self.solitaire.waste)
            self.turn_face_up()

    def doubleclick(self, e):
        self.get_draggable_pile()
        if self.face_up and len(self.draggable_pile) == 1:
            self.solitaire.save_state()
            self.solitaire.start_timer()
            self.move_on_top()
            for slot in self.solitaire.foundations:
                if self.solitaire.check_foundations_rules(self, slot):
                    self.place(slot)
                    return