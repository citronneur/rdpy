'''
@author: sylvain
'''
from twisted.internet import protocol
import tpkt, tpdu, mcs, pdu
from rdpy.network.layer import LayerMode

class RDP(object):
    '''
    use to decode and dispatch to observer PDU message and orders
    '''
    def __init__(self):
        '''
        ctor
        '''
        #list of observer
        self._observers = []
        
    def addObserver(self, observer):
        '''
        add observer to rdp protocol
        @param observer: new observer to add
        '''
        self._observers.append(observer)
        
    def recvBitmapUpdateDataPDU(self, bitmapUpdateData):
        '''
        call when a bitmap data is received from update pdu
        @param bitmapData: pdu.BitmapData struct
        '''
        for observer in self._observers:
            #for each rectangle in update PDU
            for rectangle in bitmapUpdateData.rectangles._array:
                observer.notifyBitmapUpdate(rectangle.destLeft.value, rectangle.destTop.value, rectangle.destRight.value, rectangle.destBottom.value, rectangle.width.value, rectangle.height.value, rectangle.bitsPerPixel.value, rectangle.flags | pdu.BitmapFlag.BITMAP_COMPRESSION, rectangle.bitmapDataStream.value)

class Factory(protocol.Factory):
    '''
    Factory of Client RDP protocol
    '''
    def __init__(self, observer):
        '''
        ctor
        @param observer: observer use by rdp protocol to handle events
        '''
        self._observer = observer
    
    def buildProtocol(self, addr):
        rdp = RDP()
        rdp.addObserver(self._observer)
        return tpkt.TPKT(tpdu.TPDU(mcs.MCS(pdu.PDU(LayerMode.CLIENT, rdp))));
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        
class RDPObserver(object):
    '''
    class use to inform all rdp event handle by RDPY
    '''
    def notifyBitmapUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
        '''
        notify bitmap update
        @param destLeft: xmin position
        @param destTop: ymin position
        @param destRight: xmax position because RDP can send bitmap with padding
        @param destBottom: ymax position because RDP can send bitmap with padding
        @param width: width of bitmap
        @param height: height of bitmap
        @param bitsPerPixel: number of bit per pixel
        @param isCompress: use RLE compression
        @param data: bitmap data
        '''
        pass