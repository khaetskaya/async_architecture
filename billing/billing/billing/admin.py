from billing.models import User, Task, UserTransaction

from django.contrib import admin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = list_display = ('email', 'first_name', 'last_name', 'role', 'public_id', 'username')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fields = list_display = ('description', 'status', 'assignee')


@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    fields = list_display = ('user', 'debit', 'credit', 'reason', 'billing_cycle')
