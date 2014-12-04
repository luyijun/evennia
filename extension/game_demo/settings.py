
######################################################################
# Evennia MU* server configuration file
#
# You may customize your setup by copy&pasting the variables you want
# to change from the master config file src/settings_default.py to
# this file. Try to *only* copy over things you really need to customize
# and do *not* make any changes to src/settings_default.py directly.
# This way you'll always have a sane default to fall back on
# (also, the master config file may change with server updates).
#
######################################################################

from src.settings_default import *

######################################################################
# Custom settings
######################################################################


######################################################################
# SECRET_KEY was randomly seeded when settings.py was first created.
# Don't share this with anybody. It is used by Evennia to handle
# cryptographic hashing for things like cookies on the web side.
######################################################################

SECRET_KEY = 'wOxp*280IZ&_U[;("}>+]?j.ytgNLBlo6$qzi5r/'


######################################################################
# Evennia base server config
######################################################################

WEBSOCKET_CLIENT_URL = "ws://192.168.0.99"


######################################################################
# Evennia pluggable modules
######################################################################

CONNECTION_SCREEN_MODULE = "game.gamesrc.conf.connection_screens"


######################################################################
# Default command sets
######################################################################

CMDSET_UNLOGGEDIN = "extension.commands.menu_login.UnloggedInCmdSet"
CMDSET_CHARACTER = "extension.commands.cmdset.CharacterCmdSet"
CMDSET_PLAYER = "extension.commands.cmdset.PlayerCmdSet"


######################################################################
# Typeclasses and other paths
######################################################################

BASE_OBJECT_TYPECLASS = "extension.objects.object_common.ObjectCommon"
BASE_CHARACTER_TYPECLASS = "extension.game_demo.character.Character"
BASE_ROOM_TYPECLASS = "extension.objects.room.Room"
BASE_EXIT_TYPECLASS = "extension.objects.exit.Exit"


######################################################################
# Batch processors
######################################################################

BASE_BATCHPROCESS_PATHS = ['game.gamesrc.world', 'extension.game_demo']


######################################################################
# Evennia components
######################################################################

INSTALLED_APPS += ("extension.data",)
