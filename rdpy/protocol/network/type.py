'''
@author: sylvain
'''

import struct
from StringIO import StringIO
from error import InvalidValue, InvalidType

def sizeof(element):
    '''
    byte size of type
    @param element: Type or Tuple(Type | Tuple,)
    @return: size of element in byte
    @raise InvalidType: if type is different than tuple of Type inheritance
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
        @param s: Stream which will be written
        '''
        pass
    
    def read(self, s):
        '''
        interface definition of read value
        @param s: Stream
        @return: Type read from Stream s
        '''
        pass
    
    def __sizeof__(self):
        '''
        return size of type use for sizeof function
        @return: size in byte of type
        '''
        pass

class SimpleType(Type):
    '''
    simple type
    '''
    def __init__(self, structFormat, typeSize, signed, value):
        '''
        constructor of simple type
        @param structFormat: letter that represent type in struct package
        @param typeSize: size in byte of type
        @param signed: true if type represent a signed type
        @param value: value record in this object
        '''
        self._typeSize = typeSize
        self._structFormat = structFormat
        self._signed = signed
        self.value = value
        
    @property
    def value(self):
        '''
        shortcut to access inner value
        @return: inner value(python type value)
        '''
        return self._value
    
    @value.setter
    def value(self, value):
        '''
        setter of value after check it
        @param value: new value encompass in simpletype object
        @raise InvalidValue: if value doesn't respect type range
        '''
        if not self.isInRange(value):
            raise InvalidValue("value is out of range for %s"%self.__class__)
        self._value = value    
    
    def __cmp__(self, other):
        '''
        compare inner value
        magic function of python use for any compare operators
        @param other: Type value which will be compared with self value
        @return: python value compare
        '''
        return self._value.__cmp__(other.value)
        
    def write(self, s):
        '''
        write value in stream s
        use struct package to pack value
        @param s: Stream which will be written
        '''
        s.write(struct.pack(self._structFormat, self._value))
        
    def read(self, s):
        '''
        read inner value from stream
        use struct package
        @param s: Stream
        '''
        self._value = struct.unpack(self._structFormat,s.read(self._typeSize))[0]
    
      
    def mask(self):
        '''
        compute bit mask for type
        because in python all numbers are int long or float
        '''
        if not self.__dict__.has_key("_mask"):
            mask = 0xff
            for i in range(1, self._typeSize):
                mask = mask << 8 | 0xff
            self._mask = mask
        return self._mask
    
    def isInRange(self, value):
        '''
        check if value is in mask range
        @param value: python value
        @return: true if value is in type range
        '''
        if self._signed:
            return not (value < -(self.mask() >> 1) or value > (self.mask() >> 1))
        else:
            return not (value < 0 or value > self.mask())
        
    def __sizeof__(self):
        '''
        return size of type
        @return: typeSize pass in constructor
        '''
        return self._typeSize
    
    def __invert__(self):
        '''
        implement not operator
        @return: __class__ value
        '''
        invert = ~self._value
        if not self._signed:
            invert &= self.mask()
        return self.__class__(invert)
    
    def __add__(self, other):
        '''
        implement addition operator
        @attention: type overflow are not handle
        @param other: SimpleType value
        @return: self.__class__ object with add result
        @raise InvalidValue: if new value is out of bound
        '''
        return self.__class__(self._value.__add__(other._value))
    
    def __sub__(self, other):
        '''
        implement sub operator
        @attention: type overflow are not handle
        @param other: SimpleType value
        @return: self.__class__ object with sub result
        @raise InvalidValue: if new value is out of bound
        '''
        return self.__class__(self._value.__sub__(other._value))
    
    def __and__(self, other):
        '''
        implement bitwise and operator
        @param other: SimpleType value
        @return: self.__class__ object with and result
        '''
        return self.__class__(self._value.__and__(other._value))
    
    def __or__(self, other):
        '''
        implement bitwise and operator
        @param other: SimpleType value
        @return: self.__class__ object with or result
        '''
        return self.__class__(self._value.__or__(other._value))

        
