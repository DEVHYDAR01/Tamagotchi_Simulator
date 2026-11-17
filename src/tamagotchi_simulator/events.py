"""Random events that can happen after a turn."""

import random

from .config import EVENT_CHANCE

# Each event changes one stat. The messages are formatted with the pet's name.
EVENTS = (
    {
        "message": "{name} found some food and ate it. (hunger -20)",
        "stat": "hunger",
        "amount": -20,
    },
    {
        "message": "{name} got sick. (health -15)",
        "stat": "health",
        "amount": -15,
    },
    {
        "message": "{name} had a nightmare. (exhaustion +20)",
        "stat": "exhaustion",
        "amount": 20,
    },
    {
        "message": "{name} took a cozy extra nap. (exhaustion -20)",
        "stat": "exhaustion",
        "amount": -20,
    },
)


def maybe_trigger_event(game, rng=None):
    """Trigger a random event if the dice allow it.

    Returns a message describing the event, or None if nothing happened.
    """
    if rng is None:
        rng = random

    living_pets = [pet for pet in game.pet_list() if pet.alive]
    if not living_pets or rng.random() >= EVENT_CHANCE:
        return None

    pet = rng.choice(living_pets)
    event = rng.choice(EVENTS)
    was_alive = pet.alive

    pet.change_stat(event["stat"], event["amount"])
    message = event["message"].format(name=pet.name)

    if was_alive and not pet.alive:
        message += f" {pet.name} did not survive."

    return message
