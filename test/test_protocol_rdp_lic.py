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
unit test for rdpy.protocol.rdp.lic automata
"""

import os, sys
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import unittest
from rdpy.protocol.rdp import lic, sec
import rdpy.core.type as type

class TestLic(unittest.TestCase):
    """
    @summary: Test case for MCS automata
    """
    
    class LIC_PASS(Exception):
        """
        @summary: for OK tests
        """
        pass
    
    class LIC_FAIL(Exception):
        """
        @summary: for KO tests
        """
        pass
    
    def test_valid_client_licensing_error_message(self):
        l = lic.LicenseManager(None)
        s = type.Stream()
        s.writeType(lic.createValidClientLicensingErrorMessage())
        #reinit position
        s.pos = 0
        
        self.assertTrue(l.recv(s), "Manager can retrieve valid case")
        
    def test_new_license(self):
        class Transport(object):
            def __init__(self):
                self._state = False
            def sendFlagged(self, flag, message):
                if flag != sec.SecurityFlag.SEC_LICENSE_PKT:
                    return
                s = type.Stream()
                s.writeType(message)
                s.pos = 0
                s.readType(lic.LicPacket(lic.ClientNewLicenseRequest()))
                self._state = True
        
        t = Transport()
        l = lic.LicenseManager(t)
        
        s = type.Stream()
        s.writeType(lic.LicPacket(lic.ServerLicenseRequest()))
        #reinit position
        s.pos = 0
        
        self.assertFalse(l.recv(s) and t._state, "Bad message after license request")