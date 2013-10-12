'''
Created on 4 sept. 2013

@author: sylvain
'''

from PyQt4 import QtGui
from observer import QObserver

class QRemoteDesktop(QtGui.QWidget, QObserver):
    
    def __init__(self, adaptor):
        super(QRemoteDesktop, self).__init__()
        self._adaptor = adaptor
        self._adaptor.addObserver(self)
        self._refresh = []
        self.setMouseTracking(True)
    
    def notifyImage(self, x, y, qimage):
        self._refresh.append({"x" : x, "y" : y, "image" : qimage})
        self.update()
        
    def paintEvent(self, e):
        if self._refresh == []:
            return
        qp = QtGui.QPainter()
        qp.begin(self)
        for image in self._refresh:
            qp.drawImage(image["x"], image["y"], image["image"])
        qp.end()
        
        self._lastReceive = []
        
    def mouseMoveEvent(self, event):
        self._adaptor.sendMouseEvent(event)

    def keyPressEvent(self, event):
        self._adaptor.sendKeyEvent(event)