from django.contrib import admin
from .models import CustomUser,Department

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'designation', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)