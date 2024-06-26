# Pressing W

import customPyACTR as actr
#import pyactr as actr

def get_agent(environ, middleman):
    print(middleman)
    m = actr.ACTRModel(environment=environ, motor_prepared=True, middleman=middleman)

    # Defining Chunks
    actr.chunktype("state", "state")
    actr.makechunk(nameofchunk="press_w", typename="state", state="press_w")

    # Initial Goal
    m.goal.add(actr.chunkstring(name="pressing_w", string="""
        isa     state
        state   press_w"""))

    # Productions, which result in pressing "W"
    m.productionstring(name="press_w_key", string="""
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

    return m