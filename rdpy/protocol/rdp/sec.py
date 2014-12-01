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
from rdpy.network.type import Stream, UInt32Le

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

def finalHash(key, random1, random2):
    """
    @summary: MD5(in0[:16] + in1[:32] + in2[:32])
    @param key: in 16
    @param random1: in 32
    @param random2: in 32
    @return MD5(in0[:16] + in1[:32] + in2[:32])
    """
    md5Digest = md5.new()
    md5Digest.update(key)
    md5Digest.update(random1)
    md5Digest.update(random2)
    return md5Digest.digest()

def generateMicrosoftKey(secret, random1, random2):
    """
    @summary: Generate master secret
    @param secret: secret
    @param clientRandom : client random
    @param serverRandom : server random
    """
    return saltedHash("A", secret, random1, random2) + saltedHash("BB", secret, random1, random2) + saltedHash("CCC", secret, random1, random2)

def macData(macSaltKey, data):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc241995.aspx
    """
    sha1Digest = sha.new()
    md5Digest = md5.new()
    
    #encode length
    s = Stream()
    s.writeType(UInt32Le(len(data)))
    
    sha1Digest.update(macSaltKey)
    sha1Digest.update("\x36" * 40)
    sha1Digest.update(s.getvalue())
    sha1Digest.update(data)
    
    sha1Sig = sha1Digest.digest()
    
    md5Digest.update(macSaltKey)
    md5Digest.update("\x5c" * 48)
    md5Digest.update(sha1Sig)
    
    return md5Digest.digest()