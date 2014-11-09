# -*- coding: utf-8 -*-
"""
Menu-driven login system

Contribution - Griatch 2011


This is an alternative login system for Evennia, using the
contrib.menusystem module. As opposed to the default system it doesn't
use emails for authentication and also don't auto-creates a Character
with the same name as the Player (instead assuming some sort of
character-creation to come next).


Install is simple:

To your settings file, add/edit the line:

CMDSET_UNLOGGEDIN = "contrib.menu_login.UnloggedInCmdSet"

That's it. Reload the server and try to log in to see it.

The initial login "graphic" is taken from strings in the module given
by settings.CONNECTION_SCREEN_MODULE. You will want to copy the
template file in game/gamesrc/conf/examples up one level and re-point
the settings file to this custom module. you can then edit the string
in that module (at least comment out the default string that mentions
commands that are not available) and add something more suitable for
the initial splash screen.

"""

import re
import traceback
from django.conf import settings
from ev import managers
from ev import utils, logger, create_player, create_object
from ev import Command, CmdSet
from ev import default_cmds
from ev import syscmdkeys
from src.server.models import ServerConfig
from src.objects.models import ObjectDB

from game_demo.utils.menusystem import MenuNode, MenuTree

CMD_LOGINSTART = syscmdkeys.CMD_LOGINSTART
CMD_NOINPUT = syscmdkeys.CMD_NOINPUT
CMD_NOMATCH = syscmdkeys.CMD_NOMATCH

CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE


# Commands run on the unloggedin screen. Note that this is not using
# settings.UNLOGGEDIN_CMDSET but the menu system, which is why some are
# named for the numbers in the menu.
#
# Also note that the menu system will automatically assign all
# commands used in its structure a property "menutree" holding a reference
# back to the menutree. This allows the commands to do direct manipulation
# for example by triggering a conditional jump to another node.
#

# Menu entry 1a - Entering a Username

class CmdBackToStart(Command):
    """
    Step back to node0
    """
    key = CMD_NOINPUT
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        self.menutree.goto("START")


class CmdUsernameSelect(Command):
    """
    Handles the entering of a username and
    checks if it exists.
    """
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        player = managers.players.get_player_from_name(self.args)
        # store the player so next step can find it
        self.menutree.player = player
        self.caller.msg(echo=False)
        self.menutree.goto("node1b")


# Menu entry 1b - Entering a Password

class CmdPasswordSelectBack(Command):
    """
    Steps back from the Password selection
    """
    key = CMD_NOINPUT
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        self.menutree.goto("node1a")
        self.caller.msg(echo=True)


class CmdPasswordSelect(Command):
    """
    Handles the entering of a password and logs into the game.
    """
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        self.caller.msg(echo=True)
        if not hasattr(self.menutree, "player"):
            self.caller.msg("{r发生错误，请重新登录。{n")
            self.menutree.goto("node1a")
            return

        player = self.menutree.player
        
        if not player:
            self.caller.msg("{r用户名或密码错误！{n")
            self.menutree.goto("node1a")
            return

        if not player.check_password(self.args):
            self.caller.msg("{r用户名或密码错误！{n")
            self.menutree.goto("node1a")
            return

        # before going on, check eventual bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (any(tup[0]==player.name.lower() for tup in bans)
                     or
                     any(tup[2].match(self.caller.address) for tup in bans if tup[2])):
            # this is a banned IP or name!
            string = "{r您的帐号已被封，如有疑问可与管理员联系。{x"
            self.caller.msg(string)
            self.caller.sessionhandler.disconnect(self.caller, "再见！正在断开连接……")
            return

        # we are ok, log us in.
        self.caller.msg("{g欢迎%s！正在登入游戏……{n" % player.key)
        #self.caller.session_login(player)
        self.caller.sessionhandler.login(self.caller, player)

        # abort menu, do cleanup.
        self.menutree.goto("END")


# Menu entry 2a - Creating a Username

class CmdUsernameCreate(Command):
    """
    Handle the creation of a valid username
    """
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        playername = self.args

        # sanity check on the name
        if not re.findall('^[\w]+$', playername) or not (3 <= len(playername) <= 30):
            # this echoes the restrictions made by django's auth module.
            self.caller.msg("\n\r {r用户名必须包含3到30个字符，只能使用英文字母、数字和下划线。{n")
            self.menutree.goto("node2a")
            return
        if managers.players.get_player_from_name(playername):
            self.caller.msg("\n\r {r用户名“%s”已有人使用。{n" % playername)
            self.menutree.goto("node2a")
            return
        # store the name for the next step
        self.menutree.playername = playername
        self.caller.msg(echo=False)
        self.menutree.goto("node2b")


# Menu entry 2b - Creating a Password

class CmdPasswordInputBack(Command):
    "Step back from the password creation"
    key = CMD_NOINPUT
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        self.caller.msg(echo=True)
        self.menutree.goto("node2a")


