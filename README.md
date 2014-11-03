# RDPY

Remote Desktop Protocol in twisted PYthon.

RDPY is still under development.

RDPY is a pure Python implementation ot the Microsoft RDP (Remote Desktop Protocol) protocol. RDPY is built over the event driven network engine Twisted.

## Build

RDPY is fully implemented in python, except the bitmap uncompression algorithm which is implemented in C and binded with SIP (originally conceived for the PyQt project) for performance purposes.

### Depends

* python2.7
* python-twisted
* python-openssl
* python-qt4
* python-qt4reactor
* python-sip-dev
* scons

### Make

```
$ git clone https://github.com/citronneur/rdpy.git rdpy
$ scons -C rdpy/rdpy/core install
```

## RDPY Binaries

RDPY comes with some very useful binaries; These binaries are linux and windows compatible. Pre-built binaries will be delivered with the first release of the project.

### rdpy-rdpclient

rdpy-rdpclient is a simple RDP Qt4 client .

```
$ rdpy/bin/rdpy-rdpclient [-u username] [-p password] [-d domain] [...] XXX.XXX.XXX.XXX[:3389]
```

### rdpy-vncclient

rdpy-vncclient is a simple VNC Qt4 client .

```
$ rdpy/bin/rdpy-vncclient [-p password] XXX.XXX.XXX.XXX[:5900]
```

### rdpy-rdpscreenshot

rdpy-rdpscreenshot save login screen in file.

```
$ rdpy/bin/rdpy-rdpscreenshot [-w width] [-l height] [-o output_file_path] XXX.XXX.XXX.XXX[:3389]
```

### rdpy-vncscreenshot

rdpy-vncscreenshot save first screen update in file.

```
$ rdpy/bin/rdpy-vncscreenshot [-p password] [-o output_file_path] XXX.XXX.XXX.XXX[:5900]
```

### rdpy-rdpproxy

rdpy-rdpproxy is a RDP proxy. It is used to manage and control access to the RDP servers as well as watch live sessions through any RDP client. It can be compared to a HTTP reverse proxy with added spy features.

```
$ rdpy/bin/rdpy-rdpproxy -f credentials_file_path -k private_key_file_path -c certificate_file_path [-i admin_ip[:admin_port]] listen_port
```

The credentials file is JSON file that must conform with the following format:

```
{
	"domain1":
	{
		"username1":
		[
			{"ip":"machine1", "port":3389"},
			{"ip":"machine2", "port":3389"}
		],
		"username2":
		[
			{"ip":"machine1", "port":3389"}
		]
	}
}
```

In this exemple domain1\username1 can access to machine1 and machine2 and domain1\username2 can only access to machine1.

The private key file and the certificate file are classic cryptographic files for SSL connections. The RDP protocol can negotiate its own security layer but RDPY is limited to SSL. The CredSSP security layer is planned for an upcoming release. The basic RDP security layer is not supported (windows wp sp1&2).

The IP and port admin are used in order to spy active sessions thanks to a RDP client (rdpy-rdpclient, remina, mstsc). Common values are 127.0.0.1:3389 to protect from connections by unauthorized user.

## RDPY Qt Widget

RDPY can also be used as Qt widget throw rdpy.ui.qt4.QRemoteDesktop class. It can be embedded in your own Qt application. qt4reactor must be used in your app for Twisted and Qt to work together. For more details, see sources of rdpy-rdpclient.

## RDPY library

In a nutshell the RDPY can be used as a protocol library with a twisted engine.

The RDP client code looks like this:

```
from rdpy.protocol.rdp import rdp

class MyRDPFactory(rdp.ClientFactory):

	def clientConnectionLost(self, connector, reason):
        reactor.stop()
        
    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
        
    def buildObserver(self, controller, addr):
        class MyObserver(rdp.RDPClientObserver)
        
			def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
				#here code handle bitmap
				pass
				
			def onReady(self):
				#send 'r' key
				self._controller.sendKeyEventUnicode(ord(unicode("r".toUtf8(), encoding="UTF-8")), True)
				#mouse move and click at pixel 200x200
				self._controller.sendPointerEvent(200, 200, 1, true)
				
			def onClose(self):
				pass

		return MyObserver(controller)

from twisted.internet import reactor
reactor.connectTCP("XXX.XXX.XXX.XXX", 3389), MyRDPFactory())
reactor.run()
```

The VNC client code looks like this:
```
from rdpy.protocol.rfb import rdp

class MyRDPFactory(rfb.ClientFactory):

	def clientConnectionLost(self, connector, reason):
        reactor.stop()
        
    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
        
    def buildObserver(self, controller, addr):
        class MyObserver(rfb.RFBClientObserver)
        		
			def onReady(self):
				pass

			def onUpdate(self, width, height, x, y, pixelFormat, encoding, data):
				#here code handle bitmap
				pass
				
			def onClose(self):
				pass

		return MyObserver(controller)

from twisted.internet import reactor
reactor.connectTCP("XXX.XXX.XXX.XXX", 3389), MyRDPFactory())
reactor.run()
```
