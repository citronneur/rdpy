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
GDI order structure
"""

from rdpy.core import log
from rdpy.core.error import InvalidExpectedDataException
from rdpy.core.type import CompositeType, UInt8, String, FactoryType, SInt8, SInt16Le

class ControlFlag(object):
    """
    @summary: Class order of drawing order
    @see: http://msdn.microsoft.com/en-us/library/cc241586.aspx
    """
    TS_STANDARD = 0x01
    TS_SECONDARY = 0x02
    TS_BOUNDS = 0x04
    TS_TYPE_CHANGE = 0x08
    TS_DELTA_COORDINATES = 0x10
    TS_ZERO_BOUNDS_DELTAS = 0x20
    TS_ZERO_FIELD_BYTE_BIT0 = 0x40
    TS_ZERO_FIELD_BYTE_BIT1 = 0x80
    
class OrderType(object):
    """
    @summary: Primary order type
    @see: http://msdn.microsoft.com/en-us/library/cc241586.aspx
    """
    TS_ENC_DSTBLT_ORDER = 0x00
    TS_ENC_PATBLT_ORDER = 0x01
    TS_ENC_SCRBLT_ORDER = 0x02
    TS_ENC_DRAWNINEGRID_ORDER = 0x07
    TS_ENC_MULTI_DRAWNINEGRID_ORDER = 0x08
    TS_ENC_LINETO_ORDER = 0x09
    TS_ENC_OPAQUERECT_ORDER = 0x0A
    TS_ENC_SAVEBITMAP_ORDER = 0x0B
    TS_ENC_MEMBLT_ORDER = 0x0D
    TS_ENC_MEM3BLT_ORDER = 0x0E
    TS_ENC_MULTIDSTBLT_ORDER = 0x0F
    TS_ENC_MULTIPATBLT_ORDER = 0x10
    TS_ENC_MULTISCRBLT_ORDER = 0x11
    TS_ENC_MULTIOPAQUERECT_ORDER = 0x12
    TS_ENC_FAST_INDEX_ORDER = 0x13
    TS_ENC_POLYGON_SC_ORDER = 0x14
    TS_ENC_POLYGON_CB_ORDER = 0x15
    TS_ENC_POLYLINE_ORDER = 0x16
    TS_ENC_FAST_GLYPH_ORDER = 0x18
    TS_ENC_ELLIPSE_SC_ORDER = 0x19
    TS_ENC_ELLIPSE_CB_ORDER = 0x1A
    TS_ENC_INDEX_ORDER = 0x1B
    
class CoordField(CompositeType):
    """
    @summary: used to describe a value in the range -32768 to 32767
    @see: http://msdn.microsoft.com/en-us/library/cc241577.aspx
    """
    def __init__(self, isDelta, conditional = lambda:True):
        """
        @param isDelta: callable object to know if coord field is in delta mode
        @param conditional: conditional read or write type
        """
        CompositeType.__init__(self, conditional = conditional)
        self.delta = SInt8(conditional = isDelta)
        self.coordinate = SInt16Le(conditional = isDelta)
    
class PrimaryDrawingOrder(CompositeType):
    """
    @summary: GDI Primary drawing order
    @see: http://msdn.microsoft.com/en-us/library/cc241586.aspx
    """
    def __init__(self, order = None):
        CompositeType.__init__(self)
        self.controlFlags = UInt8()
        self.orderType = UInt8()
        
        def OrderFactory():
            """
            Closure for capability factory
            """
            for c in [DstBltOrder]:
                if self.orderType.value == c._ORDER_TYPE_:
                    return c(self.controlFlags)
            log.debug("unknown Order type : %s"%hex(self.orderType.value))
            #read entire packet
            return String()
        
        if order is None:
            order = FactoryType(OrderFactory)
        elif not "_ORDER_TYPE_" in order.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid order block")

class DstBltOrder(CompositeType):
    """
    @summary: The DstBlt Primary Drawing Order is used to paint 
                a rectangle by using a destination-only raster operation.
    @see: http://msdn.microsoft.com/en-us/library/cc241587.aspx
    """
    #order type
    _ORDER_TYPE_ = 0x00
    #negotiation index
    _NEGOTIATE_ = 0x00
    
    def __init__(self, controlFlag):
        CompositeType.__init__(self)
        #only one field
        self.fieldFlag = UInt8(conditional = lambda:(controlFlag.value & ControlFlag.TS_ZERO_FIELD_BYTE_BIT0 == 0 and controlFlag.value & ControlFlag.TS_ZERO_FIELD_BYTE_BIT1 == 0))
        self.nLeftRect = CoordField(lambda:not controlFlag.value & ControlFlag.TS_DELTA_COORDINATES == 0)
        self.nTopRect = CoordField(lambda:not controlFlag.value & ControlFlag.TS_DELTA_COORDINATES == 0)
        self.nWidth = CoordField(lambda:not controlFlag.value & ControlFlag.TS_DELTA_COORDINATES == 0)
        self.nHeight = CoordField(lambda:not controlFlag.value & ControlFlag.TS_DELTA_COORDINATES == 0)
        self.bRop = CoordField(lambda:not controlFlag.value & ControlFlag.TS_DELTA_COORDINATES == 0)