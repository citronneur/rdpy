'''
Created on 4 sept. 2013

@author: sylvain
'''

class RfbObserver(object):
    '''
    Rfb protocol obserser
    '''
    def notifyFramebufferUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        recv framebuffer update
        width : width of image
        height : height of image
        x : x position
        y : y position
        pixelFormat : pixel format struct from rfb.types
        encoding : encoding struct from rfb.types
        data : in respect of dataFormat and pixelFormat
        '''
        pass
        