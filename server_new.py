import socket
from state_pb2 import *
import random
import time
import select

def generate_states():

    state_array = StateSet()

    for i in range(0, 10):

        state = State()
        state.id = random.randint(0, 10000)
        state.type = State.READY if random.random() > 0.5 else State.BUSY
        state.reason = "Task completed successfully."
        state_array.states.extend([state])

    return state_array

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
    port = 1337
    s.bind(('127.0.0.1', port))         
    print("socket binded to %s" %(port))
    s.listen(5)      
    print("socket is listening")        
    socket_list = [s]

    while True: 
        # Establish connection with client.

        read_sockets, write_sockets, error_sockets = select.select(socket_list, socket_list, [], 10)    
        serialized_states = generate_states().SerializeToString() 
        
        #print(read_sockets, write_sockets)

        if len(read_sockets):

            for sock in read_sockets:
                if sock is s:
                    print("Got connection from manticore TUI")
                    c, addr = sock.accept()
                    socket_list.append(c)
                else:
                    data = sock.recv(1024)

        if len(write_sockets):
            for sock in write_sockets:
                time.sleep(random.randint(2, 15))
                sock.send(serialized_states)


if __name__ == "__main__":
    main()