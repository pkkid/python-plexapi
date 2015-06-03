"""
PlexAPI
"""
import logging, os, platform
from logging.handlers import RotatingFileHandler
from plexapi.config import PlexConfig
from uuid import getnode

PROJECT = 'PlexAPI'
VERSION = '0.9.5'

# Load User Defined Config
CONFIG_PATH = os.path.expanduser('~/.config/plexapi/config.ini')
CONFIG = PlexConfig(CONFIG_PATH)

# Core Settings
TIMEOUT = CONFIG.get('plexapi.timeout', 5, int)

# Plex Header Configuation
X_PLEX_PROVIDES = 'player,controller'                                                   # one or more of [player, controller, server]
X_PLEX_PLATFORM = CONFIG.get('headers.platorm', platform.uname()[0])                    # Platform name, eg iOS, MacOSX, Android, LG, etc
X_PLEX_PLATFORM_VERSION = CONFIG.get('headers.platform_version', platform.uname()[2])   # Operating system version, eg 4.3.1, 10.6.7, 3.2
X_PLEX_PRODUCT = CONFIG.get('headers.product', PROJECT)                                 # Plex application name, eg Laika, Plex Media Server, Media Link
X_PLEX_VERSION = CONFIG.get('headers.version', VERSION)                                 # Plex application version number
X_PLEX_DEVICE = CONFIG.get('headers.platform', platform.platform())                     # Device name and model number, eg iPhone3,2, Motorola XOOM, LG5200TV
X_PLEX_IDENTIFIER = CONFIG.get('headers.identifier', str(hex(getnode())))               # UUID, serial number, or other number unique per device
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
LOG_FILE = CONFIG.get('logging.path')
if LOG_FILE:
    LOG_BACKUPS = CONFIG.get('logging.backup_count', 3, int)
    LOG_BYTES = CONFIG.get('logging.rotate_bytes', 512000, int)
    LOG_FORMAT = CONFIG.get('logging.format', '%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s')
    LOG_LEVEL = CONFIG.get('logging.level', 'INFO')
    filehandler = RotatingFileHandler(os.path.expanduser(LOG_FILE), 'a', LOG_BYTES, LOG_BACKUPS)
    filehandler.setFormatter(logging.Formatter(LOG_FORMAT))
    log.addHandler(filehandler)
    log.setLevel(LOG_LEVEL)
