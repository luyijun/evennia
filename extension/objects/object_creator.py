# -*- coding: utf-8 -*-
"""
"""


from ev import CmdSet
from ev import create_object
from ev import utils
from extension.commands.command import MuxCommand
from object_common import ObjectCommon
from extension.data.models import Object_Type_List, Object_Creator_Types
from extension.utils.menusystem import prompt_choice
from extension.utils.defines import OBJ_CATEGORY

import traceback


#------------------------------------------------------------
#
# object creator - spawns objects
#
#------------------------------------------------------------
class ObjectCreator(ObjectCommon):
    """
    Create objects on the list.
    """
    def at_object_creation(self):
        "called at creation"
        super(ObjectCreator, self).at_object_creation()
    
        self.ndb.obj_list = []
        self.ndb.command = ""
        self.ndb.question = ""


    def load_type_data(self):
        "Set object data from db."

        if not super(ObjectCreator, self).load_type_data():
            return False

        if not self.ndb.category == OBJ_CATEGORY.CREATOR:
            print "Category error!"
            return False
        
        cate_data = Object_Creator_Types.objects.filter(db_key=self.db.type_id)
        if not cate_data:
            print "Can not find category data."
            return False
            
        info = cate_data[0]
        obj_list = info.db_obj_list.split(",")
        try:
            self.ndb.obj_list = [int(i) for i in obj_list]
        except:
            print "Object list #%d error! (%s)" % (self.db.type_id, info.db_obj_list)

        self.ndb.command = info.db_command
        self.ndb.question = info.db_question
        
        return True


    def available_cmd_list(self, caller):
        """
        This returns a string of available commands.
        """
        command = ""
        if not self.ndb.command:
            command = "{lcloot %s{lt搜索%s{le" % (self.dbref, self.name)
        else:
            command = "{lcloot %s{lt%s{le" % (self.dbref, self.ndb.command)
        
        commands = [command]
        commands.extend(super(ObjectCreator, self).available_cmd_list(caller))
        return commands


    def give(self, caller):
        "Give objects."
        pass


#------------------------------------------------------------
#
# object provider - give all objects on the list
#
#------------------------------------------------------------
class ObjectProvider(ObjectCreator):
    """
    Give all objects on the list
    """

    def give(self, caller):
        """
        Give objects to the caller.
        """
        
        caller.msg(self.ndb.question)

        if not self.obj_list:
            # no objects
            caller.msg("没有可以获取的物品")
        else:
            # create objects in the list
            for obj_id in self.ndb.obj_list:
                # find object type's info
                matches = Object_Type_List.objects.filter(db_key=obj_id)
                if matches:
                    info = matches[0]
                    
                    new_obj = create_object(info.db_typeclass_path, location=self, home=self)
                    
                    if new_obj:
                        new_obj.set_type_id(obj_id)
                        
                        #move the object to the caller
                        if not new_obj.move_to(caller, quiet=True, emit_to_obj=caller):
                            new_obj.delete()
                        else:
                            caller.msg("你拿起了{w[%s]{n" % new_obj.key)

        commands = caller.get_available_cmd_desc(caller)
        if commands:
            caller.msg(commands + "\n")
        else:
            caller.msg("\n")


#------------------------------------------------------------
#
# object selector - selec an object on the list
#
#------------------------------------------------------------

class ObjectSelector(ObjectCreator):
    """
    Selec an object on the list.
    """
    def load_type_data(self):
        "Set object data from db."
        if not super(ObjectSelector, self).load_type_data():
            return False

        self.refresh_list()
        return True
    
    
    def refresh_list(self):
        """
        Refresh object's info.
        """
        keys = []
        names = []
        descs = []
        max_width = 0
        widths = []
        for obj_key in self.ndb.obj_list:
            matches = Object_Type_List.objects.filter(db_key=obj_key)
            
            name = ""
            desc = ""
            if matches:
                info = matches[0]
                name = info.db_name
                desc = info.db_desc
            else:
                print "OBJECT TYPE NOT FOUND!"
                name = "废品"
                desc = "这件物品已经损坏"
    
            keys.append(obj_key)
            names.append(name)
            descs.append(desc)
            
            width = len(utils.to_str(utils.to_unicode(name), encoding = "gbk"))
            widths.append(width)
            if max_width < width:
                max_width = width

        prompts = []
        for i in range(0, len(names)):
            space = " " * (max_width - widths[i] + 2)
            prompts.append(names[i] + space + descs[i])
        self.prompts = prompts

    
    def menu_selected(self, menu_node):
        """
        Choose an object.
        """
        if menu_node.key.isdigit():
            select = int(menu_node.key)
            if select > 0:
                obj_id = self.ndb.obj_list[select - 1]
                self.give_object(menu_node.caller, obj_id)
                return

        string = menu_node.caller.get_available_cmd_desc(menu_node.caller)
        menu_node.caller.msg(string)
                    
                    
    def give_object(self, caller, obj_id):
        """
        Give an object to the caller.
        """
        string = ""
        matches = Object_Type_List.objects.filter(db_key=obj_id)
        if matches:
            info = matches[0]
                    
            new_obj = create_object(info.db_typeclass_path, key="new object", location=self, home=self)
            if new_obj:
                new_obj.set_type_id(obj_id)
                
                #move the object to the caller
                if not new_obj.move_to(caller, quiet=True, emit_to_obj=caller):
                    new_obj.delete()
                else:
                    string += "你拿起了{w[%s]{n" % new_obj.key

        string += "\n " + caller.get_available_cmd_desc(caller)
        caller.msg(string)
            

    def give(self, caller):
        """
        Give an object to the caller. If there are several objects, ask the caller to choose one.
        """
        if not self.ndb.obj_list:
            # no objects
            string = "没有可以获取的物品。\n"
            string += caller.get_available_cmd_desc(caller)
            caller.msg(string)
        elif len(self.ndb.obj_list) == 1:
            # only one object
            self.give_object(caller, self.obj_list[0])
        else:
            # multi objects, choose one.
            prompt_choice(caller,
                          question=self.ndb.question,
                          prompts=self.prompts,
                          callback_func=self.menu_selected)

                         