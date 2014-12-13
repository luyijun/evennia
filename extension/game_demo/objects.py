# -*- coding: utf-8 -*-
"""
TutorialWorld - basic objects - Griatch 2011

This module holds all "dead" object definitions for
the tutorial world. Object-commands and -cmdsets
are also defined here, together with the object.

Objects:

TutorialObject

Readable
Climbable
Obelisk
LightSource
CrumblingWall
Weapon
WeaponRack

"""

import time
import random

from ev import create_object, search_object
from ev import Command, CmdSet, Script
from extension.objects.object_common import ObjectCommon as Object
from extension.objects.object_creator import ObjectSelector
from extension.objects.object_portable import ObjectPortable
from extension.objects.exit import Exit
from extension.utils.defines import OBJ_CATEGORY
from extension.utils.menusystem import prompt_choice

#------------------------------------------------------------
#
# TutorialObject
#
# The TutorialObject is the base class for all items
# in the tutorial. They have an attribute "tutorial_info"
# on them that a global tutorial command can use to extract
# interesting behind-the scenes information about the object.
#
# TutorialObjects may also be "reset". What the reset means
# is up to the object. It can be the resetting of the world
# itself, or the removal of an inventory item from a
# character's inventory when leaving the tutorial, for example.
#
#------------------------------------------------------------


class TutorialObject(Object):
    """
    This is the baseclass for all objects in the tutorial.
    """

    def at_object_creation(self):
        "Called when the object is first created."
        super(TutorialObject, self).at_object_creation()
        self.db.tutorial_info = "No tutorial info is available for this object."
        #self.db.last_reset = time.time()

    def reset(self):
        "Resets the object, whatever that may mean."
        self.location = self.home


#------------------------------------------------------------
#
# Readable - an object one can "read".
#
#------------------------------------------------------------

class CmdRead(Command):
    """
    Usage:
      read [obj]

    Read some text.
    """

    key = "read"
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "Implement the read command."
        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        # we want an attribute read_text to be defined.
        readtext = obj.db.readable_text
        if readtext:
            string = "\n {c%s{n上写着：\n  %s" % (obj.key, readtext)
        else:
            string = " %s上没有可阅读的内容。" % obj.key

        string += "\n "
        commands = self.caller.available_cmd_list(self.caller)
        string += "\n 动作：" + "  ".join(commands)
        string += "\n "
        self.caller.msg(string)


class CmdSetReadable(CmdSet):
    "CmdSet for readables"
    def at_cmdset_creation(self):
        "called when object is created."
        self.add(CmdRead())


class Readable(TutorialObject):
    """
    This object defines some attributes and defines a read method on itself.
    """
    def at_object_creation(self):
        "Called when object is created"
        super(Readable, self).at_object_creation()
        self.db.tutorial_info = "This is an object with a 'read' command defined in a command set on itself."
        self.db.readable_text = "%s上没有写任何字。" % self.key
        # define a command on the object.
        self.cmdset.add_default(CmdSetReadable, permanent=True)

    def available_cmd_list(self, pobject):
        """
        This returns a string of available commands.
        """
        commands = ["{lcread %s{lt阅读%s{le" % (self.key, self.key)]
        commands.extend(super(Readable, self).available_cmd_list(pobject))
        return commands

#------------------------------------------------------------
#
# Climbable object
#
# The climbable object works so that once climbed, it sets
# a flag on the climber to show that it was climbed. A simple
# command 'climb' handles the actual climbing.
#
#------------------------------------------------------------

class CmdClimb(Command):
    """
    Usage:
      climb <object>
    """
    key = "climb"
    locks = "cmd:all()"
    help_category = "TutorialWorld"

    def func(self):
        "Implements function"

        if not self.args:
            self.caller.msg("你想要爬什么？")
            return
        obj = self.caller.search(self.args.strip())
        if not obj:
            return
        if obj != self.obj:
            self.caller.msg("尽管你很努力，你还是无法爬上去。")
            return
        
        ostring = " \n"
        ostring += self.obj.db.climb_text
        if not ostring:
            ostring += "\n {c=============================================================={n"
            ostring += "\n {c攀爬{n"
            ostring += "\n {c=============================================================={n"
            ostring += "\n 你爬上%s，向四处张望了一下，又爬了下来。" % self.obj.name

        commands = self.caller.available_cmd_list(self.caller)
        ostring += "\n\n动作：" + ", ".join(commands)
        ostring += "\n"
        self.caller.msg(ostring)
        self.caller.db.last_climbed = self.obj


