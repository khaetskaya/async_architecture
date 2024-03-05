from users.models import User

from django.contrib import admin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = list_display = ('email', 'first_name', 'last_name', 'role', 'public_id', 'username')
