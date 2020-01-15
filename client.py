from state_pb2 import *
import socket
import random
import string

def generate_states():

    state_array = StateSet()

    for i in range(0, 10):

        state = State()
        state.type = State.READY if random.random() > 0.5 else State.BUSY
        state.reason = "Task completed successfully."
        state_array.states.extend([state])

    return state_array


if __name__ == "__main__":
    generated = generate_states()
    s = socket.socket()
    s.connect(("127.0.0.1", 13370))
    s.send(generated.SerializeToString())
    print(s.recv(1024))

    