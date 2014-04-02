'''
@author: sylvain
'''
import sys, os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import unittest, rdpy.test.network.type

def headerTest(name):
    print "-"*40
    print name
    print "-"*40
    
if __name__ == '__main__':
    headerTest("Test case rdpy.test.network.type.TypeCase")
    suite = unittest.TestLoader().loadTestsFromTestCase(rdpy.test.network.type.TypeCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

