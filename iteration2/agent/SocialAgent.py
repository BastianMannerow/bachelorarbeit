import re
from itertools import islice

import pyactr as actr
from colorama import Fore, Style

class SocialAgent:
    def __init__(self, environ):
        self.environ = environ
        self.actr_agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        self.goal_phases = ["chooseContribution", "outputs"]
        self.initial_goal = actr.chunkstring(string=f"""
            isa     {self.goal_phases[0]}
            state   start
        """)

    def get_agent(self, agent_list, button_dictionary):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # ACT-R configuration for this agent
        actr_agent = self.actr_agent
        actr_agent.model_parameters[
            "utility_noise"] = 0.5  # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
        actr_agent.model_parameters["baselevel_learning"] = True  # Test, True gibt nach zweiten Durchlauf Error

        # Goal Chunk Types
        goal_phases = self.goal_phases
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        # Imaginal
        imaginal = actr_agent.set_goal(name="imaginal", delay=0)

        # Agent Model
        self.add_choose_contribution_productions(actr_agent, goal_phases[0], goal_phases[1])
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

    # Will be called externally to dynamically add productions while simulation is running
    def add_dynamic_productions(self, agent_construct):
        actr_agent = self.actr_agent
        phase = self.goal_phases[0]
        next_phase = self.goal_phases[1]
        amount = agent_construct.get_fortune()
        # Adding productions dynamically based on amount
        for i in range(amount + 1):
            actr_agent.productionstring(name=f"{phase}_decide_to_contribute_{i}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideToContribute{i}
                    ==>
                    ~g>
                    """)
        productions = actr_agent.productions
        if agent_construct.print_actr_construct_trace:
            print(Fore.BLUE + f"{agent_construct.name} Productions: {productions.items()}" + Style.RESET_ALL)

    # Functionality, which extends ACT-R
    # In pyactr, ACT-R functionality and regular arithmetic or logical functions are strictly divided.
    # The reason for that is a clearer understanding of the agents' behaviour.
    # This method will supervise the internal state of the agent.
    def extending_actr(self, agent_construct):
        goals = agent_construct.actr_agent.goals
        goal = str(next(iter(goals.values())))
        imaginal = str(next(islice(goals.values(), 1, 2)))
        event = agent_construct.simulation.current_event
        # Extract the dictionary code of the other agent. It's important to have consistent ACT-R production names
        if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2]:
            event_2 = event[2]
            start = event_2.find("_") + 1
            end = event_2.find("_", start)
            other_agent = event_2[start:end]
        else:
            other_agent = ""

        # Logging
        if agent_construct.print_actr_construct_trace:
            print(Fore.BLUE + f"{agent_construct.name} Goal: {goal}" + Style.RESET_ALL)
            print(Fore.BLUE + f"{agent_construct.name} Imaginal: {imaginal}" + Style.RESET_ALL)
            print(Fore.BLUE + f"{agent_construct.name} Focussed Agent: {other_agent}" + Style.RESET_ALL)

        # Sorted by phase
        if self.goal_phases[0] in goal:  # choose contribution
            if "state= start" in goal:
                self.choose_contribution(agent_construct)

        elif self.goal_phases[1] in goal:  # outputs
            pass

    # Calculates the utilities and changes goal to decide between contributions
    def choose_contribution(self, agent_construct):
        print("SUCCESS")