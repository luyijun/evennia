# -*- coding: utf-8 -*-
"""

Template for Objects

Copy this module up one level and name it as you like, then
use it as a template to create your own Objects.

To make the default commands default to creating objects of your new
type (and also change the "fallback" object used when typeclass
creation fails), change settings.BASE_OBJECT_TYPECLASS to point to
your new class, e.g.

settings.BASE_OBJECT_TYPECLASS = "game.gamesrc.objects.myobj.MyObj"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Object as DefaultObject


class ObjectCommon(DefaultObject):
    """
    This is the root typeclass object of this game.
     """
    def at_object_creation(self):
        "Called when the object is first created."
        super(ObjectCommon, self).at_object_creation()
        self.db.type_id = 0

        
    def return_appearance(self, pobject):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        if not pobject:
            return
            
        # get description, build string
        string = "\n {c=============================================================={n"
        string += "\n {c%s{n" % self.key
        string += "\n {c=============================================================={n"
        
        desc = self.get_object_desc()
        if desc:
            string += "\n %s" % desc
        
        string += "\n "
        
        if self == pobject.location:
            # if caller is in this object
            # get and identify all objects
            visible = (cont for cont in self.contents if cont != pobject and
                                                        cont.access(pobject, "view"))
            exits, users, things = [], [], []
            for cont in visible:
                if cont.destination:
                    exits.append("{lcgoto %s{lt%s{le" % (cont.dbref, cont.name))
                elif cont.player:
                    users.append("{lclook %s{lt%s{le" % (cont.dbref, cont.name))
                else:
                    things.append("{lclook %s{lt%s{le" % (cont.dbref, cont.name))

            if things:
                string += "\n 看见：" + "  ".join(things)
            if users:
                string += "\n 遇到：" + "  ".join(users)
            if exits:
                string += "\n 出口：" + "  ".join(exits)

        commands = self.get_available_cmd_desc(pobject)
        if commands:
            string += commands
                
        string += "\n "
        return string

        
    def available_cmd_list(self, pobject):
        """
        This returns a list of available commands.
        """
        commands = ["{lclook{lt观察周围{le",
                    "{lcinventory{lt查看行囊{le",
                    "{lchelp{lt帮助信息{le",
                    "{lc@quit{lt退出游戏{le"]
        return commands
        
        
    def get_available_cmd_desc(self, pobject):
        """
        This returns a string of available commands.
        """
        string = ""
        commands = self.available_cmd_list(pobject)
        if commands:
            string = "\n 动作：" + "  ".join(commands)
        return string

        
    def get_object_desc(self):
        """
        Get object's description.
        """
        return self.db.desc