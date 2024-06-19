import readOpc
import socket
import json
import time

if __name__ == "__main__":
    address = ('localhost', 31550)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    wincc_opc = readOpc.opc()
    wincc_opc.connect()
    time_interval = []

    for i in range(1000):
        start_time = time.process_time()
        result = wincc_opc.readVars()
        json_string = json.dumps(result).encode()
        s.sendto(json_string, address)
        end_time = time.process_time()
        time_interval.append(end_time - start_time)

    time_interval.sort()
    print("the mid item is: {}".format(time_interval[500]))
    print("the largest item is: {}".format(time_interval[-1]))
    print("the average item is: {}".format(sum(time_interval)/len(time_interval)))
    wincc_opc.close()
    s.close()
    