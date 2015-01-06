#!/usr/bin/env python

import setuptools
from distutils.core import setup, Extension

setup(name='rdpy',
	version='1.2.0',
	description='Remote Desktop Protocol in Python',
	long_description="""
	RDPY is a pure Python implementation of the Microsoft RDP (Remote Desktop Protocol) protocol. 
	RDPY is built over the event driven network engine Twisted.
	""",
	author='Sylvain Peyrefitte',
	author_email='citronneur@gmail.com',
	url='https://github.com/citronneur/rdpy',
	packages=[
			'rdpy', 
			'rdpy.core',
			'rdpy.security', 
			'rdpy.protocol', 
			'rdpy.protocol.rdp', 
			'rdpy.protocol.rdp.pdu', 
			'rdpy.protocol.rfb', 
			'rdpy.ui'
		],
	ext_modules=[Extension('rle', ['ext/rle.c'])],
	scripts = [
			'bin/rdpy-rdpclient.py', 
			'bin/rdpy-rdpproxy.py', 
			'bin/rdpy-rdpscreenshot.py', 
			'bin/rdpy-vncclient.py', 
			'bin/rdpy-vncscreenshot.py'
		],
	install_requires=[
			'twisted',
          	'pyopenssl',
          	'service_identity',
          	'qt4reactor',
          	'rsa',
	  	],
)
