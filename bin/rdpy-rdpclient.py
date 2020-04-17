#!/usr/bin/python
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
example of use rdpy as rdp client
"""

import sys
import asyncio

from rdpy.core import tpkt, x224
from rdpy.model.type import UInt8

if __name__ == '__main__':

    #sys.exit(app.exec_())

    async def tcp_echo_client(message):
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 33389)

        x224_layer = await x224.connect(tpkt.Tpkt(reader, writer))
        await x224_layer.write(UInt8(8))
        await asyncio.sleep(1000)
        print("foooooooooooooooooooo")

    asyncio.run(tcp_echo_client('Hello World!'))