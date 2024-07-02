class Middleman:
    def __init__(self, environment):
        self.environment = environment

    def motor_input_to_environment(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()

        def move_right():
            if not self.environment.move_agent_right(agent):
                print("Movement Blocked")

        def move_left():
            if not self.environment.move_agent_left(agent):
                print("Movement Blocked")

        def move_up():
            if not self.environment.move_agent_up(agent):
                print("Movement Blocked")

        def move_down():
            if not self.environment.move_agent_down(agent):
                print("Movement Blocked")

        switch_case = {
            'D': move_right,
            'A': move_left,
            'W': move_up,
            'S': move_down
        }

        if filtered_string in switch_case:
            switch_case[filtered_string]()
        else:
            print(f"The key input {filtered_string} was not defined for your environment.")

    def set_environment(self, environment):
        self.environment = environment

def get_middleman(environment):
    return Middleman(environment)