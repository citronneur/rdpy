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

import hpfeeds
import os

"""
hpfeeds log engine in RDPY
Only logs messages
"""

class Level(object):
    """
    @summary: Level log
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    NONE = 4
    
_LOG_LEVEL = Level.DEBUG
serverid=os.environ.get('SERVERID')
hpc=None

if (os.environ.get('HPFEEDS_SERVER') and os.environ.get('HPFEEDS_SECRET') and os.environ.get(
        'HPFEEDS_IDENT') and os.environ.get('HPFEEDS_PORT') and os.environ.get('HPFEEDS_CHANNEL') and os.environ.get('SERVERID')):
    try:
        hpc = hpfeeds.new(os.environ.get('HPFEEDS_SERVER'), int(os.environ.get('HPFEEDS_PORT')), os.environ.get('HPFEEDS_IDENT'), os.environ.get('HPFEEDS_SECRET'))
    except (hpfeeds.FeedException, socket.error, hpfeeds.Disconnect), e:
        print "hpfeeds connection not successful"
        print 'Exception while connecting: {0}'.format(e)

def log(message):
    """
    @summary: Main log function
    @param message: string to print
    """
    send_hpfeeds("Log: %s "%message)

def error(message):
    """
    @summary: Log error message
    @param message: string to print as error log
    """
    if _LOG_LEVEL > Level.ERROR:
        return
    send_hpfeeds("Error: %s "%message)

    
def warning(message):
    """
    @summary: Log warning message
    @param message: string to print as warning log
    """
    if _LOG_LEVEL > Level.WARNING:
        return
    send_hpfeeds("Warning: %s "%message)

def info(message):
    """
    @summary: Log info message
    @param message: string to print as info log
    """
    if _LOG_LEVEL > Level.INFO:
        return
    send_hpfeeds("Info: %s "%message)
    
def debug(message):
    """
    @summary: Log debug message
    @param message: string to print as debug log
    """
    if _LOG_LEVEL > Level.DEBUG:
        return
    send_hpfeeds("Debug: %s "%message)

def send_hpfeeds(message):
    if hpc:
        hpfchannel = os.environ.get('HPFEEDS_CHANNEL')
        hpc.publish(hpfchannel, "["+serverid+"] " +message)
