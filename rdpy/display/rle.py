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
from rdpy.network.error import InvalidExpectedDataException

"""
Run length Encoding Algorithm implementation

It's the microsoft view of RLE algorithm

Most of bitmap in RDP protocol use this encoding

@see: http://msdn.microsoft.com/en-us/library/dd240593.aspx
"""
from rdpy.network.type import UInt8, UInt16Le, Stream, sizeof

def decode(src, width, height, colorType):
    """
    It's a python transcription of rdesktop algorithm
    """
    lastopcode = -1
    x = width
    prevLine = 0
    code = UInt8()
    opcode = UInt8()
    color1 = colorType()
    color2 = colorType()
    mix = colorType()
    isFillOrMix = False
    insertMix = False
    fom_mask = 0
    mask = 0
    line = 0
    dst = [colorType()] * width * height
    
    while src.dataLen() > 0:
        #compute orders
        
        src.readType(code)
        opcode = code >> 4
        count = UInt16Le()
        
        
        if opcode == 0xc or opcode == 0xd or opcode == 0xe:
            opcode -= 6
            count = code & 0xf
            offset = 16
        elif opcode == 0xf:
            opcode = code & 0xf
            if opcode < 9:
                src.readType(count)
            else:
                count = UInt16Le(8 if opcode < 0xb else 1)
            offset = 0
        else:
            opcode >>= 1
            count = UInt16Le((code & 0xf).value)
            offset = 32
            
        if offset != 0:
            isFillOrMix = opcode == 2 or opcode == 7
            if count == 0:
                tmp = UInt8()
                src.readType(tmp)
                if isFillOrMix:
                    count = UInt16Le((tmp + 1).value)
                else:
                    count = UInt16Le((tmp + offset).value)
            elif isFillOrMix:
                count <<= 3
        
        
        if opcode == 0:
            if lastopcode == opcode and not (x == width and prevLine == 0):
                insertMix = True
        elif opcode == 3 or opcode == 8:
            src.readType(color2)
            if opcode == 8:
                src.readType(color1)
        elif opcode == 6 or opcode == 7:
            src.readType(mix)
        elif opcode == 9:
            mask = 0x03
            opcode = UInt8(0x02)
            fom_mask = 5
            
        lastopcode = opcode
        mixmask = 0
        
        while count > 0:
            if x > width:
                if height <= 0:
                    raise InvalidExpectedDataException("In RLE decompression height must be greater than 0")
                x = 0
                height -= 1
                prevLine = line
                line = width * height
            
            #fill
            if opcode == 0:
                if insertMix:
                    if prevLine == 0:
                        dst[line + x] = mix
                    else:
                        dst[line + x] = dst[prevLine + x] ^ mix
                insertMix = False
                count -= 1
                x += 1
                
                if prevLine == 0:
                    while count > 0 and x < width:
                        dst[line + x] = colorType()
                        count -= 1
                        x += 1
                else:
                    while count > 0 and x < width:
                        dst[line + x] = dst[prevLine + x]
                        count -= 1
                        x += 1
            #mix
            elif opcode == 1:
                if prevLine == 0:
                    while count > 0 and x < width:
                        dst[line + x] = mix
                        count -= 1
                        x += 1
                else:
                    while count > 0 and x < width:
                        dst[line + x] = dst[prevLine + x] ^ mix
                        count -= 1
                        x += 1
            #fill or mix
            elif opcode == 2:
                pass
            #color
            elif opcode == 3:
                while count > 0 and x < width:
                    dst[line + x] = color2
                    count -= 1
                    x += 1
            #copy
            elif opcode == 4:
                while count > 0 and x < width:
                    src.readType(dst[line + x])
                    count -= 1
                    x += 1
            #bicolor
            elif opcode == 8:
                pass
            #write
            elif opcode == 0xd:
                while count > 0 and x < width:
                    dst[line + x] = ~colorType()
                    count -= 1
                    x += 1
            elif opcode == 0xe:
                while count > 0 and x < width:
                    dst[line + x] = colorType()
                    count -= 1
                    x += 1
    output = Stream()
    output.writeType(dst)
    return output
            
                