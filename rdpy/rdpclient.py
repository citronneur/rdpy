'''
Created on 4 sept. 2013

@author: sylvain
'''
from rdpy.protocol.rdp import rdp



if __name__ == '__main__':
    from twisted.internet import reactor
    #reactor.connectTCP("127.0.0.1", 5901, factory.RfbFactory(protocol))
    #reactor.connectTCP("192.168.1.90", 3389, factory.RfbFactory(tpkt.TPKT(tpdu.TPDU(mcs.MCS()))))
    reactor.connectTCP("192.168.135.198", 3389, rdp.Factory())
    reactor.run()