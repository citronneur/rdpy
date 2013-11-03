'''
@author: sylvain
'''

from rdpy.protocol.rfb import factory
from rdpy.protocol.rdp import tpkt, tpdu, mcs

if __name__ == '__main__':
    from twisted.internet import reactor
    #reactor.connectTCP("127.0.0.1", 5901, factory.RfbFactory(protocol))
    #reactor.connectTCP("192.168.1.90", 3389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU(mcs.MCS()))))
    reactor.listenTCP(33389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU(mcs.MCS()))))
    reactor.run()