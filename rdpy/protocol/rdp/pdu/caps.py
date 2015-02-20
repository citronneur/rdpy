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
from rdpy.core.error import InvalidExpectedDataException
import rdpy.core.log as log

"""
Definition of structure use for capabilities nego
Use in PDU layer
"""

from rdpy.core.type import CompositeType, CallableValue, String, UInt8, UInt16Le, UInt32Le, sizeof, ArrayType, FactoryType
    
class CapsType(object):
    """
    @summary: Different type of capabilities
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    """
    CAPSTYPE_GENERAL = 0x0001
    CAPSTYPE_BITMAP = 0x0002
    CAPSTYPE_ORDER = 0x0003
    CAPSTYPE_BITMAPCACHE = 0x0004
    CAPSTYPE_CONTROL = 0x0005
    CAPSTYPE_ACTIVATION = 0x0007
    CAPSTYPE_POINTER = 0x0008
    CAPSTYPE_SHARE = 0x0009
    CAPSTYPE_COLORCACHE = 0x000A
    CAPSTYPE_SOUND = 0x000C
    CAPSTYPE_INPUT = 0x000D
    CAPSTYPE_FONT = 0x000E
    CAPSTYPE_BRUSH = 0x000F
    CAPSTYPE_GLYPHCACHE = 0x0010
    CAPSTYPE_OFFSCREENCACHE = 0x0011
    CAPSTYPE_BITMAPCACHE_HOSTSUPPORT = 0x0012
    CAPSTYPE_BITMAPCACHE_REV2 = 0x0013
    CAPSTYPE_VIRTUALCHANNEL = 0x0014
    CAPSTYPE_DRAWNINEGRIDCACHE = 0x0015
    CAPSTYPE_DRAWGDIPLUS = 0x0016
    CAPSTYPE_RAIL = 0x0017
    CAPSTYPE_WINDOW = 0x0018
    CAPSETTYPE_COMPDESK = 0x0019
    CAPSETTYPE_MULTIFRAGMENTUPDATE = 0x001A
    CAPSETTYPE_LARGE_POINTER = 0x001B
    CAPSETTYPE_SURFACE_COMMANDS = 0x001C
    CAPSETTYPE_BITMAP_CODECS = 0x001D
    CAPSSETTYPE_FRAME_ACKNOWLEDGE = 0x001E
    
class MajorType(object):
    """
    @summary: Use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    """
    OSMAJORTYPE_UNSPECIFIED = 0x0000
    OSMAJORTYPE_WINDOWS = 0x0001
    OSMAJORTYPE_OS2 = 0x0002
    OSMAJORTYPE_MACINTOSH = 0x0003
    OSMAJORTYPE_UNIX = 0x0004
    OSMAJORTYPE_IOS = 0x0005
    OSMAJORTYPE_OSX = 0x0006
    OSMAJORTYPE_ANDROID = 0x0007
        
class MinorType(object):
    """
    @summary: Use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    """
    OSMINORTYPE_UNSPECIFIED = 0x0000
    OSMINORTYPE_WINDOWS_31X = 0x0001
    OSMINORTYPE_WINDOWS_95 = 0x0002
    OSMINORTYPE_WINDOWS_NT = 0x0003
    OSMINORTYPE_OS2_V21 = 0x0004
    OSMINORTYPE_POWER_PC = 0x0005
    OSMINORTYPE_MACINTOSH = 0x0006
    OSMINORTYPE_NATIVE_XSERVER = 0x0007
    OSMINORTYPE_PSEUDO_XSERVER = 0x0008
    OSMINORTYPE_WINDOWS_RT = 0x0009
 
class GeneralExtraFlag(object):
    """
    @summary: Use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    """
    FASTPATH_OUTPUT_SUPPORTED = 0x0001
    NO_BITMAP_COMPRESSION_HDR = 0x0400
    LONG_CREDENTIALS_SUPPORTED = 0x0004
    AUTORECONNECT_SUPPORTED = 0x0008
    ENC_SALTED_CHECKSUM = 0x0010
      
class Boolean(object):
    FALSE = 0x00
    TRUE = 0x01
 
class OrderFlag(object):
    """
    @summary: Use in order capability
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    """
    NEGOTIATEORDERSUPPORT = 0x0002
    ZEROBOUNDSDELTASSUPPORT = 0x0008
    COLORINDEXSUPPORT = 0x0020
    SOLIDPATTERNBRUSHONLY = 0x0040
    ORDERFLAGS_EXTRA_FLAGS = 0x0080
     
