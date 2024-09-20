import pyactr as actr


#if old_stimulus1 and old_stimulus1 != agent1_sim._Simulation__env.stimulus:
#            agent2_sim._Simulation__environment_activate.succeed(value=(agent1_sim._Simulation__env.trigger, agent1_sim._Simulation__pr.env_interaction))


def get_agent(environ, letter):
    agent = actr.ACTRModel(environment=environ, motor_prepared=True, automatic_visual_search=False)

    # Defining Chunks
    actr.chunktype("pair", "probe answer")

    actr.chunktype("goal", "state")

    dm = agent.decmem

    agent.visualBuffer("visual", "visual_location", dm, finst=30)

    start = actr.makechunk(nameofchunk="start", typename="chunk", value="start")
    actr.makechunk(nameofchunk="attending", typename="chunk", value="attending")
    actr.makechunk(nameofchunk="done", typename="chunk", value="done")
    agent.goal.add(actr.makechunk(typename="read", state=start))
    agent.set_goal("g2")
    agent.goals["g2"].delay = 0.2

    agent = add_productions(agent, letter)

    return agent

def add_productions(agent, letter):
    agent.productionstring(name=f"press_D_key", string=f"""
                =g>
                isa     goal
                state   start
                ?manual>
                state   free
                ==>
                =g>
                isa     goal
                state   afterstart
                +manual>
                isa     _manual
                cmd     'press_key'
                key     SPACE""")

    # Productions, which result in pressing the specified key
    agent.productionstring(name="find_probe", string="""
            =g>
            isa     goal
            state   afterstart
            ?visual_location>
            buffer  empty
            ==>
            =g>
            isa     goal
            state   attend
            ?visual_location>
            attended False
            +visual_location>
            isa _visuallocation
            screen_x closest""")  # this rule is used if automatic visual search does not put anything in the buffer

    agent.productionstring(name="check_probe", string="""
            =g>
            isa     goal
            state   start
            ?visual_location>
            buffer  full
            ==>
            =g>
            isa     goal
            state   attend""")  # this rule is used if automatic visual search is enabled and it puts something in the buffer

    agent.productionstring(name="attend_probe", string="""
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
            state   attend
            ~visual>
            ?visual_location>
            attended False
            +visual_location>
            isa _visuallocation
            screen_x closest""")

    return agent