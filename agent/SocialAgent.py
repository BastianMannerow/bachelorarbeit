import re
from itertools import islice

import pyactr as actr
import random

# An advanced agent with social cognition:
# Reciprocity 1 (Direct), 2 (Social Status), 3 (Social Norms) degree
class SocialAgent:
    def __init__(self, environ):
        self.environ = environ
        self.goal_phases = ["priorityGoal", "secondaryGoal", "socialRegulatoryEffect", "egoismTowardsAltruism",
                            "outputs"]

    # agent_list contains all other agents codes, which enables an iterative generation of productions, button dictionary contains the keys
    def get_agent(self, agent_list, button_dictionary):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # ACT-R configuration for this agent
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        agent.model_parameters["utility_noise"] = 0.5  # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
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
        print(f"Initial Goal of the agent: {agent.goal}")

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
                    id b{i}\
                    agent {participant}\
                    target {this_agent}\
                    effect neutral")] = [0]

        agent.set_decmem(dd)
        print(agent.decmem)

        # Agent Model
        self.add_priority_goal_productions(agent, goal_phases[0], goal_phases[1], this_agent)
        self.add_secondary_goal_productions(agent, goal_phases[1], goal_phases[2], agent_list, this_agent)
        self.add_social_regulatory_effect_productions(agent, goal_phases[2], goal_phases[3], agent_list)
        self.add_egoism_towards_altruism_productions(agent, goal_phases[3], goal_phases[4])
        self.add_outputs_productions(agent, goal_phases[4], goal_phases[0], agent_list, button_dictionary)
        return agent

    # Identify the maximum outcome strategy
    def add_priority_goal_productions(self, agent, phase, next_phase, this_agent):
        # Choose profit if possible
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   checkPositive
                +retrieval>
                isa     possibleAction
                agentAConsequence positive
                """)

        agent.productionstring(name=f"{phase}_positive_retrieval_success", string=f"""
                =g>
                isa     {phase}
                state   checkPositive
                =retrieval>
                isa     possibleAction
                agent{this_agent}Consequence   positive
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                +imaginal>
                isa     tempPrio
                agentAConsequence positive
                """)

        agent.productionstring(name=f"{phase}_positive_retrieval_failed", string=f"""
                =g>
                isa     {phase}
                state   checkPositive
                ?retrieval>
                state   error
                ==>
                =g>
                isa     {phase}
                state   retrieveNeutral
                """)

        # Choose neutral if possible
        agent.productionstring(name=f"{phase}_retrieve_neutral", string=f"""
                =g>
                isa     {phase}
                state   retrieveNeutral
                ==>
                =g>
                isa     {phase}
                state   checkNeutral
                +retrieval>
                isa     possibleAction
                agentAConsequence neutral
                """)

        agent.productionstring(name=f"{phase}_neutral_retrieval_success", string=f"""
                =g>
                isa     {phase}
                state   checkNeutral
                =retrieval>
                isa     possibleAction
                agent{this_agent}Consequence    neutral
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                +imaginal>
                isa     tempPrio
                agentAConsequence neutral
                """)

        agent.productionstring(name=f"{phase}_neutral_retrieval_failed", string=f"""
                =g>
                isa     {phase}
                state   checkNeutral
                ?retrieval>
                state   error
                ==>
                =g>
                isa     {phase}
                state   retrieveNegative
                """)

        # Choose detriment if possible
        agent.productionstring(name=f"{phase}_retrieve_negative", string=f"""
                =g>
                isa     {phase}
                state   retrieveNegative
                ==>
                =g>
                isa     {phase}
                state   checkNegative
                +retrieval>
                isa     possibleAction
                agentAConsequence negative
                """)

        agent.productionstring(name=f"{phase}_negative_retrieval_success", string=f"""
                =g>
                isa     {phase}
                state   checkNegative
                =retrieval>
                isa     possibleAction
                agent{this_agent}Consequence    negative
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                +imaginal>
                isa     tempPrio
                agentAConsequence negative
                """)

        # Loop to avoid errors caused by retrieval noise
        agent.productionstring(name=f"{phase}_negative_retrieval_failed", string=f"""
                =g>
                isa     {phase}
                state   checkNegative
                ?retrieval>
                state   error
                ==>
                =g>
                isa     {phase}
                state   {phase}start
                """)

    # How should other agents be treated based on direct reciprocity and reconsidered with social norms
    def add_secondary_goal_productions(self, agent, phase, next_phase, agent_list, this_agent):

        # Dummy production to enter the loop
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}judgeAgent{agent_list[0]}
                """)

        # Loop for each other agent
        for i, other_agent in enumerate(agent_list):
            # Remember the behaviour of the agent from last round
            agent.productionstring(name=f"{phase}_{other_agent}_remember_last_action", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgeAgent{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   checkBehaviour{other_agent}
                    +retrieval>
                    isa     lastRoundIntention
                    agent   {other_agent}
                    target  {this_agent}
                    """)

            # If he caused detriment, decide if to either forgive or to replicate his behaviour and build association
            agent.productionstring(name=f"{phase}_{other_agent}_remembered_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   checkBehaviour{other_agent}
                    =retrieval>
                    isa     lastRoundIntention
                    agent   {other_agent}
                    target  {this_agent}
                    effect  negative
                    ==>
                    =g>
                    isa     {phase}
                    state   decideOverDetriment{other_agent}
                    """)

            agent.productionstring(name=f"{phase}_{other_agent}_forgive_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverDetriment{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverDetriment{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # If he caused profit, decide if to either relativise or to replicate his behaviour and build association
            agent.productionstring(name=f"{phase}_{other_agent}_remembered_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   checkBehaviour{other_agent}
                    =retrieval>
                    isa     lastRoundIntention
                    agent   {other_agent}
                    target  {this_agent}
                    effect  positive
                    ==>
                    =g>
                    isa     {phase}
                    state   decideOverProfit{other_agent}
                    """)

            agent.productionstring(name=f"{phase}_{other_agent}_relativise_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverProfit{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverProfit{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # If he remained neutral, associate neutral at first. This can be changed later, if priority and
            # secondary strategies misalign
            agent.productionstring(name=f"{phase}_{other_agent}_remembered_neutral", string=f"""
                    =g>
                    isa     {phase}
                    state   checkBehaviour{other_agent}
                    =retrieval>
                    isa     lastRoundIntention
                    agent   {other_agent}
                    target  {this_agent}
                    effect  neutral
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Continue if the agent doesn't remember his behaviour
            agent.productionstring(name=f"{phase}_{other_agent}_remembered_failed", string=f"""
                    =g>
                    isa     {phase}
                    state   checkBehaviour{other_agent}
                    ?retrieval>
                    state   error
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)

            # Dummy production to either continue with the next agent or to continue to the next phase, if all agents
            # were judged.
            if i < len(agent_list) - 1:
                agent.productionstring(name=f"{phase}_{other_agent}_judgement_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {phase}
                        state   {phase}judgeAgent{agent_list[i+1]}
                        """)

            else:
                agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   {phase}loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   {next_phase}start
                        """)

    # Add extra punishment or reward based on social norms
    def add_social_regulatory_effect_productions(self, agent, phase, next_phase, agent_list):
        # Dummy production to enter the loop
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   judgeAgent{agent_list[0]}
                """)

        # Loop for each other agent
        for i, other_agent in enumerate(agent_list):
            # Remember the behaviour of the agent from last round
            agent.productionstring(name=f"{phase}_{other_agent}_remember_last_action", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeAgent{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    +retrieval>
                    isa     lastRoundIntention
                    agent   {other_agent}
                    """)

            # Decide if he deserves extra punishment
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_punishment", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if he deserves extra reward
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_reward", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if to remain neutral
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_nothing", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Dummy production to either continue with the next agent or to continue to the next phase, if all agents
            # were judged.
            if i < len(agent_list) - 1:
                agent.productionstring(name=f"{phase}_{other_agent}_judgement_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {phase}
                        state   judgeAgent{agent_list[i+1]}
                        """)

            else:
                agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   {next_phase}start
                        """)

    # Reconsider priority goal, if secondary goals don't align
    def add_egoism_towards_altruism_productions(self, agent, phase, next_phase):
        # Check if the current priority has an option, which aligns with secondary goals
        # This is a dummy production, which should never be fired. If Python fails to override the goal buffer,
        # the simulation will be canceled here.
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                ~g>
                """)

        # If the current priority doesn't have that option, look for a lower priority, which aligns with secondary goals
        # The production will loop back to start, which then will be reevaluated
        agent.productionstring(name=f"{phase}_evaluate_neutral_priority", string=f"""
                =g>
                isa     {phase}
                state   evaluateNeutralPriority
                ==>
                =g>
                isa     {phase}
                state   {phase}start
                +imaginal>
                isa     tempPrio
                agentAConsequence neutral
                """)

        agent.productionstring(name=f"{phase}_evaluate_negative_priority", string=f"""
                =g>
                isa     {phase}
                state   evaluateNegativePriority
                ==>
                =g>
                isa     {phase}
                state   {phase}start
                +imaginal>
                isa     tempPrio
                agentAConsequence negative
                """)

        # If an alternative was found, compare the original priority with this alternative
        agent.productionstring(name=f"{phase}_choose_original_strategy", string=f"""
                =g>
                isa     {phase}
                state   decideBetweenOriginalAndAlternativeStrategy
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)  # TODO ID der genauen gewählten Strategie muss klar sein

        agent.productionstring(name=f"{phase}_choose_alternative_strategy", string=f"""
                =g>
                isa     {phase}
                state   decideBetweenOriginalAndAlternativeStrategy
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)  # TODO ID der genauen gewählten Strategie muss klar sein

        # If no alternative was found, go with the first priority
        agent.productionstring(name=f"{phase}_no_lower_priority_aligned", string=f"""
                =g>
                isa     {phase}
                state   noLowerPriorityAligned
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)  # TODO ID der genauen gewählten Strategie muss klar sein

    # Manual output to execute decisions in the environment, the button dictionary contains the keys
    def add_outputs_productions(self, agent, phase, next_phase, agent_list, button_dictionary):  # TODO
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # Reward, punish or neither each other agent
        for other_agent in agent_list:
            # Remember if to reward
            # Press the Reward Button
            # Type in the other agents id
            # Remember if to punish
            # Press the Punish Button
            # Type in the other agents id
            pass

        # Press the Button to select a decision
        # Choose the decision
        # Press the Finish Button
        pass

    # Functionality, which extends ACT-R
    # In pyactr, ACT-R functionality and regular arithmetic or logical functions are strictly divided.
    # The reason for that is a clearer understanding of the agents' behaviour.
    # This method will supervise the internal state of the agent.
    def extending_actr(self, agent):
        goals = agent.actr_agent.goals
        goal = str(next(iter(goals.values())))
        imaginal = str(next(islice(goals.values(), 1, 2)))

        event = agent.simulation.current_event

        # Extract the dictionary code of the other agent. It's important to have consistent ACT-R production names
        if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2]:
            event_2 = event[2]
            start = event_2.find("_") + 1
            end = event_2.find("_", start)
            other_agent = event_2[start:end]
        else:
            other_agent = ""


        # Sorted by phase
        if self.goal_phases[1] in goal:  # secondary_goal
            if "state= checkBehaviour" in goal:
                self.direct_reciprocity(agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_forgive_detriment":
                self.forgive_detriment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_replicate_detriment":
                self.replicate_detriment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_relativise_profit":
                self.relativise_profit(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_replicate_profit":
                self.replicate_profit(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_remembered_neutral":
                self.remembered_neutral(agent, other_agent)

        elif self.goal_phases[2] in goal:  # social_regulatory_effect
            if "state= judgeBehaviour" in goal:
                self.social_regulatory_effect(agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_deserves_extra_punishment":
                self.deserves_extra_punishment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_deserves_extra_reward":
                self.deserves_extra_reward(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_deserves_extra_nothing":
                self.deserves_extra_nothing(agent, other_agent)

        elif self.goal_phases[3] in goal:  # egoism_towards_altruism
            if f"state= {self.goal_phases[3]}start" in goal:
                self.egoism_towards_altruism(agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_choose_original_strategy":
                self.choose_original_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_choose_alternative_strategy":
                self.choose_alternative_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE FIRED:" in event[2] and "_no_lower_priority_aligned":
                self.no_lower_priority_aligned(agent)

        elif self.goal_phases[4] in goal:  # outputs TODO
            pass

    # (Direct Reciprocity) The agent needs to:
    # 1. Identify if the other agent caused detriment, profit or neutrality
    # 2. Calculate the likelihood of direct reciprocity
    # 3. Change utilities and goal state accordingly
    def direct_reciprocity(self, agent):  # TODO
        pass

    # Add decision chunk to the decmem
    def forgive_detriment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral"): [0]}
        agent.actr_agent.decmem.add(decision)

    def replicate_detriment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect negative"): [0]}
        agent.actr_agent.decmem.add(decision)

    def relativise_profit(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral"): [0]}
        agent.actr_agent.decmem.add(decision)

    def replicate_profit(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect positive"): [0]}
        agent.actr_agent.decmem.add(decision)

    def remembered_neutral(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral"): [0]}
        agent.actr_agent.decmem.add(decision)

    # (Social Regulatory Effect) The agent needs to:
    # 1. Identify if the other agent caused detriment, profit or neutrality
    # 2. Calculate the likelihood of a social regulatory effect
    # 3. Change utilities and goal state accordingly
    def social_regulatory_effect(self, agent):  # TODO
        pass

    # Add decision chunk to the decmem
    def deserves_extra_punishment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalPunishment"): [0]}
        agent.actr_agent.decmem.add(decision)

    def deserves_extra_reward(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalReward"): [0]}
        agent.actr_agent.decmem.add(decision)

    def deserves_extra_nothing(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalNothing"): [0]}
        agent.actr_agent.decmem.add(decision)

    # (Egoism towards altriusm) The agent needs to:
    # 1. Check if the current priority goal aligns with enough secondary goals
    # 2. If yes, choose this strategy and switch goal
    # 3. If no, choose goal to lower the priority
    # 4. TODO Maybe it's better to not iteratively lower the standard, but rather calculate all 3 level utilities.
    def egoism_towards_altruism(self, agent):
        # Collect all possible strategies for the agent
        agent.choice_generator()
        choices = agent.current_choices
        classified_choices = agent.choice_classifier(choices)
        first_agent_key = list(classified_choices.keys())[0]
        first_agent_choices = classified_choices[first_agent_key]
        first_agent_numerical = choices[first_agent_key]

        # Group by classification
        positive_choices = [
            (numerical_choice, classified_choice)
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list(classified_choice.values())[0] == "positive"
        ]
        negative_choices = [
            (numerical_choice, classified_choice)
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list(classified_choice.values())[0] == "negative"
        ]
        neutral_choices = [
            (numerical_choice, classified_choice)
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list(classified_choice.values())[0] == "neutral"
        ]

        # Help function to determine the best strategy inside a category
        def get_best_strategy(choices):
            if not choices:
                return None

            # Prioritise max alignment
            max_alignments = 0
            best_choices = []
            for numerical_choice, classified_choice in choices:
                alignments = 0

                # sub goals inside the decmem
                for chunk in agent.actr_agent.decmem:
                    chunk_str = str(chunk)
                    if any(
                            f"subGoal(effect={effect}, target={target})" in chunk_str
                            for target, effect in classified_choice.items()
                    ):
                        alignments += 1

                if alignments > max_alignments:
                    max_alignments = alignments
                    best_choices = [(numerical_choice, classified_choice)]
                elif alignments == max_alignments:
                    best_choices.append((numerical_choice, classified_choice))

            # prioritise own profit, if sub goals are equal
            # Note: This shouldn't be the case in normal scenarios, if a game theoretical filter is applied before
            if len(best_choices) > 1:
                best_choices.sort(key=lambda x: x[0][first_agent_key], reverse=True)
            return best_choices[0], max_alignments

        # Determine the best strategies inside a category
        best_positive_strategy = get_best_strategy(positive_choices)
        best_negative_strategy = get_best_strategy(negative_choices)
        best_neutral_strategy = get_best_strategy(neutral_choices)

        # Results
        print(f"Results:")
        if best_positive_strategy:
            numerical, classified = best_positive_strategy[0]
            print(f"Best positive strategy: {numerical} with {best_positive_strategy[1]} alignments.")
            print(f"Classified Values: {classified}")
        else:
            print("No positive strategy found")

        if best_negative_strategy:
            numerical, classified = best_negative_strategy[0]
            print(f"Best negative strategy: {numerical} with {best_negative_strategy[1]} alignments.")
            print(f"Classified Values: {classified}")
        else:
            print("No negative strategy found")

        if best_neutral_strategy:
            numerical, classified = best_neutral_strategy[0]
            print(f"Best neutral strategy: {numerical} with {best_neutral_strategy[1]} alignments.")
            print(f"Classified Values: {classified}")
        else:
            print("No neutral strategy found")

        # Calculate the utilites
        positive_choice_utility = self.apply_social_norm(
            agent, best_positive_strategy[0][0] if best_positive_strategy else None
        )
        neutral_choice_utility = self.apply_social_norm(
            agent, best_neutral_strategy[0][0] if best_neutral_strategy else None
        )
        negative_choice_utility = self.apply_social_norm(
            agent, best_negative_strategy[0][0] if best_negative_strategy else None
        )

        # Set the goal
        # Helper function to check if a strategy meets the alignment condition
        def meets_alignment_condition(strategy):
            if strategy is None:
                return 0
            return 1 if strategy[1] > len(strategy[0][0]) / 2 else 0

        positive_meets = meets_alignment_condition(best_positive_strategy)
        neutral_meets = meets_alignment_condition(best_neutral_strategy)
        negative_meets = meets_alignment_condition(best_negative_strategy)

        # Initialize the strategy label and choice utility
        strategy_label = "Positive"
        current_choice_utility = positive_choice_utility

        # Fallback logic if positive or neutral strategy is None
        if best_positive_strategy is None:
            print("No positive strategy found. Falling back to neutral strategy.")
            best_positive_strategy = best_neutral_strategy
            positive_meets = meets_alignment_condition(best_positive_strategy)
            strategy_label = "Neutral"
            current_choice_utility = neutral_choice_utility

        if best_positive_strategy is None:
            print("No neutral strategy found. Falling back to negative strategy.")
            best_positive_strategy = best_negative_strategy
            positive_meets = meets_alignment_condition(best_positive_strategy)
            strategy_label = "Negative"
            current_choice_utility = negative_choice_utility

        # Define the truth table as a list of tuples (Positive, Neutral, Negative, Message, Consequence)
        truth_table = [
            (1, 1, 1,
             f"Positive ({positive_choice_utility}), Neutral ({neutral_choice_utility}), and Negative ({negative_choice_utility}) choice utilities will be applied."),
            (1, 1, 0,
             f"Positive ({positive_choice_utility}) and Neutral ({neutral_choice_utility}) choice utilities will be applied."),
            (1, 0, 1,
             f"Positive ({positive_choice_utility}) and Negative ({negative_choice_utility}) choice utilities will be applied."),
            (1, 0, 0, f"{strategy_label} choice utility ({current_choice_utility}) will be applied."),
            (0, 1, 1,
             f"Neutral ({neutral_choice_utility}) and Negative ({negative_choice_utility}) choice utilities will be applied."),
            (0, 1, 0, f"Neutral choice utility ({neutral_choice_utility}) will be applied."),
            (0, 0, 1, f"Negative choice utility ({negative_choice_utility}) will be applied."),
            (0, 0, 0, f"{strategy_label} choice utility ({current_choice_utility}) will be applied.")  # Default case
        ]

        # Match the truth table to determine the consequence
        for P, Neutral, Negative, message in truth_table:
            if (positive_meets == P) and (neutral_meets == Neutral) and (negative_meets == Negative):
                print(message)
                break

    # Add decision chunk to the decmem
    def choose_original_strategy(self, agent):  # TODO
        pass

    def choose_alternative_strategy(self, agent):  # TODO
        pass

    def no_lower_priority_aligned(self, agent):  # TODO
        pass

    # Calculate the individual social norm for this agent
    def apply_social_norm(self, agent, choice):
        if choice is None:
            return 0.0  # Return 0.0 if choice is None

        print(choice)

        # Access the agent dictionary
        agent_dict = agent.get_agent_dictionary()

        # Calculate social_norm (arithmetic mean of weighted values)
        total_weighted_sum = 0
        total_weight = 0

        for letter, value in choice.items():
            social_status = agent_dict[letter]["social_status"]  # Assumes key exists
            total_weighted_sum += value * social_status
            total_weight += social_status

        # Arithmetic mean calculation
        social_norm = total_weighted_sum / total_weight if total_weight != 0 else 0

        # Calculate choice_utility
        choice_utility = 0
        for letter, value in choice.items():
            social_status = agent_dict[letter]["social_status"]  # Assumes key exists
            choice_utility += value * social_status

        # Adjust choice_utility using social_agreeableness
        social_agreeableness = agent.social_agreeableness
        choice_utility = choice_utility - social_agreeableness * abs(choice_utility - social_norm)

        print(choice_utility)
        return choice_utility


