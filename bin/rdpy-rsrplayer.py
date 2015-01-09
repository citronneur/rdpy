#!/usr/bin/python
#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
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
from rdpy.ui.qt4 import QRemoteDesktop, RDPBitmapToQtImage
log._LOG_LEVEL = log.Level.INFO

class RsrPlayerWidget(QRemoteDesktop):
    """
    @summary: special rsr player widget
    """
    def __init__(self, width, height):
        class RsrAdaptor(object):
            def sendMouseEvent(self, e, isPressed):
                """ Not Handle """
            def sendKeyEvent(self, e, isPressed):
                """ Not Handle """
            def sendWheelEvent(self, e):
                """ Not Handle """
            def closeEvent(self, e):
                """ Not Handle """
        QRemoteDesktop.__init__(self, width, height, RsrAdaptor())
        
    def drawInfos(self, username):
        drawArea = QtGui.QImage(100, 100, QtGui.QImage.Format_RGB32)
        #fill with background Color
        drawArea.fill(QtCore.Qt.red)
        with QtGui.QPainter(drawArea) as qp:
            rect = QtCore.QRect(0, 0, 100, 100)
            qp.setPen(QtCore.Qt.black)  
            qp.setFont(QtGui.QFont('arial', 12, QtGui.QFont.Bold))
            qp.drawText(rect, QtCore.Qt.AlignCenter, "username %s"%username)
        
        self.notifyImage(0, 0, drawArea, 100, 100)
    
def help():
    print "Usage: rdpy-rsrplayer [-h] path"
    
def loop(widget, rsrFile):
    """
    @summary: timer function
    @param widget: {QRemoteDesktop}
    @param rsrFile: {rsr.FileReader}
    """
    e = rsrFile.nextEvent()
    if e is None:
        widget.close()
        return
    
    if e.type.value == rsr.EventType.UPDATE:
        image = RDPBitmapToQtImage(e.event.width.value, e.event.height.value, e.event.bpp.value, e.event.format.value == rsr.UpdateFormat.BMP, e.event.data.value);
        widget.notifyImage(e.event.destLeft.value, e.event.destTop.value, image, e.event.destRight.value - e.event.destLeft.value + 1, e.event.destBottom.value - e.event.destTop.value + 1)
        
    elif e.type.value == rsr.EventType.RESIZE:
        widget.resize(e.event.width.value, e.event.height.value)
        
    elif e.type.value == rsr.EventType.INFO:
        widget.drawInfos(e.event.username)
        log.info("*" * 50)
        log.info("username : %s"%e.event.username.value)
        log.info("password : %s"%e.event.password.value)
        log.info("domain : %s"%e.event.domain.value)
        log.info("hostname : %s"%e.event.hostname.value)
        log.info("*" * 50)
        
    QtCore.QTimer.singleShot(e.timestamp.value+ 1000,lambda:loop(widget, rsrFile))

if __name__ == '__main__':
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
    widget = RsrPlayerWidget(800, 600)
    widget.show()
    rsrFile = rsr.createReader(filepath)
    loop(widget, rsrFile)
    sys.exit(app.exec_())