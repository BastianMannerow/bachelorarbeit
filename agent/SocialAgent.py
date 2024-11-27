import pyactr as actr

# An advanced agent with social cognition:
# Reciprocity 1 (Direct), 2 (Social Status), 3 (Social Norms) degree
class SocialAgent:
    def __init__(self, environ):
        self.environ = environ

    # agent_list contains all other agents codes, which enables an iterative generation of productions, button dictionary contains the keys
    def get_agent(self, agent_list, button_dictionary):
        # ACT-R configuration for this agent
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        agent.model_parameters["utility_noise"] = 0.5  # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
        agent.model_parameters["baselevel_learning"] = True  # Test, True  gibt nach zweiten Durchlauf Error
        print(agent.model_parameters)

        # Goal Chunk Types
        goal_phases = ["priorityGoal", "secondaryGoal", "socialRegulatoryEffect", "prioritySecondaryCombination",
                       "outputs"]
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        # Initial Goal
        initial_goal = actr.chunkstring(string="""
            isa     priorityGoal
            state   start
        """)
        agent.goal.add(initial_goal)
        print(f"Initial Goal of the agent: {agent.goal}")

        # Declarative Memory

        # Agent Model
        self.add_priority_goal_productions(agent, goal_phases[0], goal_phases[1])
        self.add_secondary_goal_productions(agent, goal_phases[1], goal_phases[2], agent_list)
        self.add_social_regulatory_effect_productions(agent, goal_phases[2], goal_phases[3], agent_list)
        self.add_priority_secondary_combination_productions(agent, goal_phases[3], goal_phases[4])
        self.add_outputs_productions(agent, goal_phases[4], goal_phases[0], agent_list, button_dictionary)
        return agent

    # Identify the maximum outcome strategy
    def add_priority_goal_productions(self, agent, phase, next_phase):
        # Choose profit if possible
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   start
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
                type   positive
                ==>
                =g>
                isa     {next_phase}
                state   start
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
                type   neutral
                ==>
                =g>
                isa     {next_phase}
                state   start
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
                type    negative
                ==>
                =g>
                isa     {next_phase}
                state   start
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
                state   start
                """)

    # How should other agents be treated based on direct reciprocity and reconsidered with social norms
    def add_secondary_goal_productions(self, agent, phase, next_phase, agent_list):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # Dummy production to enter the loop
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   start
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
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_detriment", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverDetriment{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

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
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

            agent.productionstring(name=f"{phase}_{other_agent}_replicate_profit", string=f"""
                    =g>
                    isa     {phase}
                    state   decideOverProfit{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

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
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

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
                    state   loopHandling{other_agent}
                    """)

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
                        state   judgeAgent{other_agent+1}
                        """)

            else:
                agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   start
                        """)

    # Add extra punishment or reward based on social norms
    def add_social_regulatory_effect_productions(self, agent, phase, next_phase, agent_list):
        this_agent = agent_list[0]
        agent_list.remove(this_agent)

        # Dummy production to enter the loop
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   start
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
                    """) # TODO Assoziation bilden

            # Decide if he deserves extra reward
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_reward", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden

            # Decide if to remain neutral
            agent.productionstring(name=f"{phase}_{other_agent}_deserves_extra_nothing", string=f"""
                    =g>
                    isa     {phase}
                    state   judgeBehaviour{other_agent}
                    ==>
                    =g>
                    isa     {phase}
                    state   loopHandling{other_agent}
                    """) # TODO Assoziation bilden


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
                        state   judgeAgent{other_agent+1}
                        """)

            else:
                agent.productionstring(name=f"{phase}_phase_completed", string=f"""
                        =g>
                        isa     {phase}
                        state   loopHandling{other_agent}
                        ==>
                        =g>
                        isa     {next_phase}
                        state   start
                        """)

    # Reconsider priority goal, if secondary goals don't align
    def add_priority_secondary_combination_productions(self, agent, phase, next_phase):
        # Check if the current priority has an option, which aligns with secondary goals
        # This is a dummy production, which should never be fired. If Python fails to override the goal buffer,
        # the simulation will be canceled here.
        agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   start
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
                state   start
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
                state   start
                +imaginal>
                isa     tempPrio
                agentAConsequence negative
                """)

        # If an alternative was found, compare the original priority with this alternative
        agent.productionstring(name=f"{phase}_choose_original_strategy", string=f"""
                =g>
                isa     {phase}
                state   chooseOriginalStrategy
                ==>
                =g>
                isa     {next_phase}
                state   start
                """) # TODO ID der genauen gewählten Strategie muss klar sein

        agent.productionstring(name=f"{phase}_choose_alternative_strategy", string=f"""
                =g>
                isa     {phase}
                state   chooseAlternativeStrategy
                ==>
                =g>
                isa     {next_phase}
                state   start
                """) # TODO ID der genauen gewählten Strategie muss klar sein

        # If no alternative was found, go with the first priority
        agent.productionstring(name=f"{phase}_no_lower_priority_aligned", string=f"""
                =g>
                isa     {phase}
                state   noLowerPriorityAligned
                ==>
                =g>
                isa     {next_phase}
                state   start
                """) # TODO ID der genauen gewählten Strategie muss klar sein

    # Manual output to execute decisions in the environment, the button dictionary contains the keys
    def add_outputs_productions(self, agent, phase, next_phase, agent_list, button_dictionary):
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
    def extending_actr(self, agent):
        pass
