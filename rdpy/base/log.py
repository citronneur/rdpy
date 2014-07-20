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
Log engine in RDPY
Actually very basic log engine
"""

class Level(object):
    """
    Level log
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    
_LOG_LEVEL = Level.DEBUG

def log(message):
    print message

def error(message):
    if _LOG_LEVEL > Level.ERROR:
        return
    log("ERROR : %s"%message)
    
def warning(message):
    if _LOG_LEVEL > Level.WARNING:
        return
    log("WARNING : %s"%message)

def info(message):
    if _LOG_LEVEL > Level.INFO:
        return
    log("INFO : %s"%message)
    
def debug(message):
    if _LOG_LEVEL > Level.DEBUG:
        return
    log("DEBUG : %s"%message)