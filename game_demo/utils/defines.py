"""
define types
"""


#------------------------------------------------------------
# enum creater
#------------------------------------------------------------
def enum(**enums):
    """
    Define an enum type creater.
    usage:
        directions = enum(UP = 1, DOWN = 2)
        assert direction.UP == 1
        assert direction.DOWN == 2
    """
    return type('Enum', (object,), enums)
    
    
    
#------------------------------------------------------------
# Banding Types
#------------------------------------------------------------
BINDING_TYPE = enum(NONE = 0,
                    ON_EQUIP = 1,
                    ON_PICKUP = 2)
