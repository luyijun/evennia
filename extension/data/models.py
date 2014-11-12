from django.db import models
from src.utils.idmapper.models import SharedMemoryModel

class Object_Type_List(SharedMemoryModel):
    "store all object types"
    
    db_key = models.CharField(max_length=255, db_index=True)
    db_name = models.CharField(max_length=255)
    db_typeclass_path = models.CharField(max_length=255)
    db_desc = models.TextField(blank=True)
    db_bind_type = models.IntegerField(blank=True, default=0)
    db_unique = models.BooleanField(blank=True, default=False)


    class Meta:
        "Define Django meta options"
        verbose_name = "Object Type List"
        verbose_name_plural = "Object Type List"