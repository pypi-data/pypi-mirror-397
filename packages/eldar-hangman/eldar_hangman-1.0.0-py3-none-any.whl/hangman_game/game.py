import random
from .board import Board

class Hangman:
    def __init__(self, words=None):
        self.words = words or ["python", "hangman", "challenge", "developer"]
        self.word = random.choice(self.words).lower()
        self.board = Board(len(self.word))
        self.guesses = set()
        self.max_wrong = 6
        self.wrong_count = 0

    def guess(self, letter):
        letter = letter.lower()
        if letter in self.guesses:
            return False
        self.guesses.add(letter)

        if letter in self.word:
            self.board.update(letter, self.word)
            return True
        else:
            self.wrong_count += 1
            return False

    def is_won(self):
        return self.board.is_complete()

    def is_lost(self):
        return self.wrong_count >= self.max_wrong

    def play(self):
        while not (self.is_won() or self.is_lost()):
            self.board.render()
            print(f"Wrong guesses: {self.wrong_count}/{self.max_wrong}")
            letter = input("Guess a letter: ")
            if not self.guess(letter):
                print("❌ Wrong or repeated!")
            else:
                print("✅ Good guess!")

        if self.is_won():
            print(f"🎉 You won! The word was '{self.word}'")
        else:
            print(f"💀 You lost! The word was '{self.word}'")
