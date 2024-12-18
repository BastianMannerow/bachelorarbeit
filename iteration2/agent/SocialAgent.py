import math
import re
from itertools import islice

import pyactr as actr
from colorama import Fore, Style

class SocialAgent:
    def __init__(self, environ):
        self.this_agent_key = None
        self.other_agents_key_list = None

        self.environ = environ
        self.actr_agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        self.goal_phases = ["chooseContribution", "outputs"]
        self.initial_goal = actr.chunkstring(string=f"""
            isa     {self.goal_phases[0]}
            state   start
        """)

    # Builds an ACT-R agent
    def get_agent(self, agent_list, button_dictionary):
        self.this_agent_key = agent_list[0]
        self.other_agents_key_list = agent_list.remove(agent_list[0])

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
        self.add_outputs_productions(actr_agent, goal_phases[1], goal_phases[0], agent_list, button_dictionary)
        return actr_agent

    def add_choose_contribution_productions(self, actr_agent, phase, next_phase):
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                ~g>
                """)

    # Manual output to execute decisions in the environment, the button dictionary contains the keys
    def add_outputs_productions(self, actr_agent, phase, next_phase, agent_list, button_dictionary):  # TODO
        # Currently, the decmem will be read by python instead of using the manual output. This will be changed in the
        # future.
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}doRewardNominations
                """)

        actr_agent.productionstring(name=f"{phase}_do_reward_nominations", string=f"""
                =g>
                isa     {phase}
                state   {phase}doRewardNominations

                ==>
                =g>
                isa     {phase}
                state   {phase}doPunishmentNominations
                """)

        actr_agent.productionstring(name=f"{phase}_do_punishment_nominations", string=f"""
                =g>
                isa     {phase}
                state   {phase}doPunishmentNominations
                ==>
                =g>
                isa     {phase}
                state   {phase}loginDecisionMatrix
                """)

        actr_agent.productionstring(name=f"{phase}_login_decision_matrix", string=f"""
                =g>
                isa     {phase}
                state   {phase}loginDecisionMatrix
                ==>
                ~g>
                ~retrieval>
                """)

    # Will be called externally to dynamically add productions while simulation is running
    def add_dynamic_productions(self, agent_construct):
        actr_agent = self.actr_agent
        phase = self.goal_phases[0]
        next_phase = self.goal_phases[1]
        amount = agent_construct.get_fortune()
        # Adding productions dynamically based on amount
        for i in range(math.floor(amount) + 1):
            actr_agent.productionstring(name=f"{phase}_decide_to_contribute_{i}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DecideToContribute
                    ==>
                    =g>
                    isa     {next_phase}
                    state   {next_phase}start
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
                self.choose_contribution(agent_construct, self.goal_phases[0])
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_to_contribute" in event[2]:
                self.handle_contribution_decision(agent_construct, event[2])


        elif self.goal_phases[1] in goal:  # outputs

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_reward_nominations" in event[2]:
                self.do_reward_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_punishment_nominations" in event[2]:
                self.do_punishment_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_login_decision_matrix" in event[2]:
                self.login_decision_matrix(agent_construct)

    # Calculates the utilities and changes goal to decide between contributions
    def choose_contribution(self, agent_construct, phase):
        productions = self.actr_agent.productions
        choices = agent_construct.current_choices
        my_choices = choices[self.this_agent_key]
        for choice in my_choices:
            choice_utility = self.apply_social_norm(agent_construct, choice)
            for prod_name, prod in productions.items():
                if prod_name == f"{phase}_decide_to_contribute_{choice['id']}":
                    prod.utility = choice_utility
                    if agent_construct.print_actr_construct_trace:
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
        first_goal = next(iter(agent_construct.actr_agent.goals.values()))  # The second one is imaginal
        first_goal.add(actr.chunkstring(
            string=f"isa {phase} state {phase}DecideToContribute"))

    # Handles event if a contribution was chosen
    def handle_contribution_decision(self, agent_construct, event):
        match = re.search(r'_(\d+)$', event)
        if match:
            number = int(match.group(1))
            agent_key = self.this_agent_key
            choices_list = agent_construct.current_choices.get(agent_key, [])
            decision = next((entry for entry in choices_list if entry['id'] == number), None)
            agent_construct.decision_choice = decision
        else:
            raise ValueError("There was an error reading the contribution rule.")

    # Calculate the individual social norm for this agent
    def apply_social_norm(self, agent, choice):
        if choice is None:
            return 0.0

        agent_dict = agent.get_agent_dictionary()
        agent_name = self.this_agent_key
        total_weighted_sum = 0.0
        total_weight = 0.0

        for letter, value in choice.items():
            if letter == "id" or letter == agent_name:
                continue
            social_status = agent_dict[letter]["social_status"]
            total_weighted_sum += value * social_status
            total_weight += social_status

        social_norm = total_weighted_sum / total_weight if total_weight != 0 else 0.0
        agent_value = choice.get(agent_name, 0.0)
        social_agreeableness = agent.social_agreeableness
        adjusted_choice_utility = agent_value - social_agreeableness * abs(agent_value - social_norm)


        return adjusted_choice_utility

    # Manual Output
    def do_reward_nominations(self, agent_construct):
        agent_construct.middleman.nominate_for_reward(agent_construct)

    def do_punishment_nominations(self, agent_construct):
        agent_construct.middleman.nominate_for_punishment(agent_construct)

    def login_decision_matrix(self, agent_construct):
        agent_construct.middleman.login_final_choice(agent_construct, agent_construct.decision_choice)
