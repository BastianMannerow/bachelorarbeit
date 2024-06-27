import customPyACTR as actr

# Pressing W
def get_agent(environ, middleman):
    print(middleman)
    agent = actr.ACTRModel(environment=environ, motor_prepared=True, middleman=middleman)

    # Defining Chunks
    actr.chunktype("state", "state")
    actr.makechunk(nameofchunk="press_w", typename="state", state="press_w")

    # Initial Goal
    agent.goal.add(actr.chunkstring(name="pressing_w", string="""
        isa     state
        state   press_w"""))

    # Productions, which result in pressing "W"
    agent.productionstring(name="press_w_key", string="""
        =g>
        isa     state
        state   press_w
        ?manual>
        state   free
        ==>
        =g>
        isa     state
        state   press_w
        +manual>
        isa     _manual
        cmd     'press_key'
        key     w""")

    return agent