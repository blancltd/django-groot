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

        changelist_url = reverse('admin:%s_%s_changelist' % opts)
        changelist = self.app.get(changelist_url, user='superuser')

        # Pick the author, and try to update permissions
        self.form = changelist.forms['changelist-form']
        self.form['action'] = 'update_permissions'
        self.form.set('_selected_action', True, index=0)

    def test_superuser(self):
        response = self.form.submit(user='superuser')
        self.assertEqual(response.status_code, 200)

    def test_staff(self):
        self.form.submit(user='staff', status=403)

    def test_user(self):
        response = self.form.submit(user='user1')
        self.assertEqual(response.status_code, 302)

    def test_anon(self):
        # Logout the user to test this
        self.form.response.client.logout()
        response = self.form.submit()
        self.assertEqual(response.status_code, 302)


class TestUpdatePermissions(GrootTestMixin, WebTest):
    def setUp(self):
        super(TestUpdatePermissions, self).setUp()

        self.author = Author.objects.create(name='Author')
        opts = self.author._meta.app_label, self.author._meta.model_name

        changelist_url = reverse('admin:%s_%s_changelist' % opts)
        changelist = self.app.get(changelist_url, user='superuser')

        # Pick the author, and try to update permissions
        form = changelist.forms['changelist-form']
        form['action'] = 'update_permissions'
        form.set('_selected_action', True, index=0)
        self.update_permissions = form.submit()

    def test_add_permissions(self):
        form = self.update_permissions.forms['update-permissions']

        # Add/change permissions for group Alpha
        form['groups'] = [self.group_alpha.id]
        form.set('permissions', True, index=0)
        form.set('permissions', True, index=1)

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)

        # Test appropriate permissions
        self.assertTrue(self.user1.has_perm('tests.add_author', obj=self.author))
        self.assertTrue(self.user1.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user1.has_perm('tests.delete_author', obj=self.author))

        self.assertTrue(self.user2.has_perm('tests.add_author', obj=self.author))
        self.assertTrue(self.user2.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user2.has_perm('tests.delete_author', obj=self.author))

    def test_remove_permissions(self):
        # Assign existing permissions to Alpha
        assign_perm('add_author', self.group_alpha, self.author)
        assign_perm('change_author', self.group_alpha, self.author)
        assign_perm('delete_author', self.group_alpha, self.author)

        form = self.update_permissions.forms['update-permissions']

        # Remove delete permission from Alpha
        form['groups'] = [self.group_alpha.id]
        form.set('permissions', True, index=2)

        response = form.submit('remove_permissions').follow()
        self.assertEqual(response.status_code, 200)

        # Test appropriate permissions
        self.assertTrue(self.user1.has_perm('tests.add_author', obj=self.author))
        self.assertTrue(self.user1.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user1.has_perm('tests.delete_author', obj=self.author))

        self.assertTrue(self.user2.has_perm('tests.add_author', obj=self.author))
        self.assertTrue(self.user2.has_perm('tests.change_author', obj=self.author))
        self.assertFalse(self.user2.has_perm('tests.delete_author', obj=self.author))
