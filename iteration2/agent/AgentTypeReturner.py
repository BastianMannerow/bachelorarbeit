from iteration2.agent.SocialAgent import SocialAgent

# Only responsible to avoid overloading the simulation. Returns the Agent object needed.
# TODO imported objects shouldn't be objects.
class AgentTypeReturner:
    def __init__(self):
        pass

    # Create an agent object based on the type
    def return_agent_type(self, name, actr_environment, agent_list, button_dictionary):
        if name == "Human":
            return None

        elif name == "SocialAgent":
            return SocialAgent(actr_environment).get_agent(agent_list, button_dictionary)

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")

    # Functionality, which extends ACT-R
    def handle_agents_internal_state(self, agent):
        name = agent.actr_agent_type_name

        if name == "Human":
            return None

        elif name == "SocialAgent":
            return SocialAgent(None).extending_actr(agent)

        else:
            raise ValueError(f"Unknown Agent .py Type: {name}")