# special case only for elevator, should be customized for each PLC 
def formatInput(inputBoolArray, init=False):
    # change input to bool array (paded with 0 for convenience)
    I0 = [0, 0, 0, 0, 0, 0, 0, 0]
    I3 = [0, 0, 0, 0, 0, 0, 0, 0]
    I0[3:] = inputBoolArray[0:5]
    I1 = inputBoolArray[5:5+8]
    I2 = inputBoolArray[5+8:5+8+8]
    I3[0:4] = inputBoolArray[-4:]
    if init == True:
        I3[7] = 1

    # change to byte array
    return [changeToByte(I0), changeToByte(I1), changeToByte(I2), changeToByte(I3)]

def changeToByte(boolArray):
    # every element in boolArray is a bit at index i
    #   for example [0, 1, 0, 0, 0, 0, 1, 0] is for 0b01000010
    b = 0
    for i in range(8):
        b += boolArray[i] << i
    
    return b

def formatOutput(outputArray):
    # every element in outputArray is a byte, we need to split it into bits
    if len(outputArray) != 3:
        print("Output bytearray is not equal with count\n")
    outputCmd = []
    outputCmd += changeToBitsArray(outputArray[0])[1:]
    outputCmd += changeToBitsArray(outputArray[1])[1:]
    outputCmd += changeToBitsArray(outputArray[2])[:-1]
    
    return outputCmd

def changeToBitsArray(byteElement):
    bitsArray = []
    for i in range(8):
        bitsArray.append((byteElement & (2**i)) >> i)
    # 1 will become [1,0,0,0,0,0,0,0]

    return bitsArray

if __name__ == "__main__":
    boolArrayTest1 = [0,1,1,0,0,0,0,0]
    a = changeToByte(boolArrayTest1)
    print(a)
    inputBoolArray = [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    inputBoolArray1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    inputBoolArray2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    inputBoolArray3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    byteArray = formatInput(inputBoolArray1)
    print([b for b in byteArray])

    a = changeToBitsArray(1)
    print(a)
    a = changeToBitsArray(17)
    print(a)

    a = formatOutput([17, 45, 33])
    print(a)