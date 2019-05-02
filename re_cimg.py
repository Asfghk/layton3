
import math

# LIMG is a palette-based image format for Professor Layton and the Unwound Future


# i have no idea how to read a palette-based image 

# Tile size appears to always be 8x8 (given tiles are always square, which is a safe assumption,
#     the pixels stored per tile according to rounded BPP value is 64.

# Regular class should be setup to allow conversion between image formats

def bytesToBits(inBytes, lengthOut):
    output = []
    shiftedInput = inBytes
    for bit in range(lengthOut):
        output.insert(0, shiftedInput & 1)
        shiftedInput = shiftedInput >> 1
    return output

class ddsImage():
    def __init__(self):
        self.resX = 0
        self.resY = 0
        self.data = []
        self.colourLayout = 0

    def export(self, filename):
        with open(filename, 'wb') as ddsOut:
            pass
            
        
class colour():
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    def printColour(self):
        print("RGBA: [" + str(round(self.r, 2)) + ", " + str(round(self.g, 2)) + ", " + str(round(self.b, 2)) + ", " + str(round(self.a, 2)) + "]")
    # Add fromPacked and toPacked methods to return colour objects from binary input


class tile():
    def __init__(self):
        self.image = []
    def decode(self, data, xRes, yRes, bpp):
        indexDataByte = 0
        for indexPixel in range(int((xRes * yRes) * (bpp/8))):    # Assumes full resolution is used
            pixelByte = data[indexDataByte]
            for indexSubPixel in range(int(bpp/8)):
                self.image.append(pixelByte & ((2**bpp) - 1))
                pixelByte >> bpp
            indexDataByte += 1

class packedColour(colour):
    def __init__(self, encodedColour, pixelDivide = [6,5,5,0], pixelColour = [2,1,0,3]):
        colour.__init__(self, 0, 0, 0, 0)
        self.encodedColour = encodedColour
        self.decode(pixelDivide, pixelColour, encodedColour)

    def decode(self, pixelDivide, pixelColour, encodedColour):
        encodedBits = bytesToBits(encodedColour, 16)
        bitPosition = 0

        for indexColour in range(len(pixelColour)):
            intensity = 0

            for bitColourAppend in range(pixelDivide[indexColour]):
                intensity += ((2 ** bitColourAppend) * encodedBits[bitPosition])
                bitPosition += 1

            if pixelDivide[indexColour] > 0:
                intensity = intensity / ((2**pixelDivide[indexColour]) - 1)
            else:
                intensity = 0  
            if pixelColour[indexColour] == 0:
                self.r = intensity
            elif pixelColour[indexColour] == 1:
                self.g = intensity
            elif pixelColour[indexColour] == 2:
                self.b = intensity
            else:
                self.a = intensity
        

class laytonImage():
    def __init__(self, filename):
        
        self.filename = filename
        self.tableTile = []
        self.countTile = 0
        self.countTileSize = 0
        self.countPaletteDefinitions = 0

        self.palette = []
        self.tiles = []
        self.statBpp = 0
        self.statAlignedBpp = 0

    def load(self):
        with open(self.filename, 'rb') as laytonIn:
            if laytonIn.read(4) == b'LIMG':
                lengthHeader = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                offsetTileParam = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                laytonIn.seek(6, 1) # UNK
                offsetTableTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                lengthTableTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                offsetTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                self.countTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                self.countPaletteDefinitions = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                self.lengthPalette = int.from_bytes(laytonIn.read(2), byteorder = 'little')

                for pixelPower in range(1, 32): # up to 32bpp, will never be used
                    if (self.lengthPalette) <= (2 ** pixelPower):
                        break
                self.statBpp = pixelPower
                self.statAlignedBpp = math.ceil(pixelPower / 4) * 4

                # UNKs here
                laytonIn.seek(lengthHeader)
                for indexColour in range(self.lengthPalette): # Colour order unknown, 16 bits probs 565
                    self.palette.append(packedColour(int.from_bytes(laytonIn.read(2), byteorder = 'little')))
                    self.palette[-1].printColour()
                # UNKs here
                
                laytonIn.seek(0, 2)
                lengthFile = laytonIn.tell() - offsetTile

                laytonIn.seek(offsetTableTile)
                for indexTile in range(lengthTableTile):
                    self.tableTile.append(int.from_bytes(laytonIn.read(2), byteorder = 'little'))
                    
                self.countTileSize = lengthFile / self.countTile

                laytonIn.seek(offsetTile)
                for index in range(self.countTile):
                    self.tiles.append(tile())
                    self.tiles[-1].decode(laytonIn.read(int(self.countTileSize)), 8,8, self.statAlignedBpp)
                
                return True
            else:
                print("Bad file magic!")
                return False

    def printStats(self):
        if self.countTile > 0:
            print("Tiles: " + str(self.countTile))
            try:
                print("TSize: " + str(int(self.countTileSize)))
            except TypeError:
                print("TSize: [IRREGULAR] " + str(self.countTileSizes))
            print("BPP  : " + str(self.statAlignedBpp))

            if int(self.countTileSize / (self.statAlignedBpp / 8)) != 64:
                print("Irregular pixel mapping!")
        else:
            print("Image not imported!")
            
#testImage = laytonImage("level5_a.cimg")    # 128x16, not mentioned anywhere (probably cropped using tiles?) 8bpp allows reading
#testImage = laytonImage("nintendo_b.cimg")  # 4bpp for reading
#testImage = laytonImage("mobi_b.cimg")
testImage = laytonImage("title_a.cimg")
testImage.load()
testImage.printStats()
