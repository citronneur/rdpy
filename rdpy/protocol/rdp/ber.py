'''
@author: sylvain
'''
from rdpy.protocol.network.type import UInt8, UInt16Be
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
    '''
    if pc:
        return BerPc.BER_CONSTRUCT
    else:
        return BerPc.BER_PRIMITIVE
    
def readLength(s):
    '''
    read length of ber structure
    length be on 1 2 or 3 bytes
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
    return size

def writeLength(size):
    '''
    return strcture length as expected in Ber specification
    '''
    if size > UInt16Be(0x7f):
        return (UInt8(0x82), size)
    else:
        return UInt8(size.value)
    
def readUniversalTag(s, tag, pc):
    '''
    read tag of ber packet
    '''
    byte = UInt8()
    s.readType(byte)
    return byte == (Class.BER_CLASS_UNIV | berPC(pc) | (Tag.BER_TAG_MASK & tag))

def writeUniversalTag(tag, pc):
    '''
    return universal tag byte
    '''
    return (Class.BER_CLASS_UNIV | berPC(pc) | (Tag.BER_TAG_MASK & tag))

def readApplicationTag(s, tag):
    '''
    read application tag
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
    '''
    if tag > UInt8(30):
        return (((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | Tag.BER_TAG_MASK), tag, writeLength(size))
    else:
        return (((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | (Tag.BER_TAG_MASK & tag)), writeLength(size))
    
def readBoolean(s):
    '''
    return boolean
    '''
    if not readUniversalTag(s, Tag.BER_TAG_BOOLEAN, False):
        raise InvalidExpectedDataException("bad boolean tag")
    size = readLength(s)
    if size != UInt8(1):
        raise InvalidExpectedDataException("bad boolean size")
    b = UInt8()
    s.readType(b)
    return bool(b.value)

def writeBoolean(b):
    '''
    return structure that represent boolean in ber specification
    '''
    return (writeUniversalTag(Tag.BER_TAG_BOOLEAN, False), writeLength(UInt8(1)), UInt8(int(b)))