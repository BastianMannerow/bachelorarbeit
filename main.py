from simulation.ClassicPublicGoodsGame import ClassicPublicGoodsGame

# Test multiple agent in the same round based environment
simulation = ClassicPublicGoodsGame((0, 2))
simulation.run_simulation()

"""
An example of a model using retrieval and goal buffers. It corresponds to
the simplest model in ACT-R tutorials, Unit 1, 'count'.
"""

import pyactr as actr
import simpy

counting = actr.ACTRModel()

#Each chunk type should be defined first.
actr.chunktype("countOrder", ("first", "second"))
#Chunk type is defined as (name, attributes)

#Attributes are written as an iterable (above) or as a string (comma-separated):
actr.chunktype("countOrder", "first, second")

actr.chunktype("countFrom", ("start", "end", "count"))

dd = {actr.chunkstring(string="\
    isa countOrder\
    first 1\
    second 2"): [0], actr.chunkstring(string="\
    isa countOrder\
    first 2\
    second 3"): [0],
    actr.chunkstring(string="\
    isa countOrder\
    first 3\
    second 4"): [0],
    actr.chunkstring(string="\
    isa countOrder\
    first 4\
    second 5"): [0]}

ee = {actr.chunkstring(string="\
    isa countOrder\
    first 5\
    second 6"): [0], actr.chunkstring(string="\
    isa countOrder\
    first 8\
    second 9"): [0],
    actr.chunkstring(string="\
    isa countOrder\
    first 9\
    second 10"): [0],
    actr.chunkstring(string="\
    isa countOrder\
    first 11\
    second 12"): [0]}



#creating goal buffer
counting.goal.add(actr.chunkstring(string="""
    isa     countFrom
    start   2
    end     4
"""))

print(f"Goal: {counting.goal}")


#production rules follow; using productionstring, they are similar to Lisp ACT-R

counting.productionstring(name="start", string="""
    =g>
    isa     countFrom
    start   =x
    count   None
    ==>
    =g>
    isa     countFrom
    count   =x
    +retrieval>
    isa countOrder
    first   =x
""")

counting.productionstring(name="increment", string="""
    =g>
    isa     countFrom
    count   =x
    end     ~=x
    =retrieval>
    isa     countOrder
    first   =x
    second  =y
    ==>
    =g>
    isa     countFrom
    count   =y
    +retrieval>
    isa     countOrder
    first   =y
""")

counting.productionstring(name="stop", string="""
    =g>
    isa     countFrom
    count   =x
    end     =x
    ==>
    ~g>
""")

def looping_loui():
    while True:
        try:
            print(counting_sim.current_event)
            counting_sim.step()
        except simpy.core.EmptySchedule:
            print("Finish..................")
            break

if __name__ == "__main__":
    counting.set_decmem(dd)
    counting_sim = counting.simulation()
    counting.goal.add(actr.chunkstring(string="isa countFrom start 2 end 4"))
    print(f"Goal: {counting.goal}")

    looping_loui()
    counting.set_decmem(ee)
    counting.goal.add(actr.chunkstring(string="isa countFrom start 4 end 6"))
    counting_sim = counting.simulation()
    looping_loui()
