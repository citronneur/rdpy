#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
@summary: Credential Security Support Provider
@see: https://msdn.microsoft.com/en-us/library/cc226764.aspx
"""

from pyasn1.type import namedtype, univ
from pyasn1.codec.ber import encoder
from rdpy.core.type import Stream

class NegoData(univ.SequenceOf):
    """
    @summary: contain spnego ntlm of kerberos data
    @see: https://msdn.microsoft.com/en-us/library/cc226781.aspx
    """
    componentType = univ.OctetString()

class TSRequest(univ.Sequence):
    """
    @summary: main structure
    @see: https://msdn.microsoft.com/en-us/library/cc226780.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('version', univ.Integer()),
        namedtype.OptionalNamedType('negoTokens', NegoData()),
        namedtype.OptionalNamedType('authInfo', univ.OctetString()),
        namedtype.OptionalNamedType('pubKeyAuth', univ.OctetString()),
        namedtype.OptionalNamedType('errorCode', univ.Integer())
        )

class TSCredentials(univ.Sequence):
    """
    @summary: contain user information
    @see: https://msdn.microsoft.com/en-us/library/cc226782.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('credType', univ.Integer()),
        namedtype.NamedType('credentials', univ.OctetString())
        )
    
class TSPasswordCreds(univ.Sequence):
    """
    @summary: contain username and password
    @see: https://msdn.microsoft.com/en-us/library/cc226783.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('domainName', univ.OctetString()),
        namedtype.NamedType('userName', univ.OctetString()),
        namedtype.NamedType('password', univ.OctetString())
        )

class TSCspDataDetail(univ.Sequence):
    """
    @summary: smart card credentials
    @see: https://msdn.microsoft.com/en-us/library/cc226785.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('keySpec', univ.Integer()),
        namedtype.OptionalNamedType('cardName', univ.OctetString()),
        namedtype.OptionalNamedType('readerName', univ.OctetString()),
        namedtype.OptionalNamedType('containerName', univ.OctetString()),
        namedtype.OptionalNamedType('cspName', univ.OctetString())
        )

class TSSmartCardCreds(univ.Sequence):
    """
    @summary: smart card credentials
    @see: https://msdn.microsoft.com/en-us/library/cc226784.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('pin', univ.OctetString()),
        namedtype.NamedType('cspData', TSCspDataDetail()),
        namedtype.OptionalNamedType('userHint', univ.OctetString()),
        namedtype.OptionalNamedType('domainHint', univ.OctetString())
        )

def createBERRequest(negoTokens):
    """
    @summary: create TSRequest from list of Type
    @param negoTokens: {list(Type)}
    @return: {str}
    """
    negoData = NegoData()
    
    #fill nego data tokens
    i = 0
    for negoToken in negoTokens:
        s = Stream()
        s.writeType(negoToken)
        negoData.setComponentByPosition(i, s.getvalue())
        i += 1
        
    request = TSRequest()
    request.setComponentByName("version", univ.Integer(2))
    request.setComponentByName("negoTokens", negoData)
    return encoder.encode(request)
        