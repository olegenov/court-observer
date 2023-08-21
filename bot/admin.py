from django.contrib import admin
 
from .models import Case, Entity, Observation


class CaseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'number', 'entity') 
    search_fields = ('number', ) 
    empty_value_display = '-'


class EntityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', ) 
    search_fields = ('name', ) 
    empty_value_display = '-'


class ObservationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tg', 'entity') 
    search_fields = ('tg', ) 
    empty_value_display = '-'


admin.site.register(Case, CaseAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Observation, ObservationAdmin)