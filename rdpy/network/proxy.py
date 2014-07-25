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
Proxy Interface
client -> ProxyServer | ProxyClient -> server
"""

from rdpy.base.error import CallPureVirtualFuntion

class IProxyClient(object):
    """
    Proxy interface for client side
    """
    def getColorDepth(self):
        """
        @return: color depth of session (15,16,24,32)
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "IProxyClient"))
    
    def sendKeyEventScancode(self, code, isPressed):
        """
        Send key event with scan code
        @param code: scan code
        @param isPressed: True if keyboard key is pressed
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "IProxyClient"))
    
    def sendPointerEvent(self, x, y, button, isPressed):
        """
        Send Pointer event
        @param x: x position
        @param y: y position
        @param button: mouse button 1|2|3
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "IProxyClient"))

