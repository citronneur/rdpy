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
example of use rdpy as rdp client
"""

import sys
import os

# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from PyQt4 import QtGui
from rdpy.display.qt import RDPClientQt
from rdpy.protocol.rdp import rdp

class RDPClientQtFactory(rdp.ClientFactory):
    """
    Factory create a RDP GUI client
    """
    def buildObserver(self, controller):
        """
        Build RFB observer
        @param controller: build factory and needed by observer
        """
        #create client observer
        client = RDPClientQt(controller)
        #create qt widget
        self._w = client.getWidget()
        self._w.resize(1024, 800)
        self._w.setWindowTitle('rdpyclient-vnc')
        self._w.show()
        return client
        
    def startedConnecting(self, connector):
        pass
    
    def clientConnectionLost(self, connector, reason):
        """
        Connection lost event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        QtGui.QMessageBox.warning(self._w, "Warning", "Lost connection : %s"%reason)
        reactor.stop()
        app.exit()
        
    def clientConnectionFailed(self, connector, reason):
        """
        Connection failed event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        QtGui.QMessageBox.warning(self._w, "Warning", "Connection failed : %s"%reason)
        reactor.stop()
        app.exit()
        
if __name__ == '__main__':
    #create application
    app = QtGui.QApplication(sys.argv)
    
    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()
    
    from twisted.internet import reactor
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), RDPClientQtFactory())
    reactor.runReturn()
    app.exec_()
    reactor.stop()