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
unit test for rdpy.protocol.rdp.rc4 module
"""

import os, sys
# Change path so we find rdpy
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import unittest
import rdpy.security.rc4 as rc4


class RC4Test(unittest.TestCase):
    """
    @summary: unit tests for rc4
    @see: http://fr.wikipedia.org/wiki/RC4
    """

    def test_rc4_key_plaintext(self):
        self.assertEqual("\xBB\xF3\x16\xE8\xD9\x40\xAF\x0A\xD3", rc4.crypt(rc4.RC4Key("Key"), "Plaintext"), "RC4 bad crypt")
        self.assertEqual("Plaintext", rc4.crypt(rc4.RC4Key("Key"), "\xBB\xF3\x16\xE8\xD9\x40\xAF\x0A\xD3"), "RC4 bad crypt")
        
    def test_rc4_wiki_pedia(self):
        self.assertEqual("\x10\x21\xBF\x04\x20", rc4.crypt(rc4.RC4Key("Wiki"), "pedia"), "RC4 bad crypt")
        self.assertEqual("pedia", rc4.crypt(rc4.RC4Key("Wiki"), "\x10\x21\xBF\x04\x20"), "RC4 bad crypt")
        
    def test_rc4_secret_attack_at_down(self):
        self.assertEqual("\x45\xA0\x1F\x64\x5F\xC3\x5B\x38\x35\x52\x54\x4B\x9B\xF5", rc4.crypt(rc4.RC4Key("Secret"), "Attack at dawn"), "RC4 bad crypt")
        self.assertEqual("Attack at dawn", rc4.crypt(rc4.RC4Key("Secret"), "\x45\xA0\x1F\x64\x5F\xC3\x5B\x38\x35\x52\x54\x4B\x9B\xF5"), "RC4 bad crypt")
