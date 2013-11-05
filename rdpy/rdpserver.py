'''
@author: sylvain
'''

import sys, os
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from rdpy.protocol.rdp import rdp

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.listenTCP(33389, rdp.Factory())
    reactor.run()