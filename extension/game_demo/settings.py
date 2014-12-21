
######################################################################
# Evennia base server config
######################################################################

WEBSOCKET_CLIENT_URL = "ws://YOUR_IP_ADDRESS"


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
