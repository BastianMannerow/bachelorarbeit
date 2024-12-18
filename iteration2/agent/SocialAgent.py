import re
from itertools import islice

import pyactr as actr
from colorama import Fore, Style


class SocialAgent:
    def __init__(self, environ):
        self.environ = environ
        self.goal_phases = ["priorityGoal", "secondaryGoal", "socialRegulatoryEffect", "egoismTowardsAltruism",
                            "outputs"]

    def get_agent(self, agent_list, button_dictionary):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # ACT-R configuration for this agent
        actr_agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        actr_agent.model_parameters[
            "utility_noise"] = 0.5  # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
        actr_agent.model_parameters["baselevel_learning"] = True  # Test, True gibt nach zweiten Durchlauf Error

        # Goal Chunk Types
        goal_phases = self.goal_phases
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        # Initial Goal
        initial_goal = actr.chunkstring(string=f"""
            isa     priorityGoal
            state   {goal_phases[0]}
        """)
        actr_agent.goal.add(initial_goal)
        print(Fore.YELLOW + f"Initial Goal: {actr_agent.goal}" + Style.RESET_ALL)

        # Imaginal
        imaginal = actr_agent.set_goal(name="imaginal", delay=0)

        # Agent Model
        self.add_choose_contribution_productions(actr_agent, goal_phases[0], goal_phases[1])
        # self.add_egoism_towards_altruism_productions(agent, goal_phases[3], goal_phases[4])
        # self.add_outputs_productions(agent, goal_phases[4], goal_phases[0], agent_list, button_dictionary)
        return actr_agent

    def add_choose_contribution_productions(self, actr_agent, phase, next_phase):
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                ~g>
                """)

    def extending_actr(self, agent):
        pass

    # Can be called externally
    def generate_contribution_productions(self, actr_agent, amount, phase, next_phase):
        # Adding productions dynamically based on amount
        for i in enumerate(amount, start=1):
            actr_agent.productionstring(name=f"{phase}_decide_to_contribute_{i}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideToContribute{i}
                    ==>
                    ~g>
                    """)