class CompositeType(Type):
    '''
    keep ordering declaration of simple type
    in list and transparent for other type
    '''
    def __init__(self):
        '''
        init list of simple value
        '''
        #list of ordoned type
        self._type = []
    
    def __setattr__(self, name, value):
        '''
        magic function to update type list
        @param name: name of new attribute
        @param value: value of new attribute
        '''
        if name[0] != '_' and (isinstance(value, Type) or isinstance(value, tuple)) and not self.__dict__.has_key(name):
            self._type.append(value)
        self.__dict__[name] = value
            
    def read(self, s):
        '''
        call read on each ordered subtype 
        @param s: Stream
        '''
        for i in self._type:
            s.readType(i)
            
    def write(self, s):
        '''
        call write on each ordered subtype
        @param s: Stream
        '''
        for i in self._type:
            s.writeType(i)
            
    def __sizeof__(self):
        '''
        call sizeof on each subtype$
        @return: sum of sizeof of each public type attributes
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
        SimpleType.__init__(self, "B", 1, False, value)

class SInt8(SimpleType):
    '''
    signed byte
    '''    
    def __init__(self, value = 0):
        SimpleType.__init__(self, "b", 1, True, value)
        
        
class UInt16Be(SimpleType):
    '''
    unsigned short with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, ">H", 2, False, value)
        
class UInt16Le(SimpleType):
    '''
    unsigned short with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, "<H", 2, False, value)
        
class UInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, ">I", 4, False, value)
        
class UInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, "<I", 4, False, value)
    
class SInt32Le(SimpleType):
    '''
    signed int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, "<I", 4, True, value)
        
class SInt32Be(SimpleType):
    '''
    signed int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, ">I", 4, True, value)
        
class UInt24Be(SimpleType):
    '''
    unsigned 24 bit int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, ">I", 3, False, value)
        
    def write(self, s):
        '''
        special write for a special type
        '''
        s.write(struct.pack(">I", self._value)[1:])
        
class UInt24Le(SimpleType):
    '''
    unsigned int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0):
        SimpleType.__init__(self, "<I", 3, False, value)   
            
    def write(self, s):
        '''
        special write for a special type
        @param s: Stream
        '''
        #don't write first byte
        s.write(struct.pack("<I", self._value)[1:])
        
class String(Type):
    '''
    String network type
    '''
    def __init__(self, value = ""):
        '''
        constructor with new string
        @param value: python string use for inner value
        '''
        self._value = value
        
    def __eq__(self, other):
        '''
        call raw compare value
        @param other: other String parameter
        @return: if two inner value are equals
        '''
        return self._value == other._value
    
    def __str__(self):
        '''
        call when str function is call
        @return: inner python string
        '''
        return self._value
    
    def write(self, s):
        '''
        write the entire raw value
        @param s: Stream
        '''
        s.write(self._value)
    
    def read(self, s):
        '''
        read all stream if len of inner value is zero
        else read the len of inner string
        @param s: Stream
        '''
        if len(self._value) == 0:
            self._value = s.getvalue()
        else:
            self._value = s.read(len(self._value))
        
    def __sizeof__(self):
        '''
        return len of string
        @return: len of inner string
        '''
        return len(self._value)
    

class Stream(StringIO):
    '''
    use string io inheritance
    but in future (for python 3)
    make your own stream class
    '''
    def dataLen(self):
        '''
        @return: not yet read length
        '''
        return self.len - self.pos
    
    def readType(self, value):
        '''
        call specific read on type object
        or iterate over tuple elements
        @param value: (tuple | Type) object
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
        @param t: Type element
        '''
        self.readType(t)
        self.pos -= sizeof(t)
    
    def writeType(self, value):
        '''
        call specific write on type object
        or iterate over tuple element
        @param value: (tuple | Type)
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