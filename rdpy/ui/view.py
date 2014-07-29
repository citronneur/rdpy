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


class KeyCode(object):
    """
    Interesting Scan code
    """
    ENTER = 28
    UP = 72
    DOWN = 80

class IRender(object):
    """
    Render Interface
    """
    def translate(self, dx, dy):
        """
        Translate next render
        @param dx: delta x
        @param dy: delta y
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "translate", "IRender"))
    
    def drawImage(self, image):
        """
        Draw QImage
        @param image: QImage
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "drawImage", "IRender"))
    
    def getImageFormat(self):
        """
        @return: Image format use for render
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "getImageFormat", "IRender"))

class IView(object):
    """
    View interface
    """
    def keyEvent(self, code):
        """
        Key event notification
        @param code: scan code
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "keyEvent", "IView"))

    def pointerEvent(self, x, y, button):
        """
        Pointer event notification
        @param x: x position
        @param y: y position
        @param button: button pressed
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "pointerEvent", "IView"))

    def update(self, render, force = False):
        """
        Update view
        @param render: IRender
        @param force: force update
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "update", "IView"))


class AnchorView(IView):
    def __init__(self, x, y, view):
        self._x = x
        self._y = y
        self._view = view
        
    def keyEvent(self, code):
        self._view.keyEvent(code)
        
    def pointerEvent(self, x, y, button):
        self._view.pointerEvent(x - self._x, y - self._y)
        
    def update(self, render, force = False):
        render.translate(self._x, self._y)
        self._view.update(render, force)
        render.translate(-self._x, -self._y)

class ListView(IView):
    """
    List widget simulate by QT painter
    """
    def __init__(self, labels, width, height, callback, backgroudColor = QtCore.Qt.black):
        self._labels = labels
        self._width = width
        self._height = height
        self._cellHeight = 25
        self._backgroudColor = backgroudColor
        self._fontSize = 14
        self._current = 0
        self._callback = callback
        self._needUpdate = False
    
    def keyEvent(self, code):
        #enter key
        if len(self._labels) == 0:
            return
        if code == KeyCode.ENTER:
            self._callback(self._labels[self._current])
        elif code == KeyCode.DOWN:
            self._current = min(len(self._labels) - 1, self._current + 1)
            self._needUpdate = True
        elif code == KeyCode.UP:
            self._current = max(0, self._current - 1)
            self._needUpdate = True
    
    def pointerEvent(self, x, y, button):
        pass
        
    def update(self, render, force = False):
        """
        Draw GUI that list active session
        """
        if not force and not self._needUpdate:
            return
        self._needUpdate = False
        
        i = 0
        drawArea = QtGui.QImage(self._width, self._height, render.getImageFormat())
        #fill with background Color
        drawArea.fill(self._backgroudColor)
        with QtGui.QPainter(drawArea) as qp:
            for label in self._labels:
                rect = QtCore.QRect(0, i * self._cellHeight, self._width - 2, self._cellHeight)
                if i == self._current:
                    qp.setPen(QtCore.Qt.darkGreen)
                    qp.drawRoundedRect(rect, 5.0, 5.0)
                qp.setPen(QtCore.Qt.white)  
                qp.setFont(QtGui.QFont('arial', self._fontSize, QtGui.QFont.Bold))
                qp.drawText(rect, QtCore.Qt.AlignCenter, label)
                i += 1
        render.drawImage(drawArea)
        
class WindowView(IView):
    def __init__(self, width, height, backgroundColor = QtCore.Qt.black):
        self._views = []
        self._focusIndex = 0
        self._width = width
        self._height = height
        self._backgroundColor = backgroundColor
    def addView(self, view):
        self._views.append(view)
    def keyEvent(self, code):
        if self._focusIndex < len(self._views):
            self._views[self._focusIndex].keyEvent(code)
    def pointerEvent(self, x, y, button):
        if self._focusIndex < len(self._views):
            self._views[self._focusIndex].pointerEvent(x, y, button)
    def update(self, render, force = False):
        drawArea = QtGui.QImage(self._width, self._height, render.getImageFormat())
        #fill with background Color
        if force:
            drawArea.fill(self._backgroundColor)
            render.drawImage(drawArea)
        for view in self._views:
            view.update(render, force)

class RDPRenderer(object):
    def __init__(self, server):
        """
        @param server: RDPServerController
        """
        self._server = server
        self._colorDepth = self._server.getColorDepth()
        self._dx = 0
        self._dy = 0
        self._renderSize = 64
        
    def getImageFormat(self):
        if self._colorDepth == 15:
            return QtGui.QImage.Format_RGB15
        elif self._colorDepth == 16:
            return QtGui.QImage.Format_RGB16
        elif self._colorDepth == 24:
            return QtGui.QImage.Format_RGB24
        elif self._colorDepth == 32:
            return QtGui.QImage.Format_RGB32
        
    def translate(self, dx, dy):
        self._dx += dx
        self._dy += dy
        
    def drawImage(self, image):
        """
        Render of widget
        """
        nbWidth = image.width() / self._renderSize + 1
        nbHeight = image.height() / self._renderSize + 1
        for i in range(0, nbWidth):
            for j in range(0, nbHeight):
                tmp = image.copy(i * self._renderSize, j * self._renderSize, self._renderSize, self._renderSize)
                #in RDP image or bottom top encoded
                tmp = tmp.transformed(QtGui.QMatrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0))
                ptr = tmp.bits()
                ptr.setsize(tmp.byteCount())
                self._server.sendUpdate(i * self._renderSize + self._dx, j * self._renderSize + self._dy, min((i + 1) * self._renderSize, image.width()) + self._dx - 1, min((j + 1) * self._renderSize, image.height()) + self._dy - 1, tmp.width(), tmp.height(), self._colorDepth, False, ptr.asstring())
        