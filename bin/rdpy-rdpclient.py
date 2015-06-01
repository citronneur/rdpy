#!/usr/bin/python
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
example of use rdpy as rdp client
"""

import sys, os, getopt, socket

from PyQt4 import QtGui, QtCore
from rdpy.ui.qt4 import RDPClientQt
from rdpy.protocol.rdp import rdp
from rdpy.core.error import RDPSecurityNegoFail
from rdpy.core import rss

import rdpy.core.log as log
log._LOG_LEVEL = log.Level.INFO


class RDPClientQtRecorder(RDPClientQt):
    """
    @summary: Widget with record session
    """
    def __init__(self, controller, width, height, rssRecorder):
        """
        @param controller: {RDPClientController} RDP controller
        @param width: {int} width of widget
        @param height: {int} height of widget
        @param rssRecorder: {rss.FileRecorder}
        """
        RDPClientQt.__init__(self, controller, width, height)
        self._screensize = width, height
        self._rssRecorder = rssRecorder
        
    def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
        """
        @summary: Notify bitmap update
        @param destLeft: {int} xmin position
        @param destTop: {int} ymin position
        @param destRight: {int} xmax position because RDP can send bitmap with padding
        @param destBottom: {int} ymax position because RDP can send bitmap with padding
        @param width: {int} width of bitmap
        @param height: {int} height of bitmap
        @param bitsPerPixel: {int} number of bit per pixel
        @param isCompress: {bool} use RLE compression
        @param data: {str} bitmap data
        """
        #record update
        self._rssRecorder.update(destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, rss.UpdateFormat.BMP if isCompress else rss.UpdateFormat.RAW, data)
        RDPClientQt.onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data)
    
    def onReady(self):
        """
        @summary: Call when stack is ready
        """
        self._rssRecorder.screen(self._screensize[0], self._screensize[1], self._controller.getColorDepth())
        RDPClientQt.onReady(self)
          
    def onClose(self):
        """
        @summary: Call when stack is close
        """
        self._rssRecorder.close()
        RDPClientQt.onClose(self)
        
    def closeEvent(self, e):
        """
        @summary: Convert Qt close widget event into close stack event
        @param e: QCloseEvent
        """
        self._rssRecorder.close()
        RDPClientQt.closeEvent(self, e)

class RDPClientQtFactory(rdp.ClientFactory):
    """
    @summary: Factory create a RDP GUI client
    """
    def __init__(self, width, height, username, password, domain, fullscreen, keyboardLayout, optimized, security, recodedPath):
        """
        @param width: {integer} width of client
        @param heigth: {integer} heigth of client
        @param username: {str} username present to the server
        @param password: {str} password present to the server
        @param domain: {str} microsoft domain
        @param fullscreen: {bool} show widget in fullscreen mode
        @param keyboardLayout: {str} (fr|en) keyboard layout
        @param optimized: {bool} enable optimized session orders
        @param security: {str} (ssl | rdp | nego)
        @param recodedPath: {str | None} Rss file Path
        """
        self._width = width
        self._height = height
        self._username = username
        self._passwod = password
        self._domain = domain
        self._fullscreen = fullscreen
        self._keyboardLayout = keyboardLayout
        self._optimized = optimized
        self._nego = security == "nego"
        self._recodedPath = recodedPath
        if self._nego:
            #compute start nego nla need credentials
            if username != "" and password != "":
                self._security = rdp.SecurityLevel.RDP_LEVEL_NLA
            else:
                self._security = rdp.SecurityLevel.RDP_LEVEL_SSL
        else:
            self._security = security
        self._w = None
        
    def buildObserver(self, controller, addr):
        """
        @summary:  Build RFB observer
                    We use a RDPClientQt as RDP observer
        @param controller: build factory and needed by observer
        @param addr: destination address
        @return: RDPClientQt
        """
        #create client observer
        if self._recodedPath is None:
            self._client = RDPClientQt(controller, self._width, self._height)
        else:
            self._client = RDPClientQtRecorder(controller, self._width, self._height, rss.createRecorder(self._recodedPath))
        #create qt widget
        self._w = self._client.getWidget()
        self._w.setWindowTitle('rdpy-rdpclient')
        if self._fullscreen:
            self._w.showFullScreen()
        else:
            self._w.show()
        
        controller.setUsername(self._username)
        controller.setPassword(self._passwod)
        controller.setDomain(self._domain)
        controller.setKeyboardLayout(self._keyboardLayout)
        controller.setHostname(socket.gethostname())
        if self._optimized:
            controller.setPerformanceSession()
        controller.setSecurityLevel(self._security)
        
        return self._client
    
    def clientConnectionLost(self, connector, reason):
        """
        @summary: Connection lost event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        #try reconnect with basic RDP security
        if reason.type == RDPSecurityNegoFail and self._nego:
            #stop nego
            log.info("due to security nego error back to standard RDP security layer")
            self._nego = False
            self._security = rdp.SecurityLevel.RDP_LEVEL_RDP
            self._client._widget.hide()
            connector.connect()
            return
        
        log.info("Lost connection : %s"%reason)
        reactor.stop()
        app.exit()
        
    def clientConnectionFailed(self, connector, reason):
        """
        @summary: Connection failed event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        log.info("Connection failed : %s"%reason)
        reactor.stop()
        app.exit()
        
def autoDetectKeyboardLayout():
    """
    @summary: try to auto detect keyboard layout
    """
    try:
        if os.name == 'posix':    
            from subprocess import check_output
            result = check_output(["setxkbmap", "-print"])
            if 'azerty' in result:
                return "fr"
        elif os.name == 'nt':
            import win32api, win32con, win32process
            from ctypes import windll
            w = windll.user32.GetForegroundWindow() 
            tid = windll.user32.GetWindowThreadProcessId(w, 0) 
            result = windll.user32.GetKeyboardLayout(tid)
            log.info(result)
            if result == 0x40c040c:
                return "fr"
    except Exception as e:
        log.info("failed to auto detect keyboard layout " + str(e))
        pass
    return "en"
        
def help():
    print """
    Usage: rdpy-rdpclient [options] ip[:port]"
    \t-u: user name
    \t-p: password
    \t-d: domain
    \t-w: width of screen [default : 1024]
    \t-l: height of screen [default : 800]
    \t-f: enable full screen mode [default : False]
    \t-k: keyboard layout [en|fr] [default : en]
    \t-o: optimized session (disable costly effect) [default : False]
    \t-r: rss_filepath Recorded Session Scenario [default : None]
    """
        
if __name__ == '__main__':
    
    #default script argument
    username = ""
    password = ""
    domain = ""
    width = 1024
    height = 800
    fullscreen = False
    optimized = False
    recodedPath = None
    keyboardLayout = autoDetectKeyboardLayout()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfou:p:d:w:l:k:r:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt == "-u":
            username = arg
        elif opt == "-p":
            password = arg
        elif opt == "-d":
            domain = arg
        elif opt == "-w":
            width = int(arg)
        elif opt == "-l":
            height = int(arg)
        elif opt == "-f":
            fullscreen = True
        elif opt == "-o":
            optimized = True
        elif opt == "-k":
            keyboardLayout = arg
        elif opt == "-r":
            recodedPath = arg
            
    if ':' in args[0]:
        ip, port = args[0].split(':')
    else:
        ip, port = args[0], "3389"
    
    #create application
    app = QtGui.QApplication(sys.argv)
    
    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()
    
    if fullscreen:
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
    
    log.info("keyboard layout set to %s"%keyboardLayout)
    
    from twisted.internet import reactor
    reactor.connectTCP(ip, int(port), RDPClientQtFactory(width, height, username, password, domain, fullscreen, keyboardLayout, optimized, "nego", recodedPath))
    reactor.runReturn()
    app.exec_()