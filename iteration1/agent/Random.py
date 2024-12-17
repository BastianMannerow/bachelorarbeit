import pyactr as actr

class Random:
    def __init__(self, environ):
        self.environ = environ

    def get_agent(self):
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False, subsymbolic=True)
        agent.model_parameters["utility_noise"] = 0.5 # 1.0 verursacht ein rein nach Utility gehende Produktionsauswahl
        agent.model_parameters["baselevel_learning"] = True # Test, True  gibt nach zweiten Durchlauf Error
        print(agent.model_parameters)

        # Initial Goal
        actr.chunktype("selectContribute", "state")
        actr.chunktype("selectReward", "state")
        actr.chunktype("selectPunish", "state")

        #initial_goal = actr.chunkstring(string="""
        #    isa     selectContribute
        #    first_option    1
        #    last_option     10
        #""")

        initial_goal = actr.chunkstring(string="""
            isa     selectContribute
            state   start
        """)

        agent.goal.add(initial_goal)

        # Declarative Memory
        actr.chunktype("option", "type")
        actr.chunktype("testCoding", "code") # letter corresponds to each possibility

        dd = {actr.chunkstring(string="\
            isa option\
            type giver"): [0], actr.chunkstring(string="\
            isa option\
            type altruist"): [0],
            actr.chunkstring(string="\
            isa option\
            type test"): [0],
            actr.chunkstring(string="\
            isa option\
            type blabla"): [0]}
        agent.set_decmem(dd)
        print(agent.decmem)

        # Agent Model
        self.add_contribute_productions(agent)
        self.add_social_productions(agent)
        return agent

    def add_contribute_productions(self, agent):
        agent.productionstring(name=f"select_contribute", string=f"""
                =g>
                isa     selectContribute
                state   start
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   retrieve
                +manual>
                isa     _manual
                cmd     'press_key'
                key     C""")

        agent.productionstring(name=f"retrieve_options", string=f"""
                =g>
                isa     selectContribute
                state   retrieve
                ==>
                =g>
                isa     selectContribute
                state   contribute
                +retrieval>
                isa     option
                """)

    def add_social_productions(self, agent):
        # Self Positive
        social_egoist = 0.5
        social_neutral_profiteur = 0.7
        social_win_win = 0.7

        # Self Negative
        social_fatalist = 0.2
        social_self_destructive = 0.2
        social_altruist = 0.2

        # Self Neutral
        social_saboteur = 0.3
        social_spectator = 0.3
        social_giver = 0.3

        agent.productionstring(name=f"social_giver", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     A""",
                utility=social_giver)

        agent.productionstring(name=f"social_spectator", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     B""",
                utility=social_spectator)

        agent.productionstring(name=f"social_saboteur", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     C""",
                utility=social_saboteur)

        agent.productionstring(name=f"social_win_win", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     D""",
                utility=social_win_win)

        agent.productionstring(name=f"social_neutral_profiteur", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     E""",
                utility=social_neutral_profiteur)

        agent.productionstring(name=f"social_egoist", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     F""",
                utility=social_egoist)

        agent.productionstring(name=f"social_altruist", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     G""",
                utility=social_altruist)

        agent.productionstring(name=f"social_self_destructive", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     H""",
                utility=social_self_destructive)

        agent.productionstring(name=f"social_fatalist", string=f"""
                =g>
                isa     selectContribute
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     selectReward
                state   rew
                +manual>
                isa     _manual
                cmd     'press_key'
                key     I""",
                utility=social_fatalist)

        agent.productionstring(name=f"action_rew", string=f"""
                =g>
                isa     selectContribute
                state   rew
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   rewNow
                +manual>
                isa     _manual
                cmd     'press_key'
                key     R""")

        agent.productionstring(name=f"action_rewNone", string=f"""
                =g>
                isa     selectContribute
                state   rewNow
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   pun
                +manual>
                isa     _manual
                cmd     'press_key'
                key     Z""", utility=0.5)

        agent.productionstring(name=f"action_rewHim", string=f"""
                =g>
                isa     selectContribute
                state   rewNow
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   pun
                +manual>
                isa     _manual
                cmd     'press_key'
                key     B""", utility=0.5)

        agent.productionstring(name=f"action_pun", string=f"""
                =g>
                isa     selectContribute
                state   pun
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   punNow
                +manual>
                isa     _manual
                cmd     'press_key'
                key     P""")

        agent.productionstring(name=f"action_punNone", string=f"""
                =g>
                isa     selectContribute
                state   punNow
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   start
                +manual>
                isa     _manual
                cmd     'press_key'
                key     Z""", utility=0.5)

        agent.productionstring(name=f"action_punHim", string=f"""
                =g>
                isa     selectContribute
                state   punNow
                ?manual>
                state   free
                ==>
                =g>
                isa     selectContribute
                state   start
                +manual>
                isa     _manual
                cmd     'press_key'
                key     B""", utility=0.5)

    # Functionality, which extends ACT-R
    def extending_actr(self, agent):
        pass
