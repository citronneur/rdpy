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
All exceptions error use in RDPY
"""

class InvalidValue(Exception):
    '''
    raise when invalid value type occured
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)

class InvalidExpectedDataException(Exception):
    '''
    raise when expected data on network is invalid
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class NegotiationFailure(Exception):
    '''
    raise when negotiation failure in different protocols
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class InvalidType(Exception):
    '''
    raise when invalid value type occured
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class InvalidSize(Exception):
    '''
    raise when invalid size is present in packet type occured
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class ErrorReportedFromPeer(Exception):
    '''
    raise when peer send an error
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class DisconnectLayer(Exception):
    '''
    raise when try to send on unconnect layer
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
        
class UnRegistredObject(Exception):
    '''
    raise when an object is not registred in other objet
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        @param message: message show when exception is raised
        '''
        Exception.__init__(self, message)
