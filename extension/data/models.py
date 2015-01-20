from django.db import models
from src.utils.idmapper.models import SharedMemoryModel


#------------------------------------------------------------
#
# store all object types
#
#------------------------------------------------------------
class Object_Type_List(SharedMemoryModel):
    "store all object types"
    
    db_key = models.IntegerField(default=0)
    db_name = models.CharField(max_length=255)
    db_typeclass_path = models.CharField(max_length=255)
    db_desc = models.TextField(blank=True, default="")
    db_category = models.IntegerField(default=0)


    class Meta:
        "Define Django meta options"
        verbose_name = "Object Type List"
        verbose_name_plural = "Object Type List"


#------------------------------------------------------------
#
# store portable object types info
#
#------------------------------------------------------------
class Portable_Object_Types(SharedMemoryModel):
    "store portable object types info"
    
    db_key = models.IntegerField(default=0)
    db_bind_type = models.IntegerField(default=0)
    db_unique = models.BooleanField(default=False)


    class Meta:
        "Define Django meta options"
        verbose_name = "Portable Object Types"
        verbose_name_plural = "Portable Object Types"


#------------------------------------------------------------
#
# store object creator types info
#
#------------------------------------------------------------
class Object_Creator_Types(SharedMemoryModel):
    "store object creator types info"
    
    db_key = models.IntegerField(default=0)
    db_obj_list = models.TextField(blank=True, default="")
    db_command = models.CharField(max_length=255)
    db_question = models.TextField(blank=True, default="")


    class Meta:
        "Define Django meta options"
        verbose_name = "Object Creator Types"
        verbose_name_plural = "Object Creator Types"
