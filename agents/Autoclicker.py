# Pressing W

import customPyACTR as actr
#import pyactr as actr

def get_agent(environ):
    m = actr.ACTRModel(environment=environ, motor_prepared=True)

    # Chunks definieren
    actr.chunktype("state", "state")
    actr.makechunk(nameofchunk="press_w", typename="state", state="press_w")

    # Initiales Ziel
    m.goal.add(actr.chunkstring(name="pressing_w", string="""
        isa     state
        state   press_w"""))

    # Produktionsregel zum kontinuierlichen Drücken von 'w'
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