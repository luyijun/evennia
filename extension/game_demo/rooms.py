# -*- coding: utf-8 -*-
"""

Room Typeclasses for the TutorialWorld.

"""

import random
from ev import CmdSet, Script, Command
from ev import utils, create_object, search_object
import scripts as tut_scripts
from objects import LightSource, TutorialObject
from extension.objects.room import Room
from src.commands.default.syscommands import CMD_NOMATCH
from src.commands.default.syscommands import CMD_NOINPUT
from src.commands.default.general import CmdSay
import traceback

#------------------------------------------------------------
#
# Tutorial room - parent room class
#
# This room is the parent of all rooms in the tutorial.
# It defines a tutorial command on itself (available to
# all who is in a tutorial room).
#
#------------------------------------------------------------

class CmdTutorial(Command):
    """
    Get help during the tutorial

    Usage:
      tutorial [obj]

    This command allows you to get behind-the-scenes info
    about an object or the current location.

    """
    key = "tutorial"
    aliases = ["tut"]
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        """
        All we do is to scan the current location for an attribute
        called `tutorial_info` and display that.
        """

        caller = self.caller

        if not self.args:
            target = self.obj # this is the room the command is defined on
        else:
            target = caller.search(self.args.strip())
            if not target:
                return
        helptext = target.db.tutorial_info
        if helptext:
            caller.msg("{G%s{n" % helptext)
        else:
            caller.msg("{RSorry, there is no tutorial help available here.{n")


class TutorialRoomCmdSet(CmdSet):
    "Implements the simple tutorial cmdset"
    key = "tutorial_cmdset"

    def at_cmdset_creation(self):
        "add the tutorial cmd"
        self.add(CmdTutorial())


class TutorialRoom(Room):
    """
    This is the base room type for all rooms in the tutorial world.
    It defines a cmdset on itself for reading tutorial info about the location.
    """
    def at_object_creation(self):
        "Called when room is first created"
        self.db.tutorial_info = "This is a tutorial room. It allows you to use the 'tutorial' command."
        self.cmdset.add_default(TutorialRoomCmdSet)

    def reset(self):
        "Can be called by the tutorial runner."
        pass


#------------------------------------------------------------
#
# Weather room - scripted room
#
# The weather room is called by a script at
# irregular intervals. The script is generally useful
# and so is split out into tutorialworld.scripts.
#
#------------------------------------------------------------

class WeatherRoom(TutorialRoom):
    """
    This should probably better be called a rainy room...

    This sets up an outdoor room typeclass. At irregular intervals,
    the effects of weather will show in the room. Outdoor rooms should
    inherit from this.

    """
    def at_object_creation(self):
        "Called when object is first created."
        super(WeatherRoom, self).at_object_creation()

        # we use the imported IrregularEvent script
        self.scripts.add(tut_scripts.IrregularEvent)
        self.db.tutorial_info = \
            "This room has a Script running that has it echo a weather-related message at irregular intervals."

    def update_irregular(self):
        "create a tuple of possible texts to return."
        strings = (
            "天空一片昏暗，雨下得越来越大了。",
            "一阵狂风迎面吹来，雨点直接拍打在你脸上。尽管你穿着披风，但还是禁不住打起冷颤来。",
            "雨势稍有减缓，天空也变得亮了一些了。",
            "有一会儿雨势看起来正在减弱，但很快它又积蓄起力量卷土重来了。",
            "粗大的雨点打在你身上。远处传来隆隆的雷声。",
            "风呼啸着在你身旁吹过，夹杂的雨点落在你脸上，你觉得很冷。",
            "一道明亮的闪电划过长空，紧接着你就听到震耳欲聋的雷声。",
            "雨下得很大，你几乎无法看到前面的路。用不了多久你就要浑身湿透了。",
            "几道闪电击落下来，打在西边的树林中。",
            "你听到远处传来的嚎叫声，似乎是狗或狼发出的。",
            "巨大的乌云在天上翻滚，将装载的雨水倾斜到地上。")

        # get a random value so we can select one of the strings above.
        # Send this to the room.
        irand = random.randint(0, 15)
        if irand > 10:
            return  # don't return anything, to add more randomness
        self.msg_contents("{w%s{n" % strings[irand])


