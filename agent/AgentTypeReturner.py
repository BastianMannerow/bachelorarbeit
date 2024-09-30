from agent.Maxi import Maxi
from agent.Test import Test

class AgentTypeReturner:
    def __init__(self):
        pass

    def return_agent_type(self, name, actr_environment):
        if name == "Human":
            return None

        elif name == "Maxi":
            return Maxi(actr_environment).get_agent()

        elif name == "Test":
            return Test(actr_environment).get_agent()

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")