'''
@author: citronneur
'''
import sys
import os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from PyQt4 import QtGui
from rdpy.display.qt import RFBClientQt
from rdpy.protocol.rfb import rfb
        
class RFBClientQtFactory(rfb.ClientFactory):
    '''
    Factory create a VNC GUI client
    '''
    def buildObserver(self):
        '''
        build RFB observer
        '''
        #create client observer
        client = RFBClientQt()
        #create qt widget
        self._w = client.getWidget()
        self._w.resize(1024, 800)
        self._w.setWindowTitle('rdpyclient-vnc')
        self._w.show()
        return client
    
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

    from twisted.internet import reactor
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), RFBClientQtFactory())
    reactor.runReturn()
    app.exec_()
    reactor.stop()