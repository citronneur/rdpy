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
@summary: NTLM Authentication
@see: https://msdn.microsoft.com/en-us/library/cc236621.aspx
"""

from rdpy.core.type import CompositeType, String, UInt8, UInt16Le, UInt24Le, UInt32Le

class MajorVersion(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    @see: https://msdn.microsoft.com/en-us/library/a211d894-21bc-4b8b-86ba-b83d0c167b00#id29
    """
    WINDOWS_MAJOR_VERSION_5 = 0x05
    WINDOWS_MAJOR_VERSION_6 = 0x06
    
class MinorVersion(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    @see: https://msdn.microsoft.com/en-us/library/a211d894-21bc-4b8b-86ba-b83d0c167b00#id30
    """
    WINDOWS_MINOR_VERSION_0 = 0x00
    WINDOWS_MINOR_VERSION_1 = 0x01
    WINDOWS_MINOR_VERSION_2 = 0x02
    WINDOWS_MINOR_VERSION_3 = 0x03
    
class NTLMRevision(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    """
    NTLMSSP_REVISION_W2K3 = 0x0F
    
class Negotiate(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236650.aspx
    """
    NTLMSSP_NEGOTIATE_56 = 0x80000000
    NTLMSSP_NEGOTIATE_KEY_EXCH = 0x40000000
    NTLMSSP_NEGOTIATE_128 = 0x20000000
    NTLMSSP_NEGOTIATE_VERSION = 0x02000000
    NTLMSSP_NEGOTIATE_TARGET_INFO = 0x00800000
    NTLMSSP_REQUEST_NON_NT_SESSION_KEY = 0x00400000
    NTLMSSP_NEGOTIATE_IDENTIFY = 0x00100000
    NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY = 0x00080000
    NTLMSSP_TARGET_TYPE_SERVER = 0x00020000
    NTLMSSP_TARGET_TYPE_DOMAIN = 0x00010000
    NTLMSSP_NEGOTIATE_ALWAYS_SIGN = 0x00008000
    NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED = 0x00002000
    NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED = 0x00001000
    NTLMSSP_NEGOTIATE_NTLM = 0x00000200
    NTLMSSP_NEGOTIATE_LM_KEY = 0x00000080
    NTLMSSP_NEGOTIATE_DATAGRAM = 0x00000040
    NTLMSSP_NEGOTIATE_SEAL = 0x00000020
    NTLMSSP_NEGOTIATE_SIGN = 0x00000010
    NTLMSSP_REQUEST_TARGET = 0x00000004
    NTLM_NEGOTIATE_OEM = 0x00000002
    NTLMSSP_NEGOTIATE_UNICODE = 0x00000001

class Version(CompositeType):
    """
    @summary: Version structure as describe in NTLM spec
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    """
    def __init__(self, conditional):
        CompositeType.__init__(self, conditional = conditional)
        self.ProductMajorVersion = UInt8(MajorVersion.WINDOWS_MAJOR_VERSION_6)
        self.ProductMinorVersion = UInt8(MinorVersion.WINDOWS_MINOR_VERSION_0)
        self.ProductBuild = UInt16Le(6002)
        self.Reserved = UInt24Le()
        self.NTLMRevisionCurrent = UInt8(NTLMRevision.NTLMSSP_REVISION_W2K3)

class NegotiateMessage(CompositeType):
    """
    @summary: Negotiate capability of NTLM Authentication
    @see: https://msdn.microsoft.com/en-us/library/cc236641.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Signature = String("NTLMSSP\x00", constant = True)
        self.MessageType = UInt32Le(0x00000001)
        self.NegotiateFlags = UInt32Le(Negotiate.NTLMSSP_NEGOTIATE_KEY_EXCH |
                              Negotiate.NTLMSSP_NEGOTIATE_128 |
                              Negotiate.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY |
                              Negotiate.NTLMSSP_NEGOTIATE_ALWAYS_SIGN |
                              Negotiate.NTLMSSP_NEGOTIATE_NTLM |
                              Negotiate.NTLMSSP_NEGOTIATE_SIGN |
                              Negotiate.NTLMSSP_NEGOTIATE_SEAL |
                              Negotiate.NTLMSSP_REQUEST_TARGET |
                              Negotiate.NTLMSSP_NEGOTIATE_UNICODE)
        self.DomainNameLen = UInt16Le()
        self.DomainNameMaxLen = UInt16Le(lambda:self.DomainNameLen.value)
        self.DomainNameBufferOffset = UInt32Le()
        self.WorkstationLen = UInt16Le()
        self.WorkstationMaxLen = UInt16Le(lambda:self.WorkstationLen.value)
        self.WorkstationBufferOffset = UInt32Le()
        self.Version = Version(conditional = lambda:(self.NegotiateFlags & Negotiate.NTLMSSP_NEGOTIATE_VERSION))
        self.Payload = String()
        