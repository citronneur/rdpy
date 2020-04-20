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
import pyasn1.codec.der.encoder as der_encoder
import pyasn1.codec.der.decoder as der_decoder

from rdpy.core.nla import sspi
from rdpy.model.message import Stream
from rdpy.model import error
from rdpy.security.x509 import X509Certificate


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



def encode_der_trequest(nego_types=[], auth_info=None, pub_key_auth=None):
    """
    @summary: create TSRequest from list of Type
    @param nego_types: {list(Type)}
    @param auth_info: {str} authentication info TSCredentials encrypted with authentication protocol
    @param pub_key_auth: {str} public key encrypted with authentication protocol
    @return: {str} TRequest der encoded
    """
    negoData = NegoData().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))
    
    #fill nego data tokens
    i = 0
    for negoType in nego_types:
        s = Stream()
        s.write_type(negoType)
        negoToken = NegoToken()
        negoToken.setComponentByPosition(0, s.getvalue())
        negoData.setComponentByPosition(i, negoToken)
        i += 1
        
    request = TSRequest()
    request.setComponentByName("version", univ.Integer(2).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0)))
    
    if i > 0:
        request.setComponentByName("negoTokens", negoData)
    
    if not auth_info is None:
        request.setComponentByName("authInfo", univ.OctetString(auth_info).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2)))
    
    if not pub_key_auth is None:
        request.setComponentByName("pubKeyAuth", univ.OctetString(pub_key_auth).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3)))
        
    return der_encoder.encode(request)


def decode_der_trequest(s):
    """
    @summary: Decode the stream as 
    @param s: {str}
    """
    return der_decoder.decode(s, asn1Spec=TSRequest())[0]


def getNegoTokens(tRequest):
    negoData = tRequest.getComponentByName("negoTokens")
    return [Stream(negoData.getComponentByPosition(i).getComponentByPosition(0).asOctets()) for i in range(len(negoData))]


def encode_der_tcredentials(domain, username, password):
    passwordCred = TSPasswordCreds()
    passwordCred.setComponentByName("domainName", domain)
    passwordCred.setComponentByName("userName", username)
    passwordCred.setComponentByName("password", password)
    
    credentials = TSCredentials()
    credentials.setComponentByName("credType", 1)
    credentials.setComponentByName("credentials", der_encoder.encode(passwordCred))
    
    return der_encoder.encode(credentials)


async def connect(reader, writer, authentication_protocol: sspi.IAuthenticationProtocol):
    """
    CSSP connection sequence
    """
    # send negotiate message
    writer.write(encode_der_trequest(nego_types=[authentication_protocol.getNegotiateMessage()]))
    await writer.drain()

    trequest = decode_der_trequest(await reader.read(1500))
    message, interface = authentication_protocol.getAuthenticateMessage(getNegoTokens(trequest)[0])

    # get binary certificate
    # There is no other way to get certificate that have net been validated
    peer_certificate = writer.transport._ssl_protocol._sslpipe.ssl_object._sslobj.getpeercert(True)
    x509_certificate = der_decoder.decode(peer_certificate, asn1Spec=X509Certificate())[0]
    public_key = x509_certificate.getComponentByName("tbsCertificate").getComponentByName("subjectPublicKeyInfo").getComponentByName("subjectPublicKey").asOctets()

    # send back public key encrypted with NTLM
    writer.write(encode_der_trequest(nego_types=[message], pub_key_auth=interface.GSS_WrapEx(public_key)))
    await writer.drain()

    # now check the increment
    # sever must respond with the same key incremented to one
    trequest = decode_der_trequest(await reader.read(1500))
    public_key_inc = interface.GSS_UnWrapEx(trequest.getComponentByName("pubKeyAuth").asOctets())

    if int.from_bytes(public_key, "little") + 1 != int.from_bytes(public_key_inc, "little"):
        raise error.InvalidExpectedDataException("CSSP : Invalid public key increment")

    domain, user, password = authentication_protocol.getEncodedCredentials()
    writer.write(encode_der_trequest(auth_info=interface.GSS_WrapEx(encode_der_tcredentials(domain, user, password))))
    await writer.drain()
