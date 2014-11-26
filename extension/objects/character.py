# -*- coding: utf-8 -*-
"""

Template for Characters

Copy this module up one level and name it as you like, then
use it as a template to create your own Character class.

To make new logins default to creating characters
of your new type, change settings.BASE_CHARACTER_TYPECLASS to point to
your new class, e.g.

settings.BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.mychar.MyChar"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Character as DefaultCharacter
from object_common import ObjectCommon as Object


class Character(Object, DefaultCharacter):
    """
    The Character is like any normal Object (see example/object.py for
    a list of properties and methods), except it actually implements
    some of its hook methods to do some work:

    at_basetype_setup - always assigns the default_cmdset to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    def at_init(self):
        super(Character, self).at_init()
        
        # Clear target
        self.ndb.target = None
    
        # Set weapon.
        self.ndb.weapon = None
        items = self.contents
        if items:
            self.ndb.weapon = items[0]

    
    def at_hit(self, weapon, attacker, damage):
        if not self.ndb.target:
            self.ndb.target = attacker


    def available_cmd_list(self, pobject):
        """
        This returns a list of available commands.
        """
        if not self.ndb.target:
            return super(Character, self).available_cmd_list(pobject)

        commands = ["{lcfight %s{lt战斗！{le" % self.ndb.target.dbref]
        commands += super(Character, self).available_cmd_list(pobject)
        return commands
