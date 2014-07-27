#
# Copyright (c) 2014 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Fake widget
"""
from rdpy.base.error import CallPureVirtualFuntion
from PyQt4 import QtGui, QtCore

class IWidgetLister(object):
    """
    Listener for object
    """
    def onUpdate(self, x, y, image):
        """
        Event call by widget when it need to be updated
        @param x: x position
        @param y: y position
        @param image: QImage
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "IWidgetLister"))

class IWidget(object):
    def keyEvent(self, code):
        pass
    def pointerEvent(self, x, y, button):
        pass

class Anchor(IWidgetLister):
    def __init__(self, x, y, listener):
        self._x = x
        self._y = y
        self._listener = listener
    def onUpdate(self, x, y, image):
        self._listener.onUpdate(x + self._x, y + self._y, image)
    

class List(IWidget):
    """
    List widget simulate by QT painter
    """
    def __init__(self, labels, width, height, callback, listener):
        self._labels = labels
        self._width = width
        self._height = height
        self._current = 0
        self._listener = listener
        self.update()
        self._callback = callback
    
    def keyEvent(self, code):
        #enter key
        if code == 28 and len(self._labels) > 0:
            self._callback(self._labels[self._current])
    
    def pointerEvent(self, x, y, button):
        pass
        
    def update(self):
        """
        Draw GUI that list active session
        """
        i = 0
        drawArea = QtGui.QImage(self._width, self._height, QtGui.QImage.Format_RGB16)
        drawArea.fill(QtCore.Qt.blue)
        with QtGui.QPainter(drawArea) as qp:
            for label in self._labels:
                if i == self._current:
                    qp.setPen(QtCore.Qt.darkGreen)
                    qp.drawRoundedRect(0, i * 25, self._width, 25, 0.2, 0.2)
                    qp.setPen(QtCore.Qt.black)
                else:
                    qp.setPen(QtCore.Qt.gray)
                    
                qp.setFont(QtGui.QFont('courier', 12))
                qp.drawText(0, 0, label)
        
        self._listener.onUpdate(0, 25 * i, drawArea)

class RDPWidgetListener(IWidgetLister):
    def __init__(self, server):
        """
        @param server: RDPServerController
        """
        self._server = server
        
    def onUpdate(self, x, y, image):
        """
        Event call by widget when it need to be updated
        @param x: x position
        @param y: y position
        @param image: QImage
        """
        nbWidth = image.width() / 64 + 1
        nbHeight = image.height() / 64 + 1
        for i in range(0, nbWidth):
            for j in range(0, nbHeight):
                tmp = image.copy(i * 64, j * 64, 64, 64)
                ptr = tmp.bits()
                ptr.setsize(tmp.byteCount())
                self._server.sendUpdate(i*64 + x, j*64 + y, i*64 + x + tmp.width() - 1, j*64 + y + tmp.height() - 1, tmp.width(), tmp.height(), 16, False, ptr.asstring())
        