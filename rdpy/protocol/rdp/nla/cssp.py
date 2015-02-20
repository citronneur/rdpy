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

from pyasn1.type import namedtype, univ, tag
from pyasn1.codec.der import encoder
from rdpy.core.type import Stream

class NegoToken(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('negoToken', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
    )

class NegoData(univ.SequenceOf):
    """
    @summary: contain spnego ntlm of kerberos data
    @see: https://msdn.microsoft.com/en-us/library/cc226781.aspx
    """
    componentType = NegoToken()

class TSRequest(univ.Sequence):
    """
    @summary: main structure
    @see: https://msdn.microsoft.com/en-us/library/cc226780.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('version', univ.Integer().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.OptionalNamedType('negoTokens', NegoData().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))),
        namedtype.OptionalNamedType('authInfo', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2))),
        namedtype.OptionalNamedType('pubKeyAuth', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3))),
        namedtype.OptionalNamedType('errorCode', univ.Integer().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 4)))
        )

class TSCredentials(univ.Sequence):
    """
    @summary: contain user information
    @see: https://msdn.microsoft.com/en-us/library/cc226782.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('credType', univ.Integer().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType('credentials', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1)))
        )
    
class TSPasswordCreds(univ.Sequence):
    """
    @summary: contain username and password
    @see: https://msdn.microsoft.com/en-us/library/cc226783.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('domainName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType('userName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))),
        namedtype.NamedType('password', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2)))
        )

class TSCspDataDetail(univ.Sequence):
    """
    @summary: smart card credentials
    @see: https://msdn.microsoft.com/en-us/library/cc226785.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('keySpec', univ.Integer().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.OptionalNamedType('cardName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))),
        namedtype.OptionalNamedType('readerName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2))),
        namedtype.OptionalNamedType('containerName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3))),
        namedtype.OptionalNamedType('cspName', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 4)))
        )

class TSSmartCardCreds(univ.Sequence):
    """
    @summary: smart card credentials
    @see: https://msdn.microsoft.com/en-us/library/cc226784.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('pin', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType('cspData', TSCspDataDetail().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))),
        namedtype.OptionalNamedType('userHint', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2))),
        namedtype.OptionalNamedType('domainHint', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3)))
        )

def createBERRequest(negoTypes):
    """
    @summary: create TSRequest from list of Type
    @param negoTypes: {list(Type)}
    @return: {str}
    """
    negoData = NegoData().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))
    
    #fill nego data tokens
    i = 0
    for negoType in negoTypes:
        s = Stream()
        s.writeType(negoType)
        negoToken = NegoToken()
        negoToken.setComponentByPosition(0, s.getvalue())
        negoData.setComponentByPosition(i, negoToken)
        i += 1
        
    request = TSRequest()
    request.setComponentByName("version", univ.Integer(2).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0)))
    request.setComponentByName("negoTokens", negoData)
    return encoder.encode(request)
        