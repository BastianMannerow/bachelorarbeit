from agent.Random import Random
from agent.Test import Test
from agent.SocialAgent import SocialAgent

# Only responsible to avoid overloading the simulation. Returns the Agent object needed.
# TODO imported objects shouldn't be objects.
class AgentTypeReturner:
    def __init__(self):
        pass

    # Create an agent object based on the type
    def return_agent_type(self, name, actr_environment):
        if name == "Human":
            return None

        elif name == "Test":
            return Test(actr_environment).get_agent()

        elif name == "Random":
            return Random(actr_environment).get_agent()

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")

    # In pyactr, ACT-R functionality and regular arithmetic or logical functions are strictly divided.
    # The reason for that is a clearer understanding of the agents' behaviour.
    # This method will supervise the internal state of the agent and trigger specific events inside the agents class
    def handle_agents_internal_state(self, agent):
        name = agent.actr_agent_type_name
        goal = agent.actr_agent.goal

        if name == "Human":
            return None

        elif name == "Test":
            return Test.extending_actr(agent)

        elif name == "Random":
            return Random(None).extending_actr(agent)

        elif name == "SocialAgent":
            return SocialAgent.extending_actr(agent)

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")