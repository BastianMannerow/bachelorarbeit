import shutil
import random
from colorama import Fore, Style
import pyactr as actr

class AgentConstruct:
    def __init__(self, actr_agent_type_name, actr_environment, middleman, name, name_number, fortune,
                 contribution_cost_factor,
                 print_trace):
        self.print_trace = print_trace

        # ACT-R specific settings
        self.realtime = False
        self.actr_agent = None
        self.actr_agent_type_name = actr_agent_type_name
        self.actr_environment = actr_environment
        self.simulation = None

        # Simulation specific settings
        self.actr_construct = None
        self.middleman = middleman
        self.name = name
        self.name_number = name_number
        self.agent_dictionary = None
        self.visual_stimuli = []
        self.print_stimulus = False
        self.print_trace = print_trace
        self.social_agreeableness = 0.5  # TODO
        self.current_choices = None
        self.decision_id_counter = 0

        # Temp for the manual output of chosen strategy
        self.current_positive_choice = None
        self.current_neutral_choice = None
        self.current_negative_choice = None
        self.decision_choice = None

        self.extra_punishment_list = []
        self.extra_reward_list = []

        # Public Goods Game specific values
        self.fortune = fortune
        self.contribution_cost_factor = contribution_cost_factor

    # Triggers the middleman to evalute all choices based on the current game state
    def choice_generator(self):
        self.current_choices = self.middleman.choice_generator(self)

    # ACT-R Specific variables will be set at the end of agent generation. This is because of the agent_dictionary.
    def set_actr_agent(self, actr_agent):
        self.actr_agent = actr_agent

    # Construct, which extends ACT-R
    def set_actr_construct(self, actr_construct):
        self.actr_construct = actr_construct

    def actr_extension(self):
        self.actr_construct.extending_actr(self)

    def set_simulation(self):
        self.simulation = None if self.actr_agent is None else self.actr_agent.simulation(
            realtime=self.realtime,
            environment_process=self.actr_environment.environment_process,
            stimuli=[{'S': {'text': 'S', 'position': (1, 1)}}],
            triggers=['S'],
            times=0.1,
            gui=False,
            trace=self.print_trace)

    # Fills the visual buffer with new stimuli, based on the environments condition.
    def update_stimulus(self):
        if self.actr_agent:
            try:
                new_triggers, new_text = self.middleman.get_agent_stimulus(self)

                if (self.print_stimulus):
                    print("----------------- OLD STIMULUS -----------------")
                    print(f"{self.simulation._Simulation__env.triggers}")
                    print(f"{self.simulation._Simulation__env.stimuli}")
                self.simulation._Simulation__env.triggers = new_triggers
                self.simulation._Simulation__env.stimuli = new_text
                # self.simulation._Simulation__env.trigger = new_triggers #  Seems to make problems.
                self.simulation._Simulation__env.stimulus = new_text

                if (self.print_stimulus):
                    print("----------------- NEW STIMULUS -----------------")
                    print(f"{self.simulation._Simulation__env.triggers}")
                    print(f"{self.simulation._Simulation__env.stimuli}")
                    print("----------------- SINGLE STIMULUS -----------------")
                    print(f"{self.simulation._Simulation__env.stimulus}")
            except:
                print("ACT-R Stimulus wurde nicht überschrieben.")

    def set_visual_stimuli(self, visual_stimuli):
        self.visual_stimuli = visual_stimuli

    def get_visual_stimuli(self):
        return self.visual_stimuli

    # Important for the agent to distinguish between himself and other agents.
    # It also contains social status associations for each agent.
    def set_agent_dictionary(self, agent_list):
        if len(agent_list) > 20:
            raise ValueError("Only 20 agents are currently supported")

        # Ensure the agent is at the beginning and receives the letter A
        agent_list = [self] + [agent for agent in agent_list if agent != self]

        # Create the dictionary with letters as keys and values as a dictionary containing the agent and social_status
        self.agent_dictionary = {
            chr(65 + i): {"agent": agent, "social_status": 1.0}
            for i, agent in enumerate(agent_list)
        }
        print(Fore.YELLOW + f"Initial Dictionary of {self.name}: {self.agent_dictionary}" + Style.RESET_ALL)

    def get_agent_dictionary(self):
        return self.agent_dictionary

    # If the agents knowledge changes during the simulation, a new ACT-R simulation needs to be created. This doesn't
    # affect the agent itself, but rather resets the clock, which measures mental processes.
    # In a new version, SocialAgent should be a object attached to AgentConstruct (also random, Maxi, etc.) and they
    # should obtain a default goal, which will be called here TODO
    def reset_simulation(self):
        dd = {}
        # Add all possible actions
        self.choice_generator()
        choices = self.current_choices

        first_key = next(iter(choices.keys()))  # ID of self
        decisions = choices[first_key]
        for i, decision in enumerate(decisions, start=1):
            action_id = decision.pop("id")
            consequences = " ".join(
                f"agent{letter}Consequence {outcome}" for letter, outcome in decision.items()
            )
            dd[actr.chunkstring(string=f"""
                isa possibleAction
                id {action_id}
                {consequences}
            """)] = [0]

        # Add decisions from last round (history)
        history = self.middleman.return_agents_history()
        dic = self.get_agent_dictionary()
        first_key_in_self = next(iter(dic.keys()))
        for participant in history.keys():
            if participant is not self:  # Filter self, if own decision is irrelevant
                try:
                    # Get dictionary of other agents
                    other_agent_dictionary = participant.get_agent_dictionary()

                    # Find corresponding id to self
                    self_key_in_other = None
                    for key, value in other_agent_dictionary.items():
                        if value['agent'] is self:
                            self_key_in_other = key
                            break

                    if self_key_in_other is not None:
                        # Get decision, which related to self
                        selected_option = history[participant]['selected_option']
                        selected_values = selected_option[0][0]

                        # Find key in self dic, which corresponds to other agent
                        participant_key_in_self = None
                        for key, value in dic.items():
                            if value['agent'] is participant:
                                participant_key_in_self = key
                                break

                        # Classify numerical values
                        classified_values = self.choice_classifier({self_key_in_other: [selected_values]})
                        classified_effect = classified_values[self_key_in_other][0][self_key_in_other]

                        # Add to decmem
                        dd[actr.chunkstring(string=f"""
                            isa lastRoundIntention
                            id {participant_key_in_self}
                            agent {participant_key_in_self}
                            target {first_key_in_self}
                            effect {classified_effect}
                        """)] = [0]
                    else:
                        print(f"Kein Schlüssel in `other_agent_dictionary` gefunden, der zu `self` gehört.")
                except AttributeError:
                    print(f"{participant} hat keine Methode 'get_agent_dictionary()'")

        # Reset simulation
        self.actr_agent.decmems = {}
        self.actr_agent.set_decmem(dd)
        first_goal = next(iter(self.actr_agent.goals.values()))  # The second one is imaginal
        first_goal.add(actr.chunkstring(string="isa priorityGoal state priorityGoalstart"))
        new_simulation = self.actr_agent.simulation(
            realtime=self.realtime,
            environment_process=self.actr_environment.environment_process,
            stimuli=[{'S': {'text': 'S', 'position': (1, 1)}}],
            triggers=['S'],
            times=0.1,
            gui=False,
            trace=self.print_trace
        )

        self.simulation = new_simulation

    # An empty schedule would crash the whole simulation. Reset the agent instead, so he can reevaluate.
    def handle_empty_schedule(self):
        # 1. new simulation and goal
        print(Fore.RED + "Empty Schedule. Reset to initial goal." + Style.RESET_ALL)
        print(Fore.YELLOW + f"Current Memory of {self.name}: {self.actr_agent.decmems}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Current Goal of {self.name}: {self.actr_agent.goals}" + Style.RESET_ALL)
        # refresh declarative memory and reset goal
        self.reset_simulation()
        print(Fore.YELLOW + f"New Memory of {self.name}: {self.actr_agent.decmems}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"New Goal of {self.name}: {self.actr_agent.goals}" + Style.RESET_ALL)

    # As soon as a round finished, the agents knowledge should be updated
    def handle_new_round(self):
        if self.actr_agent:
            print(Fore.YELLOW + f"Current Memory of {self.name}: {self.actr_agent.decmems}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Current Goal of {self.name}: {self.actr_agent.goals}" + Style.RESET_ALL)
            # refresh declarative memory and reset goal
            self.reset_simulation()
            print(Fore.YELLOW + f"New Memory of {self.name}: {self.actr_agent.decmems}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"New Goal of {self.name}: {self.actr_agent.goals}" + Style.RESET_ALL)

    # Environment specific settings
    def set_fortune(self, fortune):
        self.fortune = fortune

    def get_fortune(self):
        return self.fortune

    def get_contribution_cost_factor(self):
        return self.contribution_cost_factor

    # Important for the simulation and GUI to distinguish names.
    def get_name_number(self):
        return self.name_number

    # For the GUI and logging
    def get_agent_name(self):
        return self.name

    # Help functions to translate keys into agent objects
    def replace_letters_with_agents(self, input_list):
        new_list = []

        for letter in input_list:
            if letter in self.agent_dictionary:
                agent_object = self.agent_dictionary[letter]['agent']
                if agent_object not in new_list:
                    new_list.append(agent_object)

        return new_list
