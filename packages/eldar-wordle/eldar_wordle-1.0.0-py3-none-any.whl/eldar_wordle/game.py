import random
from.words import WORDS

class Wordle:
    def __init__(self,  max_attempts=6):
        self.word = random.choice(WORDS)
        self.max_attempts = max_attempts
        self.attempts = 0


    def check_guess(self, guess):
        result = []
        for i, ch in enumerate(guess):
            if ch == self.word[i]:
                result.append("🟩")
            elif ch in self.word:
                result.append("🟨")
            else:
                result.append("⬜")

            return "".join(result)
        

    def play(self):
        print("🎯 WORDLE (5-letter Guess)")
        print(f"You have {self.max_attempts} attempts\n")


        while self.attempts < self.max_attempts:
            guess = input("Enter 5-letter word: ").lower()

            if len(guess) != 5 or not guess.isalpha():
                print("❌ Invalid word\n")
                continue

            self.attempts += 1
            result = self.check_guess(guess)
            print(result,  "\n")

            if guess == self.word:
                print(f"🎉 You won in  {self.attempts} attempts!")
                return
            
            print(f"💀 Game over! Word was: {self.word}")


def main():
    Wordle().play()

    