class Order(object):
    """
    @summary: Drawing orders supported
    Use in order capability
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    """
    TS_NEG_DSTBLT_INDEX = 0x00
    TS_NEG_PATBLT_INDEX = 0x01
    TS_NEG_SCRBLT_INDEX = 0x02
    TS_NEG_MEMBLT_INDEX = 0x03
    TS_NEG_MEM3BLT_INDEX = 0x04
    TS_NEG_DRAWNINEGRID_INDEX = 0x07
    TS_NEG_LINETO_INDEX = 0x08
    TS_NEG_MULTI_DRAWNINEGRID_INDEX = 0x09
    TS_NEG_SAVEBITMAP_INDEX = 0x0B
    TS_NEG_MULTIDSTBLT_INDEX = 0x0F
    TS_NEG_MULTIPATBLT_INDEX = 0x10
    TS_NEG_MULTISCRBLT_INDEX = 0x11
    TS_NEG_MULTIOPAQUERECT_INDEX = 0x12
    TS_NEG_FAST_INDEX_INDEX = 0x13
    TS_NEG_POLYGON_SC_INDEX = 0x14
    TS_NEG_POLYGON_CB_INDEX = 0x15
    TS_NEG_POLYLINE_INDEX = 0x16
    TS_NEG_FAST_GLYPH_INDEX = 0x18
    TS_NEG_ELLIPSE_SC_INDEX = 0x19
    TS_NEG_ELLIPSE_CB_INDEX = 0x1A
    TS_NEG_INDEX_INDEX = 0x1B
        
class OrderEx(object):
    """
    @summary: Extension orders
    Use in order capability
    """
    ORDERFLAGS_EX_CACHE_BITMAP_REV3_SUPPORT = 0x0002
    ORDERFLAGS_EX_ALTSEC_FRAME_MARKER_SUPPORT = 0x0004

class InputFlags(object):
    """
    @summary: Input flag use in input capability
    @see:  http://msdn.microsoft.com/en-us/library/cc240563.aspx
    """
    INPUT_FLAG_SCANCODES = 0x0001
    INPUT_FLAG_MOUSEX = 0x0004
    INPUT_FLAG_FASTPATH_INPUT = 0x0008
    INPUT_FLAG_UNICODE = 0x0010
    INPUT_FLAG_FASTPATH_INPUT2 = 0x0020
    INPUT_FLAG_UNUSED1 = 0x0040
    INPUT_FLAG_UNUSED2 = 0x0080
    TS_INPUT_FLAG_MOUSE_HWHEEL = 0x0100

class BrushSupport(object):
    """
    @summary: Brush support of client
    @see: http://msdn.microsoft.com/en-us/library/cc240564.aspx
    """
    BRUSH_DEFAULT = 0x00000000
    BRUSH_COLOR_8x8 = 0x00000001
    BRUSH_COLOR_FULL = 0x00000002

class GlyphSupport(object):
    """
    @summary: Use by glyph order
    @see: http://msdn.microsoft.com/en-us/library/cc240565.aspx
    """
    GLYPH_SUPPORT_NONE = 0x0000
    GLYPH_SUPPORT_PARTIAL = 0x0001
    GLYPH_SUPPORT_FULL = 0x0002
    GLYPH_SUPPORT_ENCODE = 0x0003
   
class OffscreenSupportLevel(object):
    """
    @summary: Use to determine offscreen cache level supported
    @see: http://msdn.microsoft.com/en-us/library/cc240550.aspx
    """
    FALSE = 0x00000000
    TRUE = 0x00000001
 
class VirtualChannelCompressionFlag(object):
    """
    @summary: Use to determine virtual channel compression
    @see: http://msdn.microsoft.com/en-us/library/cc240551.aspx
    """
    VCCAPS_NO_COMPR = 0x00000000
    VCCAPS_COMPR_SC = 0x00000001
    VCCAPS_COMPR_CS_8K = 0x00000002
  
class SoundFlag(object):
    """
    @summary: Use in sound capability to inform it
    @see: http://msdn.microsoft.com/en-us/library/cc240552.aspx
    """
    NONE = 0x0000
    SOUND_BEEPS_FLAG = 0x0001

