import pyactr as actr

class Maxi:
        def __init__(self, environ):
                self.environ = environ
        def get_agent(self):
            agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False)

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

            agent = self.add_productions(agent)

            return agent

        def add_productions(self, agent):
            agent.productionstring(name="begrenzung", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention nil
                ==>
                    +visual_location>
                    color yellow
                    kind line
                    value 0
                    screen_x highest
                    attended nil
                =goal>
                    intention begrenzung2
            """)

            agent.productionstring(name="begrenzung2", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention begrenzung2
                =visual_location>
                    screen_x =x
                ==>
                    +visual_location>
                    color yellow
                    kind line
                    value 0
                    screen_x lowest
                    attended nil
                    new_x - x 13
                =goal>
                    intention begrenzung3
                    rechts =new_x
            """)

            agent.productionstring(name="begrenzung3", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention begrenzung3
                =visual_location>
                    screen_x =x
                ==>
                    +visual_location>
                    color yellow
                    kind line
                    value 90
                    screen_y lowest
                    attended nil
                    new_x + x 12
                =goal>
                    intention begrenzung4
                    links =new_x
            """)

            agent.productionstring(name="begrenzung4", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention begrenzung4
                =visual_location>
                    screen_y =y
                ==>
                    +visual_location>
                    color yellow
                    kind line
                    value 90
                    screen_y highest
                    attended nil
                    new_y + y 12
                =goal>
                    intention erkennen
                    oben =new_y
            """)

            agent.productionstring(name="initiate-search", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention erkennen
                =visual_location>
                    screen_y =y
                ==>
                    new_y - y 13
                =goal>
                    intention attending
                    unten =new_y
                +visual_location>
                    isa visual_location
                    screen_y 337
                    attended nil
            """)

            agent.productionstring(name="attend-first-row", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention attending
                =visual_location>
                    ?visual state free
                ==>
                    =goal>
                    ISA goal
                    intention encode
                +visual>
                    cmd move_attention
                    screen_pos visual_location
            """)

            agent.productionstring(name="encode-first", string="""
                =goal>
                    state whats_my_color
                    intention encode
                =visual>
                ==>
                    =goal>
                    intention attending
                +visual_location>
                    isa visual_location
                    screen_y 337
                    attended nil
            """)

            agent.productionstring(name="localize-move-down-1", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention attending
                ?visual_location>
                    state error
                ?manual>
                    state free
                ==>
                    =goal>
                    intention localize
                +manual>
                    cmd press_key
                    key s
            """)

            agent.productionstring(name="localize-move-right", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention localize2
                ?visual_location>
                    state error
                ?manual>
                    state free
                ==>
                    =goal>
                    intention attending_side
                    test1 right
                +manual>
                    cmd press_key
                    key d
            """)

            agent.productionstring(name="localize-move-left", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention localize2
                    test1 right
                ?visual_location>
                    state error
                ?manual>
                    state free
                ==>
                    =goal>
                    intention attending_side
                +manual>
                    cmd press_key
                    key a
            """)

            agent.productionstring(name="localize-move-down-2", string="""
                =goal>
                    ISA goal
                    state whats_my_color
                    intention attending_side
                ?manual>
                    state free
                ==>
                    =goal>
                    intention localize
                +manual>
                    cmd press_key
                    key s
            """)

            agent.productionstring(name="localize-look", string="""
                =goal>
                    state whats_my_color
                    intention localize
                ?manual>
                    state free
                ?imaginal>
                    state free
                ==>
                    =goal>
                    intention localize2
                +imaginal>
                    isa agent
                +visual_location>
                    screen_y 362
                    attended t
            """)

            agent.productionstring(name="localize-evaluate", string="""
                =goal>
                    state whats_my_color
                    intention localize2
                    links =links
                    rechts =rechts
                    unten =unten
                    oben =oben
                =visual_location>
                    color =col
                    screen_y =y
                    screen_x =x
                ?visual>
                    state free
                =imaginal>
                    mitte_x (mitte =links =rechts)
                    mitte_y (mitte =oben =unten)
                ==>
                    =goal>
                    state lets_go_down
                    intention test_tracking
                    y_position =mitte_y
                    x_position =mitte_x
                    threshold 40
                =imaginal>
                    color =col
                    firststep down
                    y_position =y
                    x_position =x
                +visual>
                    cmd move_attention
                    screen_pos visual_location
            """)

            agent.productionstring(name="tracking", string="""
                =goal>
                    intention test_tracking
                =imaginal>
                    color =col
                =visual>
                ?visual>
                    state free
                ==>
                    +visual>
                    cmd start_tracking
                +visual_location>
                    color =col
                    kind oval
                =goal>
                    intention check
                =imaginal>
            """)

            agent.productionstring(name="check-below", string="""
                =goal>
                    intention check
                    y_position =y_goal
                    unten =unten
                    - state go_land
                =imaginal>
                    < y_position =y_goal
                    - y_position =new_unten
                    - fail down
                    - fail2 down
                =visual_location>
                    screen_x =x
                    screen_y =y
                    new_y (+ y 25)
                ?manual>
                    state free
                ==>
                    =imaginal>
                    y_position =y
                    x_position =x
                =goal>
                    main_intention down
                    key s
                    intention save
                +visual_location>
                    kind oval
                    screen_y =new_y
                    screen_x =x
            """)

            agent.productionstring(name="check-below-land", string="""
                =goal>
                    intention check
                    y_position =y_goal
                    unten =unten
                    state go_land
                =imaginal>
                    < y_position =y_goal
                =visual_location>
                    screen_x =x
                    screen_y =y
                    new_y (+ y 25)
                ?manual>
                    state free
                ==>
                    =imaginal>
                    y_position =y
                    x_position =x
                =goal>
                    main_intention down
                    key s
                    intention save
                +visual_location>
                    kind oval
                    screen_y =new_y
                    screen_x =x
            """)

            agent.productionstring(name="check-up", string="""
                =goal>
                    intention check
                    y_position =y_goal
                =imaginal>
                    >= y_position =y_goal
                    - fail up
                    - fail2 up
                =visual_location>
                    screen_x =x
                    screen_y =y
                    new_y (- y 25)
                ?manual>
                    state free
                ==>
                    =imaginal>
                    y_position =y
                    x_position =x
                =goal>
                    main_intention up
                    key w
                    intention save
                +visual_location>
                    kind oval
                    screen_y =new_y
                    screen_x =x
            """)

            agent.productionstring(name="check-right", string="""
                =goal>
                    intention check
                    x_position =x_goal
                =imaginal>
                    <= x_position =x_goal
                    - fail right
                    - fail2 right
                =visual_location>
                    screen_x =x
                    screen_y =y
                    new_x (+ x 25)
                ?manual>
                    state free
                ==>
                    =imaginal>
                    y_position =y
                    x_position =x
                =goal>
                    main_intention right
                    key d
                    intention save
                +visual_location>
                    kind oval
                    screen_y =y
                    screen_x =new_x
            """)

            agent.productionstring(name="check-left", string="""
                =goal>
                    intention check
                    x_position =x_goal
                =imaginal>
                    > x_position =x_goal
                    - fail left
                    - fail2 left
                =visual_location>
                    screen_x =x
                    screen_y =y
                    new_x (- x 25)
                ?manual>
                    state free
                ==>
                    =imaginal>
                    y_position =y
                    x_position =x
                =goal>
                    main_intention left
                    key a
                    intention save
                +visual_location>
                    kind oval
                    screen_y =y
                    screen_x =new_x
            """)

            agent.productionstring(name="nothing-there", string="""
                =goal>
                    intention save
                ?visual_location>
                    state error
                ?manual>
                    state free
                ==>
                    =goal>
                    intention move
            """)

            agent.productionstring(name="einsammeln", string="""
                =goal>
                    intention save
                    main_intention direct
                =visual_location>
                    color =col
                =imaginal>
                    plus =col
                ?manual>
                    state free
                ==>
                    =goal>
                    intention move
                =imaginal>
            """)

            agent.productionstring(name="ausweichen-minus1", string="""
                =goal>
                    intention save
                    main_intention direct
                =visual_location>
                    color =col
                =imaginal>
                    minus =col
                    fail nil
                ?manual>
                    state free
                ==>
                    =goal>
                    intention check
                =imaginal>
                    fail direct
            """)

            agent.productionstring(name="ausweichen-minus2", string="""
                =goal>
                    intention save
                    main_intention direct
                =visual_location>
                    color =col
                =imaginal>
                    minus =col
                    fail fail
                ?manual>
                    state free
                ==>
                    =goal>
                    intention check
                =imaginal>
                    fail direct
                    fail2 fail
            """)

            agent.productionstring(name="ausweichen-hindernis", string="""
                =goal>
                    intention save
                    main_intention direct
                =visual_location>
                    color =col
                =imaginal>
                    hindernis =col
                    fail nil
                ?manual>
                    state free
                ==>
                    =goal>
                    intention check
                =imaginal>
                    fail direct
            """)

            agent.productionstring(name="ausweichen-hindernis2", string="""
                =goal>
                    intention save
                    main_intention direct
                =visual_location>
                    color =col
                =imaginal>
                    hindernis =col
                    fail fail
                ?manual>
                    state free
                ==>
                    =goal>
                    intention check
                =imaginal>
                    fail direct
                    fail2 fail
            """)

            agent.productionstring(name="austesten", string="""
                =goal>
                    intention save
                =visual_location>
                    color =col
                =imaginal>
                    - plus =col
                    - minus =col
                    - hindernis =col
                ?manual>
                    state free
                ==>
                    =goal>
                    intention testing
                =imaginal>
                    last_color =col
            """)
            agent.productionstring(name="move-austesten", string="""
                =goal>
                    intention testing
                    main_intention direction
                    key =key
                =imaginal>
                    firststep =first
                ?manual>
                    state free
                ==>
                    =goal>
                    intention evaluate_color
                +manual>
                    cmd press_key
                    key =key
                =imaginal>
                    firststep direction
                -visual>
            """)

            agent.productionstring(name="evaluate-color", string="""
                =goal>
                    intention evaluate_color
                ?manual>
                    state free
                =imaginal>
                    x_position =x
                ==>
                    =goal>
                    intention evaluate_color2
                +visual_location>
                    kind text
                    > screen_y 337
                    screen_x lowest
                =imaginal>
                -visual>
            """)

            agent.productionstring(name="evaluate-hindernis", string="""
                =goal>
                    intention evaluate_color2
                    main_intention direction
                =visual_location>
                    kind oval
                =imaginal>
                    last_color =col
                ?manual>
                    state free
                ==>
                    =goal>
                    intention where_next
                    fail direction
                =imaginal>
                    hindernis =col
            """)

            agent.productionstring(name="evaluate-minus-plus", string="""
                =goal>
                    intention evaluate_color2
                =visual_location>
                    kind text
                ?manual>
                    state free
                ?visual>
                    buffer full
                ==>
                    =goal>
                    intention evaluate_color3
                +visual>
                    cmd move_attention
                    screen_pos visual_location
            """)

            agent.productionstring(name="evaluate-plus", string="""
                =goal>
                    intention evaluate_color3
                    main_intention direction
                =visual>
                    value "+"
                =imaginal>
                    color =col
                    last_color =last_col
                    firststep =first
                ?manual>
                    state free
                ==>
                    =goal>
                    intention evaluate_color4
                =imaginal>
                    plus =last_col
                    firststep direction
                +visual_location>
                    kind oval
                    color =col
            """)

            agent.productionstring(name="evaluate-minus", string="""
                =goal>
                    intention evaluate_color3
                    main_intention direction
                =visual>
                    value "-"
                =imaginal>
                    color =col
                    last_color =last_col
                ?manual>
                    state free
                ==>
                    =goal>
                    intention evaluate_color4
                +visual_location>
                    kind oval
                    color =col
                =imaginal>
                    minus =last_col
                    fail direction
            """)

            agent.productionstring(name="back-to-agent", string="""
                =goal>
                    ISA goal
                    intention evaluate_color4
                =visual_location>
                    screen_x =x
                    screen_y =y
                =imaginal>
                ==>
                    =goal>
                    ISA goal
                    intention test_tracking
                =imaginal>
                    y_position =y
                    x_position =x
                +visual>
                    cmd move_attention
                    screen_pos visual_location
            """)

            agent.productionstring(name="land", string="""
                =goal>
                    intention save
                =visual_location>
                    color green
                ?manual>
                    state free
                ==>
                    =goal>
                    intention move
            """)

            agent.productionstring(name="move", string="""
                =goal>
                    intention move
                    main_intention direction
                    key =key
                =imaginal>
                    firststep =first
                ?manual>
                    state free
                ==>
                    =goal>
                    intention where_next
                +manual>
                    cmd press_key
                    key =key
                =imaginal>
                    firststep direction
                    fail nil
                    fail2 nil
                +visual_location>
                    kind oval
                    attended nil
            """)

            agent.productionstring(name="move-up-ausweichen", string="""
                =goal>
                    intention check
                =imaginal>
                    firststep =first
                    fail =fail
                    fail2 =fail2
                ?manual>
                    state free
                ==>
                    =goal>
                    intention where_next
                +manual>
                    cmd press_key
                    key w
                =imaginal>
                    firststep up
                    fail down
                    fail2 nil
                +visual_location>
                    kind oval
                    attended nil
            """)

            agent.productionstring(name="where-to-go", string="""
                =goal>
                    intention where_next
                    x_position =t_x
                    y_position =t_y
                ?manual>
                    state free
                =imaginal>
                    color =col
                    x_position =c_x
                    y_position =c_y
                    distance (euclid =c_x =c_y =t_x =t_y)
                ==>
                    =goal>
                    intention check
                    distance =distance
                =imaginal>
                +visual_location>
                    color =col
                    kind oval
            """)

            agent.productionstring(name="left-corner", string="""
                =goal>
                    x_position =t_x
                    y_position =t_y
                    state lets_go_down
                    - state go_land
                    intention save
                    threshold =thresh
                    < distance =thresh
                    links =l_x
                    unten =l_y
                =imaginal>
                ==>
                    new_x (+ l_x 25)
                    new_y (- l_y 25)
                =goal>
                    x_position new_x
                    y_position new_y
                    state left_corner
                    distance 100
                =imaginal>
                    fail nil
            """)

            agent.productionstring(name="right-corner", string="""
                =goal>
                    x_position =t_x
                    y_position =t_y
                    state left_corner
                    - state go_land
                    intention save
                    threshold =thresh
                    < distance =thresh
                    rechts =l_x
                    unten =l_y
                =imaginal>
                ==>
                    new_x (- l_x 25)
                    new_y (- l_y 50)
                =goal>
                    x_position new_x
                    y_position new_y
                    state right_corner
                    distance 100
                =imaginal>
                    fail nil
            """)

            return agent