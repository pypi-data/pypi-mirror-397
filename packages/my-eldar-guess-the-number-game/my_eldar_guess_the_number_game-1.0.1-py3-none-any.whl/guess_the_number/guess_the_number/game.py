import random 

class GuessTheNumber:
    def __init__(self,  start=1, end=100, attempts=7):
        self.start = start 
        self.end = end 
        self.attempts = attempts
        self.number = random.randint(start, end)

    def play(self):
        print(f"I guessed a number between {self.start}")
        print(f"You have {self.attempts} attempts. Good luck \n")

        for i in range(1, self.attempts + 1):
            try:
                guess = int(input(f"Attempt {i}:"))
            except ValueError:
                print("Please enter a valid number. ")
                continue

            if guess < self.number:
                print("Too low!\n")
            elif guess > self.number:
                print("Too high!\n")
            else:
                print(f"Correct! You found it in {i} attempts 🎉")
                return True 
            

            print(f"Game over! The number was {self.number}.")
            return False 