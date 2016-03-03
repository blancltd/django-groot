from django.contrib import admin
from groot.admin import GrootAdminMixin

from .models import Author


class AuthorAdmin(GrootAdminMixin, admin.ModelAdmin):
    pass


site = admin.AdminSite(name='admin')
site.register(Author, AuthorAdmin)
