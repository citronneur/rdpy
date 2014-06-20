'''
@author: citronneur
@file: implement run length encoding algorithm use in RDP protocol to compress bit
@see: http://msdn.microsoft.com/en-us/library/dd240593.aspx
'''
from rdpy.network.type import UInt8

def extractCodeId(data):
    '''
    Read first unsigned char
    '''
    res = UInt8()
    data.readType(res)
    return res

def decode(dst, src, rowDelta):
    
    insertFgPel = False
    firstLine = True
    
    while src.dataLen() > 0:
        if firstLine:
            firstLine = False
            insertFgPel = False

