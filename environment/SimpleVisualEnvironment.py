import collections
import random
import customPyACTR as actr
from customPyACTR import utilities


class SimpleVisualEnvironment(actr.Environment):
    def __init__(self, width, height, focus_position):
        super().__init__(focus_position=focus_position)
        self.width = width
        self.height = height
        self.matrix = [[None for _ in range(width)] for _ in range(height)]
        self.agent_position = (height // 2, width // 2)  # Initial position of the agent in the middle
        self.matrix[self.agent_position[0]][self.agent_position[1]] = 'A'  # Code for the Agent

        # Place B, C, D at random positions
        letters = ['B', 'C', 'D']
        self.letter_positions = {}
        for letter in letters:
            while True:
                x, y = random.randint(0, height - 1), random.randint(0, width - 1)
                if self.matrix[x][y] is None:
                    self.matrix[x][y] = letter
                    self.letter_positions[letter] = (x, y)
                    break

    def print_matrix(self):
        for row in self.matrix:
            print(" ".join([cell if cell is not None else "." for cell in row]))

    def get_matrix(self):
        return self.matrix

    # Definition of possible Stimuli
    def get_stimuli(self):
        stimuli = ['A', 'B', 'C', 'D']
        text = []
        for letter in stimuli:
            if letter == 'A':
                x, y = self.agent_position
            else:
                x, y = self.letter_positions[letter]
            # Convert matrix coordinates to screen coordinates (this might need adjustment)
            screen_x = x * 20 + 100  # Example conversion
            screen_y = y * 20 + 100  # Example conversion
            text.append({letter: {'text': letter, 'position': (screen_x, screen_y)}})
        return stimuli, text

    # Needed to show all stimuli at once
    def environment_process(self, stimuli=None, triggers=None, times=1, start_time=0):
        start_time = self.initial_time - start_time
        if not isinstance(stimuli, collections.abc.Iterable):
            stimuli = [stimuli]
        if not isinstance(triggers, collections.abc.Iterable):
            triggers = [triggers]
        if not isinstance(times, collections.abc.Iterable):
            times = [times]

        if len(stimuli) != len(triggers):
            if len(stimuli) == 1:
                stimuli = stimuli * len(triggers)
            elif len(triggers) == 1:
                triggers = triggers * len(stimuli)
            else:
                raise utilities.ACTRError("In environment, stimuli must be the same length as triggers or one of the two must be of length 1")
        if len(stimuli) != len(times):
            if len(times) == 1:
                times = times * len(stimuli)
            else:
                raise utilities.ACTRError("In environment, times must be the same length as stimuli or times must be of length 1")
        self.stimuli = stimuli
        self.triggers = [set(x.upper() for x in trigger) for trigger in triggers]
        self.times = times

        # Zeige alle Stimuli gleichzeitig
        self.stimulus = {k: v for d in self.stimuli for k, v in d.items()}
        yield self.Event(self.roundtime(start_time), self._ENV, "PRINTED ALL STIMULI")

        for idx, stimulus in enumerate(self.stimuli):
            run_time = self.times[idx]
            start_time += run_time
            yield self.Event(self.roundtime(start_time), self._ENV, "UPDATED STIMULUS")

def get_environment(width, height, focus_position):
    return SimpleVisualEnvironment(width, height, focus_position)