class CmdSetClimbable(CmdSet):
    "Climbing cmdset"
    def at_cmdset_creation(self):
        "populate set"
        self.add(CmdClimb())


class Climbable(TutorialObject):
    "A climbable object."

    def at_object_creation(self):
        "Called at initial creation only"
        self.cmdset.add_default(CmdSetClimbable, permanent=True)

    def available_cmd_list(self, pobject):
        """
        This returns a string of available commands.
        """
        commands = ["{lcclimb %s{lt攀爬%s{le" % (self.key, self.key)]
        commands.extend(super(Climbable, self).available_cmd_list(pobject))
        return commands
        

#------------------------------------------------------------
#
# Obelisk - a unique item
#
# The Obelisk is an object with a modified return_appearance
# method that causes it to look slightly different every
# time one looks at it. Since what you actually see
# is a part of a game puzzle, the act of looking also
# stores a key attribute on the looking object for later
# reference.
#
#------------------------------------------------------------

OBELISK_DESCS = ["你可以大致辨认出这是一幅画着{c女人和蓝鸟{n的画。",
                 "有一瞬间你认出了{c一个女人骑在马上{n的样子。",
                 "你一下子就看出这是一个{c戴着皇冠的贵妇{n的浮雕。",
                 "你觉得你认出了石头上雕刻着{c一面燃烧着的盾牌{n。",
                 "有一刹那在面上似乎描绘了{c一个女人在与野兽搏斗{n。"]


class Obelisk(TutorialObject):
    """
    This object changes its description randomly.
    """

    def at_object_creation(self):
        "Called when object is created."
        super(Obelisk, self).at_object_creation()
        self.db.tutorial_info = "This object changes its desc randomly, and makes sure to remember which one you saw."
        # make sure this can never be picked up
        self.locks.add("get:false()")

    def return_appearance(self, caller):
        "Overload the default version of this hook."
        clueindex = random.randint(0, len(OBELISK_DESCS) - 1)
        # set this description
        string = "方尖碑的表面似乎在你眼前扭动、翻转着，不论你何时看它，看到的都是不一样的景象。\n"
        self.db.desc = string + OBELISK_DESCS[clueindex]
        # remember that this was the clue we got.
        caller.db.puzzle_clue = clueindex
        # call the parent function as normal (this will use db.desc we just set)
        return super(Obelisk, self).return_appearance(caller)


#------------------------------------------------------------
#
# LightSource
#
# This object that emits light and can be
# turned on or off. It must be carried to use and has only
# a limited burn-time.
# When burned out, it will remove itself from the carrying
# character's inventory.
#
#------------------------------------------------------------

class StateLightSourceOn(Script):
    """
    This script controls how long the light source is burning. When
    it runs out of fuel, the lightsource goes out.
    """
    def at_script_creation(self):
        "Called at creation of script."
        self.key = "lightsourceBurn"
        self.desc = "Keeps lightsources burning."
        self.start_delay = True # only fire after self.interval s.
        self.repeats = 1 # only run once.
        self.persistent = True  # survive a server reboot.

    def at_start(self):
        "Called at script start - this can also happen if server is restarted."
        self.interval = self.obj.db.burntime
        self.db.script_started = time.time()

    def at_repeat(self):
        "Called at self.interval seconds"
        # this is only called when torch has burnt out
        self.obj.db.burntime = -1
        self.obj.reset()

    def at_stop(self):
        """
        Since the user may also turn off the light
        prematurely, this hook will store the current
        burntime.
        """
        # calculate remaining burntime, if object is not
        # already deleted (because it burned out)
        if self.obj:
            try:
                time_burnt = time.time() - self.db.script_started
            except TypeError:
                # can happen if script_started is not defined
                time_burnt = self.interval
            burntime = self.interval - time_burnt
            self.obj.db.burntime = burntime

    def is_valid(self):
        "This script is only valid as long as the lightsource burns."
        if not super(StateLightSourceOn, self).is_valid():
            return False
        return self.obj.db.is_active


