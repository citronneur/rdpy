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
@summary: security service provider interface (Microsoft)
"""

from rdpy.core.error import CallPureVirtualFuntion

class IAuthenticationProtocol(object):
    """
    @summary: generic class for authentication Protocol (ex: ntlmv2, SPNEGO or kerberos)
    """
    def getNegotiateMessage(self):
        """
        @summary: Client first handshake message for authentication protocol
        @return: {object} first handshake message
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "getNegotiateMessage", "IAuthenticationProtocol")) 
    
    def getAuthenticateMessage(self, s):
        """
        @summary: Client last handshake message
        @param s: {Stream} challenge message stream
        @return: {(object, IGenericSecurityService)} Last handshake message and interface for application
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "getAuthenticateMessage", "IAuthenticationProtocol"))
    
    def getEncodedCredentials(self):
        """
        @summary: return encoded credentials accorded with authentication protocol nego
        @return: (domain, username, password)
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "getEncodedCredentials", "IAuthenticationProtocol"))
    
class IGenericSecurityService(object):
    """
    @summary: use by application from authentification protocol
    @see: http://www.rfc-editor.org/rfc/rfc2743.txt
    """
    def GSS_WrapEx(self, data):
        """
        @summary: encrypt data with key exchange in Authentication protocol
        @param data: {str}
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "GSS_WrapEx", "IGenericSecurityService"))
    
    def GSS_UnWrapEx(self, data):
        """
        @summary: decrypt data with key exchange in Authentication protocol
        @param data: {str}
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "GSS_UnWrapEx", "IGenericSecurityService"))