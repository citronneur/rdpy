'''
@author: sylvain
'''
from twisted.internet import protocol
import tpkt, tpdu, mcs, pdu
from rdpy.network.layer import LayerMode

class RDPController(object):
    '''
    use to decode and dispatch to observer PDU messages and orders
    '''
    def __init__(self, pduLayer):
        '''
        ctor
        '''
        #list of observer
        self._observers = []
        #transport layer
        self._pduLayer = pduLayer
        
    def addObserver(self, observer):
        '''
        add observer to rdp protocol
        @param observer: new observer to add
        '''
        self._observers.append(observer)
        observer._controller = self
        
    def recvBitmapUpdateDataPDU(self, bitmapUpdateData):
        '''
        call when a bitmap data is received from update pdu
        @param bitmapData: pdu.BitmapData struct
        '''
        for observer in self._observers:
            #for each rectangle in update PDU
            for rectangle in bitmapUpdateData.rectangles._array:
                observer.onBitmapUpdate(rectangle.destLeft.value, rectangle.destTop.value, rectangle.destRight.value, rectangle.destBottom.value, rectangle.width.value, rectangle.height.value, rectangle.bitsPerPixel.value, (rectangle.flags & pdu.BitmapFlag.BITMAP_COMPRESSION).value, rectangle.bitmapDataStream.value)

class ClientFactory(protocol.Factory):
    '''
    Factory of Client RDP protocol
    '''
    def buildProtocol(self, addr):
        '''
        Function call from twisted and build rdp protocol stack
        @param addr: destination address
        '''
        pduLayer = pdu.PDU(LayerMode.CLIENT)
        pduLayer.getController().addObserver(self.buildObserver())
        return tpkt.TPKT(tpdu.createClient(mcs.MCS(pduLayer)));
    
    def buildObserver(self):
        '''
        build observer use for connection
        '''
        pass

class ServerFactory(protocol.Factory):
    '''
    Factory of Serrve RDP protocol
    '''
    def __init__(self, privateKeyFileName, certificateFileName):
        '''
        ctor
        @param privateKeyFileName: file contain server private key
        @param certficiateFileName: file that contain publi key
        '''
        self._privateKeyFileName = privateKeyFileName
        self._certificateFileName = certificateFileName
        
    def buildProtocol(self, addr):
        '''
        Function call from twisted and build rdp protocol stack
        @param addr: destination address
        '''
        pduLayer = pdu.PDU(LayerMode.SERVER)
        #pduLayer.getController().addObserver(self.buildObserver())
        return tpkt.TPKT(tpdu.createServer(mcs.MCS(pduLayer), self._privateKeyFileName, self._certificateFileName));
    
    def buildObserver(self):
        '''
        build observer use for connection
        '''
        pass 
        
class RDPClientObserver(object):
    '''
    class use to inform all rdp event handle by RDPY
    '''
    def __init__(self):
        '''
        ctor
        '''
        self._controller = None
        
    def onBitmapUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
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