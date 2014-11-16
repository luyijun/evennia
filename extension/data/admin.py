from django.contrib import admin
from models import Object_Type_List, Portable_Object_Types, Object_Creator_Types

# Register your models here.

class ObjectTypeListAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_key', 'db_name', 'db_category', 'db_typeclass_path', 'db_desc')


class PortableObjectTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_key', 'db_bind_type', 'db_unique')


class ObjectCreatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_key', 'db_obj_list', 'db_command', 'db_question')


admin.site.register(Object_Type_List, ObjectTypeListAdmin)
admin.site.register(Portable_Object_Types, PortableObjectTypesAdmin)
admin.site.register(Object_Creator_Types, ObjectCreatorAdmin)