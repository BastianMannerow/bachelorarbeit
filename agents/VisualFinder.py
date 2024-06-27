import customPyACTR as actr

# Pressing A
def get_agent(environ, middleman):
    agent = actr.ACTRModel(environment=environ, motor_prepared=True, middleman=middleman)

    # Defining Chunks
    actr.chunktype("state", "state")
    actr.chunktype("image", "img")
    actr.makechunk(nameofchunk="find_A", typename="state", state="find_A")
    actr.makechunk(nameofchunk="press_A", typename="state", state="press_A")

    # Initial Goal
    agent.goal.add(actr.chunkstring(name="finding_A", string="""
        isa     state
        state   find_A"""))

    # Production to find A
    agent.productionstring(name="encode_A", string="""
        =g>
        isa     state
        state   find_A
        =visual_location>
        isa     _visuallocation
        value   A
        ==>
        =g>
        isa     state
        state   press_A
        +visual>
        isa     _visual
        value   A""")

    # Production to focus on A
    agent.productionstring(name="focus_on_A", string="""
        =g>
        isa     state
        state   press_A
        =visual>
        isa     _visual
        value   A
        ?visual_location>
        isa     _visuallocation
        value   A
        ==>
        +visual>
        isa     _visual
        cmd     move_attention
        screen_pos =visual_location""")

    # Production to press A
    agent.productionstring(name="press_A_key", string="""
        =g>
        isa     state
        state   press_A
        =visual>
        isa     _visual
        value   A
        ?manual>
        state   free
        ==>
        =g>
        isa     state
        state   done
        +manual>
        isa     _manual
        cmd     'press_key'
        key     A""")

    return agent
