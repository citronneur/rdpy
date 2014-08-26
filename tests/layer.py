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
        
    def test_layer_automata_more_than_expected(self):
        '''
        test layer automata mechanism if data received is more than expected
        '''
        class TestAutomata(rdpy.network.layer.RawLayer):
            def expectedCallBack(self, data):
                if data.dataLen() == 4:
                    raise LayerCase.LayerCaseException()
            
        t = TestAutomata()
        t.expect(4, t.expectedCallBack)
        self.assertRaises(LayerCase.LayerCaseException, t.dataReceived, "\x00\x00\x00\x00\x00")
        
    def test_layer_automata_less_than_expected(self):
        '''
        test layer automata mechanism
        '''
        class TestAutomata(rdpy.network.layer.RawLayer):
            def expectedCallBack(self, data):
                if data.dataLen() == 4:
                    raise LayerCase.LayerCaseException()
            
        t = TestAutomata()
        t.expect(4, t.expectedCallBack)
        self.assertEqual(t.dataReceived("\x00\x00\x00"), None, "Not enough dada")