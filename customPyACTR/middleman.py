class Middleman:
    def __init__(self, environment):
        self.environment = environment

    def motor_input_to_environment(self, input):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()
        print(f"Agent klickt: {filtered_string}")
        input = "W"
        if input == "W":
            self.environment.move_agent_right()

    def test(self):
        print("I'm functioning properly.")

def get_middleman(environment):
    return Middleman(environment)