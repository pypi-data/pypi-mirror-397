import random

class GuessTheNumber:
    def __init__(self, start=1, end=100, attempts=7):
        self.start = start
        self.end = end
        self.attempts = attempts
        self.number = random.randint(start, end)

    def play(self):
        remaining_attempts = self.attempts
        print(f"I guessed a number between {self.start} and {self.end}.")
        print(f"You have {self.attempts} attempts. Good luck!\n")

        while remaining_attempts > 0:
            try:
                guess = int(input(f"Attempt ({self.attempts - remaining_attempts + 1}): "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if guess < self.number:
                print("Too low!\n")
            elif guess > self.number:
                print("Too high!\n")
            else:
                print(f"Correct! You found it in {self.attempts - remaining_attempts + 1} attempts 🎉")
                return True

            remaining_attempts -= 1

        print(f"Game over! The number was {self.number}.")
        return False
