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
    
def loop(widget, rssFile):
    """
    @summary: timer function
    @param widget: {QRemoteDesktop}
    @param rssFile: {rss.FileReader}
    """
    e = rssFile.nextEvent()
    if e is None:
        widget.close()
        return
    
    if e.type.value == rss.EventType.UPDATE:
        image = RDPBitmapToQtImage(e.event.width.value, e.event.height.value, e.event.bpp.value, e.event.format.value == rss.UpdateFormat.BMP, e.event.data.value);
        widget.notifyImage(e.event.destLeft.value, e.event.destTop.value, image, e.event.destRight.value - e.event.destLeft.value + 1, e.event.destBottom.value - e.event.destTop.value + 1)
        
    elif e.type.value == rss.EventType.SCREEN:
        widget.resize(e.event.width.value, e.event.height.value)
        
    elif e.type.value == rss.EventType.INFO:
        widget.drawInfos(e.event.domain.value, e.event.username.value, e.event.password.value, e.event.hostname.value)
        
    QtCore.QTimer.singleShot(e.timestamp.value,lambda:loop(widget, rssFile))

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
    loop(widget, rssFile)
    sys.exit(app.exec_())