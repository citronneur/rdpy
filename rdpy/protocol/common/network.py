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
        
    @property
    def value(self):
        return self._value;
        
    def write(self, s):
        '''
        write value in stream s
        '''
        s.write(struct.pack(self._structFormat, self._value))
        
    def read(self, s):
        '''
        read value from stream
        '''
        self._value = struct.unpack(self._structFormat,s.read(self._typeSize))[0]
        
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

class UInt8(SimpleType):
    '''
    unsigned byte
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xff:
            raise InvalidValue("invalid UInt8 value")
        SimpleType.__init__(self, "B", 1, value)
        
class UInt16Be(SimpleType):
    '''
    unsigned short with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffff:
            raise InvalidValue("invalid UInt16Be value")
        SimpleType.__init__(self, ">H", 2, value)
        
class UInt16Le(SimpleType):
    '''
    unsigned short with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffff:
            raise InvalidValue("invalid UInt16Le value")
        SimpleType.__init__(self, "<H", 2, value)
        
class UInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffffffff:
            raise InvalidValue("invalid UInt32Be value")
        SimpleType.__init__(self, ">I", 4, value)
        
class UInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffffffff:
            raise InvalidValue("invalid UInt32Le value")
        SimpleType.__init__(self, "<I", 4, value)
        
class SInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < ~0x7fffffff or value > 0x7fffffff:
            raise InvalidValue("invalid UInt32Le value")
        SimpleType.__init__(self, "<I", 4, value)
        
class SInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < ~0x7fffffff or value > 0x7fffffff:
            raise InvalidValue("invalid UInt32Be value")
        SimpleType.__init__(self, ">I", 4, value)

class UInt24Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffffff:
            raise InvalidValue("invalid UInt24Be value")
        SimpleType.__init__(self, ">I", 3, value)
        
    def write(self, s):
        '''
        special write for a special type
        '''
        s.write(struct.pack(">I", self._value)[1:])
        
    def read(self, s):
        '''
        special read for a special type
        '''
        self._value = struct.unpack(">I",s.read(3))[0]
        
class UInt24Le(SimpleType):
    '''
    unsigned int with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        if value < 0 or value > 0xffffff:
            raise InvalidValue("invalid UInt24Le value")
        SimpleType.__init__(self, "<I", 3, value)
        
    def write(self, s):
        '''
        special write for a special type
        '''
        s.write(struct.pack("<I", self._value)[1:])
        
    def read(self, s):
        '''
        special read for a special type
        '''
        self._value = struct.unpack("<I",s.read(3))[0]

    

class Stream(StringIO):
    '''
    use string io inheritance
    '''
    def dataLen(self):
        '''
        not yet read length
        '''
        return self.len - self.pos
    
    def readType(self, t):
        t.read(self)
    
    def writeType(self, t):
        t.write(self)
        
    def write_unistr(self, value):
        for c in value:
            self.write_uint8(ord(c))
            self.write_uint8(0)
        self.write_uint8(0)
        self.write_uint8(0)