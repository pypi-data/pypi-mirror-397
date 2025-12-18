import argparse
from.game import TicTacToe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai",  choices=["easy",  "hard"])
    parser.add_argument("--no_emoji",  action="store_true")
    args = parser.parse_args()

    game = TicTacToe(
        ai=args.ai,
        emoji = not args.no_emoji 
    )

    game.play()

    