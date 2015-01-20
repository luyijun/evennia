# -*- coding: utf-8 -*-
"""
Example command module template

Copy this module up one level to gamesrc/commands/ and name it as
befits your use.  You can then use it as a template to define your new
commands. To use them you also need to group them in a CommandSet (see
examples/cmdset.py)

"""

import traceback
import re
import random, time
from ev import Command as BaseCommand
from ev import default_cmds
from ev import utils
from ev import syscmdkeys
from extension.utils.menusystem import prompt_yesno, prompt_choice


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own
    command styles. Note that Evennia's default commands
    use MuxCommand instead (next in this module)

    Note that the class's __doc__ string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    """
    # these need to be specified

    key = "MyCommand"
    aliases = ["mycmd", "myc"]
    locks = "cmd:all()"
    help_category = "General"

    # auto_help = False      # uncomment to deactive auto-help for this command.
    # arg_regex = r"\s.*?|$" # optional regex detailing how the part after
                             # the cmdname must look to match this command.

    # (we don't implement hook method access() here, you don't need to
    #  modify that unless you want to change how the lock system works
    #  (in that case see src.commands.command.Command))

    def at_pre_cmd(self):
        """
        This hook is called before self.parse() on all commands
        """
        pass

    def parse(self):
        """
        This method is called by the cmdhandler once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from self.func() (see below)

        The following variables are available to us:
           # class variables:

           self.key - the name of this command ('mycommand')
           self.aliases - the aliases of this cmd ('mycmd','myc')
           self.locks - lock string for this command ("cmd:all()")
           self.help_category - overall category of command ("General")

           # added at run-time by cmdhandler:

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following self.cmdstring.
           self.cmdset - the cmdset from which this command was picked. Not
                         often used (useful for commands like 'help' or to
                         list all available commands etc)
           self.obj - the object on which this command was defined. It is often
                         the same as self.caller.
        """
        pass

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
         by the cmdhandler right after self.parser() finishes, and so has access
         to all the variables defined therein.
        """
        self.caller.msg("Command called!")

    def at_post_cmd(self):
        """
        This hook is called after self.func().
        """
        pass


class MuxCommand(default_cmds.MuxCommand):
    """
    This sets up the basis for a Evennia's 'MUX-like' command
    style. The idea is that most other Mux-related commands should
    just inherit from this and don't have to implement parsing of
    their own unless they do something particularly advanced.

    A MUXCommand command understands the following possible syntax:

      name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

    The 'name[ with several words]' part is already dealt with by the
    cmdhandler at this point, and stored in self.cmdname. The rest is stored
    in self.args.

    The MuxCommand parser breaks self.args into its constituents and stores them
    in the following variables:
      self.switches = optional list of /switches (without the /)
      self.raw = This is the raw argument input, including switches
      self.args = This is re-defined to be everything *except* the switches
      self.lhs = Everything to the left of = (lhs:'left-hand side'). If
                 no = is found, this is identical to self.args.
      self.rhs: Everything to the right of = (rhs:'right-hand side').
                If no '=' is found, this is None.
      self.lhslist - self.lhs split into a list by comma
      self.rhslist - list of self.rhs split into a list by comma
      self.arglist = list of space-separated args (including '=' if it exists)

      All args and list members are stripped of excess whitespace around the
      strings, but case is preserved.
      """

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the cmdhandler right after self.parser() finishes, and so has access
        to all the variables defined therein.
        """
        # this can be removed in your child class, it's just
        # printing the ingoing variables as a demo.
        super(MuxCommand, self).func()

                 
#------------------------------------------------------------
# create new account and login
#------------------------------------------------------------
class CmdUnconnectedCreateAndConnect(default_cmds.CmdUnconnectedCreate):
    """
    This command combined create with connect.
    """
    
    def func(self):
        """
        Use the default create, then call login.
        """
        import re
        from ev import PlayerDB
        
        session = self.caller
        args = self.args
        
        parts = [part.strip() for part in re.split(r"\"|\'", args) if part.strip()]
        
        if len(parts) == 1:
            # this was (hopefully) due to no quotes being found
            parts = parts[0].split(None, 1)
        if len(parts) != 2:
            string = "\n用法：（不带< >） create <用户名> <密码>"
            string += "\n如果 <用户名> 或 <密码> 中有空格，请用引号把它括起来。"
            session.msg(string)
            return

        playername, password = parts
        
        player = PlayerDB.objects.get_player_from_name(playername)
        if player:
            session.msg("该名字已有人使用！")
            return
        
        super(CmdUnconnectedCreateAndConnect, self).func()

        player = PlayerDB.objects.get_player_from_name(playername)
        if player:
            # player has been created.
                    
            # actually do the login. This will call all other hooks:
            #   session.at_login()
            #   player.at_init()  # always called when object is loaded from disk
            #   player.at_pre_login()
            #   player.at_first_login()  # only once
            #   player.at_post_login(sessid=sessid)
            session.sessionhandler.login(session, player)


