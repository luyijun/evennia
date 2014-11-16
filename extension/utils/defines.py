"""
define types
"""


#------------------------------------------------------------
# enum creator
#------------------------------------------------------------
def enum(**enums):
    """
    Define an enum type creator.
    usage:
        directions = enum(UP = 1, DOWN = 2)
        assert direction.UP == 1
        assert direction.DOWN == 2
    """
    return type('Enum', (object,), enums)
    

#------------------------------------------------------------
# Object Catagory
#------------------------------------------------------------
OBJECT_CATE = enum(COMMON = 0,
                   CREATOR = 1,
                   PORTABLE = 2)

    
#------------------------------------------------------------
# Banding Types
#------------------------------------------------------------
BINDING_TYPE = enum(NONE = 0,
                    ON_PICKUP = 1,
                    ON_EQUIP = 2)
