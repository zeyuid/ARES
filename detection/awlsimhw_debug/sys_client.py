import socket
import json

address = ('localhost', 31550)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)

for i in range(20):
    json_string, addr = s.recvfrom(1024)
    mylist = json.loads(json_string)
    print(mylist)

s.close()
print(type(mylist))