#------------------------------------------------------------
# get object
#------------------------------------------------------------
class CmdGetObject(MuxCommand):
    """
    Usage:
      get object
    """
    key = "get"
    locks = "cmd:all()"
    help_cateogory = "General"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Implement the command"
        
        caller = self.caller

        if not self.args:
            caller.msg("你要拿什么？")
            return
        
        #print "general/get:", caller, caller.location, self.args, caller.location.contents
        obj = caller.search(self.args, location=caller.location)
        if not obj:
            caller.msg("没有找到%s" % (self.args))
            return
            
        if caller == obj:
            caller.msg("你不能拿起自己。")
            return
            
        #print obj, obj.location, caller, caller==obj.location
        if caller == obj.location:
            caller.msg("你已经拿着它了。")
            return

        if not obj.access(caller, 'get'):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("你不能拿起它。")
            return
                
        #get the object
        if not obj.move_to(caller, quiet=True, emit_to_obj=caller):
            return
        
        ostring = obj.db.get_text
        if not ostring:
            ostring = "你拿起了%s。"
        if "%s" in ostring:
            caller.msg(ostring % obj.name)
        else:
            self.caller.msg(ostring)
        caller.location.msg_contents("%s拿起了%s." %
                                        (caller.name,
                                         obj.name),
                                         exclude=caller)
        # calling hook method
        obj.at_get(caller)
        
        
#------------------------------------------------------------
# discard object
#------------------------------------------------------------
          
class CmdDiscardObject(MuxCommand):
    """
    Usage:
      get object
    """
    key = "discard"
    aliases = []
    locks = "cmd:all()"
    help_cateogory = "General"
    arg_regex = r"\s.*?|$"
    
    def func_destroy(self, menu_node):
        """
        Call parent destroy func.
        """
        caller = self.caller

        if not self.args or not self.lhslist:
            caller.msg("用法: discard [obj]")
            return
            
        obj = caller.search(self.args)
        if not obj:
            caller.msg("无法找到丢弃的物品。")
            return
            
        objname = obj.name
        if not obj.access(caller, 'delete'):
            caller.msg("你不能丢弃%s。" % objname)
            return

        # do the deletion
        okay = obj.delete()
        if not okay:
            caller.msg("发生错误：%s无法丢弃。" % objname)
            return
        
        caller.select_weapon()
        
        ostring = "\n%s已被丢弃。" % objname
        commands = caller.get_available_cmd_desc(caller)
        if commands:
            ostring += "\n" + commands + "\n"
        else:
            ostring += "\n"

        caller.msg(ostring, clear_links=True)

        return
        
        
    def func_canceled(self, menu_node):
        """
        Func canceled.
        """
        caller = self.caller
        
        ostring = "没有丢弃。"
        commands = caller.get_available_cmd_desc(caller)
        if commands:
            ostring += "\n" + commands + "\n"
        else:
            ostring += "\n"
            
        caller.msg(ostring, clear_links=True)

    
    def func(self):
        "Implement the command"
        
        caller = self.caller

        if not self.args:
            caller.msg("你想丢弃什么？")
            return
            
        obj = caller.search(self.args)
        if not obj:
            caller.msg("你不能丢弃不属于你的东西。")
            return
            
        prompt_yesno(caller, "确定丢弃吗？丢弃之后就无法找回了。",
                     yesfunc = self.func_destroy,
                     nofunc = self.func_canceled,
                     default="N")
        return
        
        
#------------------------------------------------------------
# drop object
#------------------------------------------------------------
          
class CmdDropObject(default_cmds.CmdDrop):
    """
    Usage:
      drop object
    """
    key = "drop"
    aliases = []
    locks = "perm(Builders)"
    help_cateogory = "General"
    arg_regex = r"\s.*?|$"
    

#------------------------------------------------------------
# drop object
#------------------------------------------------------------

