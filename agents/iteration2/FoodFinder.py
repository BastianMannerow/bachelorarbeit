import pyactr as actr


#if old_stimulus1 and old_stimulus1 != agent1_sim._Simulation__env.stimulus:
#            agent2_sim._Simulation__environment_activate.succeed(value=(agent1_sim._Simulation__env.trigger, agent1_sim._Simulation__pr.env_interaction))


def get_agent(environ, letter):
    agent = actr.ACTRModel(environment=environ, motor_prepared=True, automatic_visual_search=True,)

    # Defining Chunks
    actr.chunktype("goal", "state")

    start = actr.makechunk(nameofchunk="start", typename="chunk", value="start")
    agent.goal.add(actr.makechunk(typename="start", state=start))


    ## Initial Goal
    #agent.goal.add(actr.chunkstring(name=f"pressing_{letter}", string=f"""
    #    isa     state
    #    state   press_{letter}"""))



    agent = add_productions(agent, letter)

    return agent

def add_productions(agent, letter):
    # Productions, which result in pressing the specified key
    agent.productionstring(name=f"press_{letter}_key", string=f"""
            =g>
            isa     goal
            state   start
            ?manual>
            state   free
            ==>
            =g>
            isa     goal
            state   next
            +manual>
            isa     _manual
            cmd     'press_key'
            key     {letter}""")

    agent.productionstring(name=f"locate_letter", string=f"""
            =g>
            isa     goal
            state   next
            ?visual_location>
            buffer  empty
            ==>
            =g>
            isa     goal
            state   nextnext
            ?visual_location>
            attended False
            +visual_location>
            isa _visuallocation
            screen_x closest""")

    agent.productionstring(name="locate_letter_two", string="""
            =g>
            isa     goal
            state   next
            ?visual_location>
            buffer  full
            ==>
            =g>
            isa     goal
            state   attend""")

    agent.productionstring(name="attend_letter", string="""
            =g>
            isa     goal
            state   attend
            =visual_location>
            isa    _visuallocation
            ?visual>
            state   free
            ==>
            =g>
            isa     goal
            state   reading
            +visual>
            isa     _visual
            cmd     move_attention
            screen_pos =visual_location
            ~visual_location>""")

    agent.productionstring(name="encode_probe_and_find_new_location", string="""
            =g>
            isa     goal
            state   reading
            =visual>
            isa     _visual
            value   =val
            ?visual_location>
            buffer  empty
            ==>
            =g>
            isa     goal
            state   nextnext
            ~visual>
            ?visual_location>
            attended False
            +visual_location>
            isa _visuallocation
            screen_x closest""")

    agent.productionstring(name=f"press_D_key", string=f"""
            =g>
            isa     goal
            state   nextnext
            ?manual>
            state   free
            ==>
            =g>
            isa     goal
            state   start
            +manual>
            isa     _manual
            cmd     'press_key'
            key     SPACE""")

    return agent