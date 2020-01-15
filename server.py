import socket
from state_pb2 import *
s = socket.socket()          
port = 13370
s.bind(('127.0.0.1', port))         
print("socket binded to %s" %(port))
s.listen(5)      
print("socket is listening")        
  
while True: 
    # Establish connection with client.
    c, addr = s.accept()
    deserialized = StateSet()
    try:
        deserialized.ParseFromString(c.recv(4096))
        print(deserialized)
        c.send(str(deserialized).encode())
    except:
        c.send(b"Deserialization of given object failed. ") 

    c.close()
