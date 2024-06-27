class Middleman:
    def __init__(self, environment):
        self.environment = environment

    def motor_input_to_environment(self, input):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()
        #print(filtered_string)
        self.environment.move_agent_right(filtered_string)


    def test(self):
        print("I'm functioning properly.")

def get_middleman(environment):
    return Middleman(environment)