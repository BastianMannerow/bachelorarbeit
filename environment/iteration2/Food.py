import random

class Food:
    def __init__(self):
        self.saturation = random.randint(1, 3)
        self.amount = random.randint(1, 10)