#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
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
Basic Encoding Rules use in RDP.
ASN.1 standard
"""

from rdpy.core.type import UInt8, UInt16Be, UInt32Be, String
from rdpy.core.error import InvalidExpectedDataException, InvalidSize

class BerPc(object):
    BER_PC_MASK = 0x20
    BER_PRIMITIVE = 0x00
    BER_CONSTRUCT = 0x20

class Class(object):
    BER_CLASS_MASK = 0xC0
    BER_CLASS_UNIV = 0x00
    BER_CLASS_APPL = 0x40
    BER_CLASS_CTXT = 0x80
    BER_CLASS_PRIV = 0xC0
        
class Tag(object):
    BER_TAG_MASK = 0x1F
    BER_TAG_BOOLEAN = 0x01
    BER_TAG_INTEGER = 0x02
    BER_TAG_BIT_STRING = 0x03
    BER_TAG_OCTET_STRING = 0x04
    BER_TAG_OBJECT_IDENFIER = 0x06
    BER_TAG_ENUMERATED = 0x0A
    BER_TAG_SEQUENCE = 0x10
    BER_TAG_SEQUENCE_OF = 0x10

def berPC(pc):
    """
    @summary: Return BER_CONSTRUCT if true
    BER_PRIMITIVE if false
    @param pc: boolean
    @return: BerPc value
    """
    if pc:
        return BerPc.BER_CONSTRUCT
    else:
        return BerPc.BER_PRIMITIVE
    
def readLength(s):
    """
    @summary: Read length of BER structure
    length be on 1 2 or 3 bytes
    @param s: stream
    @return: int or Python long
    """
    size = None
    length = UInt8()
    s.readType(length)
    byte = length.value
    if byte & 0x80:
        byte &= ~0x80
        if byte == 1:
            size = UInt8()
        elif byte == 2:
            size = UInt16Be()
        else:
            raise InvalidExpectedDataException("BER length may be 1 or 2")
        s.readType(size)
    else:
        size = length
    return size.value

def writeLength(size):
    """
    @summary: Return structure length as expected in BER specification
    @param size: int or python long
    @return: UInt8 or (UInt8(0x82), UInt16Be)
    """
    if size > 0x7f:
        return (UInt8(0x82), UInt16Be(size))
    else:
        return UInt8(size)
    
def readUniversalTag(s, tag, pc):
    """
    @summary: Read tag of BER packet
    @param tag: Tag class attributes
    @param pc: boolean
    @return: true if tag is correctly read
    """
    byte = UInt8()
    s.readType(byte)
    return byte.value == ((Class.BER_CLASS_UNIV | berPC(pc)) | (Tag.BER_TAG_MASK & tag))

def writeUniversalTag(tag, pc):
    """
    @summary: Return universal tag byte
    @param tag: tag class attributes
    @param pc: boolean
    @return: UInt8 
    """
    return UInt8((Class.BER_CLASS_UNIV | berPC(pc)) | (Tag.BER_TAG_MASK & tag))

def readApplicationTag(s, tag):
    """
    @summary: Read application tag
    @param s: stream
    @param tag: tag class attributes
    @return: length of application packet
    """
    byte = UInt8()
    s.readType(byte)
    if tag.value > 30:
        if byte.value != ((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | Tag.BER_TAG_MASK):
            raise InvalidExpectedDataException()
        s.readType(byte)
        if byte.value != tag.value:
            raise InvalidExpectedDataException("bad tag")
    else:
        if byte.value != ((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | (Tag.BER_TAG_MASK & tag)):
            raise InvalidExpectedDataException()
        
    return readLength(s)

def writeApplicationTag(tag, size):
    """
    @summary: Return structure that represent BER application tag
    @param tag: int python that match an uint8(0xff)
    @param size: size to rest of packet  
    """
    if tag > 30:
        return (UInt8((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | Tag.BER_TAG_MASK), UInt8(tag), writeLength(size))
    else:
        return (UInt8((Class.BER_CLASS_APPL | BerPc.BER_CONSTRUCT) | (Tag.BER_TAG_MASK & tag)), writeLength(size))
    
def readBoolean(s):
    """
    @summary: Return boolean
    @param s: stream
    @return: boolean
    """
    if not readUniversalTag(s, Tag.BER_TAG_BOOLEAN, False):
        raise InvalidExpectedDataException("bad boolean tag")
    size = readLength(s)
    if size != 1:
        raise InvalidExpectedDataException("bad boolean size")
    b = UInt8()
    s.readType(b)
    return bool(b.value)

def writeBoolean(b):
    """
    @summary: Return structure that represent boolean in BER specification
    @param b: boolean
    @return: BER boolean block
    """
    boolean = UInt8(0)
    if b:
        boolean = UInt8(0xff)
    return (writeUniversalTag(Tag.BER_TAG_BOOLEAN, False), writeLength(1), boolean)

def readInteger(s):
    """
    @summary: Read integer structure from stream
    @param s: stream
    @return: int or long python
    """
    if not readUniversalTag(s, Tag.BER_TAG_INTEGER, False):
        raise InvalidExpectedDataException("Bad integer tag")
    
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
        raise InvalidExpectedDataException("Wrong integer size")
    
def writeInteger(value):
    """
    @summary: Write integer value
    @param param: INT or Python long
    @return: BER integer block 
    """
    if value <= 0xff:
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(1), UInt8(value))
    elif value <= 0xffff:
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(2), UInt16Be(value))
    else:
        return (writeUniversalTag(Tag.BER_TAG_INTEGER, False), writeLength(4), UInt32Be(value))

def readOctetString(s):
    """
    @summary: Read BER string structure
    @param s: stream
    @return: string python
    """
    if not readUniversalTag(s, Tag.BER_TAG_OCTET_STRING, False):
        raise InvalidExpectedDataException("Unexpected BER tag")
    size = readLength(s)
    return s.read(size)

def writeOctetstring(value):
    """
    @summary: Write string in BER representation
    @param value: string
    @return: BER octet string block 
    """
    return (writeUniversalTag(Tag.BER_TAG_OCTET_STRING, False), writeLength(len(value)), String(value))

def readEnumerated(s):
    """
    @summary: Read enumerated structure
    @param s: Stream
    @return: int or long
    """
    if not readUniversalTag(s, Tag.BER_TAG_ENUMERATED, False):
        raise InvalidExpectedDataException("invalid ber tag")
    if readLength(s) != 1:
        raise InvalidSize("enumerate size is wrong")
    enumer = UInt8()
    s.readType(enumer)
    return enumer.value

def writeEnumerated(enumerated):
    """
    @summary: Write enumerated structure
    @param s: Stream
    @return: BER enumerated block 
    """
    return (writeUniversalTag(Tag.BER_TAG_ENUMERATED, False), writeLength(1), UInt8(enumerated))