class CacheEntry(CompositeType):
    """
    @summary: Use in capability cache exchange
    @see: http://msdn.microsoft.com/en-us/library/cc240566.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.cacheEntries = UInt16Le()
        self.cacheMaximumCellSize = UInt16Le()
    
    
class Capability(CompositeType):
    """
    @summary: A capability
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    """
    def __init__(self, capability = None):
        CompositeType.__init__(self)
        self.capabilitySetType = UInt16Le(lambda:capability.__class__._TYPE_)
        self.lengthCapability = UInt16Le(lambda:sizeof(self))
        
        def CapabilityFactory():
            """
            Closure for capability factory
            """
            for c in [GeneralCapability, BitmapCapability, OrderCapability, BitmapCacheCapability, PointerCapability, InputCapability, BrushCapability, GlyphCapability, OffscreenBitmapCacheCapability, VirtualChannelCapability, SoundCapability, ControlCapability, WindowActivationCapability, FontCapability, ColorCacheCapability, ShareCapability, MultiFragmentUpdate]:
                if self.capabilitySetType.value == c._TYPE_ and (self.lengthCapability.value - 4) > 0:
                    return c(readLen = self.lengthCapability - 4)
            log.debug("unknown Capability type : %s"%hex(self.capabilitySetType.value))
            #read entire packet
            return String(readLen = self.lengthCapability - 4)
        
        if capability is None:
            capability = FactoryType(CapabilityFactory)
        elif not "_TYPE_" in capability.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid capability block")
            
        self.capability = capability

class GeneralCapability(CompositeType):
    """
    @summary: General capability (protocol version and compression mode)
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_GENERAL
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.osMajorType = UInt16Le()
        self.osMinorType = UInt16Le()
        self.protocolVersion = UInt16Le(0x0200, constant = True)
        self.pad2octetsA = UInt16Le()
        self.generalCompressionTypes = UInt16Le(0, constant = True)
        self.extraFlags = UInt16Le()
        self.updateCapabilityFlag = UInt16Le(0, constant = True)
        self.remoteUnshareFlag = UInt16Le(0, constant = True)
        self.generalCompressionLevel = UInt16Le(0, constant = True)
        self.refreshRectSupport = UInt8()
        self.suppressOutputSupport = UInt8()
        
class BitmapCapability(CompositeType):
    """
    @summary: Bitmap format Capability
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240554.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_BITMAP
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.preferredBitsPerPixel = UInt16Le()
        self.receive1BitPerPixel = UInt16Le(0x0001)
        self.receive4BitsPerPixel = UInt16Le(0x0001)
        self.receive8BitsPerPixel = UInt16Le(0x0001)
        self.desktopWidth = UInt16Le()
        self.desktopHeight = UInt16Le()
        self.pad2octets = UInt16Le()
        self.desktopResizeFlag = UInt16Le()
        self.bitmapCompressionFlag = UInt16Le(0x0001, constant = True)
        self.highColorFlags = UInt8(0)
        self.drawingFlags = UInt8()
        self.multipleRectangleSupport = UInt16Le(0x0001, constant = True)
        self.pad2octetsB = UInt16Le()
        
class OrderCapability(CompositeType):
    """
    @summary: Order capability list all drawing order supported
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_ORDER
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.terminalDescriptor = String("\x00" * 16, readLen = CallableValue(16))
        self.pad4octetsA = UInt32Le(0)
        self.desktopSaveXGranularity = UInt16Le(1)
        self.desktopSaveYGranularity = UInt16Le(20)
        self.pad2octetsA = UInt16Le(0)
        self.maximumOrderLevel = UInt16Le(1)
        self.numberFonts = UInt16Le()
        self.orderFlags = UInt16Le(OrderFlag.NEGOTIATEORDERSUPPORT)
        self.orderSupport = ArrayType(UInt8, init = [UInt8(0) for _ in range (0, 32)],  readLen = CallableValue(32))
        self.textFlags = UInt16Le()
        self.orderSupportExFlags = UInt16Le()
        self.pad4octetsB = UInt32Le()
        self.desktopSaveSize = UInt32Le(480 * 480)
        self.pad2octetsC = UInt16Le()
        self.pad2octetsD = UInt16Le()
        self.textANSICodePage = UInt16Le(0)
        self.pad2octetsE = UInt16Le()
        
