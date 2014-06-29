# RDPY

Remote Desktop Protocol in Twisted Python

## Requirements
* python2.7
* python-twisted
* python-openssl
* python-qt4
* python-qt4reactor

## Requirements libs
* python-sip-dev
* scons
```
$ git clone https://github.com/citronneur/rdpy.git rdpy
$ scons -C rdpy/lib install
```

## Binaries
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
$ rdpy/bin/rdpy-vncclient XXX.XXX.XXX.XXX 5901
```

##Must be implemented before first release
* CreedSSP
* Packet redirection
* License
* Most common orders
* FastPath messages
* Des VNC (using pyDes)

this project is still in progress.
