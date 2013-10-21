'''
@author: sylvain
'''

from rdpy.protocol.network.type import UInt8, UInt16Be, UInt32Be, String, Stream
from rdpy.protocol.network.error import InvalidValue, InvalidExpectedDataException

def readLength(s):
    '''
    read length use in per specification
    @param s: Stream
    @return: int python
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
    return size.value

def writeLength(value):
    '''
    write length as expected in per specification
    @param value: int or long python
    @return: UInt8, UInt16Be depend on value
    '''
    if value > 0x7f:
        return UInt16Be(value | 0x8000)
    else:
        return UInt8(value)
    
def readChoice(s):
    '''
    read per choice format
    @param s: Stream
    @return: int that represent choice
    '''
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeChoice(choice):
    '''
    read per choice structure
    @param choice: int choice value
    @return: UInt8
    '''
    return UInt8(choice)

def readSelection(s):
    '''
    read per selection format
    @param s: Stream
    @return: int that represent selection
    '''
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeSelection(selection):
    '''
    read per selection structure
    @param selection: int selection value
    @return: UInt8
    '''
    return UInt8(selection)

def readNumberOfSet(s):
    '''
    read per numberOfSet format
    @param s: Stream
    @return: int that represent numberOfSet
    '''
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeNumberOfSet(numberOfSet):
    '''
    read per numberOfSet structure
    @param numberOfSet: int numberOfSet value
    @return: UInt8
    '''
    return UInt8(numberOfSet)

def readEnumerates(s):
    '''
    read per enumerate format
    @param s: Stream
    @return: int that represent enumerate
    '''
    choice = UInt8()
    s.readType(choice)
    return choice.value

def writeEnumerates(enumer):
    '''
    read per enumerate structure
    @param enumer: int enumerate value
    @return: UInt8
    '''
    return UInt8(enumer)

def readInteger(s):
    '''
    read interger per format from stream
    @param s: Stream
    @return: python int or long
    @raise InvalidValue: if size of integer is not correct
    '''
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
    '''
    write python long or int into per integer format
    @param value: int or long python value
    @return: UInt8, UInt16Be or UInt32Be
    '''
    if value < 0xff:
        return (writeLength(1), UInt8(value))
    elif value < 0xffff:
        return (writeLength(2), UInt16Be(value))
    else:
        return (writeLength(4), UInt32Be(value))
    
def readInteger16(s, minimum):
    '''
    read UInt16Be from stream s and add minimum
    @param s: Stream
    @param minimum: minimum added to real value
    @return: int or long python value
    '''
    result = UInt16Be()
    s.readType(result)
    return result.value + minimum

def writeInteger16(value, minimum):
    '''
    write UInt16Be minus minimum
    @param value: value to write
    @param minimum: value subtracted to real value
    @return: UInt16Be
    '''
    return UInt16Be(value - minimum)

def readObjectIdentifier(s, oid):
    '''
    read object identifier
    @param oid: must be a tuple of 6 elements
    @param s: Stream
    @return: true if oid is same as in stream
    '''
    size = readLength(s)
    if size != 5:
        raise InvalidValue("size of stream oid is wrong %d != 5"%size)
    a_oid = (0, 0, 0, 0, 0, 0)
    t12 = UInt8()
    s.readType(t12)
    a_oid[0] = t12.value >> 4
    a_oid[1] = t12.value & 0x0f
    s.readType(t12)
    a_oid[3] = t12.value
    s.readType(t12)
    a_oid[4] = t12.value
    s.readType(t12)
    a_oid[5] = t12.value
    s.readType(t12)
    a_oid[6] = t12.value
    
    if oid != a_oid:
        raise InvalidExpectedDataException("invalid object identifier")

def writeObjectIdentifier(oid):
    '''
    create tuble of 6 UInt8 with oid values
    @param oid: tuple of 6 int
    @return: (UInt8, UInt8, UInt8, UInt8, UInt8, UInt8)
    '''
    return (UInt8(oid[0] << 4 | oid[1] & 0x0f), UInt8(oid[2]), UInt8(oid[3]), UInt8(oid[4]), UInt8(oid[5]))

def writeNumericString(nStr, minValue):
    '''
    write string in per format
    @param str: python string to write
    @param min: min value
    @return: String type that contain str encoded in per format
    '''
    length = len(nStr)
    mlength = minValue
    if length - minValue >= 0:
        mlength = length - minValue
    
    result = []
    
    for i in range(0, length, 2):
        c1 = ord(str[i])
        if i + 1 < length:
            c2 = ord(str[i + 1])
        else:
            c2 = 0x30
        c1 = (c1 - 0x30) % 10
        c2 = (c2 - 0x30) % 10
        
        result.append(UInt8((c1 << 4) | c2))
        
    s = Stream()
    s.writeType((writeLength(mlength), tuple(result)))
    return String(s.getvalue())

def readPadding(s, length):
    '''
    read length byte in stream
    @param s: Stream
    @param length: length of passing in bytes
    '''
    s.read(length)

def writePadding(length):
    '''
    create string with null char * length
    @param length: length of padding
    @return: String with \x00 * length
    '''
    return String("\x00"*length)

def readOctetStream(s, octetStream, minValue):
    '''
    read string as octet stream and compare with octetStream
    @param octetStream: compare stream
    @param s: Stream
    @param minValue: min value
    @return: if stream read from s is equal to octetStream
    '''
    size = readLength(s) + minValue
    if size != len(octetStream):
        raise InvalidValue("incompatible size %d != %d"(len(octetStream), size))
    for i in range(0, size):
        c = UInt8()
        s.readType(c)
        if ord(octetStream[i]) != c.value:
            return False
        
    return True

def writeOctetStream(oStr, minValue):
    '''
    write string as octet stream with per header
    @param oStr: octet stream to convert
    @param minValue: min length value
    @return: per header follow by tuple of UInt8
    '''
    length = len(oStr)
    mlength = minValue
    
    if length - minValue >= 0:
        mlength = length - minValue
    
    result = []
    for i in range(0, length):
        result.append(UInt8(ord(oStr[i])))
    
    return (writeLength(mlength), tuple(result))