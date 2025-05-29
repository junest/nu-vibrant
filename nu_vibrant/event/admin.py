from django.contrib import admin
from .models import EventRecord
from .registry import event_types


class EventTypeListFilter(admin.SimpleListFilter):
    title = 'event type'
    parameter_name = 'event_type'
    
    def lookups(self, request, model_admin):
        # Get all registered event types for the filter
        lookups = []
        for key, info in event_types.get_event_types().items():
            lookups.append((key, info['name']))
        return sorted(lookups)
    
    def queryset(self, request, queryset):
        if self.value():
            module, event_type = self.value().split('.')
            return queryset.filter(module=module, event_type=event_type)
        return queryset


@admin.register(EventRecord)
class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('get_event_name', 'user', 'created', 'description')
    list_filter = ('module', EventTypeListFilter, 'created')
    search_fields = ('description', 'user__username', 'data')
    readonly_fields = ('created', 'modified')
    date_hierarchy = 'created'
    
    def get_event_name(self, obj):
        event_info = event_types.get_event_type(obj.module, obj.event_type)
        if event_info:
            return event_info['name']
        return f"{obj.module}.{obj.event_type}"
    get_event_name.short_description = 'Event Type'