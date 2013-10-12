'''
Created on 22 aout 2013

@author: sylvain
'''
class ProtocolVersion(object):
    '''
    different ptotocol version
    '''
    UNKNOWN = 0
    RFB003003 = 1
    RFB003007 = 2
    RFB003008 = 3
    
class SecurityType:
    '''
    security type supported by twisted remote desktop
    '''
    INVALID = 0
    NONE = 1
    VNC = 2
    
class PixelFormat(object):
    def __init__(self):
        self.BitsPerPixel = 32
        self.Depth = 24
        self.BigEndianFlag = False
        self.TrueColorFlag = True
        self.RedMax = 255
        self.GreenMax = 255
        self.BlueMax = 255
        self.RedShift = 16
        self.GreenShift = 8
        self.BlueShift = 0
        
    def read(self, data):
        self.BitsPerPixel = data.read_uint8()
        self.Depth = data.read_uint8()
        self.BigEndianFlag = data.read_uint8()
        self.TrueColorFlag = data.read_uint8()
        self.RedMax = data.read_beuint16()
        self.GreenMax = data.read_beuint16()
        self.BlueMax = data.read_beuint16()
        self.RedShift = data.read_uint8()
        self.GreenShift = data.read_uint8()
        self.BlueShift = data.read_uint8()
        #padding
        data.read(3)
        
    def write(self, data):
        data.write_uint8(self.BitsPerPixel)
        data.write_uint8(self.Depth)
        data.write_uint8(self.BigEndianFlag)
        data.write_uint8(self.TrueColorFlag)
        data.write_beuint16(self.RedMax)
        data.write_beuint16(self.GreenMax)
        data.write_beuint16(self.BlueMax)
        data.write_uint8(self.RedShift)
        data.write_uint8(self.GreenShift)
        data.write_uint8(self.BlueShift)
        #padding
        data.write_uint8(0)
        data.write_uint8(0)
        data.write_uint8(0)
        
class Pointer:
    BUTTON1 = 0x1
    BUTTON2 = 0x2
    BUTTON3 = 0x4
    
class Rectangle:
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Width = 0
        self.Height = 0
        self.Encoding = 0
        
class Encoding:
    RAW = 0