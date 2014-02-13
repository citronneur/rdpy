'''
@author: sylvain
'''
from twisted.internet import protocol
import tpkt, tpdu, mcs, pdu
class Factory(protocol.Factory):
    '''
    Factory of RDP protocol
    '''
    def __init__(self, mode):
        self._mode = mode
    
    def buildProtocol(self, addr):
        return tpkt.TPKT(tpdu.TPDU(mcs.MCS(pdu.PDU(self._mode))));
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason