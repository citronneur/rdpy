'''
Created on 4 sept. 2013
@author: sylvain
'''
from PyQt4 import QtGui
from rdpy.protocols.rfb.observer import RfbObserver

class QAdaptor(object):
    '''
    Adaptor for all qt
    '''
    def __init__(self):
        self._observers = []
        
    def addObserver(self, observer):
        self._observers.append(observer)
        
    def notifyImage(self, x, y, qimage):
        for observer in self._observers:
            observer.notifyImage(x, y, qimage)
        
    def sendMouseEvent(self, e):
        pass
    def sendKeyEvent(self, e):
        pass
    

class RfbAdaptor(RfbObserver, QAdaptor):
    '''
    classdocs
    '''
    
    def __init__(self, rfb):
        QAdaptor.__init__(self)
        self._rfb = rfb
        self._rfb.addObserver(self)
    
    def notifyFramebufferUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        implement RfbAdaptor interface
        '''
        
        imageFormat = None
        if pixelFormat.BitsPerPixel == 32 and pixelFormat.RedShift == 16:
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            print "Receive image in bad format"
            return
            
        image = QtGui.QImage(data, width, height, imageFormat)
        self.notifyImage(x, y, image)
        
    def sendMouseEvent(self, e):
        '''
        convert qt mouse event to rfb mouse event
        '''
        self._rfb.writePointerEvent(0, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e):
        '''
        convert qt key press event to rfb press event
        '''
        self._rfb.writeKeyEvent(True, e.nativeVirtualKey())