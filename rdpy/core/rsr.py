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
Remote Session Recorder File format
Private protocol format to save events
"""

from rdpy.core.type import CompositeType, FactoryType, UInt8, UInt16Le, UInt32Le, String, sizeof, Stream
from rdpy.core import log, error
import time

class EventType(object):
    UPDATE = 0x00000001
    
class UpdateFormat(object):
    RAW = 0x01
    BMP = 0x02

class Event(CompositeType):
    """
    @summary: A recorded event
    """
    def __init__(self, event = None):
        CompositeType.__init__(self)
        self.type = UInt16Le(lambda:event.__class__._TYPE_)
        self.timestamp = UInt32Le()
        self.length = UInt32Le(lambda:(sizeof(self) - 12))
        
        def EventFactory():
            """
            @summary: Closure for event factory
            """
            for c in [UpdateEvent]:
                if self.type.value == c._TYPE_:
                    return c(readLen = self.length)
            log.debug("unknown event type : %s"%hex(self.type.value))
            #read entire packet
            return String(readLen = self.length - 4)
        
        if event is None:
            event = FactoryType(EventFactory)
        elif not "_TYPE_" in event.__class__.__dict__:
            raise error.InvalidExpectedDataException("Try to send an invalid event block")
            
        self.event = event
        
class UpdateEvent(CompositeType):
    _TYPE_ = EventType.UPDATE
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.destLeft = UInt16Le()
        self.destTop = UInt16Le()
        self.destRight = UInt16Le()
        self.destBottom = UInt16Le()
        self.width = UInt16Le()
        self.height = UInt16Le()
        self.bpp = UInt8()
        self.format = UInt8()
        self.length = UInt32Le(lambda:sizeof(self.data))
        self.data = String(readLen = self.length)
        
class FileRecorder(object):
    def __init__(self, f):
        self._file = f
        self._createTime = int(time.time() * 1000)
        
    def add(self, event):
        e = Event(event)
        e.timestamp.value = int(time.time() * 1000) - self._createTime
        
        s = Stream()
        s.writeType(e)
        
        self._file.write(s.getvalue())
        
class FileReader(object):
    def __init__(self, f):
        self._s = Stream(f)
        
    def next(self):
        e = Event()
        self._s.readType(e)
        return e
        
def createRecorder(path):
    return FileRecorder(open(path, "wb"))

def createReader(path):
    return FileReader(open(path, "rb"))