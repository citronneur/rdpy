#
# Copyright (c) 2014 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
All type use RDPY

It's a basic implementation that seems to protobuf but dynamically
We are in python we can use that!
"""

import struct
from copy import deepcopy
from StringIO import StringIO
from rdpy.base.error import InvalidExpectedDataException, InvalidSize, CallPureVirtualFuntion, InvalidValue
import rdpy.base.log as log

def sizeof(element):
    """
    Byte size of type sum sizeof of tuple element
    And count only element that condition is true at sizeof call
    @param element: Type or Tuple(Type | Tuple,)
    @return: size of element in byte
    """
    if isinstance(element, tuple) or isinstance(element, list):
        size = 0
        for i in element:
            size += sizeof(i)
        return size
    elif isinstance(element, Type) and element._conditional():
        return element.__sizeof__()
    return 0
            

class Type(object):
    """
    Root type object inheritance
    Record conditional optional of constant mechanism
    """
    def __init__(self, conditional = lambda:True, optional = False, constant = False):
        """
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any modification of object during reading
        """
        self._conditional = conditional
        self._optional = optional
        self._constant = constant
        #use to record read state
        #if type is optional and not present during read
        #this boolean stay false
        self._is_readed = False
        #use to know if type was written
        self._is_writed = False
        
    def write(self, s):
        """
        Write type into stream if conditional is true 
        Call virtual __write__ method 
        @param s: Stream which will be written
        """
        self._is_writed = self._conditional()
        if not self._is_writed:
            return
        self.__write__(s)
    
    def read(self, s):
        """
        Read type from stream s if conditional is true
        Check constantness
        @param s: Stream
        """
        self._is_readed = self._conditional()
        if not self._is_readed:
            return
        
        #not constant mode direct reading
        if not self._constant:
            self.__read__(s)
            return
        
        #constant mode
        old = deepcopy(self)
        self.__read__(s)
        #check constant value
        if old != self:
            #rollback read value
            s.pos -= sizeof(self)
            raise InvalidExpectedDataException("%s const value expected %s != %s"%(self.__class__, old.value, self.value))
        
    def __read__(self, s):
        """
        Interface definition of private read function
        @param s: Stream 
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "__read__", "Type"))
    
    def __write__(self, s):
        """
        Interface definition of private write function
        @param s: Stream 
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "__write__", "Type"))
    
    def __sizeof__(self):
        """
        Return size of type use for sizeof function
        @return: size in byte of type
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "__sizeof__", "Type"))
        
class CallableValue(object):
    """
    Wrap access of callable value.
    When use getter value is call.
    Constant value can also be wrap and will be transformed into callable value(lambda function)
    """
    def __init__(self, value):
        """
        @param value: value will be wrapped (constant | lambda | function)
        """
        self._value = None
        self.value = value
    
    def __getValue__(self):
        """
        Can be overwritten to add specific check before
        self.value is call
        @return: result of callable value
        """
        return self._value()
    
    def __setValue__(self, value):
        """
        Can be overwritten to add specific check before
        self.value = value is call
        Check if value is callable and if not transform it
        @param value: new value wrapped if constant -> lambda function
        """
        value_callable = lambda:value
        if callable(value):
            value_callable = value
            
        self._value = value_callable
    
    @property
    def value(self):
        """
        Shortcut to access inner value main getter of value
        @return: result of callable value
        """
        return self.__getValue__()
    
    @value.setter
    def value(self, value):
        """
        Setter of value after check it main setter of value
        @param value: new value encompass in value type object
        """
        self.__setValue__(value)

