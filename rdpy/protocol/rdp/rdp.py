'''
@author: sylvain
'''
from twisted.internet import protocol
from rdpy.network.layer import LayerMode
from rdpy.network.error import CallPureVirtualFuntion
import tpkt, tpdu, mcs, pdu

class RDPController(object):
    """
    use to decode and dispatch to observer PDU messages and orders
    """
    def __init__(self, mode):
        '''
        @param mode: mode of generate layer by controller
        @param observer: observer
        '''
        #list of observer
        self._clientObserver = []
        #transport layer
        self._pduLayer = pdu.PDU(mode, self)
        
    def getPDULayer(self):
        """
        @return: pdu layer use by controller
        """
        return self._pduLayer
        
    def addClientObserver(self, observer):
        '''
        add observer to rdp protocol
        @param observer: new observer to add
        '''
        self._clientObserver.append(observer)
        observer._controller = self
        
    def recvBitmapUpdateDataPDU(self, bitmapUpdateData):
        '''
        call when a bitmap data is received from update pdu
        @param bitmapData: pdu.BitmapData struct
        '''
        for observer in self._clientObserver:
            #for each rectangle in update PDU
            for rectangle in bitmapUpdateData.rectangles._array:
                observer.onBitmapUpdate(rectangle.destLeft.value, rectangle.destTop.value, rectangle.destRight.value, rectangle.destBottom.value, rectangle.width.value, rectangle.height.value, rectangle.bitsPerPixel.value, rectangle.flags.value & pdu.BitmapFlag.BITMAP_COMPRESSION, rectangle.bitmapDataStream.value)

class ClientFactory(protocol.Factory):
    """
    Factory of Client RDP protocol
    """
    def __init__(self, width = 1024, height = 800):
        """
        @param width: width of screen
        @param height: height of screen
        """
        self._width = width
        self._height = height
        
    def buildProtocol(self, addr):
        '''
        Function call from twisted and build rdp protocol stack
        @param addr: destination address
        '''
        controller = RDPController(LayerMode.CLIENT)
        self.buildObserver(controller)
        mcsLayer = mcs.createClient(controller)
        
        #set screen definition in MCS layer
        mcsLayer._clientSettings.core.desktopHeight.value = self._height
        mcsLayer._clientSettings.core.desktopWidth.value = self._width
        
        return tpkt.TPKT(tpdu.createClient(mcsLayer));
    
    def buildObserver(self, controller):
        '''
        build observer use for connection
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "buildObserver", "ClientFactory"))

class ServerFactory(protocol.Factory):
    '''
    Factory of Serrve RDP protocol
    '''
    def __init__(self, privateKeyFileName, certificateFileName):
        '''
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
        return tpkt.TPKT(tpdu.createServer(mcs.createServer(pduLayer), self._privateKeyFileName, self._certificateFileName));
    
    def buildObserver(self):
        '''
        build observer use for connection
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "buildObserver", "ServerFactory")) 
        
class RDPClientObserver(object):
    '''
    class use to inform all RDP event handle by RDPY
    '''
    def __init__(self, controller):
        """
        @param controller: RDP controller use to interact with protocol
        """
        self._controller = controller
        self._controller.addClientObserver(self)
        
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
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onBitmapUpdate", "RDPClientObserver")) 