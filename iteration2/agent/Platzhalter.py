import copy
import re
from itertools import islice

import pyactr as actr

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
                    id test\
                    agent {participant}\
                    target {this_agent}\
                    effect neutral")] = [0]
        agent.set_decmem(dd)

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
                agent{this_agent}Consequence positive
                """)

        agent.productionstring(name=f"{phase}_positive_retrieval_success", string=f"""
                =g>
                isa     {phase}
                state   checkPositive
                =retrieval>
                isa     possibleAction
                agent{this_agent}Consequence positive
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
                agent{this_agent}Consequence neutral
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
                agent{this_agent}Consequence negative
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
                    state   {phase}decideOverDetriment{other_agent}
                    """)

            agent.productionstring(name=f"{phase}_{other_agent}_forgive_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideOverDetriment{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideOverDetriment{other_agent}
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
                    state   {phase}decideOverProfit{other_agent}
                    """)

            agent.productionstring(name=f"{phase}_{other_agent}_relativise_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideOverProfit{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}decideOverProfit{other_agent}
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
                        state   {phase}judgeAgent{agent_list[i + 1]}
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
                    state   {phase}rememberBehaviour{other_agent}
                    +retrieval>
                    isa     {phase}lastRoundIntention
                    agent   {other_agent}
                    """)

            agent.productionstring(name=f"{phase}_{other_agent}_remembered_last_action", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}rememberBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}evaluateBehaviour{other_agent}
                    """)

            # Decide if he deserves extra punishment
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_punishment", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgeNegativeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if he deserves extra punishment
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_no_extra_punishment", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgeNegativeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if he deserves extra reward
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_reward", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgePositiveBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if he deserves extra reward
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_no_extra_reward", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgePositiveBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

            # Decide if to remain neutral
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_nothing", string=f"""
                    =g>
                    isa     {phase}
                    state   {phase}judgeNeutralBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   {phase}loopHandling{other_agent}
                    """)  # TODO Assoziation bilden

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
                        state   {phase}judgeAgent{agent_list[i + 1]}
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

        # Only one option possible
        agent.productionstring(name=f"{phase}_choose_positive_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}ChoosePositiveStrategy
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_choose_neutral_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}ChooseNeutralStrategy
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_choose_negative_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}ChooseNegativeStrategy
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        # Two options possible
        agent.productionstring(name=f"{phase}_decide_positive_over_neutral_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}PositiveVSNeutral
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_decide_neutral_over_positive_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}PositiveVSNeutral
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_decide_positive_over_negative_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}PositiveVSNegative
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_decide_negative_over_positive_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}PositiveVSNegative
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_decide_neutral_over_negative_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}NegativeVSNeutral
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_decide_negative_over_neutral_strategy", string=f"""
                =g>
                isa     {phase}
                state   {phase}NegativeVSNeutral
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        # Three options possible
        agent.productionstring(name=f"{phase}_choose_positive_strategy_over_both_alternatives", string=f"""
                =g>
                isa     {phase}
                state   {phase}ThreeAlternatives
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_choose_neutral_strategy_over_both_alternatives", string=f"""
                =g>
                isa     {phase}
                state   {phase}ThreeAlternatives
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

        agent.productionstring(name=f"{phase}_choose_negative_strategy_over_both_alternatives", string=f"""
                =g>
                isa     {phase}
                state   {phase}ThreeAlternatives
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}start
                """)

    # Manual output to execute decisions in the environment, the button dictionary contains the keys
    def add_outputs_productions(self, agent, phase, next_phase, agent_list, button_dictionary):  # TODO
        # Currently, the decmem will be read by python instead of using the manual output. This will be changed in the
        # future.
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}start
                ==>
                =g>
                isa     {phase}
                state   {phase}doRewardNominations
                """)

        agent.productionstring(name=f"{phase}_do_reward_nominations", string=f"""
                =g>
                isa     {phase}
                state   {phase}doRewardNominations

                ==>
                =g>
                isa     {phase}
                state   {phase}doPunishmentNominations
                """)

        agent.productionstring(name=f"{phase}_do_punishment_nominations", string=f"""
                =g>
                isa     {phase}
                state   {phase}doPunishmentNominations
                ==>
                =g>
                isa     {phase}
                state   {phase}loginDecisionMatrix
                """)

        agent.productionstring(name=f"{phase}_login_decision_matrix", string=f"""
                =g>
                isa     {phase}
                state   {phase}loginDecisionMatrix
                ==>
                ~g>
                ~retrieval>
                """)

        # Manual Output Version
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
                self.direct_reciprocity(agent, event)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_forgive_detriment" in event[2]:
                self.forgive_detriment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_replicate_detriment" in event[2]:
                self.replicate_detriment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_relativise_profit" in event[2]:
                self.relativise_profit(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_replicate_profit" in event[2]:
                self.replicate_profit(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_remembered_neutral" in event[2]:
                self.remembered_neutral(agent, other_agent)

        elif self.goal_phases[2] in goal:  # social_regulatory_effect
            if f"state= {self.goal_phases[2]}evaluateBehaviour" in goal:
                self.social_regulatory_effect(agent, event)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_deserves_extra_punishment" in event[2]:
                self.deserves_extra_punishment(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_deserves_no_extra_punishment" in event[2]:
                self.deserves_extra_nothing(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_deserves_extra_reward" in event[2]:
                self.deserves_extra_reward(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_deserves_no_extra_reward" in event[2]:
                self.deserves_extra_nothing(agent, other_agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_deserves_extra_nothing" in event[2]:
                self.deserves_extra_nothing(agent, other_agent)

        elif self.goal_phases[3] in goal:  # egoism_towards_altruism
            if f"state= {self.goal_phases[3]}start" in goal:
                self.egoism_towards_altruism(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and f"_choose_positive_strategy" in event[2]:
                self.choose_positive_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_choose_neutral_strategy" in event[2]:
                self.choose_neutral_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_choose_negative_strategy" in event[2]:
                self.choose_negative_strategy(agent)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_positive_over_neutral_strategy" in event[2]:
                self.choose_positive_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_neutral_over_positive_strategy" in event[2]:
                self.choose_neutral_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_positive_over_negative_strategy" in event[2]:
                self.choose_positive_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_negative_over_positive_strategy" in event[2]:
                self.choose_negative_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_neutral_over_negative_strategy" in event[2]:
                self.choose_neutral_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_decide_negative_over_neutral_strategy" in event[2]:
                self.choose_negative_strategy(agent)

            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_choose_positive_strategy_over_both_alternatives" in event[2]:
                self.choose_positive_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_choose_neutral_strategy_over_both_alternatives" in event[2]:
                self.choose_neutral_strategy(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_choose_negative_strategy_over_both_alternatives" in event[2]:
                self.choose_negative_strategy(agent)

        elif self.goal_phases[4] in goal:  # outputs
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_reward_nominations" in event[2]:
                self.do_reward_nominations(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_do_punishment_nominations" in event[2]:
                self.do_punishment_nominations(agent)
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_login_decision_matrix" in event[2]:
                self.login_decision_matrix(agent)

    # (Direct Reciprocity) The agent needs to:
    # 1. Identify if the other agent caused detriment, profit or neutrality
    # 2. Calculate the likelihood of direct reciprocity TODO
    # 3. Change utilities and goal state accordingly
    def direct_reciprocity(self, agent, event):
        effect = None
        other_agent_id = None
        pattern = r"agent=\s*([A-Za-z]+).*effect=\s*([A-Za-z]+)"
        # Extract agent from the retrieval
        if event[1] == "retrieval" and "RETRIEVED" in event[2] and "lastRoundIntention":
            match = re.search(pattern, event[2])
            if match:
                other_agent_id = match.group(1)
                effect = match.group(2)
                print(f"other_agent_id: {other_agent_id}")
                print(f"effect: {effect}")
            else:
                return
        else:
            return

        # Calculate utilities
        match effect:
            case "neutral":
                print("Der Effekt ist neutral. Es passiert nichts.")
                return
            case "positive":
                print("Der Effekt ist positiv. Belohnung wird zugewiesen.")
                replicate_profit_utility = 0.5
                relativise_profit_utility = 0.5
            case "negative":
                replicate_detriment_utility = 0.5
                forgive_detriment_utility = 0.5
            case _:
                print("Unbekannter Effekt. Standardaktion wird ausgeführt.")
                return

        # Change goal state and utility accordingly
        productions = agent.actr_agent.productions
        match effect:
            case "neutral":
                return
            case "positive":
                first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                first_goal.add(
                    actr.chunkstring(string=f"isa {self.goal_phases[1]} state {self.goal_phases[1]}decideOverProfit{other_agent_id}"))
                for prod_name, prod in productions.items():
                    if prod_name == f"{self.goal_phases[1]}_{other_agent_id}_replicate_profit":
                        prod.utility = replicate_profit_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                    if prod_name == f"{self.goal_phases[1]}_{other_agent_id}_relativise_profit":
                        prod.utility = relativise_profit_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
            case "negative":
                first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                first_goal.add(
                    actr.chunkstring(string=f"isa {self.goal_phases[1]} state {self.goal_phases[1]}decideOverDetriment{other_agent_id}"))
                for prod_name, prod in productions.items():
                    if prod_name == f"{self.goal_phases[1]}_{other_agent_id}_replicate_detriment":
                        prod.utility = replicate_detriment_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                    if prod_name == f"{self.goal_phases[1]}_{other_agent_id}_forgive_detriment":
                        prod.utility = forgive_detriment_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
            case _:
                return

    # Add decision chunk to the decmem
    def forgive_detriment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    def replicate_detriment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect negative\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    def relativise_profit(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    def replicate_profit(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect positive\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    def remembered_neutral(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa subGoal\
            target {other_agent}\
            effect neutral\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    # (Social Regulatory Effect) The agent needs to:
    # 1. Identify if the other agent caused detriment, profit or neutrality
    # 2. Calculate the likelihood of a social regulatory effect TODO
    # 3. Change utilities and goal state accordingly
    def social_regulatory_effect(self, agent, event):
        effect = None
        other_agent_id = None
        pattern = r"agent=\s*([A-Za-z]+).*effect=\s*([A-Za-z]+)"
        # Extract agent from the retrieval
        if event[1] == "retrieval" and "RETRIEVED" in event[2] and "lastRoundIntention":
            match = re.search(pattern, event[2])
            if match:
                other_agent_id = match.group(1)
                effect = match.group(2)
                print(f"other_agent_id: {other_agent_id}")
                print(f"effect: {effect}")
            else:
                return
        else:
            return

        # Calculate utilities
        match effect:
            case "neutral":
                print("Der Effekt ist neutral. Es wird keine Utility berechnet.")
            case "positive":
                print("Der Effekt ist positiv. Belohnung wird zugewiesen.")
                extra_reward_utility = 0.5
                no_extra_reward = 0.5
            case "negative":
                extra_punishment_utility = 0.5
                no_extra_punishment_utility = 0.5
            case _:
                print("Unbekannter Effekt. Standardaktion wird ausgeführt.")
                return

        # Change goal state and utility accordingly
        productions = agent.actr_agent.productions
        match effect:
            case "neutral":
                first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                first_goal.add(
                    actr.chunkstring(
                        string=f"isa {self.goal_phases[2]} state {self.goal_phases[2]}judgeNeutralBehaviour{other_agent_id}"))
            case "positive":
                first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                first_goal.add(
                    actr.chunkstring(
                        string=f"isa {self.goal_phases[2]} state {self.goal_phases[2]}judgePositiveBehaviour{other_agent_id}"))
                for prod_name, prod in productions.items():
                    if prod_name == f"{self.goal_phases[2]}_deserves_extra_reward":
                        prod.utility = extra_reward_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                    if prod_name == f"{self.goal_phases[2]}_deserves_no_extra_reward":
                        prod.utility = no_extra_reward
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
            case "negative":
                first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                first_goal.add(
                    actr.chunkstring(
                        string=f"isa {self.goal_phases[2]} state {self.goal_phases[2]}judgeNegativeBehaviour{other_agent_id}"))
                for prod_name, prod in productions.items():
                    if prod_name == f"{self.goal_phases[2]}_deserves_extra_punishment":
                        prod.utility = extra_punishment_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                    if prod_name == f"{self.goal_phases[2]}_deserves_no_extra_punishment":
                        prod.utility = no_extra_punishment_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
            case _:
                return

    # Add decision chunk to the decmem
    def deserves_extra_punishment(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalPunishment\\"): [0]}
        agent.actr_agent.decmem.add(decision)

        # Temp solution for manual input TODO
        agent.extra_punishment_list.append(other_agent)

    def deserves_extra_reward(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalReward\\"): [0]}
        agent.actr_agent.decmem.add(decision)

        # Temp solution for manual input TODO
        agent.extra_reward_list.append(other_agent)

    def deserves_extra_nothing(self, agent, other_agent):
        decision = {actr.chunkstring(string=f"\
            isa extraTreatment\
            target {other_agent}\
            effect additionalNothing\\"): [0]}
        agent.actr_agent.decmem.add(decision)

    # (Egoism towards altriusm) The agent needs to:
    # 1. Check if the current priority goal aligns with enough secondary goals
    # 2. If yes, choose this strategy and switch goal
    # 3. If no, choose goal to lower the priority
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
            (numerical_choice, {k: v for k, v in classified_choice.items() if k != "id"})
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list({k: v for k, v in classified_choice.items() if k != "id"}.values())[0] == "positive"
        ]

        negative_choices = [
            (numerical_choice, {k: v for k, v in classified_choice.items() if k != "id"})
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list({k: v for k, v in classified_choice.items() if k != "id"}.values())[0] == "negative"
        ]

        neutral_choices = [
            (numerical_choice, {k: v for k, v in classified_choice.items() if k != "id"})
            for numerical_choice, classified_choice in zip(first_agent_numerical, first_agent_choices)
            if list({k: v for k, v in classified_choice.items() if k != "id"}.values())[0] == "neutral"
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

        # Save the best strategies
        agent.current_positive_choice = best_positive_strategy
        agent.current_neutral_choice = best_neutral_strategy
        agent.current_negative_choice = best_negative_strategy

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
            positive_meets = meets_alignment_condition(best_neutral_strategy)
            strategy_label = "Neutral"
            current_choice_utility = neutral_choice_utility

        if best_positive_strategy is None:
            print("No neutral strategy found. Falling back to negative strategy.")
            positive_meets = meets_alignment_condition(best_negative_strategy)
            strategy_label = "Negative"
            current_choice_utility = negative_choice_utility

        # Override the utilities in ACT-R
        productions = agent.actr_agent.productions

        def apply_all_utilities():
            first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
            first_goal.add(actr.chunkstring(string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}ThreeAlternatives"))
            for prod_name, prod in productions.items():
                if prod_name == f"{self.goal_phases[3]}_choose_positive_strategy_over_both_alternatives":
                    prod.utility = positive_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")
                if prod_name == f"{self.goal_phases[3]}_choose_neutral_strategy_over_both_alternatives":
                    prod.utility = neutral_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")
                if prod_name == f"{self.goal_phases[3]}_choose_negative_strategy_over_both_alternatives":
                    prod.utility = negative_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")

        def apply_positive_and_neutral():
            first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
            first_goal.add(actr.chunkstring(string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}PositiveVSNeutral"))
            for prod_name, prod in productions.items():
                if prod_name == f"{self.goal_phases[3]}_decide_positive_over_neutral_strategy":
                    prod.utility = positive_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")
                if prod_name == f"{self.goal_phases[3]}_decide_neutral_over_positive_strategy":
                    prod.utility = neutral_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")

        def apply_positive_and_negative():
            first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
            first_goal.add(actr.chunkstring(string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}PositiveVSNegative"))
            for prod_name, prod in productions.items():
                if prod_name == f"{self.goal_phases[3]}_decide_positive_over_negative_strategy":
                    prod.utility = positive_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")
                if prod_name == f"{self.goal_phases[3]}_decide_negative_over_positive_strategy":
                    prod.utility = negative_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")

        def apply_neutral_and_negative():
            first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
            first_goal.add(actr.chunkstring(string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}NegativeVSNeutral"))
            for prod_name, prod in productions.items():
                if prod_name == f"{self.goal_phases[3]}_decide_neutral_over_negative_strategy":
                    prod.utility = neutral_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")
                if prod_name == f"{self.goal_phases[3]}_decide_negative_over_neutral_strategy":
                    prod.utility = negative_choice_utility
                    print(f"Updated Utility for {prod_name}: {prod.utility}")

        def apply_single_utility():
            for prod_name, prod in productions.items():
                if strategy_label == "Positive":
                    if prod_name == f"{self.goal_phases[3]}_choose_positive_strategy":
                        first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                        first_goal.add(actr.chunkstring(
                            string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}ChoosePositiveStrategy"))
                        prod.utility = positive_choice_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                if strategy_label == "Neutral":
                    if prod_name == f"{self.goal_phases[3]}_choose_neutral_strategy":
                        first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                        first_goal.add(actr.chunkstring(
                            string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}ChooseNeutralStrategy"))
                        prod.utility = neutral_choice_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")
                if strategy_label == "Negative":
                    if prod_name == f"{self.goal_phases[3]}_choose_negative_strategy":
                        first_goal = next(iter(agent.actr_agent.goals.values()))  # The second one is imaginal
                        first_goal.add(actr.chunkstring(
                            string=f"isa {self.goal_phases[3]} state {self.goal_phases[3]}ChooseNegativeStrategy"))
                        prod.utility = negative_choice_utility
                        print(f"Updated Utility for {prod_name}: {prod.utility}")

        # Define truth table with methods
        truth_table = [
            (1, 1, 1,
             f"Positive ({positive_choice_utility}), Neutral ({neutral_choice_utility}), and Negative ({negative_choice_utility}) choice utilities will be applied.",
             lambda: apply_all_utilities()),
            (1, 1, 0,
             f"Positive ({positive_choice_utility}) and Neutral ({neutral_choice_utility}) choice utilities will be applied.",
             lambda: apply_positive_and_neutral()),
            (1, 0, 1,
             f"Positive ({positive_choice_utility}) and Negative ({negative_choice_utility}) choice utilities will be applied.",
             lambda: apply_positive_and_negative()),
            (1, 0, 0,
             f"{strategy_label} choice utility ({current_choice_utility}) will be applied.",
             lambda: apply_single_utility()),
            (0, 1, 1,
             f"Neutral ({neutral_choice_utility}) and Negative ({negative_choice_utility}) choice utilities will be applied.",
             lambda: apply_neutral_and_negative()),
            (0, 1, 0,
             f"Neutral choice utility ({neutral_choice_utility}) will be applied.",
             lambda: apply_single_utility()),
            (0, 0, 1,
             f"Negative choice utility ({negative_choice_utility}) will be applied.",
             lambda: apply_single_utility()),
            (0, 0, 0,
             f"{strategy_label} choice utility ({current_choice_utility}) will be applied.",
             lambda: apply_single_utility())  # Default case
        ]

        # Iterate through the truth table
        for Positive, Neutral, Negative, message, action in truth_table:
            if (positive_meets == Positive) and (neutral_meets == Neutral) and (negative_meets == Negative):
                print(message)
                action()
                break

    # Add decision chunk to the decmem
    def choose_positive_strategy(self, agent):  # TODO
        agent.decision_choice = "positive"

    def choose_neutral_strategy(self, agent):  # TODO
        agent.decision_choice = "neutral"

    def choose_negative_strategy(self, agent):  # TODO
        agent.decision_choice = "negative"

    # Calculate the individual social norm for this agent
    def apply_social_norm(self, agent, choice):
        if choice is None:
            return 0.0  # Return 0.0 if choice is None
        agent_dict = agent.get_agent_dictionary()

        # Calculate social_norm (arithmetic mean of weighted values)
        total_weighted_sum = 0
        total_weight = 0

        for letter, value in choice.items():
            if letter == "id":
                continue
            social_status = agent_dict[letter]["social_status"]
            total_weighted_sum += value * social_status
            total_weight += social_status
        social_norm = total_weighted_sum / total_weight if total_weight != 0 else 0

        # Calculate choice_utility
        choice_utility = 0
        for letter, value in choice.items():
            if letter == "id":
                continue
            social_status = agent_dict[letter]["social_status"]
            choice_utility += value * social_status

        # Adjust choice_utility using social_agreeableness
        social_agreeableness = agent.social_agreeableness
        choice_utility = choice_utility - social_agreeableness * abs(choice_utility - social_norm)
        return choice_utility

    # Manual Output
    def do_reward_nominations(self, agent):
        agent.middleman.nominate_for_reward(agent)

    def do_punishment_nominations(self, agent):
        agent.middleman.nominate_for_punishment(agent)

    def login_decision_matrix(self, agent):
        current_positive_choice = agent.current_positive_choice
        current_neutral_choice = agent.current_neutral_choice
        current_negative_choice = agent.current_negative_choice
        effect = agent.decision_choice
        match effect:
            case "neutral":
                agent.middleman.login_final_choice(agent, current_neutral_choice)
            case "positive":
                agent.middleman.login_final_choice(agent, current_positive_choice)
            case "negative":
                agent.middleman.login_final_choice(agent, current_negative_choice)
            case _:
                print("ERROR")
                return