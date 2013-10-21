'''
@author: sylvain
'''

from rdpy.protocol.network.type import UInt8, UInt16Be, UInt32Be

def readLength(s):
    '''
    read length use in per specification
    @param s: Stream
    @return: UInt16Be
    '''
    byte = UInt8()
    s.readType(byte)
    size = None
    if (byte & UInt8(0x80)) == UInt8(0x80):
        byte &= ~UInt8(0x80)
        size = UInt16Be(byte.value << 8)
        s.readType(byte)
        size += s.value + byte
    else:
        size = UInt16Be(byte.value)
    return size