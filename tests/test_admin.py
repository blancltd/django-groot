from __future__ import unicode_literals

from django.contrib.admin import AdminSite
from django.test import TestCase

from .admin import AuthorAdmin
from .models import Author


class TestGetGrootPermissions(TestCase):
    def setUp(self):
        self.site = AdminSite(name='admin')

    def test_default_perms(self):
        self.site.register(Author, AuthorAdmin)
        author_admin = self.site._registry[Author]

        permissions = author_admin.get_groot_permissions(request=None)

        self.assertListEqual(
            list(permissions.values_list('codename', flat=True)),
            ['add_author', 'change_author', 'delete_author'],
        )

    def test_limited_perms(self):
        self.site.register(Author, AuthorAdmin, groot_permissions=('add_author',))
        author_admin = self.site._registry[Author]

        permissions = author_admin.get_groot_permissions(request=None)

        self.assertListEqual(
            list(permissions.values_list('codename', flat=True)), ['add_author'],
        )
