'''
@author: sylvain
'''

import sys
import os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from PyQt4 import QtGui
from rdpy.display.qt import RfbAdaptor, QRemoteDesktop
from rdpy.protocol.rfb import rfb
from rdpy.network.layer import LayerMode

if __name__ == '__main__':
    #create application
    app = QtGui.QApplication(sys.argv)
    
    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()
    
    #create rfb protocol
    factory = rfb.Factory(LayerMode.CLIENT)
    w = QRemoteDesktop(RfbAdaptor(factory._protocol))
    w.resize(1000, 700)
    w.setWindowTitle('vncclient')
    w.show()
    from twisted.internet import reactor
    reactor.connectTCP("127.0.0.1", 5903, factory)
    reactor.run()
    sys.exit(app.exec_())