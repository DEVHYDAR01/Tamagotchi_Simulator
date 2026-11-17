"""JSON saving and loading."""

import json
from datetime import datetime
from pathlib import Path

from .config import SAVE_FILE, SAVE_VERSION
from .exceptions import SaveFileError
from .game import Game
from .tamagotchi import Tamagotchi

PET_COUNT = 3


def save_game(game, path=SAVE_FILE):
    """Write the current game to a JSON file."""
    path = Path(path)
    data = {
        "version": SAVE_VERSION,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "turn": game.turn,
        "pets": [pet.to_dict() for pet in game.pet_list()],
    }

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(path.name + ".tmp")

        with temp_path.open("w", encoding="utf-8") as save_file:
            json.dump(data, save_file, indent=2)
            save_file.write("\n")

        temp_path.replace(path)
    except OSError as error:
        raise SaveFileError(f"could not write {path}: {error}") from error


def load_game(path=SAVE_FILE):
    """Read and validate a save file, then return the restored Game."""
    path = Path(path)

    try:
        with path.open("r", encoding="utf-8") as save_file:
            data = json.load(save_file)
    except FileNotFoundError as error:
        raise SaveFileError(f"there is no save file at {path}") from error
    except json.JSONDecodeError as error:
        raise SaveFileError(
            f"the save file at {path} is not valid JSON "
            f"(line {error.lineno}, column {error.colno})"
        ) from error
    except UnicodeDecodeError as error:
        raise SaveFileError(f"the save file at {path} is not valid UTF-8 text") from error
    except OSError as error:
        raise SaveFileError(f"could not read {path}: {error}") from error

    if not isinstance(data, dict):
        raise SaveFileError("the save file must contain a JSON object")

    version = data.get("version")
    if isinstance(version, bool) or version != SAVE_VERSION:
        raise SaveFileError(f"unsupported save version: {version!r}")

    turn = data.get("turn")
    if isinstance(turn, bool) or not isinstance(turn, int) or turn < 0:
        raise SaveFileError("the saved turn number is invalid")

    pets_data = data.get("pets")
    if not isinstance(pets_data, list) or len(pets_data) != PET_COUNT:
        raise SaveFileError(f"a save file must contain exactly {PET_COUNT} Tamagotchis")

    pets = []
    used_names = set()

    for index, pet_data in enumerate(pets_data, start=1):
        try:
            pet = Tamagotchi.from_dict(pet_data)
        except ValueError as error:
            raise SaveFileError(f"Tamagotchi #{index} is invalid: {error}") from error

        name_key = pet.name.lower()
        if name_key in used_names:
            raise SaveFileError(f"the save file has two pets named {pet.name}")
        used_names.add(name_key)
        pets.append(pet)

    return Game.from_pets(pets, turn)
