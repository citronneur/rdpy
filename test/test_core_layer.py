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
unit test for rdpy.network.layer module
"""

import os, sys
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import unittest
import rdpy.core.layer

class LayerTest(unittest.TestCase):
    """
    @summary:  represent test case for all classes and function
                present in rdpy.core.layer
    """
    
    class LayerCaseException(Exception):
        """
        @summary: exception use for event base test
        """
        pass
    
    def test_layer_connect_event(self):
        """
        @summary: test if connect event is send from transport to presentation
        """
        class TestConnect(rdpy.core.layer.Layer):
            def connect(self):
                raise LayerTest.LayerCaseException()
            
        self.assertRaises(LayerTest.LayerCaseException, rdpy.core.layer.Layer(presentation = TestConnect()).connect)
        
    def test_layer_automata_more_than_expected(self):
        """
        @summary: test layer automata mechanism if data received is more than expected
        """
        class TestAutomata(rdpy.core.layer.RawLayer):
            def expectedCallBack(self, data):
                if data.dataLen() == 4:
                    raise LayerTest.LayerCaseException()
            
        t = TestAutomata()
        t.expect(4, t.expectedCallBack)
        self.assertRaises(LayerTest.LayerCaseException, t.dataReceived, "\x00\x00\x00\x00\x00")
        
    def test_layer_automata_less_than_expected(self):
        """
        @summary: test layer automata mechanism
        """
        class TestAutomata(rdpy.core.layer.RawLayer):
            def expectedCallBack(self, data):
                if data.dataLen() == 4:
                    raise LayerTest.LayerCaseException()
            
        t = TestAutomata()
        t.expect(4, t.expectedCallBack)
        self.assertEqual(t.dataReceived("\x00\x00\x00"), None, "Not enough dada")