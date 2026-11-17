# Tamagotchi Simulator

A command-line virtual pet game written in Python. The player looks after three
Tamagotchis — Mochi, Pixel and Biscuit — keeping their hunger, health, boredom
and exhaustion under control.

This project was made for the EPITA Introduction to Python Programming course.
It uses only the Python standard library and is managed with `uv`.

## Features

- Three independent Tamagotchis.
- Four actions: feed, play, sleep and heal.
- Turn-based stat changes after every action.
- Health penalties for neglected needs.
- Random events: found food, sickness, nightmares and extra naps.
- Statistics for living and dead pets.
- JSON save and load with validation.
- Friendly error messages for bad input and broken save files.
- A Tkinter graphical interface alongside the command-line version.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)

## Running the game

From the project root:

```bash
uv sync
uv run tamagotchi-simulator
```

It can also be started as a module:

```bash
uv run python -m tamagotchi_simulator.main
```

## Graphical interface

The Tkinter version uses the same game logic and the same save file as the CLI:

```bash
uv run tamagotchi-gui
```

It shows one card per Tamagotchi with health, hunger, boredom and exhaustion
bars. Select a pet on its card, then use the Feed, Play, Sleep and Heal buttons.
Statistics and the activity log update after every action.

## How to play

Use the menu numbers to choose an option. Select a Tamagotchi first; actions
apply to the selected pet. The menu comes back after every action.

Each action uses one turn. After the action, every living pet gets a little
hungrier, more bored and more tired. If hunger or exhaustion reaches 80 (or
boredom reaches 90), the pet loses health. If health reaches 0, the pet dies
and cannot act again. A pet whose needs are all below 40 slowly regains health.

### Action effects

| Action | Hunger | Boredom | Exhaustion | Health |
| --- | ---: | ---: | ---: | ---: |
| Feed | -30 | 0 | 0 | +2 |
| Play | +15 | -35 | +20 | 0 |
| Sleep | +5 | +10 | -40 | 0 |
| Heal | 0 | 0 | 0 | +30 |

### Changes after every action

| Stat | Change |
| --- | ---: |
| Hunger | +3 |
| Boredom | +2 |
| Exhaustion | +2 |

### Random events

There is a 30% chance of a random event after each action:

| Event | Effect |
| --- | --- |
| Finds food | Hunger -20 |
| Gets sick | Health -15 |
| Nightmare | Exhaustion +20 |
| Extra nap | Exhaustion -20 |

## Statistics

The statistics screen shows the number of living and dead pets, plus the
average health, hunger, boredom and exhaustion of the living pets. Dead pets
are left out of the averages.

## Saving

Saves are written to `saves/savegame.json` in the project folder. The folder is
created automatically. The file contains all three pets, their stats, whether
they are alive, and the current turn. Loading validates the whole file before
replacing the current game, so a missing or broken save does not crash the
program or destroy the current session.

## Project structure

```text
src/tamagotchi_simulator/
├── __init__.py      package information
├── config.py        balance values and the save path
├── exceptions.py    game-specific exceptions
├── tamagotchi.py    the Tamagotchi class
├── game.py          turn flow and the three-pet collection
├── events.py        random events
├── stats.py         statistics functions
├── storage.py       JSON save and load
├── ui.py            command-line menu and display
├── gui.py           Tkinter graphical interface
└── main.py          command-line program entry point
```

All gameplay numbers are in `config.py`, so they can be tuned without changing
the rest of the code.
