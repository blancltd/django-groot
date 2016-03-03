from django.core.urlresolvers import reverse

from django_webtest import WebTest
from guardian.shortcuts import assign_perm

from .base import GrootTestMixin
from .models import Author


class TestAccessGroupPermissions(GrootTestMixin, WebTest):
    def setUp(self):
        super(TestAccessGroupPermissions, self).setUp()

        author = Author.objects.create(name='Author')
        opts = author._meta.app_label, author._meta.model_name

        self.groot_url = reverse('admin:%s_%s_groot' % opts, args=(author.id,))

    def test_superuser(self):
        response = self.app.get(self.groot_url, user='superuser')
        self.assertEqual(response.status_code, 200)

    def test_staff(self):
        self.app.get(self.groot_url, user='staff', status=403)

    def test_user(self):
        response = self.app.get(self.groot_url, user='user1')
        self.assertEqual(response.status_code, 302)

    def test_anon(self):
        response = self.app.get(self.groot_url)
        self.assertEqual(response.status_code, 302)


class TestUpdatePermissions(GrootTestMixin, WebTest):
    def setUp(self):
        super(TestUpdatePermissions, self).setUp()

        self.author = Author.objects.create(name='Author')
        opts = self.author._meta.app_label, self.author._meta.model_name

        self.groot_url = reverse('admin:%s_%s_groot' % opts, args=(self.author.id,))

        # Assign existing permissions to Gamma
        assign_perm('add_author', self.group_gamma, self.author)
        assign_perm('change_author', self.group_gamma, self.author)
        assign_perm('delete_author', self.group_gamma, self.author)

    def test_update_perms(self):
        groot = self.app.get(self.groot_url, user='superuser')
        form = groot.forms['group-permissions']

        # Alpha - add author
        form['form-0-perm_add_author'] = True

        # Beta - change author
        form['form-1-perm_change_author'] = True

        # Gamma - remove all permissions
        form['form-2-perm_add_author'] = None
        form['form-2-perm_change_author'] = None
        form['form-2-perm_delete_author'] = None

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)

        # Test appropriate permissions
        self.assertTrue(self.user1.has_perm('tests.add_author', obj=self.author))
        self.assertTrue(self.user1.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user1.has_perm('tests.delete_author', obj=self.author))

        self.assertTrue(self.user2.has_perm('tests.add_author', obj=self.author))
        self.assertFalse(self.user2.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user2.has_perm('tests.delete_author', obj=self.author))

        self.assertFalse(self.user3.has_perm('tests.add_author', obj=self.author))
        self.assertFalse(self.user3.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user3.has_perm('tests.delete_author', obj=self.author))
