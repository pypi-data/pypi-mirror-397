from colorama import Fore, Style, init
init(autoreset=True)

class Board:
    def __init__(self, length):
        self.display = ["_"] * length

    def update(self, letter, word):
        for i, c in enumerate(word):
            if c == letter:
                self.display[i] = letter

    def render(self):
        print(" ".join([Fore.GREEN + c if c != "_" else c for c in self.display]))

    def is_complete(self):
        return "_" not in self.display
