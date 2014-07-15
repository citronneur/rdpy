# RDPY

Remote Desktop Protocol in Twisted Python.

RDPY is ful python except the bitmap decompression in RDP client for performance. RDPY has no ambition to be as faster as freerdp, rdesktop or mstsc, is made to play with microsoft protocol. There are some limitations essentially due to price of license (Packet redirection and License extesion in RDP protocol).


## Requirements
* python2.7
* python-twisted
* python-openssl
* python-qt4
* python-qt4reactor
* python-sip-dev
* scons

## Build
```
$ git clone https://github.com/citronneur/rdpy.git rdpy
$ scons -C rdpy/lib install
```

## Binaries
Binaries are uses as examples to use rdpy lib.

To create an RDP client (this example doesn't need build step of project because it doesn't call bitmap uncompress):
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
			#send r key
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

RDP Client
```
$ rdpy/bin/rdpy-rdpclient XXX.XXX.XXX.XXX 3389
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
* License
* Most common orders
* Des VNC (using pyDes)
* VNC server side

this project is still in progress.
