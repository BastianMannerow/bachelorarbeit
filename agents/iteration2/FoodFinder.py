import pyactr as actr

def get_agent(environ, letter):
    agent = actr.ACTRModel(environment=environ, motor_prepared=True)

    # Defining Chunks
    actr.chunktype("state", "state")
    actr.makechunk(nameofchunk=f"press_{letter}", typename="state", state=f"press_{letter}")

    # Initial Goal
    agent.goal.add(actr.chunkstring(name=f"pressing_{letter}", string=f"""
        isa     state
        state   press_{letter}"""))

    # Productions, which result in pressing the specified key
    agent.productionstring(name=f"press_{letter}_key", string=f"""
        =g>
        isa     state
        state   press_{letter}
        ?manual>
        state   free
        ==>
        =g>
        isa     state
        state   press_{letter}
        +manual>
        isa     _manual
        cmd     'press_key'
        key     {letter}""")

    return agent
