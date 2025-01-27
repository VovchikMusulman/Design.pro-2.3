from django.contrib import admin
from .models import Request

class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'category')
    actions = ['mark_as_accepted', 'mark_as_completed']

    def mark_as_accepted(self, request, queryset):
        queryset.update(status='Принято в работу')

    def mark_as_completed(self, request, queryset):
        queryset.update(status='Выполнено')

    mark_as_accepted.short_description = 'Mark selected requests as Accepted'
    mark_as_completed.short_description = 'Mark selected requests as Completed'

admin.site.register(Request, RequestAdmin)