'''
@author: sylvain
'''
import sys, os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import unittest, rdpy.tests.network.type, rdpy.tests.network.const, rdpy.tests.network.layer

def headerTest(name):
    print "*"*70
    print name
    print "*"*70
    
if __name__ == '__main__':
    headerTest("Test case rdpy.test.network.type.TypeCase")
    suite = unittest.TestLoader().loadTestsFromTestCase(rdpy.tests.network.type.TypeCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    headerTest("Test case rdpy.test.network.const.ConstCase")
    suite = unittest.TestLoader().loadTestsFromTestCase(rdpy.tests.network.const.ConstCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    headerTest("Test case rdpy.test.network.type.layer.LayerCase")
    suite = unittest.TestLoader().loadTestsFromTestCase(rdpy.tests.network.layer.LayerCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

