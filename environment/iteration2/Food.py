import random

class Food:
    def __init__(self):
        self.saturation = random.randint(1, 3)
        self.amount = random.randint(1, 10)
        self.time_till_regrowth = 0

    def get_saturation(self):
        return self.saturation

    def get_amount(self):
        return self.amount

    def get_time_till_regrowth(self):
        return self.time_till_regrowth