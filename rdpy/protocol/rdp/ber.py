'''
@author: sylvain
'''
from rdpy.protocol.network.type import UInt16Le
from rdpy.utils.const import ConstAttributes

@ConstAttributes
class BerPc(object):
    BER_PC_MASK = UInt16Le(0x20)
    BER_PRIMITIVE = UInt16Le(0x00)
    BER_CONSTRUCT = UInt16Le(0x20)

def berPC(pc):
    '''
    return BER_CONSTRUCT if true
    BER_PRIMITIVE if false
    '''
    if pc:
        return BerPc.BER_CONSTRUCT
    else:
        return BerPc.BER_PRIMITIVE
        