class CmdLightSourceOn(Command):
    """
    Switches on the lightsource.
    """
    key = "on"
    aliases = ["switch on", "turn on", "light"]
    locks = "cmd:holds()"  # only allow if command.obj is carried by caller.
    help_category = "TutorialWorld"

    def func(self):
        "Implements the command"

        if self.obj.db.is_active:
            self.caller.msg("%s已经被点燃了。" % self.obj.key)
        else:
            # set lightsource to active
            self.obj.db.is_active = True
            # activate the script to track burn-time.
            self.obj.scripts.add(StateLightSourceOn)
            self.caller.msg("{g你点燃了{C%s。{n" % self.obj.key)
            self.caller.location.msg_contents("%s点燃了%s！" % (self.caller, self.obj.key), exclude=[self.caller])
            # run script validation on the room to make light/dark states tick.
            self.caller.location.scripts.validate()
            # look around
            self.caller.execute_cmd("look")


class CmdLightSourceOff(Command):
    """
    Switch off the lightsource.
    """
    key = "off"
    aliases = ["switch off", "turn off", "dowse"]
    locks = "cmd:holds()"  # only allow if command.obj is carried by caller.
    help_category = "TutorialWorld"

    def func(self):
        "Implements the command "

        if not self.obj.db.is_active:
            self.caller.msg("%s没有在燃烧。" % self.obj.key)
        else:
            # set lightsource to inactive
            self.obj.db.is_active = False
            # validating the scripts will kill it now that is_active=False.
            self.obj.scripts.validate()
            self.caller.msg("{G你熄灭了{C%s。{n" % self.obj.key)
            self.caller.location.msg_contents("%s熄灭了%s。" % (self.caller, self.obj.key), exclude=[self.caller])
            self.caller.location.scripts.validate()
            self.caller.execute_cmd("look")


class CmdSetLightSource(CmdSet):
    "CmdSet for the lightsource commands"
    key = "lightsource_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(CmdLightSourceOn())
        self.add(CmdLightSourceOff())


class LightSource(TutorialObject):
    """
    This implements a light source object.

    When burned out, lightsource will be moved to its home - which by
    default is the location it was first created at.
    """
    def at_object_creation(self):
        "Called when object is first created."
        super(LightSource, self).at_object_creation()
        self.db.tutorial_info = "This object can be turned on off and has a timed script controlling it."
        self.db.is_active = False
        self.db.burntime = 60 * 3  # 3 minutes
        self.db.desc = "一小段木头，上面还残留着松脂，它应该能被点燃。"
        # add commands
        self.cmdset.add_default(CmdSetLightSource, permanent=True)

    def reset(self):
        """
        Can be called by tutorial world runner, or by the script when
        the lightsource has burned out.
        """
        if self.db.burntime <= 0:
            # light burned out. Since the lightsources's "location" should be
            # a character, notify them this way.
            try:
                loc = self.location.location
            except AttributeError:
                loc = self.location
            
            if loc:
                loc.msg_contents("{c%s{n{R烧尽了。{n" % self.key)
        self.db.is_active = False
        try:
            # validate in holders current room, if possible
            self.location.location.scripts.validate()
        except AttributeError:
            # maybe it was dropped, try validating at current location.
            try:
                self.location.scripts.validate()
            except AttributeError:
                pass
        self.delete()


#------------------------------------------------------------
#
# Crumbling wall - unique exit
#
# This implements a simple puzzle exit that needs to be
# accessed with commands before one can get to traverse it.
#
# The puzzle is currently simply to move roots (that have
# presumably covered the wall) aside until a button for a
# secret door is revealed. The original position of the
# roots blocks the button, so they have to be moved to a certain
# position - when they have, the "press button" command
# is made available and the Exit is made traversable.
#
#------------------------------------------------------------

# There are four roots - two horizontal and two vertically
# running roots. Each can have three positions: top/middle/bottom
# and left/middle/right respectively. There can be any number of
# roots hanging through the middle position, but only one each
# along the sides. The goal is to make the center position clear.
# (yes, it's really as simple as it sounds, just move the roots
# to each side to "win". This is just a tutorial, remember?)