class SimpleType(Type, CallableValue):
    """
    Simple type
    """
    def __init__(self, structFormat, typeSize, signed, value, conditional = lambda:True, optional = False, constant = False):
        """
        @param structFormat: letter that represent type in struct package
        @param typeSize: size in byte of type
        @param signed: true if type represent a signed type
        @param value: value recorded in this object (can be callable value which be call when is access useful with closure)
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any modification of object during reading
        """
        self._signed = signed
        self._typeSize = typeSize
        self._structFormat = structFormat
        Type.__init__(self, conditional = conditional, optional = optional, constant = constant)
        CallableValue.__init__(self, value)
        
    def __getValue__(self):
        """
        CallableValue overwrite check mask type of value
        use CallableValue access
        @return: Python value wrap into type
        @raise InvalidValue: if value doesn't respect type range
        """
        value = CallableValue.__getValue__(self)
        if not self.isInRange(value):
            raise InvalidValue("value is out of range for %s"%self.__class__)
        
        if self._signed:
            return value
        else:
            return value & self.mask()

    def __setValue__(self, value):
        """
        CallableValue overwrite
        Check mask type of value
        @param value: new value encompass in object (respect Python type | lambda | function)
        @raise InvalidValue: if value doesn't respect type range
        """
        #check static value range
        if not callable(value) and not self.isInRange(value):
            raise InvalidValue("value is out of range for %s"%self.__class__)
        
        CallableValue.__setValue__(self, value)
            
    
    def __cmp__(self, other):
        """
        Compare inner value
        Magic function of Python use for any compare operators
        @param other: SimpleType value which will be compared with self value
        or try to construct same type as self around other value
        @return: Python value compare
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.value.__cmp__(other.value)
        
    def __write__(self, s):
        """
        Write value in stream s
        Use Struct package to pack value
        @param s: Stream which will be written
        """
        s.write(struct.pack(self._structFormat, self.value))
        
    def __read__(self, s):
        """
        Read inner value from stream
        Use struct package
        @param s: Stream
        """
        if s.dataLen() < self._typeSize:
            raise InvalidSize("Stream is too small to read expected data")
        self.value = struct.unpack(self._structFormat, s.read(self._typeSize))[0]
      
    def mask(self):
        """
        Compute bit mask for type
        Because in Python all numbers are Int long or float
        """
        if not self.__dict__.has_key("_mask"):
            mask = 0xff
            for _ in range(1, self._typeSize):
                mask = mask << 8 | 0xff
            self._mask = mask
        return self._mask
    
    def isInRange(self, value):
        """
        Check if value is in mask range
        @param value: Python value
        @return: true if value is in type range
        """
        if self._signed:
            return not (value < -(self.mask() >> 1) or value > (self.mask() >> 1))
        else:
            return not (value < 0 or value > self.mask())
        
    def __sizeof__(self):
        """
        Return size of type
        @return: typeSize pass in constructor
        """
        return self._typeSize
    
    def __invert__(self):
        """
        Implement not operator
        @return: __class__ value
        """
        invert = ~self.value
        if not self._signed:
            invert &= self.mask()
        return self.__class__(invert)
    
    def __add__(self, other):
        """
        Implement addition operator
        @param other: SimpleType value or try to construct same type as self
        around other value
        @return: self.__class__ object with add result
        @raise InvalidValue: if new value is out of bound
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__add__(other.value))
    
    def __sub__(self, other):
        """
        Implement sub operator
        @param other: SimpleType value or try to construct same type as self
        around other value
        @return: self.__class__ object with sub result
        @raise InvalidValue: if new value is out of bound
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__sub__(other.value))
    
    def __and__(self, other):
        """
        Implement bitwise and operator
        @param other: SimpleType value or try to construct same type as self
        around other value
        @return: self.__class__ object with and result
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__and__(other.value))
    
    def __or__(self, other):
        """
        implement bitwise or operator
        @param other: SimpleType value or try to construct same type as self
        around other value
        @return: self.__class__ object with or result
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__or__(other.value))
    
    def __xor__(self, other):
        """
        Implement bitwise xor operator
        @param other: SimpleType value or try to construct same type as self
        around other value
        @return: self.__class__ object with or result
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__xor__(other.value))
    
    def __lshift__(self, other):
        """
        Left shift operator
        @param other: Python Int
        @return: self.__class__ object with or result
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__lshift__(other.value))
    
    def __rshift__(self, other):
        """
        Left shift operator
        @param other: python int
        @return: self.__class__ object with or result
        """
        if not isinstance(other, SimpleType):
            other = self.__class__(other)
        return self.__class__(self.value.__rshift__(other.value))
    
    def __hash__(self):
        """
        Hash function to treat simple type in hash collection
        @return: hash of inner value
        """
        return hash(self.value)
    
    def __nonzero__(self):
        """
        Boolean conversion
        @return: bool of inner value
        """
        return bool(self.value)

        
class CompositeType(Type):
    """
    Type node of other sub type
    """
    def __init__(self, conditional = lambda:True, optional = False, constant = False, readLen = None):
        """
        Keep ordering declaration of simple type
        in list and transparent for other type
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changing of object during reading
        @param readLen: max length to read
        """
        Type.__init__(self, conditional = conditional, optional = optional, constant = constant)
        #list of ordoned type
        self._typeName = []
        self._readLen = readLen
    
    def __setattr__(self, name, value):
        """
        Magic function to update type list
        @param name: name of new attribute
        @param value: value of new attribute
        """
        if name[0] != '_' and (isinstance(value, Type) or isinstance(value, tuple)) and not name in self._typeName:
            self._typeName.append(name)
        self.__dict__[name] = value
            
    def __read__(self, s):
        """
        Call read on each ordered sub-type
        @param s: Stream
        """
        readLen = 0
        for name in self._typeName:            
            try:
                s.readType(self.__dict__[name])
                readLen += sizeof(self.__dict__[name])
                #read is ok but read out of bound
                if not self._readLen is None and readLen > self._readLen.value:
                    #roll back
                    s.pos -= sizeof(self.__dict__[name])
                    #and notify
                    raise InvalidSize("Impossible to read type %s : read length is too small"%(self.__class__))
                
            except Exception as e:
                log.error("Error during read %s::%s"%(self.__class__, name))
                #roll back already read
                for tmpName in self._typeName:
                    if tmpName == name:
                        break
                    s.pos -= sizeof(self.__dict__[tmpName])
                raise e
        if not self._readLen is None and readLen < self._readLen.value:
            log.warning("still have correct data in packet %s, read it as padding"%self.__class__)
            s.read(self._readLen.value - readLen)
            
    def __write__(self, s):
        """
        Call write on each ordered sub type
        @param s: Stream
        """
        for name in self._typeName:
            try:
                s.writeType(self.__dict__[name])
            except Exception as e:
                log.error("Error during write %s::%s"%(self.__class__, name))
                raise e
            
    def __sizeof__(self):
        """
        Call sizeof on each sub type
        @return: sum of sizeof of each public type attributes
        """
        size = 0
        for name in self._typeName:
            size += sizeof(self.__dict__[name])
        return size

    def __eq__(self, other):
        '''
        compare each properties which are Type inheritance
        if one is different then not equal
        @param other: CompositeType
        @return: True if each subtype are equals
        '''
        if self._typeName != other._typeName:
            return False
        for name in self._typeName:
            if self.__dict__[name] != other.__dict__[name]:
                return False
        return True
    
    def __ne__(self, other):
        '''
        return not equal result operator
        @param other: CompositeType
        @return: False if each subtype are equals
        '''
        return not self.__eq__(other)

class UInt8(SimpleType):
    '''
    unsigned byte
    '''    
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param value: python value wrap
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "B", 1, False, value, conditional = conditional, optional = optional, constant = constant)

class SInt8(SimpleType):
    '''
    signed byte
    '''    
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "b", 1, True, value, conditional = conditional, optional = optional, constant = constant)
        
        
class UInt16Be(SimpleType):
    '''
    unsigned short with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, ">H", 2, False, value, conditional = conditional, optional = optional, constant = constant)
        
class UInt16Le(SimpleType):
    '''
    unsigned short with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "<H", 2, False, value, conditional = conditional, optional = optional, constant = constant)
        
class UInt32Be(SimpleType):
    '''
    unsigned int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, ">I", 4, False, value, conditional = conditional, optional = optional, constant = constant)
        
class UInt32Le(SimpleType):
    '''
    unsigned int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "<I", 4, False, value, conditional = conditional, optional = optional, constant = constant)
    
class SInt32Le(SimpleType):
    '''
    signed int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "<I", 4, True, value, conditional = conditional, optional = optional, constant = constant)
        
class SInt32Be(SimpleType):
    '''
    signed int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, ">I", 4, True, value, conditional = conditional, optional = optional, constant = constant)
        
class UInt24Be(SimpleType):
    '''
    unsigned 24 bit int with big endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, ">I", 3, False, value, conditional = conditional, optional = optional, constant = constant)
        
    def __write__(self, s):
        '''
        special write for a special type
        @param s: Stream
        '''
        s.write(struct.pack(">I", self.value)[1:])
        
    def __read__(self, s):
        '''
        special read for a special type
        @param s: Stream
        '''
        self.value = struct.unpack(self._structFormat, '\x00' + s.read(self._typeSize))[0]
        
class UInt24Le(SimpleType):
    '''
    unsigned int with little endian representation
    @attention: inner value is in machine representation
    Big endian is just for read or write in stream
    '''
    def __init__(self, value = 0, conditional = lambda:True, optional = False, constant = False):
        '''
        constructor
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        '''
        SimpleType.__init__(self, "<I", 3, False, value, conditional = conditional, optional = optional, constant = constant)   
            
    def __write__(self, s):
        '''
        special write for a special type
        @param s: Stream
        '''
        #don't write first byte
        s.write(struct.pack("<I", self.value)[:3])
        
    def __read__(self, s):
        '''
        special read for a special type
        @param s: Stream
        '''
        self.value = struct.unpack(self._structFormat, s.read(self._typeSize) + '\x00')[0]
        
class String(Type, CallableValue):
    '''
    String network type
    '''
    def __init__(self, value = "", readLen = UInt32Le(), conditional = lambda:True, optional = False, constant = False, unicode = False):
        '''
        constructor with new string
        @param value: python string use for inner value
        @param readLen: length use to read in stream (SimpleType) if 0 read entire stream
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changement of object during reading
        @param unicode: Encode and decode value as unicode
        '''
        Type.__init__(self, conditional = conditional, optional = optional, constant = constant)
        CallableValue.__init__(self, value)
        #type use to know read length
        self._readLen = readLen
        self._unicode = unicode
        
    def __eq__(self, other):
        '''
        call raw compare value
        @param other: other String parameter
        @return: if two inner value are equals
        '''
        return self.value == other.value
    
    def __hash__(self):
        '''
        hash function to treat simple type in hash collection
        @return: hash of inner value
        '''
        return hash(self.value)
    
    def __str__(self):
        '''
        call when str function is call
        @return: inner python string
        '''
        return self.value
    
    def __write__(self, s):
        """
        Write the entire raw value
        @param s: Stream
        """
        if self._unicode:
            s.write(encodeUnicode(self.value))
        else:
            s.write(self.value)
    
    def __read__(self, s):
        """
        read all stream if length of inner value is zero
        else read the length of inner string
        @param s: Stream
        """
        if self._readLen.value == 0:
            self.value = s.getvalue()
        else:
            self.value = s.read(self._readLen.value)
        
        if self._unicode:
            self.value = decodeUnicode(self.value)
        
    def __sizeof__(self):
        """
        return length of string
        @return: length of inner string
        """
        if self._unicode:
            return 2 * len(self.value) + 2
        else:
            return len(self.value)
    
def encodeUnicode(s):
    """
    Encode string in unicode
    @param s: str python
    @return: unicode string
    """
    return "".join([c + "\x00" for c in s]) + "\x00\x00"

def decodeUnicode(s):
    """
    Decode Unicode string
    @param s: unicode string
    @return: str python
    """
    i = 0
    r = ""
    while i < len(s) - 2:
        if i % 2 == 0:
            r += s[i]
        i += 1
    return r

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
    
    def readLen(self):
        '''
        compute already read size
        @return: read size of stream
        '''
        return self.pos
    
    def readType(self, value):
        '''
        call specific read on type object
        or iterate over tuple elements
        @param value: (tuple | Type) object
        '''
        #read each tuple
        if isinstance(value, tuple) or isinstance(value, list):
            for element in value:
                try:
                    self.readType(element)
                except Exception as e:
                    #rollback already readed elements
                    for tmpElement in value:
                        if tmpElement == element:
                            break
                        self.pos -= sizeof(tmpElement)
                    raise e
            return
        
        #optional value not present
        if self.dataLen() == 0 and value._optional:
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
        if isinstance(value, tuple) or isinstance(value, list):
            for element in value:
                self.writeType(element)
            return
        value.write(self)
        
class ArrayType(Type):
    """
    In write mode ArrayType is just list
    But in read mode it can be dynamic
    readLen may be dynamic
    """
    def __init__(self, typeFactory, init = None, readLen = None, conditional = lambda:True, optional = False, constant = False):
        """
        @param typeFactory: class use to init new element on read
        @param init: init array
        @param readLen: number of element in sequence
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changes of object during reading
        """
        Type.__init__(self, conditional, optional, constant)
        self._typeFactory = typeFactory
        self._readLen = readLen
        self._array = []
        if not init is None:
            self._array = init
        
    def __read__(self, s):
        """
        Create new object and read it
        @param s: Stream
        """
        self._array = []
        i = 0
        #self._readLen is None means that array will be read until end of stream
        while self._readLen is None or i < self._readLen.value:
            element = self._typeFactory()
            element._optional = self._readLen is None
            s.readType(element)
            if not element._is_readed:
                break
            self._array.append(element)
            i += 1
    
    def __write__(self, s):
        """
        Just write array
        @param s: Stream
        """
        s.writeType(self._array)
    
    def __sizeof__(self):
        """
        Size of inner array
        """
        return sizeof(self._array)
    
class FactoryType(Type):
    """
    Call factory function on read
    """
    def __init__(self, factory, conditional = lambda:True, optional = False, constant = False):
        """
        @param factory: factory
        @param conditional : function call before read or write type
        @param optional: boolean check before read if there is still data in stream
        @param constant: if true check any changes of object during reading
        """
        Type.__init__(self, conditional, optional, constant)
        self._factory = factory
        if not callable(factory):
            self._factory = lambda:factory

        self._value = None
    
    def __read__(self, s):
        """
        Call factory and write it
        @param s: Stream
        """
        self._value = self._factory()
        s.readType(self._value)
        
    def __write__(self, s):
        """
        Call factory and read it
        @param s: Stream
        """
        self._value = self._factory()
        s.writeType(self._value)
    
    def __getattr__(self, name):
        """
        Magic function to be FactoryType as transparent as possible
        @return: _value parameter
        """
        return self._value.__getattribute__(name)
    
    def __getitem__(self, item):
        """
        Magic function to be FactoryType as transparent as possible
        @return: index of _value
        """
        return self._value.__getitem__(item)
    
    def __sizeof__(self):
        """
        Size of of object returned by factory
        """
        return sizeof(self._value)

def CheckValueOnRead(cls):
    '''
    wrap read method of class
    to check value on read
    if new value is different from old value
    raise InvalidValue
    @param cls: class that inherit from Type
    '''
    oldRead = cls.read
    def read(self, s):
        old = deepcopy(self)
        oldRead(self, s)
        if self != old:
            raise InvalidValue("CheckValueOnRead %s != %s"%(self, old))
    cls.read = read
    return cls