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
RDP Honey pot use Rss scenario file to simulate RDP server
"""

import sys, os, getopt, time

from rdpy.core import log, error, rss
from rdpy.protocol.rdp import rdp
from twisted.internet import reactor

log._LOG_LEVEL = log.Level.INFO

class HoneyPotServer(rdp.RDPServerObserver):
    def __init__(self, controller, rssFile):
        """
        @param controller: {RDPServerController}
        """
        rdp.RDPServerObserver.__init__(self, controller)
        self._rssFile = rssFile
        
    def onReady(self):
        """
        @summary:  Event use to inform state of server stack
                    First time this event is called is when human client is connected
                    Second time is after color depth nego, because color depth nego
                    restart a connection sequence
        @see: rdp.RDPServerObserver.onReady
        """
        self.loopScenario()
        
    def onClose(self):
        """ HoneyPot """
        
    def onKeyEventScancode(self, code, isPressed):
        """ HoneyPot """
    
    def onKeyEventUnicode(self, code, isPressed):
        """ HoneyPot """
        
    def onPointerEvent(self, x, y, button, isPressed):
        """ HoneyPot """
        
    def loopScenario(self):
        """
        @summary: main loop event
        """
        e = self._rssFile.nextEvent()
        if e is None:
            self._controller.close()
            return
        
        if e.type.value == rss.EventType.UPDATE:
            self._controller.sendUpdate(e.event.destLeft.value, e.event.destTop.value, e.event.destRight.value, e.event.destBottom.value, e.event.width.value, e.event.height.value, e.event.bpp.value, e.event.format.value == rss.UpdateFormat.BMP, e.event.data.value)
        elif e.type.value == rss.EventType.SCREEN:
            self._controller.setColorDepth(e.event.colorDepth.value)
            #restart connection sequence
            return
        reactor.callLater(float(e.timestamp.value) / 1000.0, self.loopScenario)
        
class HoneyPotServerFactory(rdp.ServerFactory):
    """
    @summary: Factory on listening events
    """
    def __init__(self, rssFilePath, privateKeyFilePath, certificateFilePath):
        """
        @param rssFilePath: Recorded Session Scenario File path
        @param privateKeyFilePath: {str} file contain server private key (if none -> back to standard RDP security)
        @param certificateFilePath: {str} file contain server certificate (if none -> back to standard RDP security)
        """
        rdp.ServerFactory.__init__(self, 16, privateKeyFilePath, certificateFilePath)
        self._rssFilePath = rssFilePath
        
    def buildObserver(self, controller, addr):
        """
        @param controller: {rdp.RDPServerController}
        @param addr: destination address
        @see: rdp.ServerFactory.buildObserver
        """
        return HoneyPotServer(controller, rss.createReader(self._rssFilePath))
    
def help():
    """
    @summary: Print help in console
    """
    print """
    Usage:  rdpy-rdphoneypot.py rss_filepath
            [-l listen_port default 3389] 
            [-k private_key_file_path (mandatory for SSL)] 
            [-c certificate_file_path (mandatory for SSL)] 
    """
    
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
    
    reactor.listenTCP(int(listen), HoneyPotServerFactory(args[0], privateKeyFilePath, certificateFilePath))
    reactor.run()