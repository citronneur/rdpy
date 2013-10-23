'''
Created on 4 sept. 2013

@author: sylvain
'''
import sys
from PyQt4 import QtGui
from rdpy.display.qt import adaptor, widget
from rdpy.protocol.rfb import rfb, factory
from rdpy.protocol.rdp import tpkt, tpdu, mcs
from twisted.internet import ssl
from OpenSSL import SSL

if __name__ == '__main__':
    #app = QtGui.QApplication(sys.argv)
    #import qt4reactor
    #qt4reactor.install()
    
    #protocol = rfb.Rfb(rfb.Rfb.CLIENT)
    #w = widget.QRemoteDesktop(adaptor.RfbAdaptor(protocol))
    #w.resize(1000, 700)
    #w.setWindowTitle('QVNCViewer')
    #w.show()
    from twisted.internet import reactor
    #reactor.connectTCP("127.0.0.1", 5901, factory.RfbFactory(protocol))
    reactor.connectTCP("192.168.1.90", 3389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU(mcs.MCS()))))
    #reactor.connectTCP("192.168.135.73", 3389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU(mcs.MCS()))))
    reactor.run()
    #sys.exit(app.exec_())