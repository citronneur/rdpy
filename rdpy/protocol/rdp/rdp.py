'''
@author: sylvain
'''
from twisted.internet import protocol
import tpkt, tpdu, mcs, gdl
class Factory(protocol.Factory):
    '''
    Factory of RDP protocol
    '''
    def __init__(self):
        mcsLayer = mcs.MCS()
        #set global channel to graphic layer
        mcsLayer._channelIds[mcs.Channel.MCS_GLOBAL_CHANNEL] = gdl.GDL()
        self._protocol = tpkt.TPKT(tpdu.TPDU(mcsLayer))
    
    def buildProtocol(self, addr):
        return self._protocol;
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason