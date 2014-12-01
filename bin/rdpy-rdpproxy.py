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
                      | ProxyAdmin |
                       ------------
                            ^
Admin ----------------------|
"""

import sys, os, getopt, json

from rdpy.base import log, error
from rdpy.protocol.rdp import rdp
from rdpy.ui import view
from twisted.internet import reactor
from PyQt4 import QtCore, QtGui

#log._LOG_LEVEL = log.Level.INFO

class ProxyServer(rdp.RDPServerObserver):
    """
    @summary: Server side of proxy
    """
    def __init__(self, controller, credentialProvider):
        """
        @param controller: RDPServerController
        @param credentialProvider: CredentialProvider
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._credentialProvider = credentialProvider
        self._client = None
        self._window = None
    
    def showSelectView(self, machines):
        """
        @summary: Show select sever view to the client
        @param machines: [(ip, port)]
        """
        self._machines = machines
        width, height = self._controller.getScreen()
        self._window = view.Window(width, height, QtGui.QColor(8, 24, 66))
        
        self._window.addView(view.Anchor(width / 2 - 250, 100, 
                                         view.Label("Please select following server", 
                                                    500, 50, QtGui.QFont('arial', 18, QtGui.QFont.Bold),
                                                    backgroundColor = QtGui.QColor(8, 24, 66))))
        
        self._window.addView(view.Anchor(width / 2 - 250, 150, 
                                         view.List(["%s:%s"%(ip, port) for ip, port in machines],
                                                   500, 500, self.onSelectMachine, 
                                                   QtGui.QColor(8, 24, 66))), True)
        
        self._window.update(view.RDPRenderer(self._controller), True) 
    
    def onSelectMachine(self, index):
        """
        @summary: Callback of view.List in Select server view
        @param: index in list
        """
        ip, port = self._machines[index]
        width, height = self._controller.getScreen()
        domain, username, password = self._controller.getCredentials()
        reactor.connectTCP(ip, port, ProxyClientFactory(self, width, height, domain, username, password))
    
    def clientConnected(self, client):
        """
        @summary: Event throw by client when it's ready
        @param client: ProxyClient
        """
        self._client = client
        #need to reevaluate color depth
        self._controller.setColorDepth(self._client._controller.getColorDepth())
        
    def showMessage(self, message):
        """
        @summary: Print a message to the client
        @param message: string
        """
        width, height = self._controller.getScreen()
        
        popup = view.Window(width, height, QtGui.QColor(8, 24, 66))
        
        popup.addView(view.Anchor(width / 2 - 250, height / 2 - 25, 
                                  view.Label(message, 500, 50, 
                                             QtGui.QFont('arial', 18, QtGui.QFont.Bold), 
                                             backgroundColor = QtGui.QColor(8, 24, 66))))
        
        popup.update(view.RDPRenderer(self._controller), True)
        
    def onReady(self):
        """
        @summary:  Event use to inform state of server stack
                    First time this event is called is when human client is connected
                    Second time is after color depth nego, because color depth nego
                    restart a connection sequence
                    Use to connect proxy client or show available server
        @see: rdp.RDPServerObserver.onReady
        """
        if self._client is None:
            #try a connection
            domain, username, password = self._controller.getCredentials()
            machines = self._credentialProvider.getProxyPass(domain, username)
            
            if len(machines) == 0:
                self.showMessage("No servers attach to account %s\\%s"%(domain, username))
            elif len(machines) == 1: 
                ip, port = machines[0]
                width, height = self._controller.getScreen()
                reactor.connectTCP(ip, port, ProxyClientFactory(self, width, height, 
                                                                domain, username, password))
            else:
                self.showSelectView(machines)
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
        #close proxy client
        self._client._controller.close()
        
    def onKeyEventScancode(self, code, isPressed):
        """
        @summary: Event call when a keyboard event is catch in scan code format
        @param code: scan code of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventScancode
        """
        #no client connected
        if not self._client is None:
            self._client._controller.sendKeyEventScancode(code, isPressed)
        elif not self._window is None and isPressed:
            self._window.keyEvent(code)
            self._window.update(view.RDPRenderer(self._controller))
        
    
    def onKeyEventUnicode(self, code, isPressed):
        """
        @summary: Event call when a keyboard event is catch in unicode format
        @param code: unicode of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventUnicode
        """
        #no client connected domain
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
        #no client connected
        if self._client is None:
            return
        self._client._controller.sendPointerEvent(x, y, button, isPressed)
        
class ProxyServerFactory(rdp.ServerFactory):
    """
    @summary: Factory on listening events
    """
    def __init__(self, credentialProvider, privateKeyFilePath, certificateFilePath):
        """
        @param credentialProvider: CredentialProvider
        @param privateKeyFilePath: file contain server private key
        @param certificateFilePath: file contain server certificate
        """
        rdp.ServerFactory.__init__(self, privateKeyFilePath, certificateFilePath, 16)
        self._credentialProvider = credentialProvider
        
    def buildObserver(self, controller, addr):
        """
        @param controller: rdp.RDPServerController
        @param addr: destination address
        @see: rdp.ServerFactory.buildObserver
        """
        return ProxyServer(controller, self._credentialProvider)
    
class ProxyClient(rdp.RDPClientObserver):
    """
    @summary: Client side of proxy
    """
    _CONNECTED_ = []
    def __init__(self, controller, server, name = None):
        """
        @param controller: rdp.RDPClientController
        @param server: ProxyServer
        @param name:  name of session None if you don't
                       want to spy this session  
        """
        rdp.RDPClientObserver.__init__(self, controller)
        self._server = server
        self._name = name
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
            
        if not self._name is None:
            ProxyClient._CONNECTED_.append(self)
        self._server.clientConnected(self)
        
    def onClose(self):
        """
        @summary: Event inform that stack is close
        @see: rdp.RDPClientObserver.onClose
        """
        if not self._name is None:
            ProxyClient._CONNECTED_.remove(self)
        
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
        return ProxyClient(controller, self._server, "%s\\%s on %s"%(self._domain, self._username, addr))
    
    def startedConnecting(self, connector):
        pass
    
    def clientConnectionLost(self, connector, reason):
        pass
        
    def clientConnectionFailed(self, connector, reason):
        pass
            
    
