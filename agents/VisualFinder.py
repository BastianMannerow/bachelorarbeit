import customPyACTR as actr

def get_agent(environ, middleman):
    agent = actr.ACTRModel(environment=environ, motor_prepared=True, middleman=middleman)

    # Defining Chunks
    actr.chunktype("state", "state")
    actr.chunktype("image", "img")
    actr.makechunk(nameofchunk="read_start", typename="state", state="start")
    actr.makechunk(nameofchunk="read_respond", typename="state", state="respond")
    actr.makechunk(nameofchunk="image_empty", typename="image", img="empty")



    return agent