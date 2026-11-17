"""Tkinter graphical interface for the Tamagotchi Simulator."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from .config import SAVE_FILE
from .exceptions import DeadPetError, NoPetSelectedError, SaveFileError
from .game import Game
from .stats import calculate_statistics
from .storage import load_game, save_game

DISPLAY_STATS = ("health", "hunger", "boredom", "exhaustion")

STAT_LABELS = {
    "health": "Health",
    "hunger": "Hunger",
    "boredom": "Boredom",
    "exhaustion": "Exhaustion",
}

ALIVE_COLOR = "#1b5e20"
WARNING_COLOR = "#b26a00"
DEAD_COLOR = "#b00020"
TEXT_COLOR = "#222222"
MUTED_COLOR = "#666666"

WARNING_WORDS = (
    "died",
    "starving",
    "exhausted",
    "bored out",
    "sick",
    "nightmare",
    "did not survive",
)

HELP_TEXT = """Each action uses one turn. After every action, every living pet gets hungrier, more bored and more tired.

Feed: hunger -30, health +2
Play: hunger +15, boredom -35, exhaustion +20
Sleep: hunger +5, boredom +10, exhaustion -40
Heal: health +30

Health risks each turn:
- hunger 80 or more: -10 health
- exhaustion 80 or more: -8 health
- boredom 90 or more: -5 health
- all needs below 40: +2 health