class CmdInventory(MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_cateogory = "General"
    arg_regex = r"\s.*?|$"

    def func(self):
        "check inventory"
        caller = self.caller
        items = caller.contents
        if not items:
            string = "\n{c=============================================================={n"
            string += "\n{c你没有携带任何东西。{n"
            string += "\n{c=============================================================={n"
        else:
            max_width = len(utils.to_str(utils.to_unicode("物品"), encoding = "gbk"))
            widths = [max_width]
            for item in items:
                if item.name:
                    width = len(utils.to_str(utils.to_unicode(item.name), encoding = "gbk"))
                    widths.append(width)
                    if max_width < width:
                        max_width = width
                else:
                    widths.append(0)

            index = 0
            space = " " * (max_width - widths[index] + 2)
            table = " %s%s%s" % ("物品", space, "描述")
            for item in items:
                name = "{lclook %s{lt%s{le" % (item.dbref, item.name)
                desc = item.db.desc if item.db.desc else ""
                index += 1
                space = " " * (max_width - widths[index] + 2)

                table += "\n%s%s%s" % (name, space, desc)
                
            string = "\n{c=============================================================={n"
            string += "\n{c你携带着{n"
            string += "\n{c=============================================================={n"
            string += "\n%s" % table

        commands = caller.get_available_cmd_desc(caller)
        if commands:
            string += "\n" + commands + "\n"
        else:
            string += "\n"
            
        caller.msg(string, clear_links=True)
        
        
#------------------------------------------------------------
# goto exit
#------------------------------------------------------------

class CmdGoto(MuxCommand):
    """
    goto exit

    Usage:
      goto exit
    """
    key = "goto"
    aliases = ["go"]
    locks = "cmd:all()"
    help_cateogory = "General"
    arg_regex = r"\s.*?|$"

    def func(self):
        "Goto exit."
        caller = self.caller

        if not self.args:
            caller.msg("你要去哪里？")
            return

        obj = caller.search(self.args, location=caller.location)
        if not obj:
            caller.msg("没有找到%s" % (self.args))
            return
            
        if obj.access(self.caller, 'traverse'):
            # we may traverse the exit.
            obj.at_traverse(caller, obj.destination)
        else:
            # exit is locked
            if obj.db.err_traverse:
                # if exit has a better error message, let's use it.
                caller.msg(self.obj.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                obj.at_failed_traverse(caller)
                
                
#------------------------------------------------------------
# look
#------------------------------------------------------------
class CmdLook(default_cmds.CmdLook):
    """
    Set CMD_NOINPUT to look.
    """
    aliases = ["l", "ls", syscmdkeys.CMD_NOINPUT]
    
    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args
        if args:
            # Use search to handle duplicate/nonexistant results.
            looking_at_obj = caller.search(args, use_nicks=True)
            if not looking_at_obj:
                return
        else:
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg("You have no location to look at!")
                return

        if not hasattr(looking_at_obj, 'return_appearance'):
            # this is likely due to us having a player instead
            looking_at_obj = looking_at_obj.character
        if not looking_at_obj.access(caller, "view"):
            caller.msg("Could not find '%s'." % args)
            return
        # get object's appearance
        ostring = looking_at_obj.return_appearance(caller)
        if ostring:
            caller.msg(ostring, clear_links=True)
        # the object's at_desc() method.
        looking_at_obj.at_desc(looker=caller)
                                                   
                                                   
#------------------------------------------------------------
# loot
#------------------------------------------------------------
class CmdLoot(MuxCommand):
    """
    Usage:
    loot object_creator
   
    This will try to loot a object_creator for portable object.
    """
    key = "loot"
    aliases = ""
    locks = "cmd:all()"
    help_cateogory = "TutorialWorld"
    arg_regex = r"\s.*?|$"

    def func(self):
        """
        Implement the command
        """

        caller = self.caller
        if not self.args:
            string = "Usage: loot <obj>"
            caller.msg(string)
            return

        obj = caller.search(self.args, location=caller.location)
        if not obj:
            caller.msg("没有找到%s" % (self.args))
            return

        if not hasattr(obj, "give"):
            string = "无法搜索该物体。"
            caller.msg(string)
            return

        obj.give(caller)
                           

#------------------------------------------------------------
# set object's type id
#------------------------------------------------------------
class CmdTypeId(MuxCommand):
    """
    Usage:
    @typeid <obj> = [id]
    
    This will try to set the type id of an object.
    """
    key = "@typeid"
    locks = "perm(Builders)"
    help_cateogory = "Building"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        if not self.args:
            string = "Usage: @typeid <obj> [=id]"
            caller.msg(string)
            return
        
        if not self.lhslist:
            objname = self.args
            obj = caller.search(objname, location=caller.location)
            if not obj:
                caller.msg("Sorry, can not find %s." % objname)
            else:
                caller.msg("%s's type id is %d" % (objname, obj.db.type_id))
            return

        objname = self.lhs
        obj = caller.search(objname, location=caller.location)
        if not obj:
            caller.msg("Sorry, can not find %s." % objname)
            return

        if not hasattr(obj, "set_type_id"):
            caller.msg("You can not set its type id")
            return
    
        if not self.rhs:
            callser.msg("Must input a type id.")
            return
        
        pattern = re.compile(r"\d+", re.I)
        if not pattern.match(self.rhs):
            caller.msg("Type id must be numbers.")
            return
         
        # change the type:
        type_id = int(self.rhs)
        if not obj.set_type_id(type_id):
            caller.msg("Type data error!")
            return
            
        caller.msg("%s's type id has been set to %s." % (objname, type_id))
        

#------------------------------------------------------------
# attack
#------------------------------------------------------------
class CmdAttack(MuxCommand):
    """
    Attack the enemy. Commands:

      stab <enemy>
      slash <enemy>
      parry

    stab - (thrust) makes a lot of damage but is harder to hit with.
    slash - is easier to land, but does not make as much damage.
    parry - forgoes your attack but will make you harder to hit on next
            enemy attack.

    """

    # this is an example of implementing many commands as a single
    # command class, using the given command alias to separate between them.

    key = "fight"
    locks = "cmd:all()"
    help_category = "General"
    
    def menu_selected(self, menu_node):
        """
        """
        caller = self.caller
        
        if not menu_node.key.isdigit():
            self.fight(0)
            caller.display_available_cmds()
            return
            
        select = int(menu_node.key)
        if select > 0:
            self.fight(select)
            
        caller.display_available_cmds()


    def func(self):
        "Implements the stab"
        
        caller = self.caller
        
        if not caller.ndb.weapon:
            caller.msg("你没有武器，无法战斗！")
            caller.display_available_cmds()
            return

        action = ""
        
        target = None
        if not self.args:
            if caller.ndb.target:
                target = caller.ndb.target
        else:
            if not self.lhs:
                objname = self.args
            else:
                objname = self.lhs
                action = self.rhs
        
            if not objname:
                caller.msg("你需要一个目标。")
                caller.display_available_cmds()
                return
            
            target = caller.search(objname, location=caller.location)
            if not target:
                caller.msg("无法找到%s。" % objname)
                caller.display_available_cmds()
                return
                
        if target.db.health <= 0:
            caller.msg("%s已经死了。" % target.key)
            caller.display_available_cmds()
            return

        # set each targets
        caller.ndb.target = target
        if not target.ndb.target:
            target.ndb.target = caller
        
        if not action:
            prompt_choice(caller,
                          question="如何战斗？",
                          prompts=["刺", "砍", "防御"],
                          callback_func=self.menu_selected)
        else:
            if action == "stab":
                self.fight(1)
            elif action == "slash":
                self.fight(2)
            elif action == "defend":
                self.fight(3)
            else:
                self.fight(0)
            
            caller.display_available_cmds()
                      
                      
    def fight(self, select):
        """
        """
        caller = self.caller
        
        string = "\n"
        tstring = "\n"
        ostring = "\n"
            
        if select == 3:
            # defend
            string += "你举起武器摆出了防御的姿势，准备格挡敌人的下一次攻击。"
            caller.msg(string)
            caller.db.combat_parry_mode = True
            caller.location.msg_contents("%s摆出了防御姿态。" % self.caller, exclude=[self.caller])
            return
        elif select == 1 or select == 2:
            target = caller.ndb.target
            weapon = caller.ndb.weapon
            hit = weapon.db.hit
            damage = weapon.db.damage
            if select == 1:
                # stab
                hit *= 0.7  # modified due to stab
                damage *= 2  # modified due to stab
                string += "你用%s刺去。" % weapon.key
                tstring += "%s用%s刺向你。" % (caller.key, weapon.key)
                ostring += "%s用%s刺向%s。" % (caller.key, weapon.key, target.key)
                self.caller.db.combat_parry_mode = False
            elif select == 2:
                # slash
                # un modified due to slash
                string += "你用%s砍去。" % weapon.key
                tstring += "%s用%s砍向你。" % (caller.key, weapon.key)
                ostring += "%s用%s砍向%s。" % (caller.key, weapon.key, target.key)
                self.caller.db.combat_parry_mode = False

            if target.db.combat_parry_mode:
                # target is defensive; even harder to hit!
                target.msg("\n{G你进行防御，想努力躲开攻击。{n")
                hit *= 0.5

            if random.random() <= hit:
                self.caller.msg(string + "{g击中了！{n")
                target.msg(tstring + "{r击中了！{n")
                self.caller.location.msg_contents(ostring + "击中了！", exclude=[target, caller])

                # call enemy hook
                if hasattr(target, "at_hit"):
                    # should return True if target is defeated, False otherwise.
                    target.at_hit(weapon, caller, damage)
                elif target.db.health:
                    target.db.health -= damage
                else:
                    # sorry, impossible to fight this enemy ...
                    self.caller.msg("敌人似乎没有受到影响。")

            else:
                self.caller.msg(string + "{r你没有击中。{n")
                target.msg(tstring + "{g没有击中你。{n")
                self.caller.location.msg_contents(ostring + "没有击中。", exclude=[target, caller])
        else:
            # no choice
            self.caller.msg("\n你拿着武器不知所措，不知是该刺、砍还是格挡……")
            self.caller.location.msg_contents("\n%s拿着武器不知所措。" % caller.key)
            self.caller.db.combat_parry_mode = False
            return

            