class CmdPasswordInput(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Execute  the command"
        password = self.args
        
        if len(password) < 3:
            # too short password
            string = "{r您输入的密码必须至少包含3个字符！"
            string += "\n\r为了提高安全性，建议至少包含8个以上的字符，"
            string += "并且应避免使用单词和数字的组合。{n"
            self.caller.msg(string)
            self.menutree.goto("node2a")
            return
            
        self.menutree.password = password
        self.caller.msg(echo=False)
        self.menutree.goto("node2c")

        
class CmdPasswordConfirmBack(Command):
    "Step back from the password creation"
    key = CMD_NOINPUT
    locks = "cmd:all()"

    def func(self):
        "Execute the command"
        self.caller.msg(echo=False)
        self.menutree.goto("node2b")
        
        
class CmdPasswordConfirm(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Execute  the command"
        password = self.args

        self.caller.msg(echo=False)
        if not hasattr(self.menutree, 'playername'):
            self.caller.msg("{r发生错误，请重新登录。{n")
            self.menutree.goto("node2a")
            return
        playername = self.menutree.playername
        
        if not hasattr(self.menutree, 'password'):
            self.caller.msg("{r发生错误，请重新注册。{n")
            self.menutree.goto("node2a")
            return
        if password != self.menutree.password:
            self.caller.msg("{r密码不一致，请重新输入密码。{n")
            self.menutree.goto("node2b")
            return

        # everything's ok. Create the new player account. Don't create
        # a Character here.
        try:
            permissions = "Immortals"
            typeclass = settings.BASE_PLAYER_TYPECLASS
            new_player = create_player(playername, None, password,
                                       typeclass=typeclass,
                                       permissions=permissions)
            if not new_player:
                self.msg("在注册中有错误发生，该错误已被记录，请与管理员联系。")
                self.menutree.goto("START")
                return

            utils.init_new_player(new_player)

            if settings.MULTISESSION_MODE < 2:
                session = self.caller
                default_home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
                character_typeclass = settings.BASE_CHARACTER_TYPECLASS
                start_location = ObjectDB.objects.get_id(settings.START_LOCATION)
                
                _create_character(session, new_player, character_typeclass, start_location,
                                default_home, permissions)

            # join the new player to the public channel
            pchanneldef = settings.CHANNEL_PUBLIC
            if pchanneldef:
                pchannel = managers.channels.get_channel(pchanneldef[0])
                if not pchannel.connect(new_player):
                    string = "新玩家“%s”无法连接到公共频道！" % new_player.key
                    logger.log_errmsg(string)

            # tell the caller everything went well.
            string = "{g新账号“%s”已建立，正在登入……{n"
            self.caller.msg(string % (playername))
            #self.caller.session_login(player)
            self.caller.sessionhandler.login(self.caller, new_player)
            # abort menu, do cleanup.
            self.menutree.goto("END")

        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't, we
            # won't see any errors at all.
            string = "%s\n有错误发生，请与管理员联系。"
            self.caller.msg(string % (traceback.format_exc()))
            logger.log_errmsg(traceback.format_exc())


# Menu entry 3

class CmdUnloggedinQuit(Command):
    """
    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "3"
    aliases = ["quit", "qu", "q"]
    locks = "cmd:all()"

    def func(self):
        "Simply close the connection."
        self.menutree.goto("END")
        self.caller.sessionhandler.disconnect(self.caller, "再见！正在断开连接……")

        
# Menu entry 4 - encoding

class CmdUnloggedinEncodingUTF8(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = "4"
    aliases = ["utf-8"]
    locks = "cmd:all()"

    def func(self):
        session = self.caller
        if not session:
            return

        session.encoding = "utf-8"
        _look_menu(self.caller)
        

class CmdUnloggedinEncodingGBK(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = "4"
    aliases = ["gbk"]
    locks = "cmd:all()"

    def func(self):
        session = self.caller
        if not session:
            return
            
        if session.protocol_key == "websocket":
            self.caller.msg("网页客户端不能使用GBK编码。")
            return

        session.encoding = "gbk"
        _look_menu(self.caller)
        

LOGIN_SCREEN_HELP = \
    """
    Welcome to %s!

    To login you need to first create an account. This is easy and
    free to do: Choose option {w(1){n in the menu and enter an account
    name and password when prompted.  Obs- the account name is {wnot{n
    the name of the Character you will play in the game!

    It's always a good idea (not only here, but everywhere on the net)
    to not use a regular word for your password. Make it longer than 3
    characters (ideally 6 or more) and mix numbers and capitalization
    into it. The password also handles whitespace, so why not make it
    a small sentence - easy to remember, hard for a computer to crack.

    Once you have an account, use option {w(2){n to log in using the
    account name and password you specified.

    Use the {whelp{n command once you're logged in to get more
    aid. Hope you enjoy your stay!


    (return to go back)""" % settings.SERVERNAME


# The login menu tree, using the commands above

node1a = MenuNode("node1a", text="请输入您的用户名（返回上一步请直接按回车键）：",
                  links=["START", "node1b"],
                  helptext=["输入您注册时所使用的用户名。"],
                  keywords=[CMD_NOINPUT, CMD_NOMATCH],
                  selectcmds=[CmdBackToStart, CmdUsernameSelect],
                  nodefaultcmds=True) # if we don't, default help/look will be triggered by names starting with l/h ...
node1b = MenuNode("node1b", text="请输入密码：",
                  links=["node1a", "END"],
                  keywords=[CMD_NOINPUT, CMD_NOMATCH],
                  selectcmds=[CmdPasswordSelectBack, CmdPasswordSelect],
                  nodefaultcmds=True)

node2a = MenuNode("node2a", text="请输入您的用户名（返回上一步请直接按回车键）：",
                  links=["START", "node2b"],
                  helptext="用户名的长度不能超过30个字符，只能使用英文字母、数字和下划线。",
                  keywords=[CMD_NOINPUT, CMD_NOMATCH],
                  selectcmds=[CmdBackToStart, CmdUsernameCreate],
                  nodefaultcmds=True)
node2b = MenuNode("node2b", text="请输入密码：",
                  links=["node2a", "START"],
                  helptext="请尽量使用长度较长、较为复杂的密码。",
                  keywords=[CMD_NOINPUT, CMD_NOMATCH],
                  selectcmds=[CmdPasswordInputBack, CmdPasswordInput],
                  nodefaultcmds=True)
node2c = MenuNode("node2c", text="请再次输入密码：",
                  links=["node2b", "START"],
                  helptext="必须和上一次输入的密码一样。",
                  keywords=[CMD_NOINPUT, CMD_NOMATCH],
                  selectcmds=[CmdPasswordConfirmBack, CmdPasswordConfirm],
                  nodefaultcmds=True)
node3 = MenuNode("node3", text=LOGIN_SCREEN_HELP,
                 links=["START"],
                 helptext="",
                 keywords=[CMD_NOINPUT],
                 selectcmds=[CmdBackToStart])


# access commands

class UnloggedInCmdSet(CmdSet):
    "Cmdset for the unloggedin state"
    key = "DefaultUnloggedin"
    priority = 0

    def at_cmdset_creation(self):
        "Called when cmdset is first created"
        self.add(CmdUnloggedinLook())


class CmdUnloggedinLook(default_cmds.MuxCommand):
    """
    An unloggedin version of the look command. This is called by the server
    when the player first connects. It sets up the menu before handing off
    to the menu's own look command..
    """
    key = CMD_LOGINSTART
    aliases = [CMD_NOINPUT]
    locks = "cmd:all()"
    arg_regex = r"^$"

    def func(self):
        "Execute the menu"
        _look_menu(self.caller)


def _look_menu(caller):
    "Define the start node."
    
    session = caller
    if session:
        desc = "UTF-8" 
        cmd = CmdUnloggedinEncodingUTF8

        if session.encoding == "utf-8":
            desc = "GBK"
            cmd = CmdUnloggedinEncodingGBK
        
        start = MenuNode("START", text=utils.random_string_from_module(CONNECTION_SCREEN_MODULE),
                         links=["node1a", "node2a", "END", "START"],
                         linktexts=["登入已有帐号",
                                    "注册新账号",
                                    "退出游戏",
                                     desc],
                         selectcmds=[None, None, CmdUnloggedinQuit, cmd])
    else:
        start = MenuNode("START", text=utils.random_string_from_module(CONNECTION_SCREEN_MODULE),
                         links=["node1a", "node2a", "END"],
                         linktexts=["登入已有帐号",
                                    "注册新账号",
                                    "退出游戏"],
                         selectcmds=[None, None, CmdUnloggedinQuit])

    "Execute the menu"
    menu = MenuTree(caller, nodes=(start, node1a, node1b,
                                   node2a, node2b, node2c),
                                   exec_end=None)
    menu.start()


def _create_character(session, new_player, typeclass, start_location, home, permissions):
    """
    Helper function, creates a character based on a player's name.
    This is meant for Guest and MULTISESSION_MODE < 2 situations.
    """
    try:
        if not start_location:
            start_location = home # fallback
        new_character = create_object(typeclass, key=new_player.key,
                                  location=start_location, home=home,
                                  permissions=permissions)
        # set playable character list
        new_player.db._playable_characters.append(new_character)

        # allow only the character itself and the player to puppet this character (and Immortals).
        new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                (new_character.id, new_player.id))

        # If no description is set, set a default description
        if not new_character.db.desc:
            new_character.db.desc = "这是一位玩家。"
        # We need to set this to have @ic auto-connect to this character
        new_player.db._last_puppet = new_character
    except Exception, e:
        session.msg("There was an error creating the Character:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False