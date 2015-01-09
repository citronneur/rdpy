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
Wrapper around RSA library
"""

import rsa

def newkeys(size):
    """
    @summary: wrapper around rsa.newkeys function
    @param size: {integer} size of key
    """
    return rsa.newkeys(size)

def PublicKey(e, n):
    """
    @param e: {long | str}public exponent
    @param n: {long | str}modulus
    """
    if isinstance(e, str):
        e = rsa.transform.bytes2int(e)
    if isinstance(n, str):
        n = rsa.transform.bytes2int(n)
    return { 'e' : e, 'n' : n }

def PrivateKey(d, n):
    """
    @param d: {long | str}private exponent
    @param n: {long | str}modulus
    """
    if isinstance(d, str):
        d = rsa.transform.bytes2int(d)
    if isinstance(n, str):
        n = rsa.transform.bytes2int(n)
    return { 'd' : d, 'n' : n }

def int2bytes(i, fill_size=None):
    """
    @summary: wrapper of rsa.transform.int2bytes
    """
    return rsa.transform.int2bytes(i,fill_size)

def random(size):
    """
    @summary: wrapper around rsa.randnum.read_random_bits function
    @param size: {integer] size in bits
    @return: {str} random bytes array
    """
    return rsa.randnum.read_random_bits(size)

def encrypt(message, publicKey):
    """
    @summary: wrapper around rsa.core.encrypt_int function
    @param message: {str} source message
    @param publicKey: {rsa.PublicKey}
    """
    return rsa.transform.int2bytes(rsa.core.encrypt_int(rsa.transform.bytes2int(message), publicKey['e'], publicKey['n']), rsa.common.byte_size(publicKey['n']))

def decrypt(message, privateKey):
    """
    @summary: wrapper around rsa.core.decrypt_int function
    @param message: {str} source message
    @param publicKey: {rsa.PrivateKey}
    """
    return rsa.transform.int2bytes(rsa.core.decrypt_int(rsa.transform.bytes2int(message), privateKey['d'], privateKey['n']))

def sign(message, privateKey):
    """
    @summary: sign message with private key
    @param message: {str} message to sign
    @param privateKey : {rsa.privateKey} key use to sugn
    """
    return rsa.transform.int2bytes(rsa.core.encrypt_int(rsa.transform.bytes2int(message), privateKey['d'], privateKey['n']), rsa.common.byte_size(privateKey['n']))

def verify(message, publicKey):
    """
    @summary: return hash
    @param message: {str} message to verify
    @param publicKey : {rsa.publicKey} key use to sugn
    """
    return rsa.transform.int2bytes(rsa.core.decrypt_int(rsa.transform.bytes2int(message), publicKey['e'], publicKey['n']))