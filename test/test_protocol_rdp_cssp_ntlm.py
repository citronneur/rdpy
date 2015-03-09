#
# Copyright (c) 2014 Sylvain Peyrefitte
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
unit test for rdpy.protocol.rdp.nla.cssp and ntlm module
"""
import unittest
import os, sys
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from rdpy.protocol.rdp.nla import cssp, ntlm
from rdpy.security import rc4

pubKeyHex = """
MIGJAoGBAJ6VtUEDxTPqKWUrZe8wcd1zuzA77Mpyz73g+C
H/ppd2oQi10saVgdK6cRBKrCU0N6DD\nV/DqH4yE63vmbF
AmH7dBCljTgIc9C0HZvFQ6D3cUefW5pDjrEwg1rr+zF1ri
WIk5xCJ/FleQCK+R\nO5XIU9DAjhmK8xC8yMdC+xLeLV6D
AgMBAAE=
"""
peer0_0 = """
MC+gAwIBAqEoMCYwJKAiBCBOVExNU1NQAAEAAAA1gghgAA
AAAAAAAAAAAAAAAAAAAA==
"""
peer1_0 = """
MIIBCaADAgECoYIBADCB/TCB+qCB9wSB9E5UTE1TU1AAAg
AAAA4ADgA4AAAANYKJYnPHQ6nn/Lv8\nAAAAAAAAAACuAK
4ARgAAAAYBsR0AAAAPUwBJAFIAQQBEAEUATAACAA4AUwBJ
AFIAQQBEAEUATAAB\nABYAVwBBAFYALQBHAEwAVwAtADAA
MAA5AAQAGgBTAGkAcgBhAGQAZQBsAC4AbABvAGMAYQBsAA
MA\nMgB3AGEAdgAtAGcAbAB3AC0AMAAwADkALgBTAGkAcg
BhAGQAZQBsAC4AbABvAGMAYQBsAAUAGgBT\nAGkAcgBhAG
QAZQBsAC4AbABvAGMAYQBsAAcACABWkzQyx1XQAQAAAAA=
"""
peer0_1 = """
MIICD6ADAgECoYIBYjCCAV4wggFaoIIBVgSCAVJOVExNU1
NQAAMAAAAYABgAUAAAANoA2gBoAAAA\nCAAIAEAAAAAIAA
gASAAAAAAAAABQAAAAEAAQAEIBAAA1gghgYwBvAGMAbwB0
AG8AdABvABqKwrxk\n2sAom6gUCFFt1rgpCdKZGTNwnlGg
bsU5R/OelmrD/LLrx+ABAQAAAAAAAABFCDLHVdABKQnSmR
kz\ncJ4AAAAAAgAOAFMASQBSAEEARABFAEwAAQAWAFcAQQ
BWAC0ARwBMAFcALQAwADAAOQAEABoAUwBp\nAHIAYQBkAG
UAbAAuAGwAbwBjAGEAbAADADIAdwBhAHYALQBnAGwAdwAt
ADAAMAA5AC4AUwBpAHIA\nYQBkAGUAbAAuAGwAbwBjAGEA
bAAFABoAUwBpAHIAYQBkAGUAbAAuAGwAbwBjAGEAbAAHAA
gAVpM0\nMsdV0AEAAAAAv+z19mkBOu9b0Kv+P991MKOCAK
AEggCcAQAAAMQOzZaPZ8DdAAAAAM+IvTDiU0pL\njUnU6a
NjH+gZWeaIlqpQNYECmpElixwPj8aRRFVfTtkbw66U3gmo
3YBkUoVK8tfHESkivuWtV2tP\n3KGuAFv/6GzbFYQYlA7r
zZ1Bw072ps8s9cWeoNmAX6oiZmFW3j7LX3xkr7+nJoOoXI
jzvorm5kz3\nldCo8Iwh+IZ3SSnj0/h4H1GR
"""

class TestCsspNtlm(unittest.TestCase):
    """
    @summary: test generate ntlmv2 over cssp authentication protocol
    """
    def testCSSPNTLMAuthentication(self):
        negotiate_data_request = cssp.decodeDERTRequest(peer0_0.decode('base64'))
        challenge_data_request = cssp.decodeDERTRequest(peer1_0.decode('base64'))
        authenticate_data_request = cssp.decodeDERTRequest(peer0_1.decode('base64'))
        
        negotiate_data = cssp.getNegoTokens(negotiate_data_request)[0]
        challenge_data = cssp.getNegoTokens(challenge_data_request)[0]
        authenticate_data = cssp.getNegoTokens(authenticate_data_request)[0]
        
        negotiate = ntlm.NegotiateMessage()
        negotiate_data.readType(negotiate)
        
        challenge = ntlm.ChallengeMessage()
        challenge_data.readType(challenge)
        
        ServerChallenge = challenge.ServerChallenge.value
        ServerName = challenge.getTargetInfo()
    
        authenticate = ntlm.AuthenticateMessage()
        authenticate_data.readType(authenticate)
        
        NtChallengeResponseTemp = authenticate.getNtChallengeResponse()
        NTProofStr = NtChallengeResponseTemp[:16]
        temp = NtChallengeResponseTemp[16:]
        Timestamp = temp[8:16]
        ClientChallenge = temp[16:24]
        
        EncryptedRandomSessionKey = authenticate.getEncryptedRandomSession()
        domain = "coco"
        user = "toto"
        password = "lolo"
        
        ResponseKeyNT = ntlm.NTOWFv2(password, user, domain)
        ResponseKeyLM = ntlm.LMOWFv2(password, user, domain)
        NtChallengeResponse, LmChallengeResponse, SessionBaseKey = ntlm.ComputeResponsev2(ResponseKeyNT, ResponseKeyLM, ServerChallenge, ClientChallenge, Timestamp, ServerName)
        KeyExchangeKey = ntlm.KXKEYv2(SessionBaseKey, LmChallengeResponse, ServerChallenge)
        ExportedSessionKey = ntlm.RC4K(KeyExchangeKey, EncryptedRandomSessionKey)
        
        domain, user = domain, user
        if challenge.NegotiateFlags.value & ntlm.Negotiate.NTLMSSP_NEGOTIATE_UNICODE:
            domain, user = ntlm.UNICODE(domain), ntlm.UNICODE(user)
            
        ClientSigningKey = ntlm.SIGNKEY(ExportedSessionKey, True)
        ServerSigningKey = ntlm.SIGNKEY(ExportedSessionKey, False)
        ClientSealingKey = ntlm.SEALKEY(ExportedSessionKey, True)
        ServerSealingKey = ntlm.SEALKEY(ExportedSessionKey, False)
        
        interface = ntlm.NTLMv2SecurityInterface(rc4.RC4Key(ClientSealingKey), rc4.RC4Key(ServerSealingKey), ClientSigningKey, ServerSigningKey)
        
        EncryptedPubKeySrc = cssp.getPubKeyAuth(authenticate_data_request)
        EncryptedPubKeyDst = interface.GSS_WrapEx(pubKeyHex.decode('base64'))
        
        self.assertTrue(EncryptedPubKeySrc == EncryptedPubKeyDst, "Public key must be equals")
        