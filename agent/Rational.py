import pyactr as actr

class Rational:
    def __init__(self, environ):
        self.environ = environ

    def get_agent(self):
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False, subsymbolic=True)
        agent.model_parameters["utility_noise"] = 1.0
        print(agent.model_parameters)

        # Chunk Types
        actr.chunktype("contribution", ("actor", "action", "opponent", "opponent_action", "payout_1", "payout_2"))

        # Initial Goal
        initial_goal = actr.makechunk(nameofchunk="select_contribute",  value="start")
        agent.goal.add(actr.makechunk(state=initial_goal))

        # Agent Model
        self.add_contribute_productions(agent)
        self.add_reward_productions(agent)
        self.add_punish_productions(agent)
        self.add_test_productions(agent)

        dm = agent.decmem  # creates variable for declarative memory (easier to access)
        dm.add(actr.chunkstring(string="""
            isa     countOrder
            first   1
            second  2
        """))
        dm.add(actr.chunkstring(string="""
            isa     countOrder
            first   2
            second  3
        """))
        dm.add(actr.chunkstring(string="""
            isa     countOrder
            first   3
            second  4
        """))
        dm.add(actr.chunkstring(string="""
            isa     countOrder
            first   4
            second  5
        """))

        return agent

    def add_contribute_productions(self, agent):
        agent.productionstring(name=f"select_contribute", string=f"""
                =g>
                isa     goal
                state   select_contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   contribute
                +manual>
                isa     _manual
                cmd     'press_key'
                key     C""",
                utility=0.9)

        agent.productionstring(name=f"select_contribute_two", string=f"""
                =g>
                isa     goal
                state   select_contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   contribute
                +manual>
                isa     _manual
                cmd     'press_key'
                key     F""",
                utility=0.0)

        agent.productionstring(name=f"contribute", string=f"""
                =g>
                isa     goal
                state   contribute
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   select_reward
                +manual>
                isa     _manual
                cmd     'press_key'
                key     1""")
    def add_reward_productions(self, agent):
        agent.productionstring(name=f"select_reward", string=f"""
                =g>
                isa     goal
                state   select_reward
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   reward
                +manual>
                isa     _manual
                cmd     'press_key'
                key     R""")

        agent.productionstring(name=f"reward", string=f"""
                =g>
                isa     goal
                state   reward
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   select_punish
                +manual>
                isa     _manual
                cmd     'press_key'
                key     Z""")

    def add_punish_productions(self, agent):
        agent.productionstring(name=f"select_punish", string=f"""
                =g>
                isa     goal
                state   select_punish
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   punish
                +manual>
                isa     _manual
                cmd     'press_key'
                key     P""")

        agent.productionstring(name=f"punish", string=f"""
                =g>
                isa     goal
                state   punish
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   test
                +manual>
                isa     _manual
                cmd     'press_key'
                key     Z""")

    def add_test_productions(self, agent):
        # First production to trigger the retrieval
        agent.productionstring(name="test", string="""
                =g>
                isa     goal
                state   test
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   retrieve_options
                +manual>
                isa     _manual
                cmd     'press_key'
                key     C""")

        # Retrieve specific contribution based on actor and action
        agent.productionstring(name="retrieve_specific_contribution_simple", string="""
            =g>
            isa     goal
            state   retrieve_options
            start =x
            ==>
            =g>
            isa     goal
            state   exit
            +retrieval>
            isa countOrder
            first   =x""")