from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active')
    search_fields = ( 'email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'email', 'first_name', 'last_name', 'phone_number','image' ,'password1', 'password2')}
        ),
    )
   
   
admin.site.register(User, CustomUserAdmin)