#------------------------------------------------------------------------------
#
# Dark Room - a scripted room
#
# This room limits the movemenets of its denizens unless they carry a and active
# LightSource object (LightSource is defined in
#                     tutorialworld.objects.LightSource)
#
#------------------------------------------------------------------------------

class CmdLookDark(Command):
    """
    Look around in darkness

    Usage:
      look

    Looks in darkness
    """
    key = "look"
    aliases = ["l", 'feel', 'feel around', 'fiddle', CMD_NOINPUT]
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "Implement the command."
        caller = self.caller

        if caller.ndb.is_first_look:
            caller.ndb.is_first_look = False
            caller.display_available_cmds()
            return
        
        string = ""
        # we don't have light, grasp around blindly.
        messages = ("周围一片漆黑。你四处摸索，但无法找到任何东西。",
                    "你看不到任何东西。你摸索着周围，手指突然重重地撞上了某个物体。哎哟！",
                    "你看不到任何东西！你盲目地向周围抓去，什么都没碰到。",
                    "这里一丝光都没有，你差点被凹凸不平的地面绊倒。",
                    "你完全失明了。有一会儿，你觉得好像听到附近有呼吸声……\n……想必你是弄错了。",
                    "看不见。你以为在地上找到了什么，但发现这只是块石头。",
                    "看不见。你撞到墙了，墙壁上似乎覆盖着一些植物，但它们太潮湿了，无法点燃。",
                    "你什么都看不到。周围的空气很潮湿，你感觉像是在深深的地下。")
        irand = random.randint(0, 10)
        if irand < len(messages):
            string += "\n " + messages[irand]
            commands = caller.available_cmd_list(None)
            if commands:
                string += "\n\n 动作：" + "  ".join(commands)
            caller.msg(string)
        else:
            # check so we don't already carry a lightsource.
            carried_lights = [obj for obj in caller.contents
                                       if utils.inherits_from(obj, LightSource)]
            
            if carried_lights:
                string += "\n 你不想继续在黑暗中摸索了。你已经找到了所需的东西，点亮它吧！"
                
                commands = ["{lclight{lt点燃木片{le"] + caller.available_cmd_list(None)
                string += "\n\n 动作：" + "  ".join(commands)
                caller.msg(string)
                return

            #if we are lucky, we find the light source.
            lightsources = [obj for obj in self.obj.contents
                                       if utils.inherits_from(obj, LightSource)]
            if lightsources:
                lightsource = lightsources[0]
            else:
                # create the light source from scratch.
                lightsource = create_object(LightSource, key="木片")

            lightsource.location = caller
            string += "\n 在角落里，你的手指碰到了一些木片。它们还带着树脂的香味，而且比较干燥，应该可以点燃！"
            string += "\n 你把它捡起来，紧紧地握手里。现在，你只需要用随身携带的火石{w点着{n它就行了。"
            
            commands = ["{lclight{lt点燃木片{le"] + caller.available_cmd_list(None)
            string += "\n\n 动作：" + "  ".join(commands)
            caller.msg(string)


class CmdDarkHelp(Command):
    """
    Help command for the dark state.
    """
    key = "help"
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "Implements the help command."
        string = "如果你不把房间照亮，我们也无法给你帮助。在周围努力寻找可以点燃的东西吧。"
        string += "即使你无法马上找到也不能放弃。"
        self.caller.msg(string)


# the nomatch system command will give a suitable error when we cannot find
# the normal commands.
class CmdDarkNoMatch(Command):
    "This is called when there is no match"
    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        "Implements the command."
        self.caller.msg("除非你把房间照亮，否则你无法做些什么。努力搜索四周吧。")


class DarkCmdSet(CmdSet):
    "Groups the commands."
    key = "darkroom_cmdset"
    mergetype = "Replace"  # completely remove all other commands

    def at_cmdset_creation(self):
        "populates the cmdset."
        self.add(CmdTutorial())
        self.add(CmdLookDark())
        self.add(CmdDarkHelp())
        self.add(CmdDarkNoMatch())
        self.add(CmdSay)

#
# Darkness room two-state system
#

