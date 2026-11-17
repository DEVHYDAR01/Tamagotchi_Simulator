"""The command-line menu and all the output formatting."""

from . import stats
from .config import SAVE_FILE
from .exceptions import DeadPetError, NoPetSelectedError, PetNotFoundError, SaveFileError
from .storage import load_game, save_game

MENU_OPTIONS = (
    (1, "Select a Tamagotchi"),
    (2, "Feed"),
    (3, "Play"),
    (4, "Sleep"),
    (5, "Heal"),
    (6, "Show selected pet's status"),
    (7, "Show game statistics"),
    (8, "Save game"),
    (9, "Load game"),
    (0, "Quit"),
)

ACTION_BY_MENU = {
    2: "feed",
    3: "play",
    4: "sleep",
    5: "heal",
}


def ask_int(prompt):
    """Ask for an integer until the player types one."""
    while True:
        text = input(prompt)
        try:
            return int(text)
        except ValueError:
            print("Please enter a number.")


def show_menu(game):
    print("\n" + "=" * 52)
    print("TAMAGOTCHI SIMULATOR".center(52))
    print("=" * 52)

    if game.selected_pet is None:
        print("Current pet: none selected")
    else:
        pet = game.selected_pet
        state = "alive" if pet.alive else "dead"
        print(f"Current pet: {pet.name} ({state})")

    print(f"Turn: {game.turn}")

    if game.is_game_over():
        print("All of your Tamagotchis are dead. Load a save or quit.")

    print("-" * 52)
    for number, label in MENU_OPTIONS:
        print(f"{number}. {label}")
    print()


def show_pet_list(game):
    print("\nYour Tamagotchis:")
    for index, pet in enumerate(game.pet_list(), start=1):
        state = "ALIVE" if pet.alive else "DEAD"
        print(
            f"  {index}. {pet.name:<10} [{state:<5}] "
            f"Hunger {pet.hunger:>3}  Health {pet.health:>3}  "
            f"Boredom {pet.boredom:>3}  Exhaustion {pet.exhaustion:>3}"
        )


def select_pet_flow(game):
    show_pet_list(game)
    choice = input("Enter a pet number or name (blank to cancel): ").strip()

    if not choice:
        print("Selection cancelled.")
        return

    try:
        pet = game.select_pet(choice)
    except PetNotFoundError as error:
        print(f"Error: {error}")
        return

    print(f"\nSelected {pet.name}.")
    pet.display_status()


def action_flow(game, action):
    try:
        messages = game.perform_action(action)
    except NoPetSelectedError:
        print("You need to select a Tamagotchi first (option 1).")
        return
    except DeadPetError as error:
        print(f"Error: {error}")
        return

    print()
    for message in messages:
        print(f"- {message}")

    pet = game.selected_pet
    if pet is not None:
        print(
            f"\n{pet.name}: Hunger {pet.hunger}/100 | Health {pet.health}/100 | "
            f"Boredom {pet.boredom}/100 | Exhaustion {pet.exhaustion}/100"
        )


def status_flow(game):
    pet = game.selected_pet
    if pet is None:
        print("No Tamagotchi is selected. Use option 1 first.")
        return

    print()
    pet.display_status()


def format_average(value):
    if value is None:
        return "N/A (no living pets)"
    return f"{value:.1f}"


def statistics_flow(game):
    data = stats.calculate_statistics(game.pet_list())

    print("\nGame statistics")
    print("-" * 30)
    print(f"Turns played: {game.turn}")
    print(f"Living pets:  {data['living']}")
    print(f"Dead pets:    {data['dead']}")
    print(f"Average health (living):     {format_average(data['average_health'])}")
    print(f"Average hunger (living):     {format_average(data['average_hunger'])}")
    print(f"Average boredom (living):    {format_average(data['average_boredom'])}")
    print(f"Average exhaustion (living): {format_average(data['average_exhaustion'])}")


def save_flow(game):
    try:
        save_game(game)
    except SaveFileError as error:
        print(f"Could not save the game: {error}.")
        return

    print(f"Game saved to {SAVE_FILE}.")


def load_flow(game):
    if game.turn > 0:
        answer = input("Loading will replace the current game. Continue? (y/n): ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Load cancelled.")
            return game

    try:
        loaded_game = load_game()
    except SaveFileError as error:
        print(f"Could not load the game: {error}.")
        return game

    print(f"Game loaded from {SAVE_FILE}.")
    print("Select a Tamagotchi to continue.")
    return loaded_game


def run_cli(game):
    names = ", ".join(game.pets)
    print("Welcome to the Tamagotchi Simulator!")
    print(f"Take care of {names}. If a pet's health reaches 0, it dies.")

    while True:
        show_menu(game)
        choice = ask_int("Choose an option: ")

        if choice == 1:
            select_pet_flow(game)
        elif choice in ACTION_BY_MENU:
            action_flow(game, ACTION_BY_MENU[choice])
        elif choice == 6:
            status_flow(game)
        elif choice == 7:
            statistics_flow(game)
        elif choice == 8:
            save_flow(game)
        elif choice == 9:
            game = load_flow(game)
        elif choice == 0:
            print("\nThanks for playing. Goodbye!")
            return
        else:
            print("That option does not exist. Please choose 0-9.")
