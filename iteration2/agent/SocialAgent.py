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
        dynamic_productions (dict): Stores dynamic calcula+-----ted utility to not overwrite utility learning by reward
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
        self.goal_phases = ["registerPunishment", "updateMentalModels", "decideOverPunishment", "chooseContribution", "manualOutputs"]
        self.initial_goal = actr.chunkstring(string=f"""
            isa     {self.goal_phases[0]}
            state   {self.goal_phases[0]}start
        """)

        # ACT-R extending memory
        self.dynamic_productions = {}
        self.impressions = {}
        self.potential_impression = ""
        self.score = {}

        # experiment configuration
        self.punishment = -2.0
        self.positive_cognitive_distortion = 0.33
        self.negative_cognitive_distortion = 0.66

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
        self.add_update_mental_models_productions(actr_agent, goal_phases[1], goal_phases[2])
        self.add_decide_over_punishment_productions(actr_agent, goal_phases[2], goal_phases[3])
        self.add_choose_contribution_productions(actr_agent, goal_phases[3], goal_phases[4])
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
            actr_agent.productionstring(name=f"{phase}_{other_agent}_judge_agent", string=f"""
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
            actr_agent.productionstring(name=f"{phase}_{other_agent}_apply_positive_cognitive_distortion", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}PositiveCognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    =imaginal>
                    isa impression
                    impression positive
                    """, utility=self.positive_cognitive_distortion)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_no_positive_cognitive_distortion", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}PositiveCognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    """, utility=1 - self.positive_cognitive_distortion)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_apply_negative_cognitive_distortion", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}NegativeCognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    =imaginal>
                    isa impression
                    impression negative
                    """, utility=self.negative_cognitive_distortion)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_no_negative_cognitive_distortion", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}NegativeCognitiveDistortion{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    """, utility=1 - self.negative_cognitive_distortion)

            # Distinguish Motive
            actr_agent.productionstring(name=f"{phase}_{other_agent}_distinguish_motive", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    ?imaginal>
                    state   free
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveDecision{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_cognitive_distortion_blocking", string=f"""
                    =imaginal>
                    isa impression
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotive{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveDecision{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_internal_disposition", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveInternalDecision{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    =imaginal>
                    isa impression
                    """)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_situative_factor", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveSituativeDecision{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}LoopHandling{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_unknown_factor", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}DistinguishMotiveUnknownDecision{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}LoopHandling{other_agent}
                    """)

            # Cognitive Algebra
            actr_agent.productionstring(name=f"{phase}_{other_agent}_cognitive_algebra", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}CognitiveAlgebra{other_agent}
                    =imaginal>
                    isa impression
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}resolveCognitiveDissonance{other_agent}
                    """)

            actr_agent.productionstring(name=f"{phase}_{other_agent}_resolved_cognitive_dissonance", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}resolveCognitiveDissonance{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}LoopHandling{other_agent}
                    ~imaginal>
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
        phase = self.goal_phases[3]
        next_phase = self.goal_phases[4]
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
            actr_agent.productionstring(name=f"{phase}_{other_agent}_judge_agent", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}JudgeAgent{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishment{other_agent}
                            """)

            # Deserves to be punished
            actr_agent.productionstring(name=f"{phase}_{other_agent}_decide_punishment", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishmentPositive{other_agent}
                            ==>
                            =g>
                            isa     {phase}
                            state   {phase}LoopHandling{other_agent}
                            """)

            # Does not deserve to be punished
            actr_agent.productionstring(name=f"{phase}_{other_agent}_decide_no_punishment", string=f"""
                            =g>
                            isa     {phase}
                            state   {phase}DecideOverPunishmentNegative{other_agent}
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
        if event[1] == "PROCEDURAL" and ("RULE FIRED:" in event[2] or "RULE SELECTED" in event[2]):
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
        if self.goal_phases[1] in goal:  # update mental models
            if f"state= {self.goal_phases[1]}CognitiveDistortion" in goal:
                self.apply_cognitive_distortion(agent_construct, other_agent, self.goal_phases[1], self.goal_phases[3])
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_apply_positive_cognitive_distortion" in event[2]:
                self.add_impression(other_agent, "positive")
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_apply_negative_cognitive_distortion" in event[2]:
                self.add_impression(other_agent, "negative")
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_distinguish_motive" in event[2]:
                self.distinguish_motive(agent_construct, other_agent, self.goal_phases[1], self.goal_phases[2])
            if f"state= {self.goal_phases[1]}CognitiveAlgebra" in goal:
                self.cognitive_algebra(agent_construct, other_agent)

        elif self.goal_phases[2] in goal:  # punishment
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_judge_agent" in event[2]:
                self.punishment_decision(agent_construct, other_agent, self.goal_phases[2])

        elif self.goal_phases[3] in goal:  # choose contribution
            if f"state= {self.goal_phases[3]}start" in goal:
                self.choose_contribution(agent_construct, self.goal_phases[3])
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_to_contribute" in event[2]:
                self.handle_contribution_decision(agent_construct, event[2])

        elif self.goal_phases[4] in goal:  # outputs

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_reward_nominations" in event[2]:
                self.do_reward_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_punishment_nominations" in event[2]:
                self.do_punishment_nominations(agent_construct)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_login_decision_matrix" in event[2]:
                self.login_decision_matrix(agent_construct)

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

    def add_impression(self, agent_name, impression):
        if agent_name not in self.impressions:
            self.impressions[agent_name] = []
        self.impressions[agent_name].append(impression)

    def add_score(self, agent_name, score):
        if agent_name not in self.score:
            self.score[agent_name] = [score]
        else:
            self.score[agent_name].append(score)

    # Mental Models
    def apply_cognitive_distortion(self, agent_construct, other_agent, phase, contribution_phase):
        first_goal = next(iter(agent_construct.actr_agent.goals.values()))
        # Extrahiere betrachtetes Verhalten
        if other_agent == "": # Keep going with contribution
            first_goal.add(actr.chunkstring(
                string=f"isa {contribution_phase} state {contribution_phase}start"))
            return
        other_agent_construct = agent_construct.replace_letters_with_agents([other_agent])[0]
        last_round_information = agent_construct.middleman.simulation.history.get_last_round()
        if not last_round_information or last_round_information.get('label') == "Runde0": # keep going with contribution
            first_goal.add(actr.chunkstring(
                string=f"isa {contribution_phase} state {contribution_phase}start"))
            return
        agent_decisions = last_round_information['agent_decisions'].get(other_agent_construct, None)
        selected_option = agent_decisions.get("selected_option", None)
        selected_amount = selected_option.get("id", None)

        # Gette Utility der Contribution der letzten Runde Zentroid bilden und 20% Toleranzbereich
        amount = len(self.dynamic_productions)
        tolerance = amount*0.2
        max_prod_name = max(self.dynamic_productions, key=self.dynamic_productions.get)
        max_utility = self.dynamic_productions[max_prod_name]
        max_prod_id = int(max_prod_name.split('_')[-1])

        # Verhalten des betrachteten Agenten positiv oder negativ klassifizieren
        if (max_prod_id - tolerance) <= selected_amount <= (max_prod_id + tolerance):  # neutral so skip to distinguish
            self.potential_impression = "neutral"
            first_goal.add(actr.chunkstring(
                string=f"isa {phase} state {phase}DistinguishMotive{other_agent}"))
        elif selected_amount < (max_prod_id - tolerance):  # negative
            self.potential_impression = "negative"
            first_goal.add(actr.chunkstring(
                string=f"isa {phase} state {phase}NegativeCognitiveDistortion{other_agent}"))
        else:  # positive
            self.potential_impression = "positive"
            first_goal.add(actr.chunkstring(
                string=f"isa {phase} state {phase}PositiveCognitiveDistortion{other_agent}"))

    def distinguish_motive(self, agent_construct, other_agent, phase, punishment_phase):
        # Falls Imaginal nicht leer war sollte der State übersprungen werden in Produktionen
        # ------ Konsistenzermittlung ------
        # Gette Vermögen, also Beitragsmöglichkeiten des Agenten aus der letzten Runde
        other_agent_construct = agent_construct.replace_letters_with_agents([other_agent])[0]
        last_round_information = agent_construct.middleman.simulation.history.get_last_round()
        last_round_fortune = agent_construct.middleman.simulation.history.get_lastlast_round()['fortunes'].get(other_agent_construct, None)
        agent_decisions = last_round_information['agent_decisions'].get(other_agent_construct, None)
        selected_option = agent_decisions.get("selected_option", None)
        selected_amount = selected_option.get("id", None)
        # Gette alle Beiträge, die der Agent getätigt hat mit der Toleranzabweichung einer Einheit
        whole_history = agent_construct.middleman.simulation.history.get_history()

        previous_round = None
        compare_values = []
        for i in range(len(whole_history) - 2): # Muss immer die Runde davor sein, weil ja in der Runde der Endbetrag gelogged wird
            if previous_round is not None:
                old_fortune = previous_round['fortunes'].get(other_agent_construct, None)
                if abs(old_fortune - last_round_fortune) <= 1:
                    past_decision = previous_round['agent_decisions'].get(other_agent_construct, None)
                    past_selected_option = past_decision.get("selected_option", None)
                    past_selected_amount = past_selected_option.get("id", None)
                    compare_values.append(past_selected_amount)
            previous_round = whole_history[i]

        # Standardabweichungsberechnung für k = 2
        k = 2
        n = len(compare_values)
        if n == 0: # Falls es keine Vergleichswerte gibt, ist es inkonsistent
            is_inconsistent = True

        else:
            mean = sum(compare_values) / n
            variance = sum((x - mean) ** 2 for x in compare_values) / n
            sigma = math.sqrt(variance)

            # Abweichung prüfen
            deviation = abs(selected_amount - mean)
            is_inconsistent = deviation > k * sigma

            # Ergebnisse ausgeben
            print(f"Abweichung: {deviation}")
            print(f"Arithmetisches Mittel: {mean}")
            print(f"Standardabweichung: {sigma}")
        print(f"Ist inkonsistent: {is_inconsistent}")


        # ------ Konsensusermittlung ------
        # Gette alle Beitragsoptionen der letzten Runde von dem betrachteten Agenten
        past_possible_contribution_options = agent_decisions["options"]

        # Wende die soziale Norm Formel auf alle an
        utility_list = []
        for choice in past_possible_contribution_options:
            utility = (self.apply_social_norm(agent_construct, choice), choice)
            utility_list.append(utility)

        # Prüfe die Utilities auf Standardabweichung
        selected_utility = None
        compare_values = []

        for utility, choice in utility_list:
            if choice == selected_option:
                selected_utility = utility
            else:
                compare_values.append(utility)

        # Überprüfung, ob Vergleichswerte existieren
        n = len(compare_values)
        print(f"TEST {compare_values}")

        if n == 0:  # Falls es keine Vergleichswerte gibt, ist es inkonsistent
            is_inconsistent = True
        else:
            # Berechnungen für Mittelwert und Standardabweichung
            mean = sum(compare_values) / n
            variance = sum((x - mean) ** 2 for x in compare_values) / n
            sigma = math.sqrt(variance)

            # Abweichung prüfen
            deviation = abs(selected_utility - mean)
            is_not_consensus = deviation > k * sigma

            # Ergebnisse ausgeben
            print(f"Abweichung: {deviation}")
            print(f"Arithmetisches Mittel: {mean}")
            print(f"Standardabweichung: {sigma}")

        print(f"Ist nicht Consensus: {is_not_consensus}")

        # ------ Tabellenüberprüfung ------
        # Auf intern oder extern oder unklar festlegen
        # Sollte es intern sein, geht es weiter mit der kognitiven Algebra. Sonst geht es zum Punishment
        first_goal = next(iter(agent_construct.actr_agent.goals.values()))
        if (not is_inconsistent and not is_not_consensus) or (is_inconsistent and not is_not_consensus):
            print("Extern")
            first_goal.add(actr.chunkstring(
                string=f"isa {punishment_phase} state {phase}DistinguishMotiveSituativeDecision{other_agent}"))

        elif not is_inconsistent and is_not_consensus:
            print("Intern")
            self.add_impression(other_agent, self.potential_impression)
            first_goal.add(actr.chunkstring(
                string=f"isa {phase} state {phase}DistinguishMotiveInternalDecision{other_agent}"))

        else:
            print("Unknown")
            first_goal.add(actr.chunkstring(
                string=f"isa {punishment_phase} state {phase}DistinguishMotiveUnknownDecision{other_agent}"))

    def cognitive_algebra(self, other_agent):
        # Imaginal laden
        impressions = self.impressions.get(other_agent) # der erste ist der erste und der letzte der aktuelle eindruck

        # Auf Intervall abbilden
        score_map = {"negative": 1, "neutral": 5, "positive": 10}
        E = [score_map[imp] for imp in impressions]

        # Alle Eindrücke aus self kriegen, dabei auch ersten Eidnruck ggf. speichern und laden
        N = len(E)
        k = 2
        w_primacy = N / k

        # Eindrücke verrechnen durch kognitive Algebra Formel
        if N > 1:
            attribution = w_primacy * E[0] + sum(E[1:]) / (N - 1)
        else:
            attribution = E[0]  # Nur ein Eindruck vorhanden, daher wird nur dieser berücksichtigt
        print(attribution)
        # mental Model Chunk aktualisieren
        self.add_score(other_agent, attribution)

    # Punishment decision
    def punishment_decision(self, agent_construct, other_agent, phase):
        # Gette Mental Model Chunk
        scores = self.score.get(other_agent)
        first_goal = next(iter(agent_construct.actr_agent.goals.values()))

        first_goal.add(actr.chunkstring(
            string=f"isa {phase} state {phase}DecideOverPunishmentNegative{other_agent}"))

        if scores and len(scores) > 0:
            current_score = scores[-1]
            if current_score < 4 and self.potential_impression == "negative":
                other_agent_construct = agent_construct.replace_letters_with_agents([other_agent])[0]
                self.do_punishment_nominations(other_agent_construct)
                first_goal.add(actr.chunkstring(
                    string=f"isa {phase} state {phase}DecideOverPunishmentPositive{other_agent}"))


    # Contribution
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
        self.potential_impression = ""
        if agent_construct.decision_choice:
            agent_construct.middleman.login_final_choice(agent_construct, agent_construct.decision_choice)
        agent_construct.decision_choice = None
