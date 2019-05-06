# LCP2 Extractor

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

class laytonPackedFile():
    def __init__(self, relativeNameTableOffset, relativeFileOffset, length):
        self.relativeNameTableOffset = relativeNameTableOffset
        self.relativeFileOffset = relativeFileOffset
        self.length = length
        self.name = ""
        self.data = b''
        
    def __str__(self):
        return (str(self.relativeNameTableOffset) + "\t" + str(self.relativeFileOffset) + "\t" + str(self.length))
    def getName(self, reader, offsetNameTable):
        self.name = getNullTerminatedString(reader, offsetNameTable + self.relativeNameTableOffset)
    def getContents(self, reader, offsetData):
        posStart = reader.tell()
        reader.seek(offsetData + self.relativeFileOffset)
        self.data = reader.read(self.length)
        reader.seek(posStart)
        
class laytonPack():
    def __init__(self):
        self.contents = []

    def load(self, filename):
        try:
            with open(filename, 'rb') as laytonIn:
                if laytonIn.read(4) == b'LPC2':
                    countFile       = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    offsetData      = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    offsetEnd       = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    offsetTableFile = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                    offsetTableName = int.from_bytes(laytonIn.read(4), byteorder = 'little')

                    # Repeat of offsetData, then packing

                    laytonIn.seek(offsetTableFile)
                    for indexFile in range(countFile):
                        self.contents.append(laytonPackedFile(int.from_bytes(laytonIn.read(4), byteorder = 'little'),
                                                              int.from_bytes(laytonIn.read(4), byteorder = 'little'),
                                                              int.from_bytes(laytonIn.read(4), byteorder = 'little')))
                        self.contents[indexFile].getName(laytonIn, offsetTableName)
                        self.contents[indexFile].getContents(laytonIn, offsetData)

                 else:
                     print("File is not an LPC2 archive!")
                     return False
                    
            for indexFile in range(countFile):
                with open(self.contents[indexFile].name, 'wb') as laytonOut:
                    laytonOut.write(self.contents[indexFile].data)
            
        except FileNotFoundError:
            print("File does not exist!")
            return False

test = laytonPack()
test.load("lt3_map.cpck")
