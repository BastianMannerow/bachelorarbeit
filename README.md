<h3 align="left">Modeling behaviour change through social cognition: A game-theoretic approach in ACT-R</h3>
<h3 align="left">Project Overview</h3>
<p align="left">
I am conducting an ACT-R based social simulation for my bachelor's thesis.
</p>
<p align="left">
<strong>Institution</strong>: Institute of Information Systems, University of Lübeck
<br>
<strong>Subject</strong>: Computer Science (B.Sc.) 
<br>
<strong>Supervisor</strong>: Prof. Dr. Nele Rußwinkel
</p>
<h3 align="left">Background</h3>
<p align="left">
Social simulations often rely purely on statistical aggregations, neglecting the individual mental models of participants. ACT-R serves as a framework to incorporate human-like cognition in social decision-making processes. My research is grounded in insights from contemporary social neuroscience.
</p>
<h3 align="left">pyactr</h3>
<p align="left">
The simulation utilizes <a href="https://github.com/jakdot/pyactr?tab=readme-ov-file">pyactr</a>, a package developed by Dr. Jakub Dotlačil of Utrecht University and other contributors. This package integrates ACT-R into Python. I extended the functionality by creating a middleman class which functions as a notifier, facilitating simultaneous communication between agents and the environment. This extension, inspired by Dr. Dotlačil's response to my inquiry, allows for both concurrent agent interactions and turn-based querying.
</p>
<h3 align="left">Environment</h3>
<p align="left">
By integrating my middleman class, connection to virtually any environment is possible, ranging from games to real-world data. It is important to note that machine vision must be manually managed. This involves translating the experimental environment into respective stimuli for the agent. Upon completion of the project, I will provide a detailed visualization of the environment's structure.
</p>
<h3 align="left">Setup</h3>
<p align="left">
The simulation setup allows for customization by modifying parameters in the main script. Users can adjust various settings to initiate their own unique simulations, enabling experimentation with different scenarios and behaviors.
</p>
<h3 align="left">Acknowledgements</h3>
<p align="left">
<ul>
<li><strong><a href="https://www.ifis.uni-luebeck.de/de/team/nele-russwinkel">Nele Rußwinkel</a></strong>: For supervising my bachelor thesis.</li>
<li><strong><a href="https://github.com/jakdot">Jakub Dotlačil</a></strong>: For answering various questions regarding pyactr.</li>
<li><strong><a href="https://github.com/MartinStuwe">Martin Stuwe</a></strong>: For addressing questions about translating the environment into visual stimuli.</li>
</ul>
</p>
