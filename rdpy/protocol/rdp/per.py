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
Per encoded function
"""

from rdpy.core.type import UInt8, UInt16Be, UInt32Be, String
from rdpy.core.error import InvalidValue, InvalidExpectedDataException

def readLength(s):
    """
    @summary: read length use in per specification
    @param s: Stream
    @return: int python
    """
    byte = UInt8()
    s.readType(byte)
    size = 0
    if byte.value & 0x80:
        byte.value &= ~0x80
        size = byte.value << 8
        s.readType(byte)
        size += byte.value
    else:
        size = byte.value
    return size

def writeLength(value):
    """
    @summary: write length as expected in per specification
    @param value: int or long python
    @return: UInt8, UInt16Be depend on value
    """
    if value > 0x7f:
        return UInt16Be(value | 0x8000)
    else:
        return UInt8(value)
    
def readChoice(s):
    """
    @summary: read per choice format
    @param s: Stream
    @return: int that represent choice
    """
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeChoice(choice):
    """
    @summary: read per choice structure
    @param choice: int choice value
    @return: UInt8
    """
    return UInt8(choice)

def readSelection(s):
    """
    @summary: read per selection format
    @param s: Stream
    @return: int that represent selection
    """
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeSelection(selection):
    """
    @summary: read per selection structure
    @param selection: int selection value
    @return: UInt8
    """
    return UInt8(selection)

def readNumberOfSet(s):
    """
    @summary: read per numberOfSet format
    @param s: Stream
    @return: int that represent numberOfSet
    """
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeNumberOfSet(numberOfSet):
    """
    @summary: read per numberOfSet structure
    @param numberOfSet: int numberOfSet value
    @return: UInt8
    """
    return UInt8(numberOfSet)

def readEnumerates(s):
    """
    @summary: read per enumerate format
    @param s: Stream
    @return: int that represent enumerate
    """
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeEnumerates(enumer):
    """
    @summary: read per enumerate structure
    @param enumer: int enumerate value
    @return: UInt8
    """
    return UInt8(enumer)

def readInteger(s):
    """
    @summary: read interger per format from stream
    @param s: Stream
    @return: python int or long
    @raise InvalidValue: if size of integer is not correct
    """
    result = None
    size = readLength(s)
    if size == 1:
        result = UInt8()
    elif size == 2:
        result = UInt16Be()
    elif size == 4:
        result = UInt32Be()
    else:
        raise InvalidValue("invalid integer size %d"%size)
    s.readType(result)
    return result.value

def writeInteger(value):
    """
    @summary: write python long or int into per integer format
    @param value: int or long python value
    @return: UInt8, UInt16Be or UInt32Be
    """
    if value <= 0xff:
        return (writeLength(1), UInt8(value))
    elif value < 0xffff:
        return (writeLength(2), UInt16Be(value))
    else:
        return (writeLength(4), UInt32Be(value))
    
def readInteger16(s, minimum = 0):
    """
    @summary: read UInt16Be from stream s and add minimum
    @param s: Stream
    @param minimum: minimum added to real value
    @return: int or long python value
    """
    result = UInt16Be()
    s.readType(result)
    return result.value + minimum

def writeInteger16(value, minimum = 0):
    """
    @summary: write UInt16Be minus minimum
    @param value: value to write
    @param minimum: value subtracted to real value
    @return: UInt16Be
    """
    return UInt16Be(value - minimum)

def readObjectIdentifier(s, oid):
    """
    @summary: read object identifier
    @param oid: must be a tuple of 6 elements
    @param s: Stream
    @return: true if oid is same as in stream
    """
    size = readLength(s)
    if size != 5:
        raise InvalidValue("size of stream oid is wrong %d != 5"%size)
    a_oid = [0, 0, 0, 0, 0, 0]
    t12 = UInt8()
    s.readType(t12)
    a_oid[0] = t12.value >> 4
    a_oid[1] = t12.value & 0x0f
    s.readType(t12)
    a_oid[2] = t12.value
    s.readType(t12)
    a_oid[3] = t12.value
    s.readType(t12)
    a_oid[4] = t12.value
    s.readType(t12)
    a_oid[5] = t12.value
    
    if list(oid) != a_oid:
        raise InvalidExpectedDataException("invalid object identifier")

def writeObjectIdentifier(oid):
    """
    @summary: Create tuple of 6 UInt8 with oid values
    @param oid: tuple of 6 int
    @return: (UInt8, UInt8, UInt8, UInt8, UInt8, UInt8, UInt8)
    """
    return (UInt8(5), UInt8((oid[0] << 4) & (oid[1] & 0x0f)), UInt8(oid[2]), UInt8(oid[3]), UInt8(oid[4]), UInt8(oid[5]))

def readNumericString(s, minValue):
    """
    @summary: Read numeric string
    @param s: Stream
    @param minValue: offset
    """
    length = readLength(s)
    length = (length + minValue + 1) / 2
    s.read(length)

def writeNumericString(nStr, minValue):
    """
    @summary: write string in per format
    @param str: python string to write
    @param min: min value
    @return: String type that contain str encoded in per format
    """
    length = len(nStr)
    mlength = minValue
    if length - minValue >= 0:
        mlength = length - minValue
    
    result = []
    
    for i in range(0, length, 2):
        c1 = ord(nStr[i])
        if i + 1 < length:
            c2 = ord(nStr[i + 1])
        else:
            c2 = 0x30
        c1 = (c1 - 0x30) % 10
        c2 = (c2 - 0x30) % 10
        
        result.append(UInt8((c1 << 4) | c2))
    
    return (writeLength(mlength), tuple(result))

def readPadding(s, length):
    """
    @summary: read length byte in stream
    @param s: Stream
    @param length: length of passing in bytes
    """
    s.read(length)

def writePadding(length):
    """
    @summary: create string with null char * length
    @param length: length of padding
    @return: String with \x00 * length
    """
    return String("\x00"*length)

def readOctetStream(s, octetStream, minValue = 0):
    """
    @summary: read string as octet stream and compare with octetStream
    @param octetStream: compare stream
    @param s: Stream
    @param minValue: min value
    @return: if stream read from s is equal to octetStream
    """
    size = readLength(s) + minValue
    if size != len(octetStream):
        raise InvalidValue("incompatible size %d != %d"(len(octetStream), size))
    for i in range(0, size):
        c = UInt8()
        s.readType(c)
        if ord(octetStream[i]) != c.value:
            return False
        
    return True

def writeOctetStream(oStr, minValue = 0):
    """
    @summary: write string as octet stream with per header
    @param oStr: octet stream to convert
    @param minValue: min length value
    @return: per header follow by tuple of UInt8
    """
    length = len(oStr)
    mlength = minValue
    
    if length - minValue >= 0:
        mlength = length - minValue
    
    result = []
    for i in range(0, length):
        result.append(UInt8(ord(oStr[i])))
    
    return (writeLength(mlength), tuple(result))