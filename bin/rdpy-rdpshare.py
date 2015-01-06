#!/usr/bin/python
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
RDP proxy with share capabilities
Share your desktop for demo
               ---------------------------
Client RDP -> | ProxyServer | ProxyClient | -> Server RDP
               ---------------------------
                    | ProxyShadow |
                    --------------
                          ^
Shadow client ------------|
"""

import sys, os, getopt, json

from rdpy.core import log, error
from rdpy.protocol.rdp import rdp
from twisted.internet import reactor

log._LOG_LEVEL = log.Level.DEBUG

class ProxyServer(rdp.RDPServerObserver):
    """
    @summary: Server side of proxy
    """
    def __init__(self, controller, target):
        """
        @param controller: {RDPServerController}
        @param target: {tuple(ip, port)}
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._target = target
        self._client = None
        self._close = False
    
    def onClientReady(self, client):
        """
        @summary: Event throw by client when it's ready
        @param client: {ProxyClient}
        """
        self._client = client
        #need to reevaluate color depth
        self._controller.setColorDepth(self._client._controller.getColorDepth())
        
    def onReady(self):
        """
        @summary:  Event use to inform state of server stack
                    First time this event is called is when human client is connected
                    Second time is after color depth nego, because color depth nego
                    restart a connection sequence
        @see: rdp.RDPServerObserver.onReady
        """
        if self._client is None:
            #try a connection
            domain, username, password = self._controller.getCredentials()
            
            width, height = self._controller.getScreen()
            reactor.connectTCP(self._target[0], int(self._target[1]), ProxyClientFactory(self, width, height, 
                                                            domain, username, password))
        else:
            #refresh client
            width, height = self._controller.getScreen()
            self._client._controller.sendRefreshOrder(0, 0, width, height)
            
    def onClose(self):
        """
        @summary: Call when human client close connection
        @see: rdp.RDPServerObserver.onClose
        """
        self._close = True
        if self._client is None:
            return
        
        #close proxy client
        self._client._controller.close()
        
    def onKeyEventScancode(self, code, isPressed):
        """
        @summary: Event call when a keyboard event is catch in scan code format
        @param code: scan code of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventScancode
        """
        if self._client is None:
            return
        self._client._controller.sendKeyEventScancode(code, isPressed)
    
    def onKeyEventUnicode(self, code, isPressed):
        """
        @summary: Event call when a keyboard event is catch in unicode format
        @param code: unicode of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventUnicode
        """
        if self._client is None:
            return
        self._client._controller.sendKeyEventUnicode(code, isPressed)
        
    def onPointerEvent(self, x, y, button, isPressed):
        """
        @summary: Event call on mouse event
        @param x: x position
        @param y: y position
        @param button: 1, 2 or 3 button
        @param isPressed: True if mouse button is pressed
        @see: rdp.RDPServerObserver.onPointerEvent
        """
        if self._client is None:
            return
        self._client._controller.sendPointerEvent(x, y, button, isPressed)
        
class ProxyServerFactory(rdp.ServerFactory):
    """
    @summary: Factory on listening events
    """
    def __init__(self, target, privateKeyFilePath = None, certificateFilePath = None):
        """
        @param target: {tuple(ip, prt)}
        @param privateKeyFilePath: {str} file contain server private key (if none -> back to standard RDP security)
        @param certificateFilePath: {str} file contain server certificate (if none -> back to standard RDP security)
        """
        rdp.ServerFactory.__init__(self, 16, privateKeyFilePath, certificateFilePath)
        self._target = target
        self._main = None
        
    def buildObserver(self, controller, addr):
        """
        @param controller: rdp.RDPServerController
        @param addr: destination address
        @see: rdp.ServerFactory.buildObserver
        """
        #first build main session
        if self._main is None or self._main._close:
            self._main = ProxyServer(controller, self._target)
            return self._main
        clientController = self._main._client._controller if not self._main._client is None else None
        return Shadow(controller, self._main._client._controller)
    
