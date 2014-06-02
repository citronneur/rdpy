'''
@author: sylvain
'''
import unittest
import rdpy.network.layer

class LayerCase(unittest.TestCase):
    '''
    represent test case for all classes and function
    present in rdpy.network.layer
    '''
    
    class LayerCaseException(Exception):
        '''
        exception use for event base test
        '''
        pass
    
    def test_layer_connect_event(self):
        '''
        test if connect event is send from transport to presentation
        '''
        class TestConnect(rdpy.network.layer.Layer):
            def connect(self):
                raise LayerCase.LayerCaseException()
            
        self.assertRaises(LayerCase.LayerCaseException, rdpy.network.layer.Layer(presentation = TestConnect()).connect)
        
    def test_layer_receive_event(self):
        '''
        test if recv event is send from transport to presentation
        '''
        class TestConnect(rdpy.network.layer.Layer):
            def recv(self, s):
                if s == "message":
                    raise LayerCase.LayerCaseException()
            
        self.assertRaises(LayerCase.LayerCaseException, rdpy.network.layer.Layer(presentation = TestConnect()).recv, "message")