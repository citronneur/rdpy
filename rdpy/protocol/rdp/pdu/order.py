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
GDI order structure
"""

from rdpy.network.type import CompositeType, UInt8

class ControlFlag(object):
    TS_STANDARD = 0x01
    TS_SECONDARY = 0x02

class DrawingOrder(CompositeType):
    """
    GDI drawing orders
    @see: http://msdn.microsoft.com/en-us/library/cc241574.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.controlFlags = UInt8()

class PrimaryDrawingOrder(CompositeType):
    """
    GDI Primary drawing order
    @see: http://msdn.microsoft.com/en-us/library/cc241586.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)