class CmdShiftRoot(Command):
    """
    Shifts roots around.

    shift blue root left/right
    shift red root left/right
    shift yellow root up/down
    shift green root up/down

    """
    key = "shift"
    aliases = ["move"]
    # the locattr() lock looks for the attribute is_dark on the current room.
    locks = "cmd:not locattr(is_dark)"
    help_category = "TutorialWorld"

    def parse(self):
        "custom parser; split input by spaces"
        self.arglist = self.args.strip().split()
    
    
    def root_selected(self, menu_node):
        "Root selected"
        if menu_node.key.isdigit():
            select = int(menu_node.key)
            if select == 1:
                self.color = "blue"
                self.choose_direction()
                return
            elif select == 2:
                self.color = "green"
                self.choose_direction()
                return
            elif select == 3:
                self.color = "red"
                self.choose_direction()
                return
            elif select == 4:
                self.color = "yellow"
                self.choose_direction()
                return

        # no valid choice
        string = self.caller.get_available_cmd_desc(self.caller)
        self.caller.msg(string)
        return
        
    
    def choose_root(self):
        "Choose a root."
        prompt_choice(self.caller,
                      question="\n 你想移动哪条树根？",
                      prompts=["{c蓝色{n的树根",
                               "{g绿色{n的树根",
                               "{r红色{n的树根",
                               "{y黄色{n的树根"],
                      choicefunc=self.root_selected)
    
    
    def direction_selected(self, menu_node):
        "Direction selected"
        if menu_node.key.isdigit():
            select = int(menu_node.key)
            if select == 1:
                if self.color == "blue" or self.color == "red":
                    self.direction = "left"
                    self.shift_root()
                    return
                elif self.color == "green" or self.color == "yellow":
                    self.direction = "up"
                    self.shift_root()
                    return
            elif select == 2:
                if self.color == "blue" or self.color == "red":
                    self.direction = "right"
                    self.shift_root()
                    return
                elif self.color == "green" or self.color == "yellow":
                    self.direction = "down"
                    self.shift_root()
                    return

        # no valid choice
        string = self.caller.get_available_cmd_desc(self.caller)
        self.caller.msg(string)
        return

    
    def choose_direction(self):
        "Choose a direction."
        if self.color == "blue" or self.color == "red":
            choices = ["向左移动", "向右移动"]
        elif self.color == "green" or self.color == "yellow":
            choices = ["向上移动", "向下移动"]
        else:
            return
        
        prompt_choice(self.caller,
                      question="\n 你想哪个方向移动？",
                      prompts=choices,
                      choicefunc=self.direction_selected)


    def func(self):
        """
        Implement the command.
          blue/red - vertical roots
          yellow/green - horizontal roots
        """

        if not self.arglist:
            self.choose_root()
            return
    
        if "root" in self.arglist:
            self.arglist.remove("root")
        
        # we accept arguments on the form <color> <direction>
        if len(self.arglist) == 0:
            self.choose_root()
            return
        elif len(self.arglist) == 1:
            self.choose_direction()
            return
        
        self.color = self.arglist[0].lower()
        self.direction = self.arglist[1].lower()
        self.shift_root()
        
        
    def shift_root(self):
        # get current root positions dict
        root_pos = self.obj.db.root_pos
        color = self.color
        direction = self.direction

        string = "\n {c=============================================================={n"
        string += "\n {c%s{n" % self.obj.key
        string += "\n {c=============================================================={n"
        string += "\n "
        
        if not self.color in root_pos:
            string += "没有这样的树根。"
            string += self.caller.get_available_cmd_desc(self.caller)
            self.caller.msg(string)
            return

        # first, vertical roots (red/blue) - can be moved left/right

        if color == "red":
            if direction == "left":
                root_pos[color] = max(-1, root_pos[color] - 1)
                string += "你把红色的树根移向左边。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["blue"]:
                    root_pos["blue"] += 1
                    string += "长着蓝花的树根占住了地方，你把它推向右边。"
            elif direction == "right":
                root_pos[color] = min(1, root_pos[color] + 1)
                string += "你把红色的树根移向右边。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["blue"]:
                    root_pos["blue"] -= 1
                    string += "长着蓝花的树根占住了地方，你把它推向左边。"
            else:
                string += "你无法把树根往那个方向移动。"
        elif color == "blue":
            if direction == "left":
                root_pos[color] = max(-1, root_pos[color] - 1)
                string +="你把长着蓝花的树根移向左边。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["red"]:
                    root_pos["red"] += 1
                    string += "红色的树根占住了地方，你把它推向右边。"
            elif direction == "right":
                root_pos[color] = min(1, root_pos[color] + 1)
                string += "你把长着蓝花的树根移向右边。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["red"]:
                    root_pos["red"] -= 1
                    string += "红色的树根占住了地方，你把它推向左边。"
            else:
                string += "你无法把树根往那个方向移动。"
        # now the horizontal roots (yellow/green). They can be moved up/down
        elif color == "yellow":
            if direction == "up":
                root_pos[color] = max(-1, root_pos[color] - 1)
                string += "你把带着黄色小花的树根移向上方。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["green"]:
                    root_pos["green"] += 1
                    string += "覆盖着绿色苔藓的树根落了下来。"
            elif direction == "down":
                root_pos[color] = min(1, root_pos[color] + 1)
                string += "你把带有黄色小花的树根移向下面。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["green"]:
                    root_pos["green"] -= 1
                    string += "为了腾出地方，覆盖着绿色苔藓的树根被移了上去。"
            else:
                string += "你无法把树根往那个方向移动。"
        elif color == "green":
            if direction == "up":
                root_pos[color] = max(-1, root_pos[color] - 1)
                string += "你把覆盖着绿色苔藓的树根移向上方。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["yellow"]:
                    root_pos["yellow"] += 1
                    string += "带有黄色小花的树根落了下来。"
            elif direction == "down":
                root_pos[color] = min(1, root_pos[color] + 1)
                string += "你把覆盖着绿色苔藓的树根移向下面。"
                if root_pos[color] != 0 and root_pos[color] == root_pos["yellow"]:
                    root_pos["yellow"] -= 1
                    string += "为了腾出地方，带有黄色小花的树根被移了上去。"
            else:
                string += "你无法把树根往那个方向移动。"

        # store new position
        self.obj.db.root_pos = root_pos

        # check victory condition
        if root_pos.values().count(0) == 0: # no roots in middle position
            self.caller.db.crumbling_wall_found_button = True
            string += "\n把树根移开之后，你注意到后面有什么东西……"
            commands = ["{lclook %s{lt观察墙壁{le" % self.obj.dbref] + self.obj.available_cmd_list(None)
            string += "\n" + "\n 动作：" + "  ".join(commands)
        else:
            string += "\n" + self.obj.get_roots_desc()
            string += "\n" + self.obj.get_available_cmd_desc(self.obj)
            
        self.caller.msg(string)


