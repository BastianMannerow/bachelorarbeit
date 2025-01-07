import math
import re
from itertools import islice

import pyactr as actr
from colorama import Fore, Style

class SocialAgent:
    """
    A basic social agent, which utilizes a norm understanding for contributing to society.

    Attributes:
        this_agent_key (str): Self identification from AgentConstruct agent_dictionary
        other_agents_key_list (list): Identification from AgentConstruct agent_dictionary for other agents but self
        environ (Environment): pyactr environment
        actr_agent (ACTRModel): pyactr agent
        goal_phases (list): All goal states, which are independent of each other. Makes code more readable
        initial_goal (Chunk): If the agent crashes, it will start again with this goal
        dynamic_productions (dict): Stores dynamic calculated utility to not overwrite utility learning by reward
    """

    def __init__(self, environ):
        """
        Args:
            environ: pyactr environment (can be overwritten later)
        """
        self.this_agent_key = None
        self.other_agents_key_list = None

        self.environ = environ
        self.actr_agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        self.goal_phases = ["registerPunishment", "chooseContribution", "updateMentalModels", "decideOverPunishment", "manualOutputs"]
        self.initial_goal = actr.chunkstring(string=f"""
            isa     {self.goal_phases[0]}
            state   {self.goal_phases[0]}start
        """)

        self.dynamic_productions = {}

        # experiment configuration
        self.punishment = -2.0
        self.cognitive_distortion = 0.75

    # Building the agent
    def get_agent(self, agent_list, button_dictionary):
        """
        Builds an ACT-R agent

        Args:
            agent_list (list): Strings from the AgentConstruct dictionary to identify other agents
            button_dictionary (dict): needed to coordinate manual output productions for environment communication

        Returns:
            pyactr.ACTRAgent: The final actr_agent object from pyactr
        """
        self.this_agent_key = agent_list[0]
        self.other_agents_key_list = agent_list[1:]

        # ACT-R configuration for this agent
        actr_agent = self.actr_agent
        actr_agent.model_parameters[
            "utility_noise"] = 0.0  # 0.0 = only base utility
        actr_agent.model_parameters["baselevel_learning"] = True

        # Goal Chunk Types
        goal_phases = self.goal_phases
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        # Imaginal
        imaginal = actr_agent.set_goal(name="imaginal", delay=0)

        # Declarative Memory, initial mental models
        dd = {}
        for other_agent in self.other_agents_key_list:
            dd[actr.chunkstring(string=f"""
                isa mentalModelAgent{other_agent}
                reputation 5
                consistency True
                normConformity 0.5
            """)] = [0]

        actr_agent.set_decmem(dd)

        # Agent Model
        self.add_register_punishment_productions(actr_agent, goal_phases[0], goal_phases[1])
        self.add_choose_contribution_productions(actr_agent, goal_phases[1], goal_phases[2])
        self.add_update_mental_models_productions(actr_agent, goal_phases[2], goal_phases[3])
        self.add_decide_over_punishment_productions(actr_agent, goal_phases[3], goal_phases[4])
        self.add_outputs_productions(actr_agent, goal_phases[4], goal_phases[0], agent_list, button_dictionary)
        return actr_agent

    def add_register_punishment_productions(self, actr_agent, phase, next_phase):
        """
        Adds productions to the ACT-R agent

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
        """
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}RememberIfPunished
                """)

        actr_agent.productionstring(name=f"{phase}_remember_if_punished", string=f"""
                =g>
                isa     {phase}
                state   {phase}RememberIfPunished
                ==>
                =g>
                isa     {phase}
                state   {phase}CheckPunishment
                +retrieval>
                isa     socialRegulatoryEffects
                agent{self.this_agent_key}Consequence punishment
                """)

        actr_agent.productionstring(name=f"{phase}_remember_punishment", string=f"""
                =g>
                isa     {phase}
                state   {phase}CheckPunishment
                =retrieval>
                isa     socialRegulatoryEffects
                agent{self.this_agent_key}Consequence punishment
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """, reward=self.punishment)

        actr_agent.productionstring(name=f"{phase}_dont_remember_punishment", string=f"""
                =g>
                isa     {phase}
                state   {phase}CheckPunishment
                ?retrieval>
                state   error
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

    def add_update_mental_models_productions(self, actr_agent, phase, next_phase):
        """
        Adds productions to the ACT-R agent

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
        """
        # Dummy production to enter the loop
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}JudgeAgent{self.other_agents_key_list[0]}
                """)

        for i, other_agent in enumerate(self.other_agents_key_list):
            # Remember last action
            actr_agent.productionstring(name=f"{phase}_judge_agent_{other_agent}", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}JudgeAgent{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}CognitiveDistortion{other_agent}
                            +retrieval>
                            isa     lastRoundIntention
                            agent agent{other_agent}Classification
                            target {self.this_agent_key}
                            """)

            # Cognitive Distortion
            actr_agent.productionstring(name=f"{phase}_apply_cognitive_distortion_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    """, utility=self.cognitive_distortion)

            actr_agent.productionstring(name=f"{phase}_no_cognitive_distortion_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    """, utility=1 - self.cognitive_distortion)

            # Distinguish Motive
            actr_agent.productionstring(name=f"{phase}_distinguish_motive_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveDecision{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_internal_disposition_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveDecision{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_situative_factor_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveDecision{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    """)

            # Cognitive Algebra
            actr_agent.productionstring(name=f"{phase}_cognitive_algebra_{other_agent}", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}LoopHandling{other_agent}
                    """)

            # Dummy production to either continue with the next agent or to continue to the next phase, if all agents
            # were judged.
            if i < len(self.other_agents_key_list) - 1:
                actr_agent.productionstring(name=f"{phase}_{other_agent}_judgement_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}LoopHandling{other_agent}
                        ==>
                        =g>
                        isa     {phase}
                        state   {phase}JudgeAgent{self.other_agents_key_list[i + 1]}
                        """)

            else:
                actr_agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}LoopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   {next_phase}start
                        """)

    def add_choose_contribution_productions(self, actr_agent, phase, next_phase):
        """
        Adds productions to the ACT-R agent. Will be completed by add_dynamic_productions.

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
        """
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                ~g>
                """)

    def add_dynamic_productions(self, agent_construct):
        """
        Will be called externally to dynamically add productions while simulation is running

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """

        actr_agent = self.actr_agent
        phase = self.goal_phases[1]
        next_phase = self.goal_phases[3]
        amount = agent_construct.get_fortune()
        decision_count = min(amount, agent_construct.middleman.simulation.contribution_limit)
        num_decisions = math.floor(decision_count) + 1

        for i in range(num_decisions):
            production_name = f"{phase}_decide_to_contribute_{i}"

            # CRUCIAL! Skip if the production already exists. Otherwise, the utility will be overwritten!
            if production_name not in actr_agent.productions:
                production_string = f"""
                    =g>
                    isa     {phase}
                    state   {phase}DecideToContribute
                    ==>
                    =g>
                    isa     {next_phase}
                    state   {next_phase}start
                    """
                actr_agent.productionstring(name=production_name, string=production_string, utility=1.0)
                self.dynamic_productions[production_name] = 0.0 # Initially 0, because no utility was learned.
                print(Fore.GREEN + f"Produktion '{production_name}' hinzugefügt." + Style.RESET_ALL)

        productions = actr_agent.productions
        if agent_construct.print_actr_construct_trace:
            print(Fore.BLUE + f"{agent_construct.name} Productions: {productions.items()}" + Style.RESET_ALL)

    def add_decide_over_punishment_productions(self, actr_agent, phase, next_phase):
        """
        Adds productions to the ACT-R agent

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
        """

        # Dummy production to enter the loop
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}JudgeAgent{self.other_agents_key_list[0]}
                """)

        for i, other_agent in enumerate(self.other_agents_key_list):
            # Remember mental model
            actr_agent.productionstring(name=f"{phase}_judge_agent_{other_agent}", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}JudgeAgent{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishment{other_agent}
                            +retrieval>
                            isa     mentalModelAgent{other_agent}
                            """)

            # Deserves to be punished
            actr_agent.productionstring(name=f"{phase}_decide_punishment_{other_agent}", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishmentPositive{other_agent}
                            =retrieval>
                            isa     mentalModelAgent{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}LoopHandling{other_agent}
                            """)

            # Does not deserve to be punished
            actr_agent.productionstring(name=f"{phase}_decide_no_punishment_{other_agent}", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishmentNegative{other_agent}
                            =retrieval>
                            isa     mentalModelAgent{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}LoopHandling{other_agent}
                            """)

            # Dummy production to either continue with the next agent or to continue to the next phase, if all agents
            # were judged.
            if i < len(self.other_agents_key_list) - 1:
                actr_agent.productionstring(name=f"{phase}_{other_agent}_judgement_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}LoopHandling{other_agent}
                        ==>
                        =g>
                        isa     {phase}
                        state   {phase}JudgeAgent{self.other_agents_key_list[i + 1]}
                        """)

            else:
                actr_agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}LoopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   {next_phase}start
                        """)

    def add_outputs_productions(self, actr_agent, phase, next_phase, agent_list, button_dictionary):  # TODO
        """
        Manual output to execute decisions in the environment, the button dictionary contains the keys

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
            agent_list (list): Strings from the AgentConstruct dictionary to identify other agents
            button_dictionary (dict): needed to coordinate manual output productions for environment communication
        """

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

    # Extending ACT-R
    def extending_actr(self, agent_construct):
        """
        Functionality, which extends ACT-R
        In pyactr, ACT-R functionality and regular arithmetic or logical functions are strictly divided.
        The reason for that is a clearer understanding of the agents' behaviour.
        This method will supervise the internal state of the agent.

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
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
        if self.goal_phases[1] in goal:  # choose contribution
            if f"state= {self.goal_phases[1]}start" in goal:
                self.choose_contribution(agent_construct, self.goal_phases[1])
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_to_contribute" in event[2]:
                self.handle_contribution_decision(agent_construct, event[2])


        elif self.goal_phases[4] in goal:  # outputs

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_reward_nominations" in event[2]:
                self.do_reward_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_punishment_nominations" in event[2]:
                self.do_punishment_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_login_decision_matrix" in event[2]:
                self.login_decision_matrix(agent_construct)

    def choose_contribution(self, agent_construct, phase):
        """
        Calculates the utilities and changes goal to decide between contributions

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
            phase (String): The current phase, which is important for identifying the production name and goal state
        """

        productions = self.actr_agent.productions
        choices = agent_construct.current_choices
        my_choices = choices[self.this_agent_key]
        for choice in my_choices:
            choice_utility = self.apply_social_norm(agent_construct, choice)
            for prod_name, prod in productions.items():
                if prod_name == f"{phase}_decide_to_contribute_{choice['id']}":
                    # Check if utility learning happened to avoid overwriting it
                    old_utility = prod.utility
                    learned_utility = old_utility - self.dynamic_productions[prod_name] # negative when punished vv.

                    # Update the utility
                    productions[f"{phase}_decide_to_contribute_{choice['id']}"]["utility"] = choice_utility
                    prod.utility = choice_utility + learned_utility

                    if agent_construct.print_actr_construct_trace:
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                    # Save in the dictionary to avoid overwriting utility learning
                    self.dynamic_productions[prod_name] = choice_utility
        first_goal = next(iter(agent_construct.actr_agent.goals.values()))  # The second one is imaginal
        first_goal.add(actr.chunkstring(
            string=f"isa {phase} state {phase}DecideToContribute"))

        agent_construct.reset_simulation(actr.chunkstring(
            string=f"isa {phase} state {phase}DecideToContribute"))

    def handle_contribution_decision(self, agent_construct, event):
        """
        Handles event if a contribution was chosen

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
            event (String): Stepper event
        """

        match = re.search(r'_(\d+)$', event)
        if match:
            number = int(match.group(1))
            agent_key = self.this_agent_key
            choices_list = agent_construct.current_choices.get(agent_key, [])
            decision = next((entry for entry in choices_list if entry['id'] == number), None)
            agent_construct.decision_choice = decision
        else:
            raise ValueError("There was an error reading the contribution rule.")

    def apply_social_norm(self, agent_construct, choice):
        """
        Calculate the individual social norm for this agent

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
            choice (Dict): The choice and its consequences
        Returns:
            adjusted_choice_utility (Double): The calculated norm utility
        """

        if choice is None:
            return 0.0

        agent_dict = agent_construct.get_agent_dictionary()
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
        social_agreeableness = agent_construct.social_agreeableness
        adjusted_choice_utility = agent_value - social_agreeableness * abs(social_norm - agent_value)
        return adjusted_choice_utility

    # Manual Output
    def do_reward_nominations(self, agent_construct):
        """
        Manual Output

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
        agent_construct.middleman.nominate_for_reward(agent_construct)

    def do_punishment_nominations(self, agent_construct):
        """
        Manual Output

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
        agent_construct.middleman.nominate_for_punishment(agent_construct)

    def login_decision_matrix(self, agent_construct):
        """
        Manual Output

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
        if agent_construct.decision_choice:
            agent_construct.middleman.login_final_choice(agent_construct, agent_construct.decision_choice)
        agent_construct.decision_choice = None
