# -*- coding: utf-8 -*-
"""
"""

import traceback
from django.conf import settings

from ev import Command, CmdSet
from object_common import ObjectCommon as Object

from game.extension import BINDING_TYPE


#------------------------------------------------------------
# Portable Object
#------------------------------------------------------------
class ObjectPortable(Object):
    """
    This is the baseclass for bandable objects.
    """

    def at_object_creation(self):
        "Called when the object is first created."
        super(ObjectPortable, self).at_object_creation()

        self.db.bind_type = BINDING_TYPE.NONE
        self.db.is_bound = False
        self.db.is_unique = False


    def basetype_posthook_setup(self):
        """
        Called once, after basetype_setup and at_object_creation. This should
        generally not be overloaded unless you are redefining how a
        room/exit/object works. It allows for basetype-like setup after the
        object is created. An example of this is EXITs, who need to know keys,
        aliases, locks etc to set up their exit-cmdsets.
        """
        # The owner can destroy this object.
        lock_string = self.locks.get("discard")
        if lock_string:
            lock_string += " or holds()"
        else:
            lock_string = "delete:holds()"
        self.locks.add(lock_string)

        
    def at_before_move(self, destination):
        """
        Called just before starting to move
        this object to destination.

        destination - the object we are moving to

        If this method returns False/None, the move
        is cancelled before it is even started.
        """
        if not super(ObjectPortable, self).at_before_move(destination):
            return False
        
        if not destination:
            return True
           
        if not destination.player:
            return True
            
        # Check if this object is bound.
        if self.db.is_bound:
            destination.msg("该物品已绑定其他人。")
            return False

        # Check if user try to get another unique objects.
        if self.db.is_unique:
            type_id = self.db.type_id
            contents = destination.contents;
 
            same_obj = [cont for cont in contents if cont.db.type_id == type_id]
            if len(same_obj) > 0:
                destination.msg("不能携带更多此类物品。")
                return False

        return True
        

    def at_after_move(self, source_location):
        """
        Called after move has completed, regardless of quiet mode or not.
        Allows changes to the object due to the location it is now in.

        source_location - where we came from. This may be None.
        """        
        if self.db.bind_type == BINDING_TYPE.ON_PICKUP:
            self.db.is_bound = True

        
    def get_bind_desc(self):
        """
        Get object's bind description.
        """
        desc = None
        if self.db.is_bound:
            desc = "已绑定"
        else:
            if self.db.bind_type == BINDING_TYPE.ON_EQUIP:
                desc = "装备绑定"
            elif self.db.bind_type == BINDING_TYPE.ON_PICKUP:
                desc = "拾取绑定"
                
        if self.db.is_unique:
            if desc:
                desc += "  "
            else:
                desc = ""
            desc += "唯一物品"
            
        if desc:
            desc = "（" + desc + "）"
        return desc
        
        
    def get_object_desc(self):
        """
        Get object's description.
        """
        desc = super(ObjectPortable, self).get_object_desc()
        bind_desc = self.get_bind_desc()
        if bind_desc:
            desc += "\n" + bind_desc
        return desc
        
        
    def available_cmd_list(self, pobject):
        """
        This returns a string of available commands.
        """
        commands = []
        if pobject and self.location != pobject:
            commands = ["{lcget %s{lt拿起%s{le" % (self.dbref, self.name)]
        else:
            commands = ["{lcdiscard %s{lt丢弃%s{le" % (self.dbref, self.name)]
           
        commands.extend(super(ObjectPortable, self).available_cmd_list(pobject))
        return commands
