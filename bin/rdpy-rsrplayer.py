#!/usr/bin/python
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
rsr file player
"""

import sys, os, getopt, socket

from PyQt4 import QtGui, QtCore

from rdpy.core import log, rsr
from rdpy.ui.qt4 import RDPBitmapToQtImage
log._LOG_LEVEL = log.Level.INFO

class QRsrPlayer(QtGui.QWidget):
    def __init__(self):
        self._refresh = []
        #buffer image
        self._buffer = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
        self._f = rsr.createReader("/tmp/toto")
        self._nextEvent = self._f.next()
        
    def next(self):
        #if self._nextEvent.type.value = rsr.EventType.UPDATE:
        #    self.notifyImage(self._nextEvent.event., y, RDPBitmapToQtImage(width, height, bitsPerPixel, isCompress, data), width, height)
        self._nextEvent = self._f.next()
        QtCore.QTimer.singleShot(0,)
    
    def notifyImage(self, x, y, qimage, width, height):
        """
        @summary: Function call from QAdaptor
        @param x: x position of new image
        @param y: y position of new image
        @param qimage: new QImage
        """
        #save in refresh list (order is important)
        self._refresh.append((x, y, qimage, width, height))
        #force update
        self.update()
        
    def paintEvent(self, e):
        """
        @summary: Call when Qt renderer engine estimate that is needed
        @param e: QEvent
        """
        #fill buffer image
        with QtGui.QPainter(self._buffer) as qp:
        #draw image
            for (x, y, image, width, height) in self._refresh:
                qp.drawImage(x, y, image, 0, 0, width, height)
        #draw in widget
        with QtGui.QPainter(self) as qp:
            qp.drawImage(0, 0, self._buffer)

        self._refresh = []
        
def help():
    print "Usage: rdpy-rsrplayer [options] ip[:port]"
        
if __name__ == '__main__':
    
    #default script argument
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
            
    filepath = args[0]
    #create application
    app = QtGui.QApplication(sys.argv)
    app.exec_()