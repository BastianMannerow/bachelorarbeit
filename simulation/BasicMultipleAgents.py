"""
Demo for multiple agents.

This code shows how one can build an environment with multiple agents in which actions of each agent affects the environment for them both.

There are two agents. AG1 should press keys A and C when those letters appear on the screen. AG2 should press B when that letter appears on the screen.

Pressing the right key moves the screen from one letter to the next.

pyactr was not designed with the functionality of supporting multiagents in mind. So the package has to be hacked a bit.

First, sim.run() does not work. You have to go through events manually (see lines at while True how that is done). But that's fine, any serious modeling should do that, instead of using the running function.

Second, in the two lines following the comment "# update stimulus for the other agent..." we have to go into the internal setup of event simulation and manually update the values there. It's not nice and it's likely it will break in more complicated cases. Please, use this code with caution.

Third, there is some inherent asymmetry in the agents. If agent 1 cannot fire any rules whatsoever, the simulation would stop even if agent 2 has some actions ready. This could be avoided with some extra code (e.g., specify that break from the loop only happens after you check both/all agents).

"""

import simpy
from agents import TestAgents

import pyactr as actr

def run_simulation():
    stimuli = ['A', 'B', 'C']
    text = [{1: {'text': stimuli[0], 'position': (100, 100)}}, {2: {'text': stimuli[1], 'position': (100, 100)}},
            {3: {'text': stimuli[2], 'position': (100, 100)}}]

    # environments
    environ = actr.Environment(focus_position=(100, 100))
    environproc = environ.environment_process

    # import agents
    agent_one, agent_two = TestAgents.generate_agents(environ)

    # We start the simulation for both agents
    agent1_sim = agent_one.simulation(realtime=False, environment_process=environproc, stimuli=text, triggers=stimuli,
                                      times=3)
    agent2_sim = agent_two.simulation(realtime=False, environment_process=environproc, stimuli=text, triggers=stimuli,
                                      times=3)

    # this is used for internal updates of environment
    old_stimulus1, old_stimulus2 = None, None

    # The following loop runs the whole simulation

    while True:

        # store current stimulus
        try:
            old_stimulus1 = agent1_sim._Simulation__env.stimulus.copy()
        except AttributeError:
            pass

        try:
            # do one simulation step
            agent1_sim.step()

            # print event
            print("AGENT1, ", agent1_sim.current_event)

            # update stimulus for the other agent if they changed due to the event agent 1 carried
            if old_stimulus1 and old_stimulus1 != agent1_sim._Simulation__env.stimulus:
                agent2_sim._Simulation__environment_activate.succeed(
                    value=(agent1_sim._Simulation__env.trigger, agent1_sim._Simulation__pr.env_interaction))

        # if the schedule is empty, the agent has no rules to do and the action is stopped
        except simpy.core.EmptySchedule:
            break

        # switch to the other agent who should work as long as its internal time is smaller than agent 1 - the timing does not always show well in the trace because of internal time updates in pyactr, which are not always visible to the user
        while agent1_sim.show_time() > agent2_sim._Simulation__simulation.peek():

            # store stimuli /triggers
            try:
                old_stimulus2 = agent2_sim._Simulation__env.stimulus.copy()
            except AttributeError:
                pass

            try:
                # do one simulation step
                agent2_sim.step()

                # print event
                print("AGENT2, ", agent2_sim.current_event)

                # update stimulus for the other agent if they changed due to the event agent 2 carried
                if old_stimulus2 and old_stimulus2 != agent2_sim._Simulation__env.stimulus:
                    agent1_sim._Simulation__environment_activate.succeed(
                        value=(agent2_sim._Simulation__env.trigger, agent2_sim._Simulation__pr.env_interaction))
                    break

            # if the schedule is empty, the agent has no rules to do and the action is stopped
            except simpy.core.EmptySchedule:
                break