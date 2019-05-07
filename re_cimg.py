import math

class ddsImage():
    def __init__(self):
        self.resX = 0
        self.resY = 0
        self.image = []

    def export(self, filename): # Change to 16bpp RGBA
        
        ddsHeader = bytearray(b''.join([b'DDS\x20\x7c\x00\x00\x00\x07\x10\x00\x00', self.resY.to_bytes(4, byteorder = 'little'),
                                        self.resX.to_bytes(4, byteorder = 'little'), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']))
        ddsHeader.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x41\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFF\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # DDS flags set for BGRA32 - wasteful!
        with open(filename, 'wb') as ddsOut:
            ddsOut.write(ddsHeader)
            for row in self.image:
                for pixel in row:
                    ddsOut.write(round(pixel.b * 255).to_bytes(1, byteorder = 'little'))
                    ddsOut.write(round(pixel.g * 255).to_bytes(1, byteorder = 'little'))
                    ddsOut.write(round(pixel.r * 255).to_bytes(1, byteorder = 'little'))
                    ddsOut.write(round(pixel.a * 255).to_bytes(1, byteorder = 'little'))
        
class colour():
    def __init__(self, r = 1, g = 1, b = 1, a = 1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
            
    def fromBytesLayton(encodedColour, pixelDivide = [1,5,5,5], pixelColour = [3,2,1,0], correctColour = False):
        
        encodedBits = []
        for bit in range(16):   # Change encodedColour from int to bits
            encodedBits.insert(0, encodedColour & 1)
            encodedColour = encodedColour >> 1
            
        bitPosition = 0
        colourOut = colour(0,0,0,0)
        for indexColour in range(len(pixelColour)):
            intensity = 0
            if pixelDivide[indexColour] > 1:
                for bitColourAppend in range(pixelDivide[indexColour]):
                    intensity += ((2 ** (7 - bitColourAppend)) * encodedBits[bitPosition])
                    bitPosition += 1
                if correctColour:               # Colours can be corrected by scaling the intensity properly
                    intensity = intensity / 248 # Reduced palette puts actual max at 248
                else:
                    intensity = intensity / 255 #     but the game treats the max at 255, leaving grey whites
            else:
                intensity = encodedBits[bitPosition]
                bitPosition += 1
            
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

        for indexPixel in range(int(xRes * yRes * (bpp/8))):
            pixelByte = data[indexPixel]
            if indexPixel % int(xRes * bpp/8) == 0:
                self.image.append([])
            for indexSubPixel in range(int(1/(bpp/8))):
                self.image[-1].append(palette[(pixelByte & ((2**bpp) - 1)) % len(palette)])
                pixelByte = pixelByte >> bpp
                

class laytonImage():
    def __init__(self, filename):
        
        self.filename = filename
        
        self.countTile = 0

        self.palette = []
        self.tiles = []
        self.tilesReconstructed = []
        
        self.statAlignedBpp = 0

    def load(self):
        
        with open(self.filename, 'rb') as laytonIn:
            if laytonIn.read(4) == b'LIMG':
                lengthHeader = int.from_bytes(laytonIn.read(4), byteorder = 'little')
                offsetTileParam = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                
                laytonIn.seek(2, 1) # UNK

                offsetImageParam = int.from_bytes(laytonIn.read(2), byteorder = 'little')

                laytonIn.seek(2, 1) # UNK
                
                offsetTableTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                lengthTableTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                offsetTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                self.countTile = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                
                laytonIn.seek(2, 1) # UNK
                
                self.lengthPalette = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                self.statAlignedBpp = math.ceil(math.ceil(math.log(self.lengthPalette, 2)) / 4) * 4

                # UNKs
                laytonIn.seek(lengthHeader)
                for indexColour in range(self.lengthPalette):
                    self.palette.append(colour.fromBytesLayton(int.from_bytes(laytonIn.read(2), byteorder = 'little')))
                # UNKs

                laytonIn.seek(offsetTile)
                for index in range(self.countTile):
                    self.tiles.append(tile())
                    self.tiles[-1].decode(laytonIn.read(int((self.statAlignedBpp * 64) / 8)), self.statAlignedBpp, self.palette)    # decode 64 pixels

                laytonIn.seek(offsetTableTile)
                for indexTile in range(lengthTableTile):
                    self.tilesReconstructed.append(self.tiles[int.from_bytes(laytonIn.read(2), byteorder = 'little')])
                
                laytonIn.seek(offsetImageParam + 10)
                imageTileY = int.from_bytes(laytonIn.read(2), byteorder = 'little')
                imageTileX = int(lengthTableTile / imageTileY)

                outputImage = ddsImage()
                outputImage.resX = imageTileX * 8
                outputImage.resY = imageTileY * 8
                outputImage.image = []
                indexTile = 0
                
                for yTile in range(imageTileY):
                    outputImage.image.extend([[],[],[],[],[],[],[],[]])
                    for xTile in range(imageTileX):
                        for yRes in range(8):
                            outputImage.image[(yTile * 8) + yRes].extend(self.tilesReconstructed[indexTile].image[yRes])
                        indexTile += 1

                outputImage.export(self.filename.split("//")[-1][0:-5] + ".dds")
                        
                return True
            
            else:
                print("Bad file magic!")
                return False
            
testImage = laytonImage("assets//nintendo_b.cimg")
testImage.load()