class DarkState(Script):
    """
    The darkness state is a script that keeps tabs on when
    a player in the room carries an active light source. It places
    a new, very restrictive cmdset (DarkCmdSet) on all the players
    in the room whenever there is no light in it. Upon turning on
    a light, the state switches off and moves to LightState.
    """
    def at_script_creation(self):
        "This setups the script"
        self.key = "tutorial_darkness_state"
        self.desc = "A dark room"
        self.persistent = True

    def at_start(self):
        "called when the script is first starting up."
        for char in [char for char in self.obj.contents if char.has_player]:
            if char.is_superuser:
                char.msg("You are Superuser, so you are not affected by the dark state.")
            else:
                char.cmdset.add(DarkCmdSet)
            # char.msg("房间里一片漆黑！你感觉好像被吞进了巨人的肚子。")

    def is_valid(self):
        "is valid only as long as noone in the room has lit the lantern."
        return not self.obj.is_lit()

    def at_stop(self):
        "Someone turned on a light. This state dies. Switch to LightState."
        for char in [char for char in self.obj.contents if char.has_player]:
            char.cmdset.delete(DarkCmdSet)
        self.obj.db.is_dark = False
        self.obj.scripts.add(LightState)


class LightState(Script):
    """
    This is the counterpart to the Darkness state. It is active when the
    lantern is on.
    """
    def at_script_creation(self):
        "Called when script is first created."
        self.key = "tutorial_light_state"
        self.desc = "A room lit up"
        self.persistent = True

    def is_valid(self):
        """
        This state is only valid as long as there is an active light
        source in the room.
        """
        return self.obj.is_lit()

    def at_stop(self):
        "Light disappears. This state dies. Return to DarknessState."
        self.obj.db.is_dark = True
        self.obj.scripts.add(DarkState)


class DarkRoom(TutorialRoom):
    """
    A dark room. This tries to start the DarkState script on all
    objects entering. The script is responsible for making sure it is
    valid (that is, that there is no light source shining in the room).
    """
    def is_lit(self):
        """
        Helper method to check if the room is lit up. It checks all
        characters in room to see if they carry an active object of
        type LightSource.
        """
        return any([any([True for obj in char.contents
                         if utils.inherits_from(obj, LightSource) and obj.db.is_active])
                                 for char in self.contents if char.has_player])

    def at_object_creation(self):
        "Called when object is first created."
        super(DarkRoom, self).at_object_creation()
        self.db.tutorial_info = "This is a room with custom command sets on itself."
        # this variable is set by the scripts. It makes for an easy flag to
        # look for by other game elements (such as the crumbling wall in
        # the tutorial)
        self.db.is_dark = True
        # the room starts dark.
        self.scripts.add(DarkState)

    def at_object_receive(self, character, source_location):
        """
        Called when an object enters the room. We crank the wheels to make
        sure scripts are synced.
        """
        if character.has_player:
            if not self.is_lit() and not character.is_superuser:
                character.cmdset.add(DarkCmdSet)
            if character.db.health and character.db.health <= 0:
                # heal character coming here from being defeated by mob.
                health = character.db.health_max
                if not health:
                    health = 20
                character.db.health = health
            character.ndb.is_first_look = True
        self.scripts.validate()

    def at_object_leave(self, character, target_location):
        """
        In case people leave with the light, we make sure to update the
        states accordingly.
        """
        character.cmdset.delete(DarkCmdSet)  # in case we are teleported away
        self.scripts.validate()

    def return_appearance(self, caller):
        if caller.ndb.is_first_look:
            # disabled the first look
            caller.ndb.is_first_look = False
            caller.display_available_cmds()
            return
        
        return super(DarkRoom, self).return_appearance(caller)

#------------------------------------------------------------
#
# Teleport room - puzzle room
#
# This is a sort of puzzle room that requires a certain
# attribute on the entering character to be the same as
# an attribute of the room. If not, the character will
# be teleported away to a target location. This is used
# by the Obelisk - grave chamber puzzle, where one must
# have looked at the obelisk to get an attribute set on
# oneself, and then pick the grave chamber with the
# matching imagery for this attribute.
#
#------------------------------------------------------------

