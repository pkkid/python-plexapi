"""
PlexAPI
"""
import logging, os, platform
from logging.handlers import RotatingFileHandler
from uuid import getnode

PROJECT = 'PlexAPI'
VERSION = '0.9.4'
TIMEOUT = 5

# Plex Header Configuation
X_PLEX_PLATFORM = platform.uname()[0]               # Platform name, eg iOS, MacOSX, Android, LG, etc
X_PLEX_PLATFORM_VERSION = platform.uname()[2]       # Operating system version, eg 4.3.1, 10.6.7, 3.2
X_PLEX_PROVIDES = 'controller'                      # one or more of [player, controller, server]
X_PLEX_PRODUCT = PROJECT                            # Plex application name, eg Laika, Plex Media Server, Media Link
X_PLEX_VERSION = VERSION                            # Plex application version number
X_PLEX_DEVICE = platform.platform()                 # Device name and model number, eg iPhone3,2, Motorola XOOM, LG5200TV
X_PLEX_IDENTIFIER = str(hex(getnode()))             # UUID, serial number, or other number unique per device
BASE_HEADERS = {
    'X-Plex-Platform': X_PLEX_PLATFORM,
    'X-Plex-Platform-Version': X_PLEX_PLATFORM_VERSION,
    'X-Plex-Provides': X_PLEX_PROVIDES,
    'X-Plex-Product': X_PLEX_PRODUCT,
    'X-Plex-Version': X_PLEX_VERSION,
    'X-Plex-Device': X_PLEX_DEVICE,
    'X-Plex-Client-Identifier': X_PLEX_IDENTIFIER,
}

# Logging Configuration
log = logging.getLogger('plexapi')
logfile = os.path.join('/tmp', 'plexapi.log')
logformat = logging.Formatter('%(asctime)s %(module)-12s %(levelname)-6s %(message)s')
filehandler = RotatingFileHandler(logfile, 'a', 512000, 3)
filehandler.setFormatter(logformat)
log.addHandler(filehandler)
log.setLevel(logging.INFO)
