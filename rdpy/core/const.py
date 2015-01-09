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
Const it's use to create fake object enum in python
"""

from copy import deepcopy

class Constant(object):
    """
    @summary: Constant descriptor that deep copy value on get
    """
    def __init__(self, value):
        """
        @param value: value to protect
        """
        self._value = value
        
    def __get__(self, obj, objType):
        """
        @summary: on get constant return deep copy of wrapped value
        @param obj: unknown
        @param objType: unknown
        """
        return deepcopy(self._value)
    
    def __set__(self, obj, value):
        """
        @summary:  Try to set a protect value is forbidden
                    in python 2.7 this function work only
                    on instanciate object
        @param obj: 
        """
        raise Exception("can't assign constant")
    
    def __delete__(self, obj):
        """
        @summary: delete is forbidden on constant
        """
        raise Exception("can't delete constant")

def TypeAttributes(typeClass):
    """
    @summary:  Call typeClass ctor on each attributes
                to uniform atributes type on class
    @param typeClass: class use to construct each class attributes
    @return: class decorator
    """
    def wrapper(cls):
        for c_name, c_value in cls.__dict__.iteritems():
            if c_name[0] != '_' and not callable(c_value):
                setattr(cls, c_name, typeClass(c_value))
        return cls
    return wrapper

def ConstAttributes(cls):
    """
    @summary:  Copy on read attributes
                transform all attributes of class 
                in constant attribute
                only attributes which are not begining with '_' char
                and are not callable
    """
    return TypeAttributes(Constant)(cls)