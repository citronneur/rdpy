#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name='rdpy',
	version='1.0',
	description='Remote Desktop Protocol in Python',
	author='Sylvain Peyrefitte',
	author_email='citronneur@gmail.com',
	url='https://github.com/citronneur/rdpy',
	packages=[
			'rdpy', 
			'rdpy.base', 
			'rdpy.network', 
			'rdpy.protocol', 
			'rdpy.protocol.rdp', 
			'rdpy.protocol.rdp.pdu', 
			'rdpy.protocol.rfb', 
			'rdpy.ui'
		],
	ext_modules=[Extension('rle', ['ext/rle.c'])],
	scripts = [
			'bin/rdpy-rdpclient', 
			'bin/rdpy-rdpproxy', 
			'bin/rdpy-rdpscreenshot', 
			'bin/rdpy-vncclient', 
			'bin/rdpy-vncscreenshot'
		],
	install_requires=[
			'twisted',
          	'pyopenssl',
          	'qt4reactor',
	  	],
)
