'''
@author: sylvain
'''

from rdpy.protocol.network.layer import LayerAutomata

class MCS(LayerAutomata):
    '''
    Multi Channel Service layer
    the main layer of RDP protocol
    is why he can do everything and more!
    '''
    
    def __init__(self, presentation = None):
        '''
        ctor call base class ctor
        '''
        LayerAutomata.__init__(self, presentation)
    
    def connect(self):
        '''
        connection send for client mode
        a write connect initial packet
        '''
        