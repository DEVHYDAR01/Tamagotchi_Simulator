"""The Game class, which keeps the three pets and runs the turns."""

import random

from .config import (
    PET_NAMES,
    STARTING_BOREDOM,
    STARTING_EXHAUSTION,
    STARTING_HEALTH,
    STARTING_HUNGER,
)
from .events import maybe_trigger_event
from .exceptions import DeadPetError, NoPetSelectedError, PetNotFoundError
from .tamagotchi import Tamagotchi

ACTION_MESSAGES = {
    "feed": "You fed {name}.",
    "play": "You played with {name}.",
    "sleep": "You put {name} to sleep.",
    "heal": "You healed {name}.",
}


class Game:
    """Owns the three Tamagotchis and the state of the current game."""

    def __init__(self, pet_names=PET_NAMES, seed=None):
        self.pets = {}
        for name in pet_names:
            self.pets[name] = Tamagotchi(
                name,
                hunger=STARTING_HUNGER,
                health=STARTING_HEALTH,
                boredom=STARTING_BOREDOM,
                exhaustion=STARTING_EXHAUSTION,
            )

        self.selected_name = None
        self.turn = 0
        self.rng = random.Random(seed)

    def pet_list(self):
        """Return the pets in the order they appear in the menu."""
        return list(self.pets.values())

    @property
    def selected_pet(self):
        if self.selected_name is None:
            return None
        return self.pets.get(self.selected_name)

    def select_pet(self, choice):
        """Select a pet by its 1-based number or by name."""
        choice = str(choice).strip()
        pets = self.pet_list()

        if choice.isdigit():
            number = int(choice)
            if 1 <= number <= len(pets):
                pet = pets[number - 1]
                self.selected_name = pet.name
                return pet

        for pet in pets:
            if pet.name.lower() == choice.lower():
                self.selected_name = pet.name
                return pet

        raise PetNotFoundError(
            f"'{choice}' is not a valid pet. "
            f"Choose a number from 1 to {len(pets)} or a pet name."
        )

    def perform_action(self, action):
        """Perform an action, let time pass, then possibly trigger an event.

        Returns a list of messages for the player. If the action is not
        possible, one of the game exceptions is raised instead.
        """
        pet = self.selected_pet
        if pet is None:
            raise NoPetSelectedError("Select a Tamagotchi first.")
        if not pet.alive:
            raise DeadPetError(f"{pet.name} is dead and cannot do anything.")

        actions = {
            "feed": pet.feed,
            "play": pet.play,
            "sleep": pet.sleep,
            "heal": pet.heal,
        }
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        actions[action]()
        messages = [ACTION_MESSAGES[action].format(name=pet.name)]

        # Time passes for every living pet, not only the one we used.
        for other_pet in self.pet_list():
            messages.extend(other_pet.pass_turn())

        event_message = maybe_trigger_event(self, self.rng)
        if event_message:
            messages.append(event_message)

        self.turn += 1
        return messages

    def is_game_over(self):
        return all(not pet.alive for pet in self.pets.values())

    @classmethod
    def from_pets(cls, pets, turn=0, seed=None):
        """Create a game from already-built pets, used when loading a save."""
        game = cls(seed=seed)
        game.pets = {pet.name: pet for pet in pets}
        game.turn = turn
        game.selected_name = None
        return game