class CmdPressButton(Command):
    """
    Presses a button.
    """
    key = "press"
    aliases = ["press button", "button", "push", "push button"]
    # only accessible if the button was found and there is light.
    locks = "cmd:attr(crumbling_wall_found_button) and not locattr(is_dark)"
    help_category = "TutorialWorld"

    def func(self):
        "Implements the command"

        if self.caller.db.crumbling_wall_found_exit:
            # we already pushed the button
            self.caller.msg("秘道露出来的时候按钮已移到了一边，你不能再按它了。")
            return

        # pushing the button
        string = "\n 你把手放进这个可疑的凹陷中，用力地推了一下。"
        string += "\n 一开始什么都没发生，但紧接着传来一阵隆隆声，一条{w密道{n露了出来。"
        string += "\n 随着墙的移动，墙上的鹅卵石也纷纷落下。"
        string += "\n" + self.caller.get_available_cmd_desc(self.caller)

        # we are done - this will make the exit traversable!
        self.caller.db.crumbling_wall_found_exit = True
        # this will make it into a proper exit
        eloc = self.caller.search(self.obj.db.destination, global_search=True)
        if not eloc:
            self.caller.msg("这个出口没有通往任何地方，在它后面是更多的石头……")
            return
        self.obj.destination = eloc
        self.caller.msg(string)


class CmdSetCrumblingWall(CmdSet):
    "Group the commands for crumblingWall"
    key = "crumblingwall_cmdset"

    def at_cmdset_creation(self):
        "called when object is first created."
        self.add(CmdShiftRoot())
        self.add(CmdPressButton())


