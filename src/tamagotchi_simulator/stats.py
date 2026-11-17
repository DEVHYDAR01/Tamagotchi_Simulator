"""Functions that calculate the game statistics."""

from .config import STAT_NAMES


def living_pets(pets):
    return [pet for pet in pets if pet.alive]


def count_living(pets):
    return len(living_pets(pets))


def count_dead(pets):
    return sum(1 for pet in pets if not pet.alive)


def average_health(pets):
    alive = living_pets(pets)
    if not alive:
        return None
    return round(sum(pet.health for pet in alive) / len(alive), 1)


def average_stat(pets, stat_name):
    if stat_name not in STAT_NAMES:
        raise ValueError(f"Unknown stat: {stat_name}")

    alive = living_pets(pets)
    if not alive:
        return None
    return round(sum(getattr(pet, stat_name) for pet in alive) / len(alive), 1)


def calculate_statistics(pets):
    """Return all the numbers needed by the statistics screen.

    Averages only include living pets. If every pet is dead, they are None.
    """
    pets = list(pets)
    return {
        "living": count_living(pets),
        "dead": count_dead(pets),
        "average_health": average_health(pets),
        "average_hunger": average_stat(pets, "hunger"),
        "average_boredom": average_stat(pets, "boredom"),
        "average_exhaustion": average_stat(pets, "exhaustion"),
    }
