import re
from itertools import islice
import pyactr as actr

class Defector:
    """
    A basic social agent, which utilizes a norm understanding for contributing to society.

    Attributes:
        this_agent_key (str): Self identification from AgentConstruct agent_dictionary
        other_agents_key_list (list): Identification from AgentConstruct agent_dictionary for other agents but self
        environ (Environment): pyactr environment
        actr_agent (ACTRModel): pyactr agent
        goal_phases (list): All goal states, which are independent of each other. Makes code more readable
        initial_goal (Chunk): If the agent crashes, it will start again with this goal
        dynamic_productions (dict): Stores dynamic calcula+-----ted utility to not overwrite utility learning by reward
    """

    def __init__(self, environ, initial_punishment_factor):
        """
        Args:
            environ: pyactr environment (can be overwritten later)
        """
        self.this_agent_key = None
        self.other_agents_key_list = None

        self.environ = environ
        self.actr_agent = actr.ACTRModel(environment=self.environ, motor_prepared=True, automatic_visual_search=False,
                               subsymbolic=True)
        self.goal_phases = ["initialise", "defect"]
        self.initial_goal = actr.chunkstring(string=f"""
            isa     {self.goal_phases[0]}
            state   {self.goal_phases[0]}Start
        """)

        # ACT-R extending memory
        self.dynamic_productions = {}
        self.impressions = {}
        self.potential_impression = ""
        self.score = {}

        # experiment configuration
        self.punishment = initial_punishment_factor
        self.positive_cognitive_distortion = 0.33
        self.negative_cognitive_distortion = 0.66

    # Building the agent
    def get_agent(self, agent_list, button_dictionary):
        """
        Builds an ACT-R agent

        Args:
            agent_list (list): Strings from the AgentConstruct dictionary to identify other agents
            button_dictionary (dict): needed to coordinate manual output productions for environment communication

        Returns:
            pyactr.ACTRAgent: The final actr_agent object from pyactr
        """
        self.this_agent_key = agent_list[0]
        self.other_agents_key_list = agent_list[1:]

        # ACT-R configuration for this agent
        actr_agent = self.actr_agent
        actr_agent.model_parameters[
            "utility_noise"] = 5  # 0.0 = only base utility, will be changed adaptevly
        actr_agent.model_parameters["baselevel_learning"] = True

        # Goal Chunk Types
        goal_phases = self.goal_phases
        for phase in goal_phases:
            actr.chunktype(phase, "state")

        actr.chunktype("impression", "positive")

        # Imaginal
        imaginal = actr_agent.set_goal(name="imaginal", delay=0)

        # Declarative Memory, initial mental models
        dd = {}
        for other_agent in self.other_agents_key_list:
            dd[actr.chunkstring(string=f"""
                isa mentalModelAgent{other_agent}
                reputation 5
                consistency True
                normConformity 0.5
            """)] = [0]

        actr_agent.set_decmem(dd)

        # Agent Model
        self.add_always_defect_productions(actr_agent, goal_phases[0], goal_phases[1])
        return actr_agent

    def add_always_defect_productions(self, actr_agent, phase, next_phase):
        """
        Adds productions to the ACT-R agent

        Args:
            actr_agent (pyactr.ACTRAgent): The agent object, where productions will be added
            phase (String): The current phase, which is important for identifying the production name and goal state
            next_phase (String): The next phase, which is important for the last production
        """
        actr_agent.productionstring(name=f"{phase}_start", string=f"""
                =g>
                isa     {phase}
                state   {phase}Start
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}Defect
                """)

        actr_agent.productionstring(name=f"{next_phase}_defect", string=f"""
                =g>
                isa     {next_phase}
                state   {next_phase}Defect
                ==>
                =g>
                isa     {next_phase}
                state   {next_phase}Restart
                """)

        actr_agent.productionstring(name=f"{next_phase}_contribute_and_restart", string=f"""
                =g>
                isa     {next_phase}
                state   {next_phase}Restart
                ==>
                =g>
                isa     {phase}
                state   {phase}Start
                """)

    def extending_actr(self, agent_construct):
        """
        Functionality, which extends ACT-R
        In pyactr, ACT-R functionality and regular arithmetic or logical functions are strictly divided.
        The reason for that is a clearer understanding of the agents' behaviour.
        This method will supervise the internal state of the agent.

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
        goals = agent_construct.actr_agent.goals
        goal = str(next(iter(goals.values())))
        imaginal = str(next(islice(goals.values(), 1, 2)))
        event = agent_construct.simulation.current_event
        # Extract the dictionary code of the other agent. It's important to have consistent ACT-R production names
        if event[1] == "PROCEDURAL" and ("RULE FIRED:" in event[2] or "RULE SELECTED" in event[2]):
            event_2 = event[2]
            start = event_2.find("_") + 1
            end = event_2.find("_", start)
            other_agent = event_2[start:end]
            try:
                other_agent_objekt = agent_construct.replace_letters_with_agents(other_agent)[0]
            except:
                pass
        else:
            other_agent = ""
            other_agent_objekt = None

        if self.goal_phases[1] in goal:  # outputs
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_defect" in event[2]:
                self.handle_contribution_decision(agent_construct, "_0")  # 0 for defect
            if event[1] == "PROCEDURAL" and "RULE SELECTED:" in event[2] and "_contribute_and_restart" in event[2]:
                self.login_decision_matrix(agent_construct)

    def handle_contribution_decision(self, agent_construct, event):
        """
        Handles event if a contribution was chosen

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
            event (String): Stepper event
        """

        match = re.search(r'_(\d+)$', event)
        if match:
            number = int(match.group(1))
            agent_key = self.this_agent_key
            choices_list = agent_construct.current_choices.get(agent_key, [])
            decision = next((entry for entry in choices_list if entry['id'] == number), None)
            agent_construct.decision_choice = decision
        else:
            raise ValueError("There was an error reading the contribution rule.")

    def login_decision_matrix(self, agent_construct):
        """
        Manual Output

        Args:
            agent_construct (AgentConstruct): Parent of the SocialAgent
        """
        self.potential_impression = ""
        if agent_construct.decision_choice:
            agent_construct.middleman.login_final_choice(agent_construct, agent_construct.decision_choice)
        agent_construct.decision_choice = None

    def add_dynamic_productions(self, dummy):
        pass