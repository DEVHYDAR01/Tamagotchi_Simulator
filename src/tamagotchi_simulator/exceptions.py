"""Exceptions used by the game."""


class TamagotchiError(Exception):
    """Base class for errors that the game can explain to the player."""


class DeadPetError(TamagotchiError):
    """Raised when the player tries to do something with a dead pet."""


class PetNotFoundError(TamagotchiError):
    """Raised when the chosen pet does not exist."""


class NoPetSelectedError(TamagotchiError):
    """Raised when an action is requested without a selected pet."""


class SaveFileError(TamagotchiError):
    """Raised when a save file cannot be read or written."""
