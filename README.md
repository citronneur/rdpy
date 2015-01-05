# RDPY [![Build Status](https://travis-ci.org/citronneur/rdpy.svg?branch=dev)](https://travis-ci.org/citronneur/rdpy)

Remote Desktop Protocol in twisted PYthon.

RDPY is a pure Python implementation of the Microsoft RDP (Remote Desktop Protocol) protocol. RDPY is built over the event driven network engine Twisted.

## Build

RDPY is fully implemented in python, except the bitmap uncompression algorithm which is implemented in C for performance purposes.

### Depends

#### Linux

Exemple from Debian based system :
```
sudo apt-get install python-qt4
```

#### Windows

x86 | x86_64
----|-------
[PyQt4](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt4-4.11.3-gpl-Py2.7-Qt4.8.6-x32.exe) | [PyQt4](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt4-4.11.3-gpl-Py2.7-Qt4.8.6-x64.exe/download)
[PyWin32](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/pywin32-218.win32-py2.7.exe/download) | [PyWin32](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/pywin32-218.win-amd64-py2.7.exe/download)

### Build

```
$ git clone https://github.com/citronneur/rdpy.git rdpy
$ pip install twisted pyopenssl qt4reactor service_identity rsa
$ python rdpy/setup.py install
```

Or use PIP:
```
$ pip install rdpy
```

For virtualenv, you need to link qt4 library to it:
```
$ ln -s /usr/lib/python2.7/dist-packages/PyQt4/ $VIRTUAL_ENV/lib/python2.7/site-packages/
$ ln -s /usr/lib/python2.7/dist-packages/sip.so $VIRTUAL_ENV/lib/python2.7/site-packages/
```

## RDPY Binaries

RDPY comes with some very useful binaries; These binaries are linux and windows compatible.

### rdpy-rdpclient

rdpy-rdpclient is a simple RDP Qt4 client .

```
$ rdpy-rdpclient.py [-u username] [-p password] [-d domain] [...] XXX.XXX.XXX.XXX[:3389]
```

### rdpy-vncclient

rdpy-vncclient is a simple VNC Qt4 client .

```
$ rdpy-vncclient.py [-p password] XXX.XXX.XXX.XXX[:5900]
```

### rdpy-rdpscreenshot

rdpy-rdpscreenshot save login screen in file.

```
$ rdpy-rdpscreenshot.py [-w width] [-l height] [-o output_file_path] XXX.XXX.XXX.XXX[:3389]
```

### rdpy-vncscreenshot

rdpy-vncscreenshot save first screen update in file.

```
$ rdpy-vncscreenshot.py [-p password] [-o output_file_path] XXX.XXX.XXX.XXX[:5900]
```

### rdpy-rdpproxy

rdpy-rdpproxy is a RDP proxy with shadow and record function.

```
$ rdpy-rdpproxy.py -t target_ip[:target_port] [-k private_key_file_path] [-c certificate_file_path] [-i admin_ip[:admin_port]] listen_port
```

The target ip and port represent the target host.

The private key file and the certificate file are classic cryptographic files for SSL connections. The RDP protocol can negotiate its own security layer. The CredSSP security layer is planned for an upcoming release. If one of both parameters are omitted, the server use standard RDP as security layer.

The IP and port admin are used in order to shadow active sessions thanks to a RDP client (rdpy-rdpclient, remina, mstsc) set username parameter like name of session printed by proxy.

Exemple : 
```
$ rdpy-rdpproxy.py -t [my_computer] -i 0.0.0.0:56654 3389
$ INFO : Shadow listener on 0.0.0.0:56654
$ INFO : **************************************************
$ INFO : Now connected
$ INFO : ['super-administrator']
$ INFO : **************************************************
```

To shadow 'super-administrator' session :
```
$ rdpy-rdpclient.py -u super-administrator 127.0.0.1:56654
```

## RDPY Qt Widget

RDPY can also be used as Qt widget throw rdpy.ui.qt4.QRemoteDesktop class. It can be embedded in your own Qt application. qt4reactor must be used in your app for Twisted and Qt to work together. For more details, see sources of rdpy-rdpclient.

## RDPY library

In a nutshell the RDPY can be used as a protocol library with a twisted engine.

### Simple RDP Client

