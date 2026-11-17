"""The Tamagotchi class."""

from .config import (
    ACTION_EFFECTS,
    BOREDOM_LIMIT,
    BOREDOM_PENALTY,
    EXHAUSTION_LIMIT,
    EXHAUSTION_PENALTY,
    GOOD_CARE_BONUS,
    GOOD_CARE_LIMIT,
    HUNGER_LIMIT,
    HUNGER_PENALTY,
    MAX_STAT,
    MIN_STAT,
    STARTING_BOREDOM,
    STARTING_EXHAUSTION,
    STARTING_HEALTH,
    STARTING_HUNGER,
    STAT_NAMES,
    TURN_CHANGES,
)
from .exceptions import DeadPetError


class Tamagotchi:
    """A single virtual pet."""

    def __init__(
        self,
        name,
        hunger=STARTING_HUNGER,
        health=STARTING_HEALTH,
        boredom=STARTING_BOREDOM,
        exhaustion=STARTING_EXHAUSTION,
    ):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("A Tamagotchi needs a name.")

        self.name = name.strip()
        self.hunger = self._clamp(hunger)
        self.health = self._clamp(health)
        self.boredom = self._clamp(boredom)
        self.exhaustion = self._clamp(exhaustion)
        self.alive = self.health > 0

    @staticmethod
    def _clamp(value):
        return max(MIN_STAT, min(MAX_STAT, int(value)))

    def _require_alive(self, action):
        if not self.alive:
            raise DeadPetError(f"{self.name} is dead and cannot {action}.")

    def change_stat(self, stat_name, amount):
        """Change one stat and keep it within 0-100. Also checks for death."""
        if stat_name not in STAT_NAMES:
            raise ValueError(f"Unknown stat: {stat_name}")

        value = getattr(self, stat_name) + amount
        setattr(self, stat_name, max(MIN_STAT, min(MAX_STAT, value)))

        if self.health <= 0:
            self.health = 0
            self.alive = False

    def _apply_effects(self, action):
        for stat_name, amount in ACTION_EFFECTS[action].items():
            self.change_stat(stat_name, amount)

    def feed(self):
        self._require_alive("eat")
        self._apply_effects("feed")

    def play(self):
        self._require_alive("play")
        self._apply_effects("play")

    def sleep(self):
        self._require_alive("sleep")
        self._apply_effects("sleep")

    def heal(self):
        self._require_alive("be healed")
        self._apply_effects("heal")

    def pass_turn(self):
        """Apply the changes that happen to a living pet each turn.

        Returns a list of messages for anything important, such as health
        penalties or the pet dying.
        """
        if not self.alive:
            return []

        messages = []

        # The needs get worse a little on their own.
        for stat_name, amount in TURN_CHANGES.items():
            self.change_stat(stat_name, amount)

        penalties = []
        if self.hunger >= HUNGER_LIMIT:
            penalties.append((HUNGER_PENALTY, f"{self.name} is starving."))
        if self.exhaustion >= EXHAUSTION_LIMIT:
            penalties.append((EXHAUSTION_PENALTY, f"{self.name} is exhausted."))
        if self.boredom >= BOREDOM_LIMIT:
            penalties.append((BOREDOM_PENALTY, f"{self.name} is bored out of its mind."))

        for penalty, message in penalties:
            self.change_stat("health", -penalty)
            messages.append(f"{message} (-{penalty} health)")
            if not self.alive:
                messages.append(f"{self.name} has died.")
                return messages

        # Good care helps the pet recover slowly.
        if (
            self.hunger < GOOD_CARE_LIMIT
            and self.boredom < GOOD_CARE_LIMIT
            and self.exhaustion < GOOD_CARE_LIMIT
        ):
            self.change_stat("health", GOOD_CARE_BONUS)

        return messages

    def status_report(self):
        state = "ALIVE" if self.alive else "DEAD"
        return (
            f"{self.name} ({state})\n"
            f"  Hunger:     {self.hunger:>3}/100\n"
            f"  Health:     {self.health:>3}/100\n"
            f"  Boredom:    {self.boredom:>3}/100\n"
            f"  Exhaustion: {self.exhaustion:>3}/100"
        )

    def display_status(self):
        print(self.status_report())

    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "health": self.health,
            "boredom": self.boredom,
            "exhaustion": self.exhaustion,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a pet from saved data, rejecting anything invalid."""
        if not isinstance(data, dict):
            raise ValueError("pet must be a JSON object")

        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

        stats = {}
        for stat_name in STAT_NAMES:
            value = data.get(stat_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{stat_name} must be an integer")
            if not MIN_STAT <= value <= MAX_STAT:
                raise ValueError(f"{stat_name} must be between {MIN_STAT} and {MAX_STAT}")
            stats[stat_name] = value

        alive = data.get("alive")
        if not isinstance(alive, bool):
            raise ValueError("alive must be true or false")
        if alive != (stats["health"] > 0):
            raise ValueError("alive must be false exactly when health is 0")

        return cls(name, **stats)
