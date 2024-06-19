from ForceVector import *
from utils import *
from ForceConnet import *

def checkPacket(rawData, jobName):
    PDUpos = [8, 9, 10, 11]
    jobDataTruth = {
        'Read job list': "320700003b00000c0020000112081241100000000000ff09001c00140004000000000001000000010001000100010001000000000000",
        'Delete job': "320700004000000c00200001120812410f0000000000ff09001c00140004000000000001000000000001000100010001000000010904", 
        'Replace job':
        "320700003d00000c0052000112081241120000000000ff09004e001400360000000000010000000000010001000100010000000009040014001a00000100000200040001000100010001000100000002200100000002200200000002000900010000000900010000"
    }
    truth = jobDataTruth[jobName]
    for diffPos in diff(rawData, truth):
        if not diffPos in PDUpos:
            print("Wrong for <", jobName, ">")
            print("truth: \t", truth)
            print("yours: \t", rawData)
            return
    
    print("Okay for <", jobName, "> with only PDU differences")

def diff(a, b):
    # a, b : str
    # return the different position with int list
    diffList = []
    (shorterStr, longerStr) = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(shorterStr)):
        if not shorterStr[i] == longerStr[i]:
            diffList.append(i)

    print(diffList, type(diffList))
    return diffList

if __name__ == "__main__":
    # test for pad2Hex
    a = 2
    print(pad2Hex(a, 4))
    a = 32
    print(pad2Hex(a, 2))

    # test for parseAddr
    b = 'Q2.2'
    c = 'DB20'
    print(parseAddr(b))
    print(parseAddr(c)) 
    (d, e, f) = parseAddr(b)
    print(d, " ", e, " ", f)

    # test for tis addr segment
    g = 'Q2.2'
    tisaddr = TisItemAddr(g)
    print(tisaddr.get())

    # test for tis value segment
    v = 1
    tisvalue = TisItemValue(v)
    print(tisvalue.get())

    # test for tis data segment
    addr = ['Q2.1', 'Q2.2']
    vals = [1, 1]
    tisSeg = TISData(addr, vals, 2)
    print(tisSeg.get(), " len is: ", len(tisSeg.get())/2)
    addr = ['Q2.1']
    vals = [1]
    tisSeg = TISData(addr, vals, 1)
    print(tisSeg.get(), " len is: ", len(tisSeg.get())/2)

    # test for tis parameter
    tisParam = TISParam()
    print(tisParam.get())

    # test for data, changed

    # test for param
    param = Parameter('Force')
    print(param.get(), " len is: ", len(param.get())//2)

    # test for head
    head = Header()
    print(head.get(), " len is: ", len(head.get())//2)

    # test for force job
    addr = ['Q2.1', 'Q2.2']
    vals = [1, 0]
    forcejob = ForceJob(addr, vals, 2)
    print(forcejob.get(), " len is: ", len(forcejob.get())//2)
    addr = ['Q2.1']
    vals = [1]
    forcejob = ForceJob(addr, vals, 1)
    print(forcejob.get(), " len is: ", len(forcejob.get())//2)

    # test for read job list
    readjob = ReadJob()
    print("Read Job: ", readjob.get(), " len is: ", len(readjob.get())//2)
    checkPacket(readjob.get(), 'Read job list')

    # test for delete job
    deletejob = DeleteJob(4)
    print("Delete Job: ", deletejob.get(), " len is: ", len(deletejob.get())//2)
    checkPacket(deletejob.get(), 'Delete job')

    # test for replace job
    addr = ['Q2.1', 'Q2.2']
    vals = [0, 0]
    replacejob = ReplaceJob(addr, vals, 2, 4)
    print("Replace Job: ", replacejob.get(), " len is: ", len(replacejob.get())//2)
    checkPacket(replacejob.get(), 'Replace job')

    # test for help function
    helper()

    # test for get the job referenc number
    pkt = "0300003102f080320700003b00000c0014000112081281100600000000ff09001000040008010000010904010010060000"
    pkt = (bytearray.fromhex(pkt), [0, 1])
    a = getJobRefNumber(pkt, 'Read job list')
    print(a)
    b = getJobRefNumber(pkt, 'Force')
    print(b)

    # test for getByteArray
    print(getByteArray(deletejob))