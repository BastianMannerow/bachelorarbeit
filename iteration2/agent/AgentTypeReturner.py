from iteration2.agent.SocialAgent import SocialAgent

# Only responsible to avoid overloading the simulation. Returns the Agent object needed.
class AgentTypeReturner:
    def __init__(self):
        pass

    # Create an agent object based on the type
    def return_agent_type(self, name, actr_environment, initial_punishment_factor):
        if name == "Human":
            return None

        elif name == "SocialAgent":
            return SocialAgent(actr_environment, initial_punishment_factor)

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")