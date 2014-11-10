# -*- coding: utf-8 -*-
"""
"""


from ev import CmdSet
from ev import create_object
from extension.commands.command import MuxCommand
from object_common import ObjectCommon


#------------------------------------------------------------
#
# Weapon rack - spawns weapons
#
#------------------------------------------------------------

class CmdFillShelf(MuxCommand):
    """
    Usage:
    @fill shelf = object_type, object_type, object_type...
    
    This will try to set possible objects to object_creater.
    """
    key = "@fill"
    locks = "perm(Builders)"
    help_cateogory = "Building"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        if not self.args:
            string = "Usage: @fill <obj> [=object_type[,object_type,object_type...]]"
            caller.msg(string)
            return
        
        if self.lhslist:
            objname = self.lhs
            obj = caller.search(objname)
            if not obj:
                return
        
        if self.rhslist:
            types = self.rhslist
        else:
            types = None

        # change the obj_list:
        obj.set_objects(types)
        caller.msg("%s is filled with %s." % (objname, types))


class CmdDemandObject(MuxCommand):
    """
    Usage:
    demand object_creater
    
    This will try to demand a object_creater for portable object.
    """
    key = "demand"
    aliases = "dem"
    locks = "cmd:all()"
    help_cateogory = "TutorialWorld"

    def func(self):
        """
        Implement the command
        """
        
        caller = self.caller
        if not self.args:
            string = "Usage: demand <obj>"
            caller.msg(string)
            return
        
        obj = self.obj
        if not obj:
            string = "你想要获取什么？"
            caller.msg(string)
            return

        obj.give(caller)


class CmdSetDemandObject(CmdSet):
    "group the demand cmd"
    key = "demandobject_cmdset"
    
    def at_cmdset_creation(self):
        "Called at first creation of cmdset"
        self.add(CmdDemandObject())
        self.add(CmdFillShelf())


class ObjectShelf(ObjectCommon):
    """
    """
    def __init__(self, dbobj):
        super(ObjectShelf, self).__init__(dbobj)
    
        self.db.obj_info = {"1":{"name":"生锈的剑1",
                                 "desc":"这是一把生锈的阔剑。它曾经是把好剑，但现在只有剑柄还是保持完好。",
                                 "typeclass":"extension.objects.object_portable.ObjectPortable"},
                            "2":{"name":"生锈的剑2",
                                 "desc":"这是一把生锈的阔剑。它曾经是把好剑，但现在只有剑柄还是保持完好。",
                                 "typeclass":"extension.objects.object_portable.ObjectPortable"},
                            "3":{"name":"生锈的剑3",
                                 "desc":"这是一把生锈的阔剑。它曾经是把好剑，但现在只有剑柄还是保持完好。",
                                 "typeclass":"extension.objects.object_portable.ObjectPortable"},}


    def at_object_creation(self):
        "called at creation"
        super(ObjectShelf, self).at_object_creation()
        self.cmdset.add_default(CmdSetDemandObject, permanent=True)


    def set_objects(self, obj_list):
        "set possible objects"
        self.db.obj_list = obj_list


    def give(self, caller):
        ""
        if not self.db.obj_list:
            # no objects
            caller.msg("没有可以获取的物品")
            return
        else:
            for obj_id in self.db.obj_list:
                if obj_id in self.db.obj_info:
                    info = self.db.obj_info[obj_id]
                    new_obj = create_object(info["typeclass"], key=info["name"], location=self, home=self)
                    
                    if new_obj:
                        new_obj.db.desc = info["desc"]
                        
                        #move the object to the caller
                        if not new_obj.move_to(caller, quiet=True, emit_to_obj=caller):
                            new_obj.delete()
                        else:
                            caller.msg("你拿起了%s" % info["name"])

