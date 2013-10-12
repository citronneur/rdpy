'''
@author: citronneur
'''
class Layer(object):
    '''
    Network abstraction for protocol
    Try as possible to divide user protocol in layer
    default implementation is a transparent layer
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        #presentation layer higher layer in model
        self._presentation = presentation
        #transport layer under layer in model
        self._transport = None
        #auto set transport layer of own presentation layer
        if not self._presentation is None:
            self._presentation._transport = self
    
    def connect(self):
        '''
        call when transport layer is connected
        default is send connect event to presentation layer
        '''
        if not self._presentation is None:
            self._presentation.connect()
    
    def read(self, data):
        '''
        signal that data is available for this layer
        call by transport layer
        default is to pass data to presentation layer
        '''
        if not self._presentation is None:
            self._presentation.read(data)
      
    def write(self, data):
        '''
        classical use by presentation layer
        write data for this layer
        default pass data to transport layer
        '''
        self.transport.write(data)