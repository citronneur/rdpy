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
Run length Encoding Algorithm implementation

It's the microsoft view of RLE algorithm

Most of bitmap in RDP protocol use this encoding

@see: http://msdn.microsoft.com/en-us/library/dd240593.aspx
"""
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

