from django.contrib import admin
from models import Object_Type_List

# Register your models here.

class ObjectTypeListAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_key', 'db_name', 'db_typeclass_path', 'db_bind_type', 'db_unique')


admin.site.register(Object_Type_List, ObjectTypeListAdmin)