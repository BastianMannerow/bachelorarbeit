import pyactr as actr

# Initialisiere Umgebung und Stimuli
stimuli = ['A', 'B', 'C']
text = [
    {1: {'text': stimuli[0], 'position': (100, 100)}},
    {2: {'text': stimuli[1], 'position': (100, 100)}},
    {3: {'text': stimuli[2], 'position': (100, 100)}}
]

environ = actr.Environment(focus_position=(100, 100))
environproc = environ.environment_process

# Chunk-Typen und Chunks definieren
actr.chunktype("chunk", "value")
actr.chunktype("read", "state")
actr.chunktype("image", "img")
actr.makechunk(nameofchunk="start", typename="chunk", value="start")
actr.makechunk(nameofchunk="attend_let", typename="chunk", value="attend_let")
actr.makechunk(nameofchunk="response", typename="chunk", value="response")
actr.makechunk(nameofchunk="done", typename="chunk", value="done")
