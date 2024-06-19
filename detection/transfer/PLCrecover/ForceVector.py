from utils import *

# Tested
class Job(object):
    def __init__(self):
        self.header = ""
        self.param = ""
        self.data = ""
        self.job = ""
        self.descrip = "Job"

    def get(self):
        return self.job

    def getInfo(self):
        return self.descrip

    def combine(self):
        tpkt = TPKT()
        cotp = COTP()
        self.job += self.header.get()
        param = self.param.get()
        data = self.data.get()
        self.job += pad2Hex(len(param)//2, 4) # Parameter Length
        self.job += pad2Hex(len(data)//2, 4) # Data Length
        self.job += param
        self.job += data

        length = len(self.job)//2 + 7 # the TPKT length = COTP(3) + TPKT(4) + S7 comm
        self.job = tpkt.get() + pad2Hex(length, 4) + cotp.get() + self.job

# Tested
class ForceJob(Job):
    def __init__(self, addr, vals, cnt):
        self.header = Header()
        self.descrip = 'Force'
        self.param = Parameter(self.descrip)
        self.data = ForceData(addr, vals, cnt)
        self.job = ""

        self.combine()

# Tested
class ReplaceJob(Job):
    def __init__(self, addr, vals, cnt, jobId):
        self.header = Header()
        self.descrip = 'Replace'
        self.param = Parameter(self.descrip)
        self.data = ReplaceData(addr, vals, cnt, jobId)
        self.job = ""

        self.combine()

# Tested
class DeleteJob(Job):
    def __init__(self, jobId):
        self.header = Header()
        self.descrip = 'Delete'
        self.param = Parameter(self.descrip)
        self.data = DeleteData(jobId)
        self.job = ""

        self.combine()

# Tested
class ReadJob(Job):
    def __init__(self): 
        self.header = Header()
        self.descrip = 'Read job list' 
        self.param = Parameter(self.descrip)
        self.data = ReadData()
        self.job = ""
        
        self.combine()

class TPKT(object):
    def __init__(self):
        self.tpkt = "03" # version
        self.tpkt += "00" # reserved
        # self.tpkt += ""  # length
    
    def get(self):
        return self.tpkt

class COTP(object):
    def __init__(self):
        self.cotp = "02f080"

    def get(self):
        return self.cotp

# Tested
class Header(object):
    def __init__(self):
        self.header = "32" # protocol id
        self.header += "07" # userdata
        self.header += "0000" # reserved
        self.header += "3100" # PDU num, may not useful

    def get(self):
        return self.header

# Tested
class Parameter(object):
    cmdDict = {'Force': 9, 'Replace': 18, 'Delete': 15, 'Read job list': 16}
    def __init__(self, descrip):
        self.param = ""
        self.descrip = descrip

        self.initParam()

    def get(self):
        return self.param
    
    def initParam(self):
        self.param += "000112" # param header
        self.param += "08" # param length, fixed
        self.param += "12" # method, res
        self.param += "4" # req
        self.param += "1" # prog cmd
        # subfunction
        self.param += pad2Hex(Parameter.cmdDict[self.descrip], 2) 
        self.param += "00" # sequence num
        self.param += "00" # ref num
        self.param += "00" # yes for last data unit
        self.param += "0000" # no error

# Tested
class Data(object):
    def __init__(self):
        self.data = ""
    
    def get(self):
        return self.data

# Tested
class ForceData(Data):
    # addr and val are lists
    def __init__(self, addr, val, cnt):
        self.data = "ff" # return suc code
        self.data += "09" # octet str
        self.addr = addr
        self.val = val
        self.cnt = cnt

        self.combineSegs()

    def combineSegs(self):
        # get the data segment except for the starting "ff09"
        tisParam = TISParam().get()
        tisData = TISData(self.addr, self.val, self.cnt).get()
        lenParam = len(tisParam)//2
        # print(lenParam)
        lenData = len(tisData)//2
        self.data += pad2Hex(lenParam + lenData + 4, 4) # Length
        self.data += pad2Hex(lenParam, 4) # TIS paramter size
        self.data += pad2Hex(lenData, 4) # TIS data size

        self.data += tisParam
        self.data += tisData

# Tested
class ReplaceData(ForceData):
    def __init__(self, addr, val, cnt, jobId):
        # get the second layer first
        self.data = ""
        self.addr = addr
        self.val = val
        self.cnt = cnt

        self.combineSegs()
        self.data = self.data[4:] # get rid of the length info

        lenData = len(self.data)//2 + 4 # recalculate the length info here
        # print("lenData is: ", lenData)
        
        firstLayer = "0000000000010000000000010001000100010000"
        firstLayer += "0000" # reserved
        firstLayer += "09" # Force
        firstLayer += pad2Hex(jobId, 2)
        firstLayerTisParamSz = 20

        length = lenData + firstLayerTisParamSz + 4
        self.data = firstLayer + self.data
        self.data = pad2Hex(length,4) + pad2Hex(firstLayerTisParamSz, 4) + pad2Hex(lenData, 4) + self.data

        self.data = "ff09" + self.data

# Tested
class DeleteData(Data):
    # for delete force job
    def __init__(self, jobId):
        # all are fixed except the reference sequence number
        TisParam = "ff09001c001400040000000000010000000000010001000100010000"
        self.data = TisParam
        self.data += "0001" # reserved
        self.data += "09" # Force
        self.data += pad2Hex(jobId, 2)

# Tested
class ReadData(Data):
    # for read job list
    def __init__(self):
        # all are fixed
        self.data = "ff09001c00140004000000000001000000010001000100010001000000000000"

# Tested
class TISParam(object):
    def __init__(self):
        self.params = "0000"
        self.params += "0100" # force immediately
        self.params += "0002" # always force
        self.params += "0004"
        self.params += "0001"
        self.params += "0001"
        self.params += "0001"
        self.params += "0001"
        self.params += "0001"
        self.params += "0000" # trigger event: immediately

    def get(self):
        return self.params

# Tested
class TISData(object):
    # addr and val may be two list
    def __init__(self, addr, val, itemCnt):
        if not (itemCnt == len(addr) and itemCnt == len(val)):
            print("Error! Length of the input are not compatible")
        self.addrList = addr
        self.valList = val
        self.tisdata = ""
        self.itemCnt = itemCnt

        self.combineTis()
    
    def get(self):
        return self.tisdata
    
    def combineTis(self):
        self.tisdata = pad2Hex(self.itemCnt, 4)
        for i in range(self.itemCnt):
            self.itemAddr = TisItemAddr(self.addrList[i])
            self.tisdata += self.itemAddr.get()
        for i in range(self.itemCnt):
            self.itemValue = TisItemValue(self.valList[i])
            self.tisdata += self.itemValue.get()

# Tested
class TisItemAddr(object):
    dataBlockTbl = {'Q':32}

    def __init__(self, addr):
        self.rawAddr = addr
        self.itemAddr = ""

        self.getMySeg()
    
    def get(self):
        return self.itemAddr
    
    def getMySeg(self):
        # for example Q2.1
        (dataBlock, startAddr, bitOffset) = parseAddr(self.rawAddr)
        # memory area
        memoryArea = TisItemAddr.dataBlockTbl[dataBlock]
        self.itemAddr += pad2Hex(memoryArea, 2)
        # bit position
        self.itemAddr += pad2Hex(int(bitOffset), 2)
        # DB number, 0 for none db data block
        if not dataBlock.upper() == 'DB':
            self.itemAddr += pad2Hex(0, 4)
        else:
            # todo, add the db area
            self.itemAddr += ""
        # start address
        self.itemAddr += pad2Hex(int(startAddr), 4)
        
# Tested
class TisItemValue(object):
    reserved = "00"
    octetStr = "09"
    fillByte = "00"

    def __init__(self, val):
        self.rawVal = val
        self.itemValue = ""

        self.getMySeg()

    def get(self):
        return self.itemValue

    def getMySeg(self):
        # multiple kind of data to handle here
        # only match Q bit value here
        self.itemValue += TisItemValue.reserved
        self.itemValue += TisItemValue.octetStr
        if type(self.rawVal) == int:
            # length
            self.itemValue += pad2Hex(1, 4)
            # data
            self.itemValue += pad2Hex(self.rawVal, 2)
            self.itemValue += TisItemValue.fillByte
        if type(self.rawVal) == float:
            print("Haven't done yet!")

