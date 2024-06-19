import re

# Tested
def pad2Hex(n, padLen):
    # Pad the int value to wanted length in hex
    # n : int
    # padLen : lenth in bytes
    # print(n, type(n))
    try:   
        strN = hex(n).split("x", 1)[1]
        hexstr = (padLen - len(strN)) * "0" + strN
    except:
        print("Error in pad2Hex: n is ", n, " padLen is ", padLen)

    return hexstr

# Tested
def parseAddr(strAddr):
    # parse addr into data block and position -1 for none
    if '.' in strAddr:
        m = re.match(r'^([a-zA-Z]+)(\d+).(\d+)', strAddr)
        dataBlock = m.group(1)
        startAddr = m.group(2)
        bitOffset = m.group(3)
    else: 
        m = re.match(r'^([a-zA-Z]+)(\d+)',strAddr)
        dataBlock = m.group(1)
        startAddr = m.group(2)
        bitOffset = 'N'
    
    return (dataBlock, startAddr, bitOffset)

def helper():
    print("====================================================")
    print("Force job tools for s7-300")
    print("")
    print("Create a force job:")
    print(">>> ForceJob(addrList, valueList, cnt)")
    print("")
    print("Replace a forced job:")
    print(">>> ReplaceJob(addrList, valueList, cnt, jobId)")
    print("")
    print("Delete the current force job")
    print(">>> DeleteJob(jobId)")
    print("")
    print("Read job list")
    print(">>> ReadJob()")