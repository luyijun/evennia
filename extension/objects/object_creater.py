# -*- coding: utf-8 -*-
"""
"""


from ev import CmdSet
from ev import create_object
from extension.commands.command import MuxCommand
from object_common import ObjectCommon
from extension.data.models import Object_Type_List


#------------------------------------------------------------
#
# Weapon rack - spawns weapons
#
#------------------------------------------------------------

class CmdShelfFill(MuxCommand):
    """
    Usage:
    @fill shelf = object_type, object_type, object_type...
    
    This will try to set possible objects to object_creater.
    """
    key = "@shelf_fill"
    locks = "perm(Builders)"
    help_cateogory = "Building"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        if not self.args:
            string = "Usage: @shelf_fill <obj> [=object_type[,object_type,object_type...]]"
            caller.msg(string)
            return
        
        if self.lhslist:
            objname = self.lhs
            obj = caller.search(objname)
            if not obj:
                return
    
        types = []
        if self.rhslist:
            types = self.rhslist

        # change the obj_list:
        obj.set_objects(types)
        caller.msg("%s is filled with %s." % (objname, types))


class CmdShelfMessage(MuxCommand):
    """
    Usage:
    @shelf_msg <obj> = [message]
    
    This will try to set possible objects to object_creater.
    """
    key = "@shelf_msg"
    locks = "perm(Builders)"
    help_cateogory = "Building"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        if not self.args:
            string = "Usage: @shelf_msg <obj> = [message]"
            caller.msg(string)
            return
        
        if not self.lhslist:
            objname = self.args
            obj = caller.search(objname)
            if obj:
                caller.msg("%s", obj.db.message)
            return
        
        objname = self.lhs
        obj = caller.search(objname)
        if not obj:
            return
    
        message = ""
        if self.rhs:
            message = self.rhs

        # change the message:
        obj.set_message(message)
        caller.msg("%s's message is set to %s." % (objname, message))


class CmdSetObjectCreater(CmdSet):
    "group the search cmd"
    key = "searchobject_cmdset"
    
    def at_cmdset_creation(self):
        "Called at first creation of cmdset"
        self.add(CmdShelfFill())
        self.add(CmdShelfMessage())


class ObjectShelf(ObjectCommon):
    """
    """
    def at_object_creation(self):
        "called at creation"
        super(ObjectShelf, self).at_object_creation()
        self.cmdset.add_default(CmdSetObjectCreater, permanent=True)


    def set_objects(self, obj_list):
        "set possible objects"
        self.db.obj_list = obj_list
    
    
    def set_message(self, message):
        "set creater's message"
        self.db.message = message
    
    
    def available_cmd_list(self, pobject):
        """
        This returns a string of available commands.
        """
        commands = ["{lcloot %s{lt搜索%s{le" % (self.dbref, self.name)]
        commands.extend(super(ObjectShelf, self).available_cmd_list(pobject))
        return commands


    def give(self, caller):
        """
        """
        
        caller.msg(self.db.message)

        if not self.db.obj_list:
            # no objects
            caller.msg("没有可以获取的物品")
        else:
            # create objects in the list
            for obj_id in self.db.obj_list:
                # find object type's info
                matches = Object_Type_List.objects.filter(db_key=obj_id)
                if matches:
                    info = matches[0]
                    
                    new_obj = create_object(info.db_typeclass_path, key=info.db_name, location=self, home=self)
                    
                    if new_obj:
                        new_obj.db.type_id = info.db_key
                        new_obj.db.desc = info.db_desc
                        new_obj.db.bind_type = info.db_bind_type
                        new_obj.db.is_unique = info.db_unique
                        
                        #move the object to the caller
                        if not new_obj.move_to(caller, quiet=True, emit_to_obj=caller):
                            new_obj.delete()
                        else:
                            caller.msg("你拿起了{w[%s]{n" % new_obj.key)


