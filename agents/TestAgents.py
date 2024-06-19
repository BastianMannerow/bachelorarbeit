import pyactr as actr

# chunk types
actr.chunktype("chunk", "value")
actr.chunktype("read", "state")
actr.chunktype("image", "img")
actr.makechunk(nameofchunk="start", typename="chunk", value="start")
actr.makechunk(nameofchunk="start", typename="chunk", value="start")
actr.makechunk(nameofchunk="attend_let", typename="chunk", value="attend_let")
actr.makechunk(nameofchunk="response", typename="chunk", value="response")
actr.makechunk(nameofchunk="done", typename="chunk", value="done")

# rules
encode_letter = """
        =g>
        isa     read
        state   start
        =visual>
        isa     _visual
        value  =letter
        ==>
        =g>
        isa     read
        state   respond
        +g2>
        isa     image
        img     =letter"""

respond_toA = """
        =g>
        isa     read
        state   respond
        =g2>
        isa     image
        img     A
        ?manual>
        state   free
        ==>
        =g>
        isa     read
        state   start
        =g2>
        isa     image
        img     empty
        +manual>
        isa     _manual
        cmd     'press_key'
        key     A"""

respond_toC = """
        =g>
        isa     read
        state   respond
        =g2>
        isa     image
        img     C
        ?manual>
        state   free
        ==>
        =g>
        isa     read
        state   done
        =g2>
        isa     image
        img     empty
        +manual>
        isa     _manual
        cmd     'press_key'
        key     C"""

dontrespond_toB = """
        =g>
        isa     read
        state   respond
        =g2>
        isa     image
        img     B
        ?manual>
        state   free
        ==>
        =g>
        isa     read
        state   start"""

dontrespond_toA = """
        =g>
        isa     read
        state   respond
        =g2>
        isa     image
        img     A
        ?manual>
        state   free
        ==>
        =g>
        isa     read
        state   start"""

respond_toB = """
        =g>
        isa     read
        state   respond
        =g2>
        isa     image
        img     B
        ?manual>
        state   free
        ==>
        =g>
        isa     read
        state   done
        =g2>
        isa     image
        img     empty
        +manual>
        isa     _manual
        cmd     'press_key'
        key     B"""


class Agent:
    """
    Create agent for environment. Delay specifies delay in creating imaginal buffer (called g2 here).
    delay is used for illustration, just to differentiate between agents.
    """

    def __init__(self, environment, delay):
        self.agent = actr.ACTRModel(environment=environment, motor_prepared=True)
        self.agent.goal.add(actr.chunkstring(name="reading", string="""
        isa     read
        state   start"""))
        self.agent.productionstring(name="encode_letter", string=encode_letter)
        g2 = self.agent.set_goal("g2")
        g2.delay = delay


def generate_agents(environ):
    # 2 agents with different speed of encoding goals
    magent1 = Agent(environ, delay=0.2).agent
    magent2 = Agent(environ, delay=0.4).agent

    # 2 agents differ in their rules - see the description at the start of this script
    magent1.productionstring(name="respond_toA", string=respond_toA)
    magent1.productionstring(name="respond_toC", string=respond_toC)
    magent1.productionstring(name="dontrespond_toB", string=dontrespond_toB)
    magent2.productionstring(name="dontrespond_toA", string=dontrespond_toA)
    magent2.productionstring(name="respond_toB", string=respond_toB)
    return magent1, magent2
