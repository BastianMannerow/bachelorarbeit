import re
from itertools import islice

import pyactr as actr

YELLOW = "\033[33m"
RESET = "\033[0m"

class SocialAgent:
    def __init__(self, environ):
        self.environ = environ
        self.goal_phases = ["priorityGoal", "secondaryGoal", "socialRegulatoryEffect", "egoismTowardsAltruism",
                            "outputs"]

    def get_agent(self, agent_list, button_dictionary):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # ACT-R configuration for this agent
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        agent.model_parameters[
            "utility_noise"] = 0.5  # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
        agent.model_parameters["baselevel_learning"] = True  # Test, True gibt nach zweiten Durchlauf Error

        # Goal Chunk Types
        goal_phases = self.goal_phases
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        # Initial Goal
        initial_goal = actr.chunkstring(string="""
            isa     priorityGoal
            state   priorityGoalstart
        """)
        agent.goal.add(initial_goal)
        print(f"{YELLOW}Initial Goal: {agent.goal}{RESET}")

        # Imaginal
        imaginal = agent.set_goal(name="imaginal", delay=0)

        # Declarative Memory
        dd = {}
        for i, participant in enumerate(agent_list):  # Possible Actions TODO
            dd[actr.chunkstring(string=f"\
                    isa possibleAction\
                    id a{i}\
                    agent{this_agent}Consequence neutral\
                    agent{participant}Consequence neutral")] = [0]

        # This is how to add agents decisions dynamically.
        """
        other_agents = ""
        for i, participant in enumerate(agent_list):  # Round 0
            other_agents = other_agents + f"agent{participant}Consequence neutral"
            if i < len(agent_list) - 1:
                other_agents = other_agents + "\n"

        dd[actr.chunkstring(string=f"\
                isa possibleAction\
                agent{this_agent}Consequence neutral\
                {other_agents}")] = [0]
        """
        for i, participant in enumerate(agent_list):  # Round 0
            dd[actr.chunkstring(string=f"\
                    isa lastRoundIntention\
                    id test\
                    agent {participant}\
                    target {this_agent}\
                    effect neutral")] = [0]
        agent.set_decmem(dd)

        # Agent Model
        # self.add_priority_goal_productions(agent, goal_phases[0], goal_phases[1], this_agent)
        # self.add_secondary_goal_productions(agent, goal_phases[1], goal_phases[2], agent_list, this_agent)
        # self.add_social_regulatory_effect_productions(agent, goal_phases[2], goal_phases[3], agent_list)
        # self.add_egoism_towards_altruism_productions(agent, goal_phases[3], goal_phases[4])
        # self.add_outputs_productions(agent, goal_phases[4], goal_phases[0], agent_list, button_dictionary)
        return agent

    def extending_actr(self, agent):
        pass