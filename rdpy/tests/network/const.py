'''
@author: sylvain
'''
import unittest
import rdpy.network.const
import rdpy.network.type

class ConstCase(unittest.TestCase):
    '''
    represent test case for all classes and function
    present in rdpy.network.const
    '''
    def test_type_attributes(self):
        '''
        test if type attributes decorator works
        '''
        @rdpy.network.const.TypeAttributes(rdpy.network.type.UInt16Le)
        class Test:
            MEMBER_1 = 1
            MEMBER_2 = 2
        
        self.assertIsInstance(Test.MEMBER_1, rdpy.network.type.UInt16Le, "MEMBER_1 is not in correct type")
        self.assertIsInstance(Test.MEMBER_2, rdpy.network.type.UInt16Le, "MEMBER_2 is not in correct type")
        
    def test_const(self):
        '''
        test if get on const class member generate new object each
        '''
        @rdpy.network.const.ConstAttributes
        class Test:
            MEMBER_1 = 1
            MEMBER_2 = 2
            
        self.assertEquals(Test.MEMBER_1, Test.MEMBER_1, "handle same type of object")