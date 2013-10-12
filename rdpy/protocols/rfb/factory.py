'''
Created on 22 aout 2013

@author: sylvain
'''
from twisted.internet import protocol

class RfbFactory(protocol.Factory):
    '''
    classdocs
    '''
    def __init__(self, protocol):
        self._protocol = protocol
    
    def buildProtocol(self, addr):
        return self._protocol;
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason