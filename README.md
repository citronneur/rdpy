# RDPY

Remote Desktop Protocol in Twisted Python.

RDPY is full python implementation of RDP and VNC protocol, except the bitmap uncompress for performance. The main goal of RDPY is not to be as faster as freerdp, rdesktop or mstsc, but is made to play with protocol. You can use it as twisted library. In library mode build step is not necessary until you want to uncompress bitmap data. You can use it as QWidget in your Qt4 application. Most of GUI library compatibility would be implemented. You can use pre made script (call binaries) for rdp and vnc client, or rdp proxy with admin spy port.

## Requirements

### Twisted library requirements

* python2.7
* python-twisted
* python-openssl

### Binaries and graphical examples requirements

* python-qt4
* python-qt4reactor
* python-sip-dev
* scons

## Build
```
$ git clone https://github.com/citronneur/rdpy.git rdpy
$ scons -C rdpy/rdpy/core install
```

## Library Mode
To create a RDP client:
```
from rdpy.protocol.rdp import rdp
class MyRDPFactory(rdp.ClientFactory):
    def buildObserver(self, controller):
        class MyObserver(rdp.RDPClientObserver)
			def __init__(self, controller)
				rdp.RDPClientObserver.__init__(self, controller)
			def onBitmapUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
				#here code handle bitmap
				pass
			def onReady(self):
				#send 'r' key
				self._controller.sendKeyEventUnicode(ord(unicode("r".toUtf8(), encoding="UTF-8")), True)
				#mouse move and click at pixel 200x200
				self._controller.sendPointerEvent(200, 200, 1, true)

		return MyObserver(controller)

    def startedConnecting(self, connector):
        pass
    def clientConnectionLost(self, connector, reason):
        pass
    def clientConnectionFailed(self, connector, reason):
        pass

from twisted.internet import reactor
reactor.connectTCP("XXX.XXX.XXX.XXX", 3389), MyRDPFactory())
reactor.run()
```
For more details on client rdp see rdpy/bin/rdpy-rdpclient binaries.

## Binaries Mode
RDPY is delivered with 3 binaries : 

RDP Client
```
$ rdpy/bin/rdpy-rdpclient [-u username] [-p password] [-d domain] [...] XXX.XXX.XXX.XXX[:3389]
```

VNC Client
```
$ rdpy/bin/rdpy-vncclient XXX.XXX.XXX.XXX 5901
```

RDP Proxy
```
$ rdpy/bin/rdpy-rdpproxy
```

##Limitations
* CreedSSP
* Packet redirection
* License (in progress)
* Most common orders (in progress)
* DES VNC (using pyDes) (in progress)
* VNC server side
* RDP server side (in progress)

this project is still in progress.