class CrumblingWall(TutorialObject, Exit):
    """
    The CrumblingWall can be examined in various
    ways, but only if a lit light source is in the room. The traversal
    itself is blocked by a traverse: lock on the exit that only
    allows passage if a certain attribute is set on the trying
    player.

    Important attribute
     destination - this property must be set to make this a valid exit
                   whenever the button is pushed (this hides it as an exit
                   until it actually is)
    """
    def at_object_creation(self):
        "called when the object is first created."
        super(CrumblingWall, self).at_object_creation()

        self.aliases.add(["secret passage", "passage",
                          "crack", "opening", "secret door"])
        # this is assigned first when pushing button, so assign
        # this at creation time!

        self.db.destination = 2
        # locks on the object directly transfer to the exit "command"
        self.locks.add("cmd:not locattr(is_dark)")

        self.db.tutorial_info = "This is an Exit with a conditional traverse-lock. Try to shift the roots around."
        # the lock is important for this exit; we only allow passage
        # if we "found exit".
        self.locks.add("traverse:attr(crumbling_wall_found_exit)")
        # set cmdset
        self.cmdset.add(CmdSetCrumblingWall, permanent=True)

        # starting root positions. H1/H2 are the horizontally hanging roots,
        # V1/V2 the vertically hanging ones. Each can have three positions:
        # (-1, 0, 1) where 0 means the middle position. yellow/green are
        # horizontal roots and red/blue vertical, all may have value 0, but n
        # ever any other identical value.
        self.db.root_pos = {"yellow": 0, "green": 0, "red": 0, "blue": 0}

    def get_roots_desc(self):
        "Get desc of roots on the wall."
        string = ""
        for key, pos in self.db.root_pos.items():
            string += "\n" + self._translate_position(key, pos)
        return string

    
    def _translate_position(self, root, ipos):
        "Translates the position into words"
        rootnames = {"red": "一条垂直的{r红色{n的树根。",
                     "blue": "一条垂直的粗壮树根，上面长着{c蓝色{n的花。",
                     "yellow": "一条细长的横挂着的树根，上面长着{y黄色{n的小花。",
                     "green": "一条覆盖着{g绿色{n苔藓的横向的树根。"}
        vpos = {-1: "墙的{w左侧{n挂着",
                 0: "墙的{w正中{n挂着",
                 1: "墙的{w右侧{n挂着"}
        hpos = {-1: "墙的{w上面{n覆盖着",
                 0: "墙的{w中间{n横挂着",
                 1: "墙的{w底部{n堆积着"}

        if root in ("yellow", "green"):
            string = rootnames[root] + hpos[ipos]
        else:
            string = rootnames[root] + vpos[ipos]
        return string

    def return_appearance(self, caller):
        """
        This is called when someone looks at the wall. We need to echo the
        current root positions.
        """
        if caller.db.crumbling_wall_found_button:
            string =  "移开所有的树根之后，你发现在墙壁正中先前被植物遮蔽的地方有一个奇怪的方形\n"
            string += "凹陷。如果是在很久以前你肯定无法发现它，因为它伪装成了墙壁的一部分，但现\n"
            string += "在覆盖在它上面的石头早已破碎，很容易就能认出这是个按钮。"
        else:
            string =  "墙壁很古老。根系从石缝间伸展进来（也可能是藤蔓，因为有些还长着不知名的小\n"
            string += "花。），在墙上纵横交错，使你很难看清墙壁的石头表面。\n"
            for key, pos in self.db.root_pos.items():
                string += "\n" + self._translate_position(key, pos)
        self.db.desc = string
        # call the parent to continue execution (will use desc we just set)
        return super(CrumblingWall, self).return_appearance(caller)
        

    def available_cmd_list(self, caller):
        """
        This returns a list of available commands.
        """
        commands = ["{lcshift{lt移动树根{le"] + super(CrumblingWall, self).available_cmd_list(caller)
        if caller and caller.db.crumbling_wall_found_button:
            commands = ["{lcpress{lt按动按钮{le"] + commands
        return commands
    

    def at_after_traverse(self, traverser, source_location):
        """
        This is called after we traversed this exit. Cleans up and resets
        the puzzle.
        """
        del traverser.db.crumbling_wall_found_button
        del traverser.db.crumbling_wall_found_exit
        self.reset()

    def at_failed_traverse(self, traverser):
        "This is called if the player fails to pass the Exit."
        traverser.msg("不论你怎么努力，都无法穿过%s." % self.key)

    def reset(self):
        """
        Called by tutorial world runner, or whenever someone successfully
        traversed the Exit.
        """
        self.location.msg_contents("The secret door closes abruptly, roots falling back into place.")
        for obj in self.location.contents:
            # clear eventual puzzle-solved attribues on everyone that didn't
            # get out in time. They have to try again.
            del obj.db.crumbling_wall_found_exit

        # Reset the roots with some random starting positions for the roots:
        start_pos = [{"yellow":1, "green":0, "red":0, "blue":0},
                     {"yellow":0, "green":0, "red":0, "blue":0},
                     {"yellow":0, "green":1, "red":-1, "blue":0},
                     {"yellow":1, "green":0, "red":0, "blue":0},
                     {"yellow":0, "green":0, "red":0, "blue":1}]
        self.db.root_pos = start_pos[random.randint(0, 4)]
        self.destination = None