```python
from rdpy.protocol.rdp import rdp

class MyRDPFactory(rdp.ClientFactory):

	def clientConnectionLost(self, connector, reason):
        reactor.stop()
        
    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
        
    def buildObserver(self, controller, addr):
    
        class MyObserver(rdp.RDPClientObserver)
        
        	def onReady(self):
		        """
		        @summary: Call when stack is ready
		        """
				#send 'r' key
				self._controller.sendKeyEventUnicode(ord(unicode("r".toUtf8(), encoding="UTF-8")), True)
				#mouse move and click at pixel 200x200
				self._controller.sendPointerEvent(200, 200, 1, true)
				
			def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
		        """
		        @summary: Notify bitmap update
		        @param destLeft: xmin position
		        @param destTop: ymin position
		        @param destRight: xmax position because RDP can send bitmap with padding
		        @param destBottom: ymax position because RDP can send bitmap with padding
		        @param width: width of bitmap
		        @param height: height of bitmap
		        @param bitsPerPixel: number of bit per pixel
		        @param isCompress: use RLE compression
		        @param data: bitmap data
		        """
				
			def onClose(self):
		        """
		        @summary: Call when stack is close
		        """

		return MyObserver(controller)

from twisted.internet import reactor
reactor.connectTCP("XXX.XXX.XXX.XXX", 3389), MyRDPFactory())
reactor.run()
```

### Simple RDP Server
```python
from rdpy.protocol.rdp import rdp

class MyRDPFactory(rdp.ServerFactory):

    def buildObserver(self, controller, addr):
    
        class MyObserver(rdp.RDPServerObserver)
        
        	def onReady(self):
        		"""
        		@summary: Call when server is ready 
        		to send and receive messages
        		"""
        		
        	def onKeyEventScancode(self, code, isPressed):
        		"""
		        @summary: Event call when a keyboard event is catch in scan code format
		        @param code: scan code of key
		        @param isPressed: True if key is down
		        @see: rdp.RDPServerObserver.onKeyEventScancode
		        """
	        
	        def onKeyEventUnicode(self, code, isPressed):
		        """
		        @summary: Event call when a keyboard event is catch in unicode format
		        @param code: unicode of key
		        @param isPressed: True if key is down
		        @see: rdp.RDPServerObserver.onKeyEventUnicode
		        """
		    
		    def onPointerEvent(self, x, y, button, isPressed):
		        """
		        @summary: Event call on mouse event
		        @param x: x position
		        @param y: y position
		        @param button: 1, 2 or 3 button
		        @param isPressed: True if mouse button is pressed
		        @see: rdp.RDPServerObserver.onPointerEvent
		        """
		        
		    def onClose(self):
		        """
		        @summary: Call when human client close connection
		        @see: rdp.RDPServerObserver.onClose
		        """

		return MyObserver(controller)

from twisted.internet import reactor
reactor.listenTCP(3389, MyRDPFactory())
reactor.run()
```

### Simple VNC Client
```python
from rdpy.protocol.rfb import rdp

class MyRFBFactory(rfb.ClientFactory):

	def clientConnectionLost(self, connector, reason):
        reactor.stop()
        
    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
        
    def buildObserver(self, controller, addr):
        class MyObserver(rfb.RFBClientObserver)
        		
			def onReady(self):
		        """
		        @summary: Event when network stack is ready to receive or send event
		        """

			def onUpdate(self, width, height, x, y, pixelFormat, encoding, data):
		        """
		        @summary: Implement RFBClientObserver interface
		        @param width: width of new image
		        @param height: height of new image
		        @param x: x position of new image
		        @param y: y position of new image
		        @param pixelFormat: pixefFormat structure in rfb.message.PixelFormat
		        @param encoding: encoding type rfb.message.Encoding
		        @param data: image data in accordance with pixel format and encoding
		        """
		        
		    def onCutText(self, text):
		        """
		        @summary: event when server send cut text event
		        @param text: text received
		        """
		        
		    def onBell(self):
		        """
		        @summary: event when server send biiip
		        """
				
			def onClose(self):
		        """
		        @summary: Call when stack is close
		        """

		return MyObserver(controller)

from twisted.internet import reactor
reactor.connectTCP("XXX.XXX.XXX.XXX", 3389), MyRFBFactory())
reactor.run()
```
