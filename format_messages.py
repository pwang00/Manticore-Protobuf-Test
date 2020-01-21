def generate_states():

    state_array = StateSet()

    for i in range(0, 10):

        state = State()
        state.type = State.READY if random.random() > 0.5 else State.BUSY
        state.reason = "Task completed successfully."
        state_array.states.extend([state])

    return state_array

def format(deserialized):