#------------------------------------------------------------
#
# Weapon - object type
#
# A weapon is necessary in order to fight in the tutorial
# world. A weapon (which here is assumed to be a bladed
# melee weapon for close combat) has three commands,
# stab, slash and defend. Weapons also have a property "magic"
# to determine if they are usable against certain enemies.
#
# Since Characters don't have special skills in the tutorial,
# we let the weapon itself determine how easy/hard it is
# to hit with it, and how much damage it can do.
#
#------------------------------------------------------------
class Weapon(ObjectPortable):
    """
    This defines a bladed weapon.

    Important attributes (set at creation):
      hit - chance to hit (0-1)
      parry - chance to parry (0-1)
      damage - base damage given (modified by hit success and
               type of attack) (0-10)

    """
    def at_object_creation(self):
        "Called at first creation of the object"
        super(Weapon, self).at_object_creation()
        self.db.hit = 0.4    # hit chance
        self.db.parry = 0.8  # parry chance
        self.db.damage = 8.0
        self.db.magic = False

    def reset(self):
        """
        When reset, the weapon is simply deleted, unless it has a place
        to return to.
        """
        if self.location.has_player and self.home == self.location:
            self.location.msg_contents("%s突然神奇地消失了，就像它从来没有存在过一样……" % self.key)
            self.delete()
        else:
            self.location = self.home


#------------------------------------------------------------
#
# Weapon barrel - spawns weapons
#
#------------------------------------------------------------
class WeaponBarrel(ObjectSelector):
    """
    This defines a weapon provider.
    """
    def give(self, caller):
        """
        Only allow to pick up if caller don't already has something called weapon
        """
        contents = caller.contents;
        weapons = [cont for cont in contents if cont.db.type_id in [1, 2, 3]]
        if weapons:
            caller.msg("\n 酒保微笑着对你说：“朋友，别太贪心了，你已经有一把武器了。”")

            commands = caller.get_available_cmd_desc(caller)
            if commands:
                caller.msg(commands + "\n")
            else:
                caller.msg("\n")

            return

        super(WeaponBarrel, self).give(caller)


#------------------------------------------------------------
#
# Weapon rack - spawns weapons
#
#------------------------------------------------------------

class CmdGetWeapon(Command):
    """
    Usage:
      get weapon

    This will try to obtain a weapon from the container.
    """
    key = "take"
    aliases = "take weapon"
    locks = "cmd:all()"
    help_cateogory = "TutorialWorld"

    def func(self):
        "Implement the command"

        if self.caller.ndb.weapon:
            # we don't allow a player to take more than one weapon from rack.
            string = "\n 你已经有一把武器了。"
            string += self.caller.get_available_cmd_desc(self.caller)
            self.caller.msg(string)
        else:
            dmg, name, aliases, desc, magic = self.obj.randomize_type()
            new_weapon = create_object(Weapon, key=name, aliases=aliases, location=self, home=self)
            new_weapon.db.damage = dmg
            new_weapon.db.desc = desc
            new_weapon.db.magic = magic
            
            #take the object
            if not new_weapon.move_to(caller, quiet=True, emit_to_obj=caller):
                new_weapon.delete()
                return
            
            ostring = self.obj.db.get_text
            if not ostring:
                ostring = "你拿起了%s。"
            if '%s' in ostring:
                self.caller.msg(ostring % name)
            else:
                self.caller.msg(ostring)


class CmdSetWeaponRack(CmdSet):
    "group the rack cmd"
    key = "weaponrack_cmdset"
    mergemode = "Replace"

    def at_cmdset_creation(self):
        "Called at first creation of cmdset"
        self.add(CmdGetWeapon())


