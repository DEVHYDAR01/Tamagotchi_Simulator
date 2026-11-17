"""Program entry point."""

from .game import Game
from .ui import run_cli


def main():
    game = Game()

    try:
        run_cli(game)
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
