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

if __name__ == '__main__':
    #create application
    app = QtGui.QApplication(sys.argv)
    
    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()
    
    #create widget
    w = QRemoteDesktop()
    w.resize(1024, 800)
    w.setWindowTitle('rdpyclient')
    w.show()
    
    if sys.argv[3] == 'rdp':
        factory = rdp.Factory(RDPAdaptor(w))
    else:
        factory = rfb.ClientFactory(RfbAdaptor(w))
    
    from twisted.internet import reactor
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), factory)
    reactor.run()
    sys.exit(app.exec_())