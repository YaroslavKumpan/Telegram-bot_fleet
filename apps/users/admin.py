# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
import uuid
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'role', 'telegram_id', 'invite_code', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'telegram_id')
    ordering = ('username',)

    # Важно: добавляем invite_code в fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Telegram'), {'fields': ('role', 'telegram_id', 'invite_code')}),
    )

    # Для формы создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'invite_code'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # При создании нового пользователя генерируем invite_code
        if not obj and 'invite_code' in form.base_fields:
            form.base_fields['invite_code'].initial = uuid.uuid4()
        return form

    def save_model(self, request, obj, form, change):
        # Если пользователь не директор, запрещаем вход в админку
        if obj.role != User.Role.DIRECTOR:
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)