class TeleportRoom(TutorialRoom):
    """
    Teleporter - puzzle room.

    Important attributes (set at creation):
      puzzle_key    - which attr to look for on character
      puzzle_value  - what char.db.puzzle_key must be set to
      teleport_to   - where to teleport to in case of failure to match

    """
    def at_object_creation(self):
        "Called at first creation"
        super(TeleportRoom, self).at_object_creation()
        # what character.db.puzzle_clue must be set to, to avoid teleportation.
        self.db.puzzle_value = 1
        # target of successful teleportation. Can be a dbref or a
        # unique room name.
        self.db.success_teleport_to = "treasure room"
        # the target of the failure teleportation.
        self.db.failure_teleport_to = "dark cell"

    def at_object_receive(self, character, source_location):
        """
        This hook is called by the engine whenever the player is moved into
        this room.
        """
        if not character.has_player:
            # only act on player characters.
            return
        #print character.db.puzzle_clue, self.db.puzzle_value
        if character.db.puzzle_clue != self.db.puzzle_value:
            # we didn't pass the puzzle. See if we can teleport.
            teleport_to = self.db.failure_teleport_to  # this is a room name
        else:
            # passed the puzzle
            teleport_to = self.db.success_teleport_to  # this is a room name

        results = search_object(teleport_to)
        if not results or len(results) > 1:
            # we cannot move anywhere since no valid target was found.
            print "no valid teleport target for %s was found." % teleport_to
            return
        if character.player.is_superuser:
            # superusers don't get teleported
            character.msg("Superuser block: You would have been teleported to %s." % results[0])
            return
        # teleport
        character.execute_cmd("look")
        character.location = results[0]  # stealth move
        character.location.at_object_receive(character, self)

    def return_appearance(self, caller):
        return self.db.desc


#------------------------------------------------------------
#
# Bridge - unique room
#
# Defines a special west-eastward "bridge"-room, a large room it takes
# several steps to cross. It is complete with custom commands and a
# chance of falling off the bridge. This room has no regular exits,
# instead the exiting are handled by custom commands set on the player
# upon first entering the room.
#
# Since one can enter the bridge room from both ends, it is
# divided into five steps:
#       westroom <- 0 1 2 3 4 -> eastroom
#
#------------------------------------------------------------


class CmdEast(Command):
    """
    Try to cross the bridge eastwards.
    """
    key = "east"
    aliases = ["e"]
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "move forward"
        caller = self.caller

        bridge_step = min(5, caller.db.tutorial_bridge_position + 1)

        if bridge_step > 4:
            # we have reached the far east end of the bridge.
            # Move to the east room.
            eexit = search_object(self.obj.db.east_exit)
            if eexit:
                caller.move_to(eexit[0])
            else:
                caller.msg("No east exit was found for this room. Contact an admin.")
            return
        caller.db.tutorial_bridge_position = bridge_step
        caller.location.msg_contents("%s steps eastwards across the bridge." % caller.name, exclude=caller)
        caller.execute_cmd("look")


# go back across the bridge
class CmdWest(Command):
    """
    Go back across the bridge westwards.
    """
    key = "west"
    aliases = ["w"]
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "move forward"
        caller = self.caller

        bridge_step = max(-1, caller.db.tutorial_bridge_position - 1)

        if bridge_step < 0:
            # we have reached the far west end of the bridge.#
            # Move to the west room.
            wexit = search_object(self.obj.db.west_exit)
            if wexit:
                caller.move_to(wexit[0])
            else:
                caller.msg("No west exit was found for this room. Contact an admin.")
            return
        caller.db.tutorial_bridge_position = bridge_step
        caller.location.msg_contents("%s steps westwartswards across the bridge." % caller.name, exclude=caller)
        caller.execute_cmd("look")


