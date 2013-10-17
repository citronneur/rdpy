'''
@author: sylvain
'''

import struct
from StringIO import StringIO
from error import InvalidValue, InvalidType

def sizeof(element):
    '''
    byte size of type
    '''
    if isinstance(element, tuple):
        size = 0
        for i in element:
            size += sizeof(i)
        return size
    elif isinstance(element, Type):
        return element.__sizeof__()
    
    raise InvalidType("invalid type for sizeof")
            

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
    
    def __sizeof__(self):
        '''
        return size of type
        '''
        pass

class SimpleType(Type):
    '''
    simple type
    '''
    def __init__(self, structFormat, typeSize, value):
        self._typeSize = typeSize
        self._structFormat = structFormat
        self.value = value
        
    @property
    def value(self):
        '''
        shortcut to access inner value
        '''
        return self._value
    
    @value.setter
    def value(self, value):
        '''
        setter of value after check it
        '''
        if self.__class__.__dict__.has_key("isInRange") and not self.__class__.isInRange(value):
            raise InvalidValue("value is out of range for %s"%self.__class__)
        self._value = value    
    
    def __cmp__(self, other):
        '''
        compare inner value
        '''
        return self._value.__cmp__(other.value)
        
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
        
    def __sizeof__(self):
        '''
        return size of type
        '''
        return self._typeSize
        
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
        if name[0] != '_' and (isinstance(value, Type) or isinstance(value, tuple)):
            self._type.append(value)
        self.__dict__[name] = value
            
    def read(self, s):
        '''
        call read on each ordered subtype 
        '''
        for i in self._type:
            s.readType(i)
            
    def write(self, s):
        '''
        call write on each ordered subtype
        '''
        for i in self._type:
            s.writeType(i)
            
    def __sizeof__(self):
        '''
        call sizeof on each subtype
        '''
        size = 0
        for i in self._type:
            size += sizeof(i)
        return size

class UInt8(SimpleType):
    '''
    unsigned byte
    '''    
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, "B", 1, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xff)
        
        
class UInt16Be(SimpleType):
    '''
    unsigned short with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, ">H", 2, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffff)
        
class UInt16Le(SimpleType):
    '''
    unsigned short with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, "<H", 2, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffff)
        
class UInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, ">I", 4, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffffffff)
        
class UInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, "<I", 4, value)
    
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffffffff)
        
class SInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, "<I", 4, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < ~0x7fffffff or value > 0x7fffffff)
        
class SInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, ">I", 4, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < ~0x7fffffff or value > 0x7fffffff)

class UInt24Be(SimpleType):
    '''
    unsigned int with big endian representation
    '''
    def __init__(self, value = 0):
        '''
        constructor check value range
        '''
        SimpleType.__init__(self, ">I", 3, value)
        
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffffff)
        
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
        SimpleType.__init__(self, "<I", 3, value)
    
    @staticmethod
    def isInRange(value):
        '''
        return true if value is in UInt8 range
        '''
        return not (value < 0 or value > 0xffffff)    
            
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
        
class String(Type):
    '''
    String network type
    '''
    def __init__(self, value = ""):
        '''
        constructor with new string
        '''
        self._value = value
        
    def __eq__(self, other):
        '''
        call raw compare value
        '''
        return self._value == other._value
    
    def __str__(self):
        '''
        call when str function is call
        '''
        return self._value
    
    def write(self, s):
        '''
        write the entire raw value
        '''
        s.write(self._value)
    
    def read(self, s):
        '''
        read all stream
        '''
        self._value = s.getvalue()
        
    def __sizeof__(self):
        '''
        return len of string
        '''
        return len(self._value)
    

class Stream(StringIO):
    '''
    use string io inheritance
    '''
    def dataLen(self):
        '''
        not yet read length
        '''
        return self.len - self.pos
    
    def readType(self, value):
        '''
        call specific read on type object
        '''
        #read each tuple
        if isinstance(value, tuple):
            for element in value:
                self.readType(element)
            return
        value.read(self)
        
    def readNextType(self, t):
        '''
        read next type but didn't consume it
        '''
        self.readType(t)
        self.pos -= sizeof(t)
    
    def writeType(self, value):
        '''
        call specific write on type object
        '''
        #write each element of tuple
        if isinstance(value, tuple):
            for element in value:
                self.writeType(element)
            return
        value.write(self)
        
    def write_unistr(self, value):
        for c in value:
            self.write_uint8(ord(c))
            self.write_uint8(0)
        self.write_uint8(0)
        self.write_uint8(0)