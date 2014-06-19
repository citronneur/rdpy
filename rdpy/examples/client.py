'''
@author: citronneur
'''
import sys
import os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from PyQt4 import QtGui
from rdpy.display.qt import RDPAdaptor, RfbAdaptor, QRemoteDesktop
from rdpy.protocol.rdp import rdp
from rdpy.protocol.rfb import rfb

class RDPClientQtFactory(rdp.ClientFactory):
    '''
    Factory create a RDP GUI client
    '''
    def __init__(self):
        '''
        ctor that init qt context and protocol needed
        '''
        #create qt widget
        self._w = QRemoteDesktop()
        self._w.resize(1024, 800)
        self._w.setWindowTitle('rdpyclient-rdp')
        self._w.show()
        #build protocol
        rdp.ClientFactory.__init__(self, RDPAdaptor(self._w))
        
    def startedConnecting(self, connector):
        pass
        
    def clientConnectionLost(self, connector, reason):
        '''
        connection lost event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        '''
        QtGui.QMessageBox.warning(self._w, "Warning", "Lost connection : %s"%reason)
        reactor.stop()
        app.exit()
        
    def clientConnectionFailed(self, connector, reason):
        '''
        connection failed event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        '''
        QtGui.QMessageBox.warning(self._w, "Warning", "Connection failed : %s"%reason)
        reactor.stop()
        app.exit()
        
class RFBClientQtFactory(rfb.ClientFactory):
    '''
    Factory create a VNC GUI client
    '''
    def __init__(self):
        '''
        ctor that init qt context and protocol needed
        '''
        #create qt widget
        self._w = QRemoteDesktop()
        self._w.resize(1024, 800)
        self._w.setWindowTitle('rdpyclient-vnc')
        self._w.show()
        
        rfb.ClientFactory.__init__(self, RfbAdaptor(self._w))
    
    def startedConnecting(self, connector):
        pass
        
    def clientConnectionLost(self, connector, reason):
        '''
        connection lost event
        @param connector: twisted connector use for vnc connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        '''
        QtGui.QMessageBox.warning(self._w, "Warning", "Lost connection : %s"%reason)
        reactor.stop()
        app.exit()
        
    def clientConnectionFailed(self, connector, reason):
        '''
        connection failed event
        @param connector: twisted connector use for vnc connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        '''
        QtGui.QMessageBox.warning(self._w, "Warning", "Connection failed : %s"%reason)
        reactor.stop()
        app.exit()
        
if __name__ == '__main__':
    #create application
    app = QtGui.QApplication(sys.argv)
    
    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()
    
    if sys.argv[3] == 'rdp':
        factory = RDPClientQtFactory()
    else:
        factory = RFBClientQtFactory()
    
    from twisted.internet import reactor
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), factory)
    reactor.runReturn()
    app.exec_()
    reactor.stop()