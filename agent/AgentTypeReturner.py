from agent.Random import Rational
from agent.Test import Test

# Only responsible to avoid overloading the simulation. Returns the Agent object needed.
class AgentTypeReturner:
    def __init__(self):
        pass

    def return_agent_type(self, name, actr_environment):
        if name == "Human":
            return None

        elif name == "Test":
            return Test(actr_environment).get_agent()

        elif name == "Rational":
            return Rational(actr_environment).get_agent()

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")