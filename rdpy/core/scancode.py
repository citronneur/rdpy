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
Basic virtual scancode mapping
"""

_SCANCODE_QWERTY_ = {
    0x10 : "q",
    0x11 : "w",
    0x12 : "e",
    0x13 : "r",
    0x14 : "t",
    0x15 : "y",
    0x16 : "u",
    0x17 : "i",
    0x18 : "o",
    0x19 : "p",
    0x1e : "a",
    0x1f : "s",
    0x20 : "d",
    0x21 : "f",
    0x22 : "g",
    0x23 : "h",
    0x24 : "j",
    0x25 : "k",
    0x26 : "l",
    0x2c : "z",
    0x2d : "x",
    0x2e : "c",
    0x2f : "v",
    0x30 : "b",
    0x31 : "n",
    0x32 : "m"
}
        
def scancodeToChar(code):
    """
    @summary: try to convert native code to char code
    @return: char
    """
    if not _SCANCODE_QWERTY_.has_key(code):
        return "<unknown scancode %x>"%code
    return _SCANCODE_QWERTY_[code];