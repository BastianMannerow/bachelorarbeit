Aggression vs. Altruism: Modelling the Impact of Deviant Behaviour on Fitness in a Dynamic Environment
Project Overview
I am conducting an ACT-R based social simulation for my bachelor's thesis.

Institution: University of Lübeck in Computer Science
Supervisor: Prof. Dr. Nele Rußwinkel

Background
Social simulations often rely purely on statistical aggregations, neglecting the individual mental models of participants. ACT-R serves as a framework to incorporate human-like cognition in social decision-making processes, grounded in insights from contemporary social neuroscience.

pyactr
The simulation utilizes pyactr, a package developed by Dr. Jakub Dotlačil of Utrecht University and other contributors (pyactr GitHub). This package integrates ACT-R into Python. I extended the package by creating a middleman class that functions as a notifier, facilitating simultaneous communication between agents and the environment. This extension, inspired by Dr. Dotlačil's response to my inquiry, allows for concurrent agent interactions rather than just turn-based querying.

Environment
By integrating my middleman class, connection to virtually any environment is possible, ranging from games to real-world data. It is important to note that machine vision must be manually managed. This involves translating the experimental environment into respective stimuli for the agent. Upon completion of the project, I will provide a detailed visualization of the environment's structure.

Limitations
The project's progress is documented in the milestones.
Upon completion, I intend to propose my implementation for inclusion in the official pyactr package.
Acknowledgements
Nele Rußwinkel: For supervising my bachelor thesis.
Dr. Jakub Dotlačil: For answering various questions regarding pyactr (Jakub Dotlačil GitHub).
Martin Stuwe: For addressing questions about translating the environment into visual stimuli (Martin Stuwe GitHub).
