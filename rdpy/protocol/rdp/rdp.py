'''
@author: sylvain
'''
from twisted.internet import protocol
import tpkt, tpdu, mcs
class Factory(protocol.Factory):
    '''
    Factory of RFB protocol
    '''
    def __init__(self):
        self._protocol = tpkt.TPKT(tpdu.TPDU(mcs.MCS()))
    
    def buildProtocol(self, addr):
        return self._protocol;
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason