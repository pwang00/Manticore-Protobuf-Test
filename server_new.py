import socket
from state_pb2 import *
import random
import time

def generate_states():

    state_array = StateSet()

    for i in range(0, 10):

        state = State()
        state.type = State.READY if random.random() > 0.5 else State.BUSY
        state.reason = "Task completed successfully."
        state_array.states.extend([state])

    return state_array

def main():
    s = socket.socket()          
    port = 1337
    s.bind(('127.0.0.1', port))         
    print("socket binded to %s" %(port))
    s.listen(5)      
    print("socket is listening")        

    while True: 
        # Establish connection with client.
        c, addr = s.accept()
        serialized_states = generate_states().SerializeToString()
        try:
            time.sleep(random.randint(4, 8))
            c.send(serialized_states)
        except KeyboardInterrupt:
            c.close()
            quit()

if __name__ == "__main__":
    main()