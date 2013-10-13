'''
Created on 12 aout 2013

@author: sylvain
'''
import struct
from StringIO import StringIO

class Stream(StringIO):
    
    def dataLen(self):
        return self.len - self.pos

    def read_uint8(self):
        return struct.unpack("B",self.read(1))[0]
    
    def read_beuint16(self):
        return struct.unpack(">H",self.read(2))[0]
    
    def read_leuint16(self):
        return struct.unpack("<H",self.read(2))[0]
    
    def read_beuint24(self):
        return struct.unpack(">I",'\x00'+self.read(3))[0]
    
    def read_leuint24(self):
        return struct.unpack("<I",'\x00'+self.read(3))[0]
    
    def read_beuint32(self):
        return struct.unpack(">I",self.read(4))[0]
    
    def read_leuint32(self):
        return struct.unpack("<I",self.read(4))[0]
    
    def read_besint32(self):
        return struct.unpack(">i",self.read(4))[0]
    
    def read_lesint32(self):
        return struct.unpack("<i",self.read(4))[0]
    
    def write_uint8(self, value):
        self.write(struct.pack("B", value))
    
    def write_beuint16(self, value):
        self.write(struct.pack(">H", value))
        
    def write_leuint16(self, value):
        self.write(struct.pack("<H", value))
    
    def write_beuint24(self, value):
        self.write(struct.pack(">I", value)[1:])
    
    def write_beuint32(self, value):
        self.write(struct.pack(">I", value))
        
    def write_leuint32(self, value):
        self.write(struct.pack("<I", value))
        
    def write_besint32(self, value):
        self.write(struct.pack(">i", value))
        
    def write_lesint32(self, value):
        self.write(struct.pack("<i", value))
        
    def write_unistr(self, value):
        for c in value:
            self.write_uint8(ord(c))
            self.write_uint8(0)
        self.write_uint8(0)
        self.write_uint8(0)