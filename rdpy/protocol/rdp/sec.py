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
Some use full methods for security in RDP
"""

import sha, md5

def saltedHash(inputData, salt, salt1, salt2):
    """
    @summary: Generate particular signature from combination of sha1 and md5
    @see: http://msdn.microsoft.com/en-us/library/cc241992.aspx
    @param inputData: strange input (see doc)
    @param salt: salt for context call
    @param salt1: another salt (ex : client random)
    @param salt2: another another salt (ex: server random)
    @return : MD5(Salt + SHA1(Input + Salt + Salt1 + Salt2))
    """
    sha1Digest = sha.new()
    md5Digest = md5.new()
    
    sha1Digest.update(inputData)
    sha1Digest.update(salt[:48])
    sha1Digest.update(salt1)
    sha1Digest.update(salt2)
    sha1Sig = sha1Digest.digest()
    
    md5Digest.update(salt[:48])
    md5Digest.update(sha1Sig)
    
    return md5Digest.digest()

def masterSecret(preMasterSecret, clientRandom, serverRandom):
    """
    """