import math

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
        self.image = []
        self.colourLayout = 0

    def export(self, filename):
        ddsHeader = bytearray(b''.join([b'DDS\x20\x7c\x00\x00\x00\x07\x10\x00\x00', self.resY.to_bytes(4, byteorder = 'little'),
                                                    self.resX.to_bytes(4, byteorder = 'little'), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']))
        ddsHeader.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        with open(filename, 'wb') as ddsOut:
            ddsOut.write(ddsHeader)
            for row in self.image:
                for pixel in row:
                    ddsOut.write(round(pixel.r * 255).to_bytes(1, byteorder = 'little'))
                    ddsOut.write(round(pixel.g * 255).to_bytes(1, byteorder = 'little'))
                    ddsOut.write(round(pixel.b * 255).to_bytes(1, byteorder = 'little'))
        
class colour():
    def __init__(self, r = 1, g = 1, b = 1, a = 1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def invert(self, includeAlpha = True):
        self.r = 1 - self.r
        self.g = 1 - self.g
        self.b = 1 - self.b
        if includeAlpha:
            self.a = 1 - self.a
        
    def printColour(self):
        print("RGBA: [" + str(round(self.r, 2)) + ", " + str(round(self.g, 2)) + ", " + str(round(self.b, 2)) + ", " + str(round(self.a, 2)) + "]")
        
    def fromBytes(encodedColour, pixelDivide = [6,5,5,0], pixelColour = [0,1,2,3]):
        encodedBits = bytesToBits(encodedColour, 16)
        bitPosition = 0
        colourOut = colour(0,0,0,0)

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
                colourOut.r = intensity
            elif pixelColour[indexColour] == 1:
                colourOut.g = intensity
            elif pixelColour[indexColour] == 2:
                colourOut.b = intensity
            else:
                colourOut.a = intensity
        return colourOut

class tile(ddsImage):
    def __init__(self):
        ddsImage.__init__(self)
        
    def decode(self, data, bpp, palette, xRes = 8, yRes = 8):
        self.resX = xRes
        self.resY = yRes
        
        tempImage = []

        for indexPixel in range(int(xRes * yRes * (bpp/8))):
            pixelByte = data[indexPixel]
            for indexSubPixel in range(int(1/(bpp/8))):
                tempImage.append(pixelByte & ((2**bpp) - 1))
                pixelByte = pixelByte >> bpp
            
        indexDataByte = 0
        for indexRow in range(xRes):
            self.image.append([])
            for indexColumn in range(yRes):
                self.image[-1].append(palette[tempImage[indexDataByte]])
                indexDataByte += 1
                

class laytonImage():
    def __init__(self, filename):
        
        self.filename = filename
        
        self.countTile = 0
        self.countTileSize = 0
        self.countPaletteDefinitions = 0

        self.palette = []
        self.tiles = []
        self.tilesReconstructed = []
        
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

                for pixelPower in range(1, 32):
                    if (self.lengthPalette) <= (2 ** pixelPower):
                        break
                self.statBpp = pixelPower
                self.statAlignedBpp = math.ceil(pixelPower / 4) * 4

                # UNKs here
                laytonIn.seek(lengthHeader)
                for indexColour in range(self.lengthPalette): # Colour order unknown, 16 bits probs 565
                    self.palette.append(colour.fromBytes(int.from_bytes(laytonIn.read(2), byteorder = 'little')))
                    self.palette[-1].printColour()
                # UNKs here
                
                laytonIn.seek(0, 2)            
                self.countTileSize = (laytonIn.tell() - offsetTile) / self.countTile

                laytonIn.seek(offsetTile)
                for index in range(self.countTile):
                    self.tiles.append(tile())
                    self.tiles[-1].decode(laytonIn.read(int(self.countTileSize)), self.statAlignedBpp, self.palette)

                laytonIn.seek(offsetTableTile)
                for indexTile in range(lengthTableTile):
                    self.tilesReconstructed.append(self.tiles[int.from_bytes(laytonIn.read(2), byteorder = 'little')])

                outputImage = ddsImage()
                outputImage.resX = 256
                outputImage.resY = 192
                outputImage.image = []
                indexTile = 0
                
                for yTile in range(24):
                    outputImage.image.extend([[],[],[],[],[],[],[],[]])
                    for xTile in range(32):
                        for yRes in range(8):
                            outputImage.image[(yTile * 8) + yRes].extend(self.tilesReconstructed[indexTile].image[yRes])
                        indexTile += 1

                outputImage.export("test.dds")
                        
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
            
#testImage = laytonImage("assets//level5_a.cimg")    # 128x16, not mentioned anywhere (probably cropped using tiles?) 8bpp allows reading
#testImage = laytonImage("assets//nintendo_b.cimg")  # 4bpp for reading
#testImage = laytonImage("assets//mobi_b.cimg")
testImage = laytonImage("assets//title_b.cimg")
testImage.load()
testImage.printStats()