class BitmapCacheCapability(CompositeType):
    """
    @summary: Order use to cache bitmap very useful
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240559.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_BITMAPCACHE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.pad1 = UInt32Le()
        self.pad2 = UInt32Le()
        self.pad3 = UInt32Le()
        self.pad4 = UInt32Le()
        self.pad5 = UInt32Le()
        self.pad6 = UInt32Le()
        self.cache0Entries = UInt16Le()
        self.cache0MaximumCellSize = UInt16Le()
        self.cache1Entries = UInt16Le()
        self.cache1MaximumCellSize = UInt16Le()
        self.cache2Entries = UInt16Le()
        self.cache2MaximumCellSize = UInt16Le()
        
class PointerCapability(CompositeType):
    """
    @summary: Use to indicate pointer handle of client
    Paint by server or per client
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240562.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_POINTER
    
    def __init__(self, isServer = False, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.colorPointerFlag = UInt16Le()
        self.colorPointerCacheSize = UInt16Le(20)
        #old version of rdp doesn't support ...
        self.pointerCacheSize = UInt16Le(conditional = lambda:isServer)
        
class InputCapability(CompositeType):
    """
    @summary: Use to indicate input capabilities
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240563.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_INPUT
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.inputFlags = UInt16Le()
        self.pad2octetsA = UInt16Le()
        #same value as gcc.ClientCoreSettings.kbdLayout
        self.keyboardLayout = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardType
        self.keyboardType = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardSubType
        self.keyboardSubType = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardFnKeys
        self.keyboardFunctionKey = UInt32Le()
        #same value as gcc.ClientCoreSettingrrs.imeFileName
        self.imeFileName = String("\x00" * 64, readLen = CallableValue(64))
        
class BrushCapability(CompositeType):
    """
    @summary: Use to indicate brush capability
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240564.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_BRUSH
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.brushSupportLevel = UInt32Le(BrushSupport.BRUSH_DEFAULT)
        
class GlyphCapability(CompositeType):
    """
    @summary: Use in font order
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240565.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_GLYPHCACHE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.glyphCache = ArrayType(CacheEntry, init = [CacheEntry() for _ in range(0,10)], readLen = CallableValue(10))
        self.fragCache = UInt32Le()
        #all fonts are sent with bitmap format (very expensive)
        self.glyphSupportLevel = UInt16Le(GlyphSupport.GLYPH_SUPPORT_NONE)
        self.pad2octets = UInt16Le()
        
class OffscreenBitmapCacheCapability(CompositeType):
    """
    @summary: use to cached bitmap in offscreen area
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240550.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_OFFSCREENCACHE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.offscreenSupportLevel = UInt32Le(OffscreenSupportLevel.FALSE)
        self.offscreenCacheSize = UInt16Le()
        self.offscreenCacheEntries = UInt16Le()
        
class VirtualChannelCapability(CompositeType):
    """
    @summary: use to determine virtual channel compression
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240551.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_VIRTUALCHANNEL
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.flags = UInt32Le(VirtualChannelCompressionFlag.VCCAPS_NO_COMPR)
        self.VCChunkSize = UInt32Le(optional = True)
        
class SoundCapability(CompositeType):
    """
    @summary: Use to exchange sound capability
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240552.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_SOUND
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.soundFlags = UInt16Le(SoundFlag.NONE)
        self.pad2octetsA = UInt16Le()
        
class ControlCapability(CompositeType):
    """
    @summary: client -> server but server ignore contents! Thanks krosoft for brandwidth
    @see: http://msdn.microsoft.com/en-us/library/cc240568.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_CONTROL
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.controlFlags = UInt16Le()
        self.remoteDetachFlag = UInt16Le()
        self.controlInterest = UInt16Le(0x0002)
        self.detachInterest = UInt16Le(0x0002)
    
class WindowActivationCapability(CompositeType):
    """
    @summary: client -> server but server ignore contents! Thanks krosoft for brandwidth
    @see: http://msdn.microsoft.com/en-us/library/cc240569.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_ACTIVATION
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.helpKeyFlag = UInt16Le()
        self.helpKeyIndexFlag = UInt16Le()
        self.helpExtendedKeyFlag = UInt16Le()
        self.windowManagerKeyFlag = UInt16Le()
        
class FontCapability(CompositeType):
    """
    @summary: Use to indicate font support
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240571.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_FONT
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.fontSupportFlags = UInt16Le(0x0001)
        self.pad2octets = UInt16Le()
        
class ColorCacheCapability(CompositeType):
    """
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc241564.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_COLORCACHE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.colorTableCacheSize = UInt16Le(0x0006)
        self.pad2octets = UInt16Le()
        
class ShareCapability(CompositeType):
    """
    @summary: Use to advertise channel id of server
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240570.aspx
    """
    _TYPE_ = CapsType.CAPSTYPE_SHARE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.nodeId = UInt16Le()
        self.pad2octets = UInt16Le()
        
class MultiFragmentUpdate(CompositeType):
    """
    @summary: Use to advertise fast path max buffer to use
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240649.aspx
    """
    _TYPE_ = CapsType.CAPSETTYPE_MULTIFRAGMENTUPDATE
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.MaxRequestSize = UInt32Le(0)