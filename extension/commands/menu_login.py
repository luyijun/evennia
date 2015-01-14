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

from extension.utils.menusystem import MenuNode, MenuTree, prompt_choice, prompt_inputtext

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

class CmdUnloggedinLogin(Command):
    """
    Login
    """
    key = "login"
    locks = "cmd:all()"
    username = None
    password = None
    
    def func(self):
        "Execute the command"
        prompt_inputtext(self.caller,
                         question="请输入{w用户名{n",
                         callback_func=self.username_input)
    
    def username_input(self, menu_node):
        "Root selected"
        caller = self.caller
        if not caller:
            return
        
        if not menu_node:
            caller.msg("\n在登录中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        key = menu_node.key
        args = menu_node.args
        raw = menu_node.raw_string
        
        if not key:
            caller.msg("\n在登录中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        if key == CMD_NOINPUT and raw == CMD_NOINPUT:
            # user canceled
            caller.msg(_create_menu(caller))
            return
        
        if not args:
            caller.msg("\n{r用户名为空！{n", type="text")
            caller.msg(_create_menu(caller))
            return
            
        self.username = args
        prompt_inputtext(caller,
                         question="请输入{w密码{n",
                         callback_func=self.password_input,
                         type="input_password")

    def password_input(self, menu_node):
        "Root selected"
        caller = self.caller
        if not caller:
            return

        if not menu_node:
            caller.msg("\n在登录中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        key = menu_node.key
        args = menu_node.args
        raw = menu_node.raw_string

        if not key:
            caller.msg("\n在登录中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        if key == CMD_NOINPUT and raw == CMD_NOINPUT:
            # user canceled
            caller.msg(_create_menu(caller))
            return
            
        if not args:
            caller.msg("\n{r密码为空！{n", type="text")
            caller.msg(_create_menu(caller))
            return

        self.password = args
        _login(caller, self.username, self.password)


def _login(caller, username, password):
    ""
    if not caller:
        return
    
    if not username:
        return

    if not password:
        return

    player = managers.players.get_player_from_name(username)
        
    if not player:
        caller.msg("\n{r用户名或密码错误！{n", type="text")
        caller.msg(_create_menu(caller))
        return

    if not player.check_password(password):
        caller.msg("\n{r用户名或密码错误！{n", type="text")
        caller.msg(_create_menu(caller))
        return

    # before going on, check eventual bans
    bans = ServerConfig.objects.conf("server_bans")
    if bans and (any(tup[0]==player.name.lower() for tup in bans)
                 or
                 any(tup[2].match(caller.address) for tup in bans if tup[2])):
        # this is a banned IP or name!
        caller.msg("\n{r您的帐号已被封，如有疑问可与管理员联系。{n", type="text")
        caller.msg(_create_menu(caller))
        return

    # we are ok, log us in.
    caller.msg("\n{g欢迎%s！正在登入游戏……{n" % player.key)
    #caller.session_login(player)
    caller.sessionhandler.login(caller, player)


class CmdUnloggedinRegister(Command):
    """
    Register
    """
    key = "register"
    locks = "cmd:all()"
    username = None
    password = None
    
    def func(self):
        "Execute the command"
        prompt_inputtext(self.caller,
                         question="请输入{w用户名{n",
                         callback_func=self.username_input)
    
    def username_input(self, menu_node):
        "Root selected"
        caller = self.caller
        if not caller:
            return
        
        if not menu_node:
            caller.msg("\n在注册中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        key = menu_node.key
        args = menu_node.args
        raw = menu_node.raw_string

        if not key:
            caller.msg("\n在注册中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        if key == CMD_NOINPUT and raw == CMD_NOINPUT:
            # user canceled
            caller.msg(_create_menu(caller))
            return
        
        if not args:
            caller.msg("\n{r用户名为空！{n", type="text")
            caller.msg(_create_menu(caller))
            return
            
        username = args
        if not re.findall('^[\w]+$', username) or not (3 <= len(username) <= 30):
            # this echoes the restrictions made by django's auth module.
            caller.msg("\n{r用户名必须包含3到30个字符，只能使用英文字母、数字和下划线。{n", type="text")
            caller.msg(_create_menu(caller))
            return
        
        if managers.players.get_player_from_name(username):
            caller.msg("\n{r用户名“%s”已有人使用。{n" % username, type="text")
            caller.msg(_create_menu(caller))
            return
            
        self.username = username
        prompt_inputtext(caller,
                         question="请输入{w密码{n",
                         callback_func=self.password_input,
                         type="input_password")

    def password_input(self, menu_node):
        "Root selected"
        caller = self.caller
        if not caller:
            return
        
        if not menu_node:
            caller.msg("\n在注册中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        key = menu_node.key
        args = menu_node.args
        raw = menu_node.raw_string

        if not key:
            caller.msg("\n在注册中发生错误，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return
        
        if key == CMD_NOINPUT and raw == CMD_NOINPUT:
            # user canceled
            caller.msg(_create_menu(caller))
            return
            
        if not args:
            caller.msg("\n{r密码为空！{n", type="text");
            caller.msg(_create_menu(caller))
            return

        password = args
        if len(password) < 3:
            # too short password
            string = "\n{r您输入的密码必须至少包含3个字符！" +\
                     "\n为了提高安全性，建议至少包含8个以上的字符，" +\
                     "\n并且应避免使用单词和数字的组合。{n"
            caller.msg(string)
            caller.msg(_create_menu(caller))
            return

        self.password = password
        _register(caller, self.username, password)

        
def _register(caller, username, password):
    # Create the new player account and character here.
    if not caller:
        return
    
    if not username:
        return

    if not password:
        return

    try:
        permissions = settings.PERMISSION_PLAYER_DEFAULT
        typeclass = settings.BASE_PLAYER_TYPECLASS
        new_player = create_player(username, None, password,
                                   typeclass=typeclass,
                                   permissions=permissions)
        if not new_player:
            caller.msg("\n在注册中有错误发生，该错误已被记录，请与管理员联系。", type="text")
            caller.msg(_create_menu(caller))
            return

        utils.init_new_player(new_player)

        if settings.MULTISESSION_MODE < 2:
            session = caller
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
                string = "\n新玩家“%s”无法连接到公共频道！" % new_player.key
                logger.log_errmsg(string)

        # tell the caller everything went well.
        string = "\n{g新账号“%s”已建立，正在登入……{n" % username
        caller.msg(string)
        #caller.session_login(player)
        caller.sessionhandler.login(caller, new_player)

    except Exception:
        # We are in the middle between logged in and -not, so we have
        # to handle tracebacks ourselves at this point. If we don't, we
        # won't see any errors at all.
        string = "\n%s\n有错误发生，请与管理员联系。"
        caller.msg(string % (traceback.format_exc()))
        logger.log_errmsg(traceback.format_exc())
        caller.msg(_create_menu(caller))


# Menu entry 3

class CmdUnloggedinQuit(Command):
    """
    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "quit"
    aliases = ["qu", "q"]
    locks = "cmd:all()"

    def func(self):
        "Simply close the connection."
        self.caller.sessionhandler.disconnect(self.caller, "再见！正在断开连接……")

        
# Menu entry 4 - encoding

class CmdUnloggedinEncodingUTF8(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = "utf-8"
    locks = "cmd:all()"

    def func(self):
        session = self.caller
        if not session:
            return

        session.encoding = "utf-8"
        _look_menu(self.caller)
        

class CmdUnloggedinEncodingGBK(Command):
    "Handle the creation of a password. This also creates the actual Player/User object."
    key = "gbk"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        session = caller
        if not session:
            return
            
        if session.protocol_key == "websocket":
            caller.msg("\n{r网页客户端不能使用GBK编码。{n")
            caller.msg(_create_menu(caller))
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
"""
node1a = MenuNode("node1a", text="请输入您的用户名（直接按回车键可返回上一步）：",
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

node2a = MenuNode("node2a", text="请输入您的用户名（直接按回车键可返回上一步）：",
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
"""

# access commands

class UnloggedInCmdSet(CmdSet):
    "Cmdset for the unloggedin state"
    key = "DefaultUnloggedin"
    priority = 0

    def at_cmdset_creation(self):
        "Called when cmdset is first created"
        self.add(CmdUnloggedinLook())
        self.add(CmdUnloggedinLogin())
        self.add(CmdUnloggedinRegister())
        self.add(CmdUnloggedinQuit())
        self.add(CmdUnloggedinEncodingUTF8())
        self.add(CmdUnloggedinEncodingGBK())


class CmdUnloggedinLook(default_cmds.MuxCommand):
    """
    An unloggedin version of the look command. This is called by the server
    when the player first connects. It sets up the menu before handing off
    to the menu's own look command..
    """
    key = CMD_LOGINSTART
    # aliases = [CMD_NOINPUT]
    locks = "cmd:all()"
    arg_regex = r"^$"

    def func(self):
        "Execute the menu"
        # check if it is called by cancel
        caller = self.caller
        session = caller
        
        ostring = utils.random_string_from_module(CONNECTION_SCREEN_MODULE)
        question = _create_menu(caller)
    
        caller.msg(ostring + "\n" + question)


def _create_menu(session):
    "create connection menu"
    question = "请选择：" +\
               "\n{lclogin{lt[1]{le登入已有帐号" +\
               "\n{lcregister{lt[2]{le注册新账号"

    if session:
        if session.encoding == "utf-8":
            question += "\n{lcgbk{lt[3]{leGBK"
        else:
            question += "\n{lcutf-8{lt[3]{leUTF-8"

    return question


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