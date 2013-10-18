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
    write length as expected in Ber specification
    '''
    if size > UInt16Be(0x7f):
        return (UInt8(0x82), size)
    else:
        return UInt8(size.value)