class ProxyAdmin(rdp.RDPServerObserver):
    """
    @summary:  Use to manage admin session
                Add GUI to select which session to see
                Just escape key is authorized during spy session
                To switch from spy state to admin state
    """
    class State(object):
        GUI = 0 #->list of active session
        SPY = 1 #->watch active session
        
    def __init__(self, controller):
        """
        @param server: rdp.RDPServerController
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._spy = None
        self._state = ProxyAdmin.State.GUI
        
    def initView(self):
        """
        @summary: Initialize Admin GUI view
        """
        self._sessions = list(ProxyClient._CONNECTED_) #copy at t time
        width, height = self._controller.getScreen()
        self._window = view.Window(width, height, QtGui.QColor(8, 24, 66))
        
        self._window.addView(view.Anchor(width / 2 - 250, 100, 
                                         view.Label("Please select following session", 
                                                    500, 50, QtGui.QFont('arial', 18, QtGui.QFont.Bold), 
                                                    backgroundColor = QtGui.QColor(8, 24, 66))))
        
        self._window.addView(view.Anchor(width / 2 - 250, 150, 
                                         view.List([p._name for p in self._sessions], 
                                                   500, 500, self.onSelect, 
                                                   QtGui.QColor(8, 24, 66))), True)
         
    def clientConnected(self, client):
        pass
     
    def onReady(self):
        """
        @summary:  Stack is ready and connected
                    May be called after an setColorDepth too
        @see: rdp.RDPServerObserver.onReady
        """
        if self._state == ProxyAdmin.State.GUI:
            self.initView()
            self._window.update(view.RDPRenderer(self._controller), True)
        elif self._state == ProxyAdmin.State.SPY:
            #refresh client
            width, height = self._controller.getScreen()
            self._spy._controller.sendRefreshOrder(0, 0, width, height)
    
    def onClose(self):
        """
        @summary: Stack is close
        @see: rdp.RDPServerObserver.onClose
        """
        pass
    
    def onKeyEventScancode(self, code, isPressed):
        """
        @summary:  Event call when a keyboard event 
                    is catch in scan code format
        @param code: scan code of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventScancode
        """
        if self._state == ProxyAdmin.State.GUI:
            if not isPressed:
                return
            self._window.keyEvent(code)
            self._window.update(view.RDPRenderer(self._controller))
        elif code == 1:
            #escape button refresh GUI
            self._state = ProxyAdmin.State.GUI
            self._spy._controller.removeClientObserver(self._spy)
            self.onReady()
    
    def onKeyEventUnicode(self, code, isPressed):
        """
        @summary:  Event call when a keyboard event is catch in unicode format
                    Admin GUI add filter for this event
        @param code: unicode of key
        @param isPressed: True if key is down
        @see: rdp.RDPServerObserver.onKeyEventUnicode
        """
        pass
    
    def onPointerEvent(self, x, y, button, isPressed):
        """
        @summary:  Event call on mouse event
                    Admin GUI add filter for this event
        @param x: x position
        @param y: y position
        @param button: 1, 2 or 3 button
        @param isPressed: True if mouse button is pressed
        @see: rdp.RDPServerObserver.onPointerEvent
        """
        pass
        
    def onSelect(self, index):
        """
        @summary:  Callback of list view of active session
                    Connect to select session
        @param index: index in sessions array
        """
        self._state = ProxyAdmin.State.SPY
        self._spy = ProxyClient(self._sessions[index]._controller, self)
        self._controller.setColorDepth(self._spy._controller.getColorDepth())
        
class ProxyAdminFactory(rdp.ServerFactory):
    """
    @summary:  Factory for admin session
    """
    def __init__(self, privateKeyFilePath, certificateFilePath):
        """
        @param privateKeyFilePath: private key for admin session
        @param certificateFilePath: certificate for admin session
        """
        rdp.ServerFactory.__init__(self, privateKeyFilePath, certificateFilePath, 16)
        
    def buildObserver(self, controller, addr):
        """
        @summary: Build ProxyAdmin
        @param controller: rdp.RDPServerController
        @param addr: destination address
        @return: ProxyAdmin
        @see: rdp.ServerFactory.buildObserver
        """
        return ProxyAdmin(controller)

class CredentialProvider(object):
    """
    @summary: Credential provider for proxy
    """
    def __init__(self, config):
        """
        @param config: rdp proxy config
        """
        self._config = config
        
    def getAccount(self, domain, username):
        """
        @summary: Find account that match domain::username in config file
        @param domain: Windows domain
        @param username: username for session
        @return: [(unicode(ip), port] or None if not found
        """
        if not self._config.has_key(domain) or not self._config[domain].has_key(username):
            return None
        return self._config[domain][username]
        
    def getProxyPass(self, domain, username):
        """
        @summary: Find list of server available for thi account
        @param domain: domain to check
        @param username: username in domain
        @return: [(ip, port)]
        """
        account = self.getAccount(domain, username)
        if account is None:
            return []
        return [(str(machine["ip"]), machine["port"]) for machine in account]
       
def help():
    """
    @summary: Print help in console
    """
    print "Usage: rdpy-rdpproxy -f credential_file_path -k private_key_file_path -c certificate_file_path [-i admin_ip[:admin_port]] listen_port"
    
def loadConfig(configFilePath):
    """
    @summary: Load and check config file
    @param configFilePath: config file path
    """
    if not os.path.isfile(configFilePath):
        log.error("File %s doesn't exist"%configFilePath)
        return None
    
    f = open(configFilePath, 'r')
    config = json.load(f)
    f.close()
    
    return config

if __name__ == '__main__':
    configFilePath = None
    privateKeyFilePath = None
    certificateFilePath = None
    adminInterface = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:k:c:i:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt == "-f":
            configFilePath = arg
        elif opt == "-k":
            privateKeyFilePath = arg
        elif opt == "-c":
            certificateFilePath = arg
        elif opt == "-i":
            adminInterface = arg
            
    if configFilePath is None:
        print "Config file is mandatory"
        help()
        sys.exit()
        
    if certificateFilePath is None:
        print "Certificate file is mandatory"
        help()
        sys.exit()
        
    if  privateKeyFilePath is None:
        print "Private key file is mandatory"
        help()
        sys.exit()
    
    #load config file
    config = loadConfig(configFilePath)
    if config is None:
        log.error("Bad configuration file")
        sys.exit()
    
    #use to init font
    app = QtGui.QApplication(sys.argv)
    
    reactor.listenTCP(int(args[0]), ProxyServerFactory(CredentialProvider(config), privateKeyFilePath, certificateFilePath))
    
    if not adminInterface is None:
        if ':' in adminInterface:
            adminInterface, adminPort = adminInterface.split(':')
        else:
            adminInterface, adminPort = adminInterface, "3390"
        log.info("Admin listen on %s:%s"%(adminInterface, adminPort))
        reactor.listenTCP(int(adminPort), ProxyAdminFactory(privateKeyFilePath, certificateFilePath), interface = adminInterface)
    reactor.run()