class WeaponRack(TutorialObject):
    """
    This will spawn a new weapon for the player unless the player already has
    one from this rack.

    attribute to set at creation:
    min_dmg  - the minimum damage of objects from this rack
    max_dmg - the maximum damage of objects from this rack
    magic - if weapons should be magical (have the magic flag set)
    get_text - the echo text to return when getting the weapon. Give '%s'
               to include the name of the weapon.
    """
    def at_object_creation(self):
        "called at creation"
        #self.cmdset.add_default(CmdSetWeaponRack, permanent=True)
        self.db.rack_id = "weaponrack_1"
        self.db.min_dmg = 1.0
        self.db.max_dmg = 4.0
        self.db.magic = False
    
    
    def available_cmd_list(self, caller):
        """
        This returns a list of available commands.
        """
        commands = ["{lcloot %s{lt取走武器{le" % self.dbref] + super(WeaponRack, self).available_cmd_list(caller)
        return commands
    
    
    def give(self, caller):
        "Give weapon"
        string = "\n {c=============================================================={n"
        string += "\n {c取走武器{n"
        string += "\n {c=============================================================={n"
        string += "\n "
        
        if caller.ndb.weapon:
            # we don't allow a player to take more than one weapon from rack.
            string += "你已经有一把武器了。\n"
            string += "（你要先丢弃行囊中的武器才能拿取新武器）\n"
            string += caller.get_available_cmd_desc(caller)
            caller.msg(string)
            return
        
        dmg, name, aliases, desc, magic = self.randomize_type()
        new_weapon = create_object(Weapon, key=name, aliases=aliases, location=self, home=self)
        new_weapon.db.damage = dmg
        new_weapon.db.desc = desc
        new_weapon.db.magic = magic
        
        #take the object
        if not new_weapon.move_to(caller, quiet=True, emit_to_obj=caller):
            new_weapon.delete()
            return
        
        ostring = self.db.get_text
        if not ostring:
            ostring = "你拿起了%s。"
        if '%s' in ostring:
            ostring = ostring % name
        string += ostring + "\n"
        string += caller.get_available_cmd_desc(caller)
        caller.msg(string)
        
        destination = search_object("tut#17")
        if not destination:
            destination = search_object("#2")
        if destination:
            source = caller.location
            caller.location = destination[0]  # stealth move
            caller.location.at_object_receive(caller, source)


    def randomize_type(self):
        """
        this returns a random weapon
        """
        min_dmg = float(self.db.min_dmg)
        max_dmg = float(self.db.max_dmg)
        magic = bool(self.db.magic)
        dmg = min_dmg + random.random()*(max_dmg - min_dmg)
        aliases = [self.db.rack_id, "weapon"]
        if dmg < 1.5:
            name = "菜刀"
            desc = "一把生锈的菜刀，总比什么都没有要强。"
        elif dmg < 2.0:
            name = "生锈的匕首"
            desc = "一把木柄的匕首，刀刃已经钝了。"
        elif dmg < 3.0:
            name = "剑"
            desc = "一把生锈的短剑，柄上缠绕着皮带。"
        elif dmg < 4.0:
            name = "狼牙棒"
            desc = "一根沉重的狼牙棒，上面带着生锈的长钉。"
        elif dmg < 5.0:
            name = "华丽的长剑"
            aliases.extend(["longsword","ornate"])
            desc = "一把不错的长剑。"
        elif dmg < 6.0:
            name = "符文斧"
            aliases.extend(["rune","axe"])
            desc = "一把单刃的斧头，虽然重但用起来很称手。"
        elif dmg < 7.0:
            name = "王者之剑"
            aliases.extend(["thruning","broadsword"])
            desc = "这是一把阔剑，沉重而锋利，上面刻着四个字：“王者之剑”。在熟练的人手里，它能发挥出巨大的威力。"
        elif dmg < 8.0:
            name = "银色战锤"
            aliases.append("warhammer")
            desc = "这把沉重的战锤镶嵌着银质的纹饰，它能造成巨大的伤害。"
        elif dmg < 9.0:
            name = "屠杀者战斧"
            aliases.extend(["waraxe","slayer"])
            desc = "在这把巨大的双刃战斧上用符文雕刻着三个字：“屠杀者”。在它的前端还刻着更多的符文，但你看不懂它们写的是什么。"
        elif dmg < 10.0:
            name = "幽魂之刃"
            aliases.append("ghostblade")
            desc =  "虽然你已经够魁梧了，但相比之下这把剑还是显得很大。剑身上散发着浅蓝色的光芒。"
        else:
            name = "雄鹰之刃"
            aliases.append("hawkblade")
            desc = "白色的魔法能量在这把神秘的剑上涌动着，剑柄上描绘的雄鹰像是有生命一样。"
        if dmg < 9 and magic:
            desc += "这把武器在隐隐发光，似乎灌注了异乎寻常的力量。"
        return dmg, name, aliases, desc, magic