At 0 health a pet dies and cannot act again. Random events happen after 30% of actions."""


class TamagotchiApp:
    """The main application window."""

    def __init__(self, root):
        self.root = root
        self.game = Game()
        self.game.select_pet("1")

        self.root.title("Tamagotchi Simulator")
        self.root.geometry("1040x760")
        self.root.minsize(900, 700)

        self.pet_cards = {}
        self.stat_value_labels = {}
        self.action_buttons = {}
        self.turn_label = None
        self.summary_label = None
        self.current_label = None
        self.pets_frame = None
        self.log = None

        self._configure_styles()
        self._build_menu()
        self._build_layout()
        self._rebuild_pet_cards()
        self._refresh_all()
        self._log_welcome()

        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def _configure_styles(self):
        base = tkfont.nametofont("TkDefaultFont")
        fixed = tkfont.nametofont("TkFixedFont")

        title_font = base.copy()
        title_font.configure(size=22, weight="bold")

        section_font = base.copy()
        section_font.configure(size=11, weight="bold")

        turn_font = base.copy()
        turn_font.configure(size=13, weight="bold")

        status_font = base.copy()
        status_font.configure(size=10, weight="bold")

        current_font = base.copy()
        current_font.configure(size=11, weight="bold")

        button_font = base.copy()
        button_font.configure(size=11, weight="bold")

        stat_font = fixed.copy()
        stat_font.configure(size=10, weight="bold")

        self.log_turn_font = base.copy()
        self.log_turn_font.configure(size=10, weight="bold")

        # Keep references to the font objects so Tk does not delete them.
        self._fonts = (
            title_font,
            section_font,
            turn_font,
            status_font,
            current_font,
            button_font,
            stat_font,
            self.log_turn_font,
        )

        style = ttk.Style(self.root)
        style.configure("Title.TLabel", font=title_font)
        style.configure("Subtitle.TLabel", foreground=MUTED_COLOR)
        style.configure("Turn.TLabel", font=turn_font)
        style.configure("Status.TLabel", font=status_font)
        style.configure("Current.TLabel", font=current_font)
        style.configure("StatValue.TLabel", font=stat_font)
        style.configure("Action.TButton", font=button_font, padding=(10, 8))
        style.configure("TLabelframe.Label", font=section_font)

    def _build_menu(self):
        menu_bar = tk.Menu(self.root)

        game_menu = tk.Menu(menu_bar, tearoff=False)
        game_menu.add_command(label="New Game", command=self._new_game)
        game_menu.add_command(label="Save Game", command=self._save_game)
        game_menu.add_command(label="Load Game", command=self._load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self._quit)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="How to Play", command=self._show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _build_layout(self):
        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(3, weight=1)

        self._build_header(main)
        self._build_pet_area(main)
        self._build_actions(main)
        self._build_bottom(main)

    def _build_header(self, parent):
        header = ttk.Frame(parent)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        title_block = ttk.Frame(header)
        title_block.grid(row=0, column=0, sticky="w")
        ttk.Label(
            title_block,
            text="Tamagotchi Simulator",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_block,
            text="Keep three small creatures alive. Health 0 means death.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        info = ttk.Frame(header)
        info.grid(row=0, column=1, sticky="e")

        self.turn_label = ttk.Label(info, text="Turn 0", style="Turn.TLabel")
        self.turn_label.pack(anchor="e")

        self.summary_label = ttk.Label(info, text="3 alive / 0 dead", style="Status.TLabel")
        self.summary_label.pack(anchor="e", pady=(1, 6))

        buttons = ttk.Frame(info)
        buttons.pack(anchor="e")
        ttk.Button(buttons, text="New Game", command=self._new_game).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(buttons, text="Save", command=self._save_game).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(buttons, text="Load", command=self._load_game).pack(side="left")

    def _build_pet_area(self, parent):
        self.pets_frame = ttk.Frame(parent)
        self.pets_frame.grid(row=1, column=0, sticky="ew")

    def _build_actions(self, parent):
        frame = ttk.LabelFrame(parent, text="Actions", padding=12)
        frame.grid(row=2, column=0, sticky="ew", pady=(12, 12))

        for column in range(4):
            frame.columnconfigure(column, weight=1)

        self.current_label = ttk.Label(
            frame,
            text="Current pet: none",
            style="Current.TLabel",
        )
        self.current_label.grid(row=0, column=0, columnspan=4, sticky="w")

        action_buttons = (
            ("feed", "Feed"),
            ("play", "Play"),
            ("sleep", "Sleep"),
            ("heal", "Heal"),
        )

        for index, (action, label) in enumerate(action_buttons):
            button = ttk.Button(
                frame,
                text=label,
                style="Action.TButton",
                command=lambda action=action: self._perform_action(action),
            )
            button.grid(
                row=1,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 8, 0),
                pady=(10, 0),
            )
            self.action_buttons[action] = button

    def _build_bottom(self, parent):
        bottom = ttk.Frame(parent)
        bottom.grid(row=3, column=0, sticky="nsew")
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)

        stats_frame = ttk.LabelFrame(bottom, text="Statistics", padding=12)
        stats_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        rows = (
            ("Living pets", "living"),
            ("Dead pets", "dead"),
            ("Average health", "average_health"),
            ("Average hunger", "average_hunger"),
            ("Average boredom", "average_boredom"),
            ("Average exhaustion", "average_exhaustion"),
        )

        for row, (label, key) in enumerate(rows):
            ttk.Label(stats_frame, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 18), pady=2
            )
            value_label = ttk.Label(
                stats_frame,
                text="0",
                style="StatValue.TLabel",
                width=7,
                anchor="e",
            )
            value_label.grid(row=row, column=1, sticky="e", pady=2)
            self.stat_value_labels[key] = value_label

        ttk.Label(
            stats_frame,
            text="Averages include living pets only.",
            style="Subtitle.TLabel",
        ).grid(row=len(rows), column=0, columnspan=2, sticky="w", pady=(8, 0))

        log_frame = ttk.LabelFrame(bottom, text="Activity log", padding=8)
        log_frame.grid(row=0, column=1, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_frame,
            height=10,
            wrap="word",
            state="disabled",
            padx=8,
            pady=8,
        )
        self.log.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        self.log.tag_configure("turn", font=self.log_turn_font, spacing1=6)
        self.log.tag_configure("warning", foreground=DEAD_COLOR)
        self.log.tag_configure("success", foreground=ALIVE_COLOR)

    def _rebuild_pet_cards(self):
        for child in self.pets_frame.winfo_children():
            child.destroy()
        self.pet_cards.clear()

        for index, pet in enumerate(self.game.pet_list()):
            self.pets_frame.columnconfigure(index, weight=1, uniform="pet")

            card = ttk.LabelFrame(
                self.pets_frame,
                text=pet.name,
                padding=12,
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 8, 0),
            )
            card.columnconfigure(0, weight=1)

            top = ttk.Frame(card)
            top.grid(row=0, column=0, sticky="ew")
            ttk.Label(top, text="Status", style="Subtitle.TLabel").pack(side="left")
            status_label = ttk.Label(
                top,
                text="ALIVE",
                style="Status.TLabel",
                foreground=ALIVE_COLOR,
            )
            status_label.pack(side="right")

            values = {}
            bars = {}

            for offset, stat_name in enumerate(DISPLAY_STATS):
                row_frame = ttk.Frame(card)
                row_frame.grid(row=1 + offset * 2, column=0, sticky="ew", pady=(8, 0))
                row_frame.columnconfigure(1, weight=1)

                ttk.Label(
                    row_frame,
                    text=STAT_LABELS[stat_name],
                    width=10,
                    anchor="w",
                ).grid(row=0, column=0, sticky="w")

                value_label = ttk.Label(
                    row_frame,
                    text="0/100",
                    style="StatValue.TLabel",
                    width=7,
                    anchor="e",
                )
                value_label.grid(row=0, column=1, sticky="e")

                bar = ttk.Progressbar(
                    row_frame,
                    maximum=100,
                    mode="determinate",
                )
                bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(3, 0))

                values[stat_name] = value_label
                bars[stat_name] = bar

            select_button = ttk.Button(
                card,
                text="Select",
                command=lambda name=pet.name: self._select_pet(name),
            )
            select_button.grid(
                row=1 + len(DISPLAY_STATS) * 2,
                column=0,
                sticky="ew",
                pady=(12, 0),
            )

            self.pet_cards[pet.name] = {
                "frame": card,
                "status": status_label,
                "values": values,
                "bars": bars,
                "select_button": select_button,
            }

        self._refresh_cards()

    def _refresh_all(self):
        self._refresh_cards()
        self._refresh_header()
        self._refresh_actions()
        self._refresh_statistics()

    def _refresh_cards(self):
        for pet in self.game.pet_list():
            card = self.pet_cards.get(pet.name)
            if card is None:
                continue

            selected = pet.name == self.game.selected_name
            title = f"{pet.name}  (selected)" if selected else pet.name
            card["frame"].configure(text=title)

            card["status"].configure(
                text="ALIVE" if pet.alive else "DEAD",
                foreground=ALIVE_COLOR if pet.alive else DEAD_COLOR,
            )

            for stat_name in DISPLAY_STATS:
                value = getattr(pet, stat_name)
                card["values"][stat_name].configure(
                    text=f"{value:>3}/100",
                    foreground=self._stat_color(stat_name, value),
                )
                card["bars"][stat_name]["value"] = value

            card["select_button"].configure(
                text="Selected" if selected else "Select",
                state="disabled" if selected else "normal",
            )

    def _refresh_header(self):
        data = calculate_statistics(self.game.pet_list())
        self.turn_label.configure(text=f"Turn {self.game.turn}")

        if self.game.is_game_over():
            self.summary_label.configure(
                text="All pets are dead",
                foreground=DEAD_COLOR,
            )
        elif data["dead"] > 0:
            self.summary_label.configure(
                text=f"{data['living']} alive / {data['dead']} dead",
                foreground=WARNING_COLOR,
            )
        else:
            self.summary_label.configure(
                text=f"{data['living']} alive / {data['dead']} dead",
                foreground=ALIVE_COLOR,
            )

    def _refresh_actions(self):
        if self.game.is_game_over():
            self.current_label.configure(
                text="Game over - all pets are dead. Start a new game or load a save.",
                foreground=DEAD_COLOR,
            )
            enabled = False
        elif self.game.selected_pet is None:
            self.current_label.configure(
                text="Select a Tamagotchi to use an action.",
                foreground=MUTED_COLOR,
            )
            enabled = False
        elif not self.game.selected_pet.alive:
            self.current_label.configure(
                text=f"{self.game.selected_pet.name} is dead. Select another pet.",
                foreground=DEAD_COLOR,
            )
            enabled = False
        else:
            self.current_label.configure(
                text=f"Current pet: {self.game.selected_pet.name}",
                foreground=TEXT_COLOR,
            )
            enabled = True

        state = "normal" if enabled else "disabled"
        for button in self.action_buttons.values():
            button.configure(state=state)

    def _refresh_statistics(self):
        data = calculate_statistics(self.game.pet_list())

        for key, label in self.stat_value_labels.items():
            value = data[key]
            if value is None:
                text = "N/A"
            elif key in ("living", "dead"):
                text = str(value)
            else:
                text = f"{value:.1f}"
            label.configure(text=text)

    @staticmethod
    def _stat_color(stat_name, value):
        if stat_name == "health":
            if value <= 30:
                return DEAD_COLOR
            if value <= 60:
                return WARNING_COLOR
            return ALIVE_COLOR

        if value >= 80:
            return DEAD_COLOR
        if value >= 60:
            return WARNING_COLOR
        return ALIVE_COLOR

    def _select_pet(self, name):
        self.game.select_pet(name)
        self._refresh_all()

    def _perform_action(self, action):
        try:
            messages = self.game.perform_action(action)
        except NoPetSelectedError:
            self._append_log("Select a Tamagotchi before using an action.", "warning")
            self._refresh_all()
            return
        except DeadPetError as error:
            self._append_log(str(error), "warning")
            self._refresh_all()
            return

        self._append_log(f"Turn {self.game.turn}", "turn")
        for message in messages:
            tag = "warning" if self._is_warning(message) else None
            self._append_log(f"  {message}", tag)

        if self.game.is_game_over():
            self._append_log(
                "All three Tamagotchis are dead. Start a new game or load a save.",
                "warning",
            )

        self._refresh_all()

    @staticmethod
    def _is_warning(message):
        text = message.lower()
        return any(word in text for word in WARNING_WORDS)

    def _append_log(self, text, tag=None):
        self.log.configure(state="normal")
        if tag is None:
            self.log.insert("end", text + "\n")
        else:
            self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _log_welcome(self):
        self._append_log("Welcome to the Tamagotchi Simulator!", "success")
        self._append_log(
            "Every action uses one turn. All living pets get hungrier, "
            "more bored and more tired as time passes."
        )
        self._append_log(
            "Use the Select button on a card to change pets, then choose an action."
        )

    def _new_game(self):
        if self.game.turn > 0:
            if not messagebox.askyesno(
                "New Game",
                "Start a new game? Unsaved progress will be lost.",
                parent=self.root,
            ):
                return

        self.game = Game()
        self.game.select_pet("1")
        self._rebuild_pet_cards()
        self._clear_log()
        self._log_welcome()
        self._refresh_all()

    def _save_game(self):
        try:
            save_game(self.game, SAVE_FILE)
        except SaveFileError as error:
            messagebox.showerror(
                "Save failed",
                f"Could not save the game:\n{error}",
                parent=self.root,
            )
            return

        self._append_log(f"Game saved to {SAVE_FILE}.", "success")
        messagebox.showinfo(
            "Game saved",
            f"Game saved to:\n{SAVE_FILE}",
            parent=self.root,
        )

    def _load_game(self):
        if self.game.turn > 0:
            if not messagebox.askyesno(
                "Load Game",
                "Loading will replace the current game. Continue?",
                parent=self.root,
            ):
                return

        try:
            loaded_game = load_game(SAVE_FILE)
        except SaveFileError as error:
            messagebox.showerror(
                "Load failed",
                f"Could not load the game:\n{error}",
                parent=self.root,
            )
            return

        self.game = loaded_game
        living = [pet for pet in self.game.pet_list() if pet.alive]
        target = living[0] if living else self.game.pet_list()[0]
        self.game.select_pet(target.name)

        self._rebuild_pet_cards()
        self._clear_log()
        self._append_log(f"Loaded game from {SAVE_FILE}.", "success")
        self._append_log(f"Resuming on turn {self.game.turn}.")

        if self.game.is_game_over():
            self._append_log("All pets in this save are dead.", "warning")

        self._refresh_all()

    def _show_help(self):
        messagebox.showinfo("How to Play", HELP_TEXT, parent=self.root)

    def _quit(self):
        if self.game.turn > 0:
            if not messagebox.askyesno(
                "Quit",
                "Quit the game? Unsaved progress will be lost.",
                parent=self.root,
            ):
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    TamagotchiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
