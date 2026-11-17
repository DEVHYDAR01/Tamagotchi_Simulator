"""Game settings.

The numbers that control the difficulty of the game live here, so they can be
changed without touching the game logic.
"""

from pathlib import Path

# All stats use a 0-100 scale. For the three needs, higher is worse.
# For health, higher is better and 0 means the pet is dead.
MIN_STAT = 0
MAX_STAT = 100

PET_NAMES = ("Mochi", "Pixel", "Biscuit")
STAT_NAMES = ("hunger", "health", "boredom", "exhaustion")

STARTING_HUNGER = 30
STARTING_HEALTH = 100
STARTING_BOREDOM = 30
STARTING_EXHAUSTION = 20

# What each action does to the selected pet.
ACTION_EFFECTS = {
    "feed": {"hunger": -30, "health": 2},
    "play": {"hunger": 15, "boredom": -35, "exhaustion": 20},
    "sleep": {"hunger": 5, "boredom": 10, "exhaustion": -40},
    "heal": {"health": 30},
}

# Applied to every living pet after each successful action. These increases are
# small because all three pets age at once while the player only gets one action.
TURN_CHANGES = {
    "hunger": 3,
    "boredom": 2,
    "exhaustion": 2,
}

# Neglected needs damage the pet's health.
HUNGER_LIMIT = 80
HUNGER_PENALTY = 10
EXHAUSTION_LIMIT = 80
EXHAUSTION_PENALTY = 8
BOREDOM_LIMIT = 90
BOREDOM_PENALTY = 5

# A pet whose needs are all low slowly recovers some health.
GOOD_CARE_LIMIT = 40
GOOD_CARE_BONUS = 2

# Chance of a random event after each action.
EVENT_CHANCE = 0.30

# The config file lives in src/tamagotchi_simulator, so this is the project root.
SAVE_VERSION = 1
SAVE_FILE = Path(__file__).resolve().parents[2] / "saves" / "savegame.json"
