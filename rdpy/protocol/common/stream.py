'''
@author: sylvain
'''

import struct
from StringIO import StringIO
from error import InvalidValue

class Type(object):
    '''
    root type
    '''
    def write(self, s):
        '''
        interface definition of write function
        '''
        pass
    
    def read(self, s):
        '''
        interface definition of read value
        '''
        pass

class SimpleType(Type):
    '''
    simple type
    '''
    def __init__(self, typeSize, structFormat, value):
        self._typeSize = typeSize
        self._structFormat = structFormat
        self._value = value
        
    def write(self, s):
        '''
        write value in stream s
        '''
        s.write(struct.pack(self._structFormat, self._value))
        
    def read(self, s):
        '''
        read value from stream
        '''
        self._value = struct.unpack(self._structFormat,self.read(self._typeSize))[0]
        
class CompositeType(Type):
    '''
    keep ordering declaration of simple type
    in list and transparent for other type
    '''
    def __init__(self):
        '''
        init list of simple value
        '''
        self._type = []
    
    def __setattr__(self, name, value):
        '''
        magic function to update type list
        '''
        if isinstance(value, Type):
            self._type.append(value)
        self.__dict__[name] = value
        
    def __iter__(self):
        '''
        iteration over object
        '''
        for i in self._type:
            yield i
            
    def write(self, s):
        '''
        call format on each ordered subtype
        '''
        for i in self._type:
            i.write(s)

class Uint8(SimpleType):
    '''
    unsigned byte
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xff:
            raise InvalidValue("invalid uint8 value")
        SimpleType.__init__(self, "B", 1, value)
        
class Uint16Be(SimpleType):
    '''
    unsigned short with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffff:
            raise InvalidValue("invalid Uint16Be value")
        SimpleType.__init__(self, ">H", 2, value)
        
class Uint16Le(SimpleType):
    '''
    unsigned short with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffff:
            raise InvalidValue("invalid Uint16Le value")
        SimpleType.__init__(self, "<H", 2, value)

    

class Stream(StringIO):
    '''
    use string io inheritance
    '''
    def dataLen(self):
        '''
        no read length
        '''
        return self.len - self.pos
    
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
    
    def readType(self, t):
        t.read(self)
    
    def writeType(self, t):
        t.write(self)
        
    
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