# LSCR

from struct import unpack

class LaytonOperand():
    def __init__(self, operandType, operandValue):
        self.type = operandType
        self.value = operandValue

    def __str__(self):
        return str(self.type) + " " + str(self.value)

class LaytonInstruction():
    def __init__(self, instructionBytes):
        self.unk = instructionBytes[0:2]
        self.countOperands = int.from_bytes(instructionBytes[2:4], byteorder = 'little')
        self.indexOperandsStart = int.from_bytes(instructionBytes[4:], byteorder = 'little')
        self.operands = []

    def __str__(self):
        output = str(self.unk) + "\t" + str(self.countOperands) + " ops"
        for operand in self.operands:
            output += "\n\t" + str(operand)
        return output + "\n"

class LaytonScript():
    def __init__(self, filename):
        self.bankString = {}
        self.bankOperands = {}
        self.commands = []
        try:
            with open(filename, 'rb') as laytonIn:
                if self.load(laytonIn):
                    print("Read okay!")
                else:
                    print("Read fail!")
        except FileNotFoundError:
            print("File does not exist!")

    def populateBankString(self, reader, offsetString):
        reader.seek(0,2)
        lengthFile = reader.tell()
        reader.seek(offsetString)
        tempString = bytearray(b'')
        while reader.tell() != lengthFile:
            tempByte = reader.read(1)
            if tempByte == b'\x00':
                self.bankString[reader.tell() - offsetString - len(tempString) - 1] = tempString.decode("shift-jis")
                tempString = bytearray(b'')
            else:
                tempString.extend(tempByte)

    def populateBankOperands(self, reader, countOperands, offsetCommand):
        reader.seek(offsetCommand)
        for indexOperand in range(countOperands):
            tempOperandType = reader.read(1)
            if tempOperandType == b'\x00':
                tempOperand = int.from_bytes(reader.read(4), byteorder = 'little', signed=True)
            elif tempOperandType == b'\x01':
                tempOperand = unpack("<f", reader.read(4))[0]
            elif tempOperandType == b'\x02':
                tempOperand = self.bankString[int.from_bytes(reader.read(4), byteorder = 'little')]
            else:
                tempOperand = reader.read(4)
            self.bankOperands[indexOperand] = LaytonOperand(tempOperandType, tempOperand)

    def populateInstructionOperands(self):
        for command in self.commands:
            for indexInstruction in range(command.indexOperandsStart, command.indexOperandsStart + command.countOperands):
                command.operands.append(self.bankOperands[indexInstruction])
    
    def load(self, reader):
        if reader.read(4) == b'LSCR':
            countCommand = int.from_bytes(reader.read(2), byteorder = 'little')
            offsetHeader = int.from_bytes(reader.read(2), byteorder = 'little')
            offsetCommand = int.from_bytes(reader.read(4), byteorder = 'little')
            offsetString = int.from_bytes(reader.read(4), byteorder = 'little')

            self.populateBankString(reader, offsetString)

            countOperands = 0
            reader.seek(offsetHeader)
            for indexCommand in range(countCommand):
                self.commands.append(LaytonInstruction(reader.read(8)))
                countOperands = max(countOperands, self.commands[indexCommand].indexOperandsStart + self.commands[indexCommand].countOperands)

            self.populateBankOperands(reader, countOperands, offsetCommand)
            self.populateInstructionOperands()
            
            return True
        else:
            return False
