'''
Created on 4 sept. 2013

@author: sylvain
'''
import sys
from PyQt4 import QtGui
from rdpy.ui.qt import adaptor, widget
from rdpy.protocols.rfb import rfb, factory
from rdpy.protocols.rdp import tpkt, tpdu
from twisted.internet import ssl
from OpenSSL import SSL

class ClientTLSContext(ssl.ClientContextFactory):
    isClient = 1
    def getContext(self):
        context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_options(SSL.OP_DONT_INSERT_EMPTY_FRAGMENTS)
        context.set_options(SSL.OP_TLS_BLOCK_PADDING_BUG)
        return context

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
    reactor.connectTCP("192.168.122.184", 3389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU())))
    reactor.run()
    sys.exit(app.exec_())