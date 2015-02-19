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
@summary: Simple and protected GSS-API Negotiation Mechanism
@see: https://msdn.microsoft.com/en-us/library/cc247021.aspx
"""

from pyasn1.type import namedtype, univ

class NegTokenInit2(univ.Sequence):
    """
    @summary: main structure
    @see: https://msdn.microsoft.com/en-us/library/cc247039.aspx
    """
    componentType = namedtype.NamedTypes(
        namedtype.OptionalNamedType('mechTypes', univ.Integer()),
        namedtype.OptionalNamedType('reqFlags', NegoData()),
        namedtype.OptionalNamedType('mechToken', univ.OctetString()),
        namedtype.OptionalNamedType('negHints', univ.OctetString()),
        namedtype.OptionalNamedType('mechListMIC', univ.Integer())
        )