class CmdLookBridge(Command):
    """
    looks around at the bridge.
    """
    key = 'look'
    aliases = ["l"]
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "Looking around, including a chance to fall."
        bridge_position = self.caller.db.tutorial_bridge_position


        messages =("你正站在吊桥上，{w离西面的出口很近{n。如果你向西走可以回到坚实的大地上……",
                   "吊桥向东延伸，从这里到桥的中间点是一段下坡路。",
                   "你已经在这座不太牢固的桥上走了{w一半{n的路程了。",
                   "吊桥向西延伸，从这里到桥的中间点是一段下坡路。",
                   "你正站在吊桥上，{w离东面的出口很近{n。如果你向东走可以回到坚实的大地上……")
        moods = ("桥在风中摇晃着。",
                 "吊桥在嘎嘎作响，让你感到有些害怕。",
                 "你脚下的桥摇晃着发出嘎吱嘎吱的声响，你紧紧地抓着边上的绳索。",
                 "从城堡方向传来了远远的嚎叫声，像是由一条大狗或什么野兽发出的。",
                 "桥在你的脚下嘎嘎作响，那些木板看上去不太牢固。",
                 "大海远远地在你下面，正咆哮着将海浪砸向悬崖，仿佛想要拍到你身上。",
                 "几块木板在你身后断裂开，坠如下面的深渊中。",
                 "一阵狂风吹过，吊桥摇晃了起来。",
                 "你脚下的一块木板松脱了，翻滚着坠落下去。你的半个身子悬在了空中……",
                 "你手中握着的绳索部分断裂开了，你摇摆着努力恢复平衡。")

        message = "\n {c=============================================================={n"
        message += "\n {c%s{n" % self.obj.key
        message += "\n {c=============================================================={n"
        message += "\n" + messages[bridge_position] + "\n" + moods[random.randint(0, len(moods) - 1)]
        chars = [obj for obj in self.obj.contents if obj != self.caller and obj.has_player]
        if chars:
            message += "\n 你看见：%s" % ", ".join("{c%s{n" % char.key for char in chars)

        message += "\n {lceast{lt向东走{le  {lcwest{lt向西走{le"
        self.caller.msg(message)

        # there is a chance that we fall if we are on the western or central
        # part of the bridge.
        if bridge_position < 3 and random.random() < 0.05 and not self.caller.is_superuser:
            # we fall on 5% of the times.
            fexit = search_object(self.obj.db.fall_exit)
            if fexit:
                string = "\n {r突然，你脚下的木板断开了！你掉下去了！"
                string += "\n 你想尽力抓住相邻的木板，但只是改变了你坠落的方向。你正摔向西面的悬崖。这"
                string += "\n 次肯定要受伤了……"
                string += "\n ……整个世界一片黑暗……{n\n"
                string += self.caller.get_available_cmd_desc(None)
                # note that we move silently so as to not call look hooks (this is a little trick to leave
                # the player with the "world goes dark ..." message, giving them ample time to read it. They
                # have to manually call look to find out their new location). Thus we also call the
                # at_object_leave hook manually (otherwise this is done by move_to()).
                self.caller.msg(string)
                self.obj.at_object_leave(self.caller, fexit)
                self.caller.location = fexit[0] # stealth move, without any other hook calls.
                self.obj.msg_contents("一块木板在%s的脚下断开了，他摔下桥了！" % self.caller.key)


# custom help command
class CmdBridgeHelp(Command):
    """
    Overwritten help command
    """
    key = "help"
    aliases = ["h"]
    locks = "cmd:all()"
    help_category = "Tutorial world"

    def func(self):
        "Implements the command."
        string = "You are trying hard not to fall off the bridge ..."
        string += "\n\nWhat you can do is trying to cross the bridge {weast{n "
        string += "or try to get back to the mainland {wwest{n)."
        self.caller.msg(string)


class BridgeCmdSet(CmdSet):
    "This groups the bridge commands. We will store it on the room."
    key = "Bridge commands"
    priority = 1 # this gives it precedence over the normal look/help commands.
    def at_cmdset_creation(self):
        "Called at first cmdset creation"
        self.add(CmdTutorial())
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdLookBridge())
        self.add(CmdBridgeHelp())


