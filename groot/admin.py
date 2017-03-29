from functools import update_wrapper

from django.contrib import messages
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import model_ngettext, unquote
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _
from guardian.shortcuts import assign_perm, get_groups_with_perms, remove_perm

from .actions import update_permissions
from .forms import get_group_permission_form


PERM_PREFIX = 'perm_'


class GrootAdminMixin(object):
    change_form_template = 'admin/groot_change_form.html'
    actions = [update_permissions]
    groot_permissions = ()

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        return [
            url(r'^(.+)/groot/$', wrap(self.groot_view), name='%s_%s_groot' % info),
        ] + super(GrootAdminMixin, self).get_urls()

    def get_groot_permissions(self, request):
        """
        Returns a list of permissions which can be edited as part of the Group Permissions page.
        """
        permission_content_type = ContentType.objects.get_for_model(self.model)
        permissions = Permission.objects.filter(content_type=permission_content_type)

        if self.groot_permissions:
            permissions = permissions.filter(codename__in=self.groot_permissions)

        return permissions

    @csrf_protect_m
    @transaction.atomic
    def groot_view(self, request, object_id):
        # Only allow superusers to edit permissions
        if not request.user.is_superuser:
            raise PermissionDenied

        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id),
            })

        opts = self.model._meta
        app_label = opts.app_label

        group_list = Group.objects.all()
        group_count = group_list.count()

        GroupPermissionForm = get_group_permission_form(
            model_perms=self.get_groot_permissions(request),
        )
        GroupPermissionFormSet = formset_factory(
            GroupPermissionForm, extra=0, min_num=group_count, validate_min=True,
            max_num=group_count)

        obj_group_perms = get_groups_with_perms(obj=obj, attach_perms=True)
        initial_data = []

        for group in group_list:
            try:
                group_perms = obj_group_perms[group]
            except KeyError:
                group_perms = []

            group_initial = {
                'group': group,
            }

            for perm in group_perms:
                field_name = '%s%s' % (PERM_PREFIX, perm)
                group_initial[field_name] = True

            initial_data.append(group_initial)

        formset = GroupPermissionFormSet(request.POST or None, initial=initial_data)

        if formset.is_valid():
            # The user has confirmed the update
            group_count = 0

            for form in formset.forms:
                # Only act on changed data
                if form.has_changed():
                    group_count += 1

                    for field in form.changed_data:
                        group = form.cleaned_data['group']
                        changed_perm = field.replace(PERM_PREFIX, '', 1)
                        add_perm = form.cleaned_data[field]

                        # Change perm action accordingly
                        if add_perm:
                            update_perm = assign_perm
                        else:
                            update_perm = remove_perm

                        update_perm(perm=changed_perm, user_or_group=group, obj=obj)

            if group_count:
                self.message_user(request, _((
                    'Successfully updated permissions for %(count)d %(groups)s.'
                )) % {
                    'count': group_count,
                    'groups': model_ngettext(Group, n=group_count),
                }, messages.SUCCESS)
            else:
                self.message_user(request, _('No permissions were updated.'), messages.INFO)

            return HttpResponseRedirect(request.path)

        context = self.admin_site.each_context(request)

        context.update({
            'title': _('Group permissions: %s') % force_text(obj),
            'object': obj,
            'opts': opts,
            'formset': formset,
            'group_formsets': zip(group_list, formset.forms),
        })

        request.current_app = self.admin_site.name

        template_name = getattr(self, 'group_permissions_template', None) or [
            'admin/%s/%s/group_permissions.html' % (app_label, opts.model_name),
            'admin/%s/group_permissions.html' % app_label,
            'admin/group_permissions.html'
        ]

        # Display the form page
        return TemplateResponse(request, template_name, context)
