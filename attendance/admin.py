from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Topic, AttendanceEntry, Profile

admin.site.register(Profile)

class AttendanceEntryInline(admin.TabularInline):
    model = AttendanceEntry
    extra = 1

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1

class UserAdmin(BaseUserAdmin):
    inlines = [TopicInline]

class TopicAdmin(admin.ModelAdmin):
    inlines = [AttendanceEntryInline]
    list_display = ('title', 'created_at', 'user')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at', 'user')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Topic, TopicAdmin)