class BridgeRoom(TutorialRoom):
    """
    The bridge room implements an unsafe bridge. It also enters the player into
    a state where they get new commands so as to try to cross the bridge.

     We want this to result in the player getting a special set of
        commands related to crossing the bridge. The result is that it will
        take several steps to cross it, despite it being represented by only a
        single room.

        We divide the bridge into steps:

        self.db.west_exit     -   -  |  -   -     self.db.east_exit
                              0   1  2  3   4

        The position is handled by a variable stored on the player when entering
        and giving special move commands will increase/decrease the counter
        until the bridge is crossed.

    """
    def at_object_creation(self):
        "Setups the room"
        super(BridgeRoom, self).at_object_creation()

        # at irregular intervals, this will call self.update_irregular()
        self.scripts.add(tut_scripts.IrregularEvent)
        # this identifies the exits from the room (should be the command
        # needed to leave through that exit). These are defaults, but you
        # could of course also change them after the room has been created.
        self.db.west_exit = "cliff"
        self.db.east_exit = "gate"
        self.db.fall_exit = "cliffledge"
        # add the cmdset on the room.
        self.cmdset.add_default(BridgeCmdSet)

        self.db.tutorial_info = \
            """The bridge seem large but is actually only a single room that assigns custom west/east commands."""

    def update_irregular(self):
        """
        This is called at irregular intervals and makes the passage
        over the bridge a little more interesting.
        """
        strings = (
            "雨越下越大，桥上的木板变得更加湿滑了。",
            "一阵狂风迎面吹来，雨点直接拍打在你脸上。",
            "雨势稍有减缓，天空也变得亮了一些了。",
            "一声惊雷在不远处炸响，桥也随之震动了一下。",
            "粗大的雨点打在你身上。远处传来猎犬的低吼声。",
            "风呼啸着在你身旁吹过，桥也开始左右摇晃起来。",
            "一只巨大的鸟在上空掠过，发出了一声尖啸。很快它就消失在昏暗的天空中了。",
            "桥在风中左右摇晃。")
        self.msg_contents("{w%s{n" % strings[random.randint(0, 7)])

    def at_object_receive(self, character, source_location):
        """
        This hook is called by the engine whenever the player is moved
        into this room.
        """
        if character.has_player:
            # we only run this if the entered object is indeed a player object.
            # check so our east/west exits are correctly defined.
            wexit = search_object(self.db.west_exit)
            eexit = search_object(self.db.east_exit)
            fexit = search_object(self.db.fall_exit)
            if not wexit or not eexit or not fexit:
                character.msg("The bridge's exits are not properly configured. Contact an admin. Forcing west-end placement.")
                character.db.tutorial_bridge_position = 0
                return
            if source_location == eexit[0]:
                character.db.tutorial_bridge_position = 4
            else:
                character.db.tutorial_bridge_position = 0

    def at_object_leave(self, character, target_location):
        """
        This is triggered when the player leaves the bridge room.
        """
        if character.has_player:
            # clean up the position attribute
            del character.db.tutorial_bridge_position


#-----------------------------------------------------------
#
# Intro Room - unique room
#
# This room marks the start of the tutorial. It sets up properties on
# the player char that is needed for the tutorial.
#
#------------------------------------------------------------

class IntroRoom(TutorialRoom):
    """
    Intro room

    properties to customize:
     char_health - integer > 0 (default 20)
    """

    def at_object_receive(self, character, source_location):
        """
        Assign properties on characters
        """

        # setup
        health = self.db.char_health
        if not health:
            health = 20

        if character.has_player:
            character.db.health = health
            character.db.health_max = health

        if character.is_superuser:
            string = "-"*78
            string += "\nWARNING: YOU ARE PLAYING AS A SUPERUSER (%s). TO EXPLORE NORMALLY YOU NEED " % character.key
            string += "\nTO CREATE AND LOG IN AS A REGULAR USER INSTEAD. IF YOU CONTINUE, KNOW THAT "
            string += "\nMANY FUNCTIONS AND PUZZLES WILL IGNORE THE PRESENCE OF A SUPERUSER.\n"
            string += "-"*78
            character.msg("{r%s{n" % string)


#------------------------------------------------------------
#
# Outro room - unique room
#
# Cleans up the character from all tutorial-related properties.
#
#------------------------------------------------------------

class OutroRoom(TutorialRoom):
    """
    Outro room.

    One can set an attribute list "wracklist" with weapon-rack ids
        in order to clear all weapon rack ids from the character.

    """

    def at_object_receive(self, character, source_location):
        """
        Do cleanup.
        """
        if character.has_player:
            if self.db.wracklist:
                for wrackid in self.db.wracklist:
                    character.del_attribute(wrackid)
            del character.db.health_max
            del character.db.health
            del character.db.last_climbed
            del character.db.puzzle_clue
            del character.db.combat_parry_mode
            del character.db.tutorial_bridge_position
            for tut_obj in [obj for obj in character.contents
                                  if utils.inherits_from(obj, TutorialObject)]:
                tut_obj.reset()
