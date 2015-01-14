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
rss file player
"""

import sys, os, getopt, socket

from PyQt4 import QtGui, QtCore

from rdpy.core import log, rss
from rdpy.ui.qt4 import QRemoteDesktop, RDPBitmapToQtImage
log._LOG_LEVEL = log.Level.INFO

class RssPlayerWidget(QRemoteDesktop):
    """
    @summary: special rss player widget
    """
    def __init__(self, width, height):
        class RssAdaptor(object):
            def sendMouseEvent(self, e, isPressed):
                """ Not Handle """
            def sendKeyEvent(self, e, isPressed):
                """ Not Handle """
            def sendWheelEvent(self, e):
                """ Not Handle """
            def closeEvent(self, e):
                """ Not Handle """
        QRemoteDesktop.__init__(self, width, height, RssAdaptor())
        
    def drawInfos(self, domain, username, password, hostname):
        QtGui.QMessageBox.about(self, "Credentials Event", "domain : %s\nusername : %s\npassword : %s\nhostname : %s" % (
            domain, username, password, hostname))

def help():
    print "Usage: rdpy-rssplayer [-h] rss_filepath"

def start(widget, rssFile):
    loop(widget, rssFile, rssFile.nextEvent())
  
def loop(widget, rssFile, nextEvent):
    """
    @summary: timer function
    @param widget: {QRemoteDesktop}
    @param rssFile: {rss.FileReader}
    """
   
    if nextEvent.type.value == rss.EventType.UPDATE:
        image = RDPBitmapToQtImage(nextEvent.event.width.value, nextEvent.event.height.value, nextEvent.event.bpp.value, nextEvent.event.format.value == rss.UpdateFormat.BMP, nextEvent.event.data.value);
        widget.notifyImage(nextEvent.event.destLeft.value, nextEvent.event.destTop.value, image, nextEvent.event.destRight.value - nextEvent.event.destLeft.value + 1, nextEvent.event.destBottom.value - nextEvent.event.destTop.value + 1)
        
    elif nextEvent.type.value == rss.EventType.SCREEN:
        widget.resize(nextEvent.event.width.value, nextEvent.event.height.value)
        
    elif nextEvent.type.value == rss.EventType.INFO:
        widget.drawInfos(nextEvent.event.domain.value, nextEvent.event.username.value, nextEvent.event.password.value, nextEvent.event.hostname.value)
        
    elif nextEvent.type.value == rss.EventType.CLOSE:
        widget.close()
        return
    
    e = rssFile.nextEvent()
    QtCore.QTimer.singleShot(e.timestamp.value,lambda:loop(widget, rssFile, e))

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
    widget = RssPlayerWidget(800, 600)
    widget.show()
    rssFile = rss.createReader(filepath)
    start(widget, rssFile)
    sys.exit(app.exec_())