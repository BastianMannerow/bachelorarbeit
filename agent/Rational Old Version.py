import pyactr as actr

class Rational:
    def __init__(self, environ):
        self.environ = environ

    def get_agent(self):
        agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False, subsymbolic=True)
        agent.model_parameters["utility_noise"] = 1.0
        print(agent.model_parameters)


        # Initial Goal
        actr.chunktype("selectContribute", ("first_option", "last_option"))
        initial_goal = actr.chunkstring(string="""
            isa     selectContribute
            first_option    1
            last_option     10
        """)

        agent.goal.add(initial_goal)
        print(f"Initial Goal of the agent: {agent.goal}")

        # Agent Model
        self.add_contribute_productions(agent)
        return agent

    def add_contribute_productions(self, agent):
        agent.productionstring(name=f"select_contribute", string=f"""
                =g>
                isa     selectContribute
                ?manual>
                state   free
                ==>
                ~g>
                +manual>
                isa     _manual
                cmd     'press_key'
                key     C""",
                utility=0.5)