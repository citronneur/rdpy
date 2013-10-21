'''
@author: sylvain
'''
from rdpy.protocol.network.type import UInt8, UInt16Be, UInt32Be, String
from rdpy.utils.const import ConstAttributes
from rdpy.protocol.network.error import InvalidExpectedDataException

@ConstAttributes
class BerPc(object):
    BER_PC_MASK = UInt8(0x20)
    BER_PRIMITIVE = UInt8(0x00)
    BER_CONSTRUCT = UInt8(0x20)

@ConstAttributes  
class Class(object):
    BER_CLASS_MASK = UInt8(0xC0)
    BER_CLASS_UNIV = UInt8(0x00)
    BER_CLASS_APPL = UInt8(0x40)
    BER_CLASS_CTXT = UInt8(0x80)
    BER_CLASS_PRIV = UInt8(0xC0)
    
@ConstAttributes     
class Tag(object):
    BER_TAG_MASK = UInt8(0x1F)
    BER_TAG_BOOLEAN = UInt8(0x01)
    BER_TAG_INTEGER = UInt8(0x02)
    BER_TAG_BIT_STRING = UInt8(0x03)
    BER_TAG_OCTET_STRING = UInt8(0x04)
    BER_TAG_OBJECT_IDENFIER = UInt8(0x06)
    BER_TAG_ENUMERATED = UInt8(0x0A)
    BER_TAG_SEQUENCE = UInt8(0x10)
    BER_TAG_SEQUENCE_OF = UInt8(0x10)

def berPC(pc):
    '''
    return BER_CONSTRUCT if true
    BER_PRIMITIVE if false
    @param pc: boolean
    @return: BerPc value
    '''
    if pc:
        return BerPc.BER_CONSTRUCT
    else:
        return BerPc.BER_PRIMITIVE
    
def readLength(s):
    '''
    read length of ber structure
    length be on 1 2 or 3 bytes
    @param s: stream
    @return: int or python long
    '''
    size = None
    byte = UInt8()
    s.readType(byte)
    if (byte & UInt8(0x80)) == UInt8(0x80):
        byte &= ~UInt8(0x80)
        if byte == UInt8(1):
            size = UInt8()
        elif byte == UInt8(2):
            size = UInt16Be()
        else:
            raise InvalidExpectedDataException("ber length may be 1 or 2")
        s.readType(size)
    else:
        size = byte
    return size.value

def writeLength(size):
    '''
    return strcture length as expected in Ber specification
    @param size: int or python long
    @return: UInt8 or (UInt8(0x82), UInt16Be)
    '''
    if size > 0x7f:
        return (UInt8(0x82), UInt16Be(size))
    else:
        return UInt8(size)
    
def readUniversalTag(s, tag, pc):
    '''
    read tag of ber packet
    @param tag: Tag class attributes
    @param pc: boolean
    @return: true if tag is correctly read
    '''
    byte = UInt8()
    s.readType(byte)
    return byte == (Class.BER_CLASS_UNIV | berPC(pc) | (Tag.BER_TAG_MASK & tag))

def writeUniversalTag(tag, pc):
    '''
    return universal tag byte
    @param tag: tag class attributes
    @param pc: boolean
    @return: UInt8 
    '''
    return (Class.BER_CLASS_UNIV | berPC(pc) | (Tag.BER_TAG_MASK & tag))

def readApplicationTag(s, tag):
    '''
    read application tag
    @param s: stream
    @param tag: tag class attributes
    @return: length of application packet
    '''
    byte = UInt8()
    s.readType(byte)
    if tag > UInt8(30):
        if byte != ((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | Tag.BER_TAG_MASK):
            raise InvalidExpectedDataException()
        s.readType(byte)
        if byte != tag:
            raise InvalidExpectedDataException("bad tag")
    else:
        if byte != ((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | (Tag.BER_TAG_MASK & tag)):
            raise InvalidExpectedDataException()
        
    return readLength(s)

def writeApplicationTag(tag, size):
    '''
    return struct that represent ber application tag
    @param tag: tag class attribute
    @param size: size to rest of packet  
    '''
    if tag > UInt8(30):
        return (((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | Tag.BER_TAG_MASK), tag, writeLength(size))
    else:
        return (((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | (Tag.BER_TAG_MASK & tag)), writeLength(size))
    
def readBoolean(s):
    '''
    return boolean
    @param s: stream
    @return: boolean
    '''
    if not readUniversalTag(s, Tag.BER_TAG_BOOLEAN, False):
        raise InvalidExpectedDataException("bad boolean tag")
    size = readLength(s)
    if size != 1:
        raise InvalidExpectedDataException("bad boolean size")
    b = UInt8()
    s.readType(b)
    return bool(b.value)

def writeBoolean(b):
    '''
    return structure that represent boolean in ber specification
    @param b: boolean
    @return: ber boolean structure
    '''
    return (writeUniversalTag(Tag.BER_TAG_BOOLEAN, False), writeLength(1), UInt8(int(b)))

def readInteger(s):
    '''
    read integer structure from stream
    @param s: stream
    @return: int or long python
    '''
    if not readUniversalTag(s, Tag.BER_TAG_INTEGER, False):
        raise InvalidExpectedDataException("bad integer tag")
    
    size = readLength(s)
    
    if size == 1:
        integer = UInt8()
        s.readType(integer)
        return integer.value
    elif size == 2:
        integer = UInt16Be()
        s.readType(integer)
        return integer.value
    elif size == 3:
        integer1 = UInt8()
        integer2 = UInt16Be()
        s.readType(integer1)
        s.readType(integer2)
        return integer2.value + (integer1.value << 16)
    elif size == 4:
        integer = UInt32Be()
        s.readType(integer)
        return integer.value
    else:
        raise InvalidExpectedDataException("wrong integer size")
    
def writeInteger(value):
    '''
    write integer value
    @param param: UInt32Be
    @return ber interger structure 
    '''
    if value < UInt32Be(0xff):
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(1), UInt8(value.value))
    elif value < UInt32Be(0xff80):
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(2), UInt16Be(value.value))
    else:
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(4), UInt32Be(value.value))

def readOctetString(s):
    '''
    read ber string structure
    @param s: stream
    @return: String
    '''
    if not readUniversalTag(s, Tag.BER_TAG_OCTET_STRING, False):
        raise InvalidExpectedDataException("unexpected ber tag")
    size = readLength(s)
    return String(s.read(size.value))

def writeOctetstring(value):
    '''
    write string in ber representation
    @param value: String
    @return: string ber structure 
    '''
    return (writeUniversalTag(Tag.BER_TAG_OCTET_STRING, False), writeLength(len(value.value)), value)

def readEnumerated(s):
    '''
    read enumerated structure
    @param s: Stream
    @return: int or long
    '''
    if not readUniversalTag(s, Tag.BER_TAG_ENUMERATED, False):
        raise InvalidExpectedDataException("invalid ber tag")
    size = readLength(s)
    if size != UInt32Be(1):
        raise InvalidExpectedDataException("enumerate size is wrong")
    enumer = UInt8()
    s.readType(enumer)
    return enumer.value