class ProxyClient(rdp.RDPClientObserver):
    """
    @summary: Client side of proxy
    """
    def __init__(self, controller, server):
        """
        @param controller: rdp.RDPClientController
        @param server: ProxyServer 
        """
        rdp.RDPClientObserver.__init__(self, controller)
        self._server = server
        self._connected = False
        
    def onReady(self):
        """
        @summary:  Event use to signal that RDP stack is ready
                    Inform ProxyServer that i'm connected
        @see: rdp.RDPClientObserver.onReady
        """
        #prevent multiple on ready event
        #because each deactive-reactive sequence 
        #launch an onReady message
        if self._connected:
            return
        else:
            self._connected = True
    
        self._server.onClientReady(self)
        
    def onClose(self):
        """
        @summary: Event inform that stack is close
        @see: rdp.RDPClientObserver.onClose
        """
        self._server._controller.close()
        
    def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
        """
        @summary: Event use to inform bitmap update
        @param destLeft: xmin position
        @param destTop: ymin position
        @param destRight: xmax position because RDP can send bitmap with padding
        @param destBottom: ymax position because RDP can send bitmap with padding
        @param width: width of bitmap
        @param height: height of bitmap
        @param bitsPerPixel: number of bit per pixel
        @param isCompress: use RLE compression
        @param data: bitmap data
        @see: rdp.RDPClientObserver.onUpdate
        """
        self._server._controller.sendUpdate(destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data)

class ProxyClientFactory(rdp.ClientFactory):
    """
    @summary: Factory for proxy client
    """
    def __init__(self, server, width, height, domain, username, password):
        """
        @param server: ProxyServer
        @param width: screen width
        @param height: screen height
        @param domain: domain session
        @param username: username session
        @param password: password session
        """
        self._server = server
        self._width = width
        self._height = height
        self._domain = domain
        self._username = username
        self._password = password
        
    def buildObserver(self, controller, addr):
        """
        @summary: Build observer
        @param controller: rdp.RDPClientController
        @param addr: destination address
        @see: rdp.ClientFactory.buildObserver
        @return: ProxyClient
        """
        #set screen resolution
        controller.setScreen(self._width, self._height)
        #set credential
        controller.setDomain(self._domain)
        controller.setUsername(self._username)
        controller.setPassword(self._password)
        return ProxyClient(controller, self._server)          
    
class Shadow(rdp.RDPServerObserver):
    """
    @summary:  Use to manage admin session
    """
    def __init__(self, controller, clientController):
        """
        @param server: rdp.RDPServerController
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._clientController = clientController
        self._client = None
        if not self._clientController is None:
            self._client = ProxyClient(clientController, self)
            self._controller.setColorDepth(self._client._controller.getColorDepth())
     
    def onReady(self):
        """
        @summary:  Stack is ready and connected
                    May be called after an setColorDepth too
        @see: rdp.RDPServerObserver.onReady
        """
        if self._client is None:
            self._controller.close()
            return
        
        width, height = self._controller.getScreen()
        self._client._controller.sendRefreshOrder(0, 0, width, height)
    
    def onClose(self):
        """ Shadow """
    
    def onKeyEventScancode(self, code, isPressed):
        """ Shadow """
    
    def onKeyEventUnicode(self, code, isPressed):
        """ Shadow """
    
    def onPointerEvent(self, x, y, button, isPressed):
        """ Shadow """
    
def help():
    """
    @summary: Print help in console
    """
    print "Usage: rdpy-rdpshare.py [-l listen_port default 3389] [-k private_key_file_path (mandatory for SSL)] [-c certificate_file_path (mandatory for SSL)] [-i admin_ip[:admin_port]] target"

def parseIpPort(interface, defaultPort = "3389"):
    if ':' in interface:
        return interface.split(':')
    else:
        return interface, defaultPort

if __name__ == '__main__':
    listen = "3389"
    privateKeyFilePath = None
    certificateFilePath = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:k:c:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt == "-l":
            listen = arg
        elif opt == "-k":
            privateKeyFilePath = arg
        elif opt == "-c":
            certificateFilePath = arg
    
    reactor.listenTCP(int(listen), ProxyServerFactory(parseIpPort(args[0]), privateKeyFilePath, certificateFilePath))
    reactor.run()