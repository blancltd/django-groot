from django.contrib.auth.models import Group, User


class GrootTestMixin(object):
    def setUp(self):
        # Super user - all permissions
        self.superuser = User.objects.create_superuser(
            username='superuser', password='superuser', email='')

        # Staff - admin access without the ability to edit permissions
        self.staff = User.objects.create_user(username='staff', password='staff')
        self.staff.is_staff = True
        self.staff.save()

        # Groups
        self.group_alpha = Group.objects.create(name='Alpha')
        self.group_beta = Group.objects.create(name='Beta')
        self.group_gamma = Group.objects.create(name='Gamma')

        # Users
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.user2 = User.objects.create_user(username='user2', password='user2')
        self.user3 = User.objects.create_user(username='user3', password='user3')

        # Assign groups
        self.user1.groups.add(self.group_alpha)
        self.user1.groups.add(self.group_beta)
        self.user2.groups.add(self.group_alpha)
        self.user3.groups.add(self.group_gamma)
