# LSCR

def getNullTerminatedString(reader, startPosition):
    posStart = reader.tell()
    reader.seek(startPosition)
    output = ""
    while True:
        stringByte = reader.read(1)
        if stringByte == b'\x00':
            break
        else:
            output += stringByte.decode('ascii')
    reader.seek(posStart)
    return output

class laytonOpcode():
    def __init__(self, opcode, operand=None):
        self.opcode = opcode
        self.operand = operand

class laytonScript():
    def __init__(self):
        self.opcodes = []

    def load(self, filename):
        try:
            with open(filename, 'rb') as laytonIn:
                if laytonIn.read(4) == b'LSCR':
                    countOpcode     = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                    lengthOpcode    = int.from_bytes(laytonIn.read(2), byteorder = 'little')    # UNK, usually 16
                    offsetParam     = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    offsetData      = int.from_bytes(laytonIn.read(4), byteorder = 'little')

                    for indexOpcode in range(countOpcode):
                        self.opcodes.append(laytonOpcode(laytonIn.read(int(lengthOpcode / 8)), operand = laytonIn.read(6)))
                        print("[PROC    ] Added opcode!")

                    # This functionality is only valid for text scripts
                    laytonIn.seek(offsetParam + 1)
                    countText = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    for indexText in range(countText):
                        laytonIn.seek(11, 1)
                        print(getNullTerminatedString(laytonIn, offsetData + int.from_bytes(laytonIn.read(4), byteorder = 'little')))
                    
                else:
                    return False
                
            return True

        except FileNotFoundError:
            print("File does not exist!")
            return False

test = laytonScript()
test.load(r"assets\lbin\00_002000.lbin")
