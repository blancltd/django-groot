from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ugettext_lazy
from guardian.shortcuts import assign_perm, remove_perm

from .forms import get_permission_form


def update_permissions(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Only allow superusers to edit permissions
    if not request.user.is_superuser:
        raise PermissionDenied

    PermissionForm = get_permission_form(modeladmin.model)
    form = PermissionForm()

    # The user has confirmed the update
    if request.POST.get('post'):
        form = PermissionForm(request.POST)

        if form.is_valid():
            groups = form.cleaned_data['groups']
            permissions = form.cleaned_data['permissions']

            # Can be either add or remove varying on button
            if request.POST.get('remove_permissions'):
                update_perm = remove_perm
            else:
                update_perm = assign_perm

            for obj in queryset:
                for group in groups:
                    for permission in permissions:
                        update_perm(perm=permission, user_or_group=group, obj=obj)

            modeladmin.message_user(request, _((
                'Successfully updated permissions for %(group_count)d %(groups)s on '
                '%(obj_count)d %(items)s.')
            ) % {
                'group_count': len(groups),
                'obj_count': queryset.count(),
                'groups': model_ngettext(Group, n=len(groups)),
                'items': model_ngettext(queryset),
            }, messages.SUCCESS)

            # Display change list page again
            return None

    adminForm = helpers.AdminForm(
        form=form,
        fieldsets=[(None, {'fields': form.base_fields})],
        prepopulated_fields={},
        model_admin=modeladmin)

    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)

    context = modeladmin.admin_site.each_context(request)

    context.update({
        'title': _('Update permissions'),
        'adminform': adminForm,
        'objects_name': objects_name,
        'queryset': queryset,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
        'form': form,
    })

    request.current_app = modeladmin.admin_site.name

    template_name = getattr(modeladmin, 'update_permissions_template', None) or [
        'admin/%s/%s/update_permissions.html' % (app_label, opts.model_name),
        'admin/%s/update_permissions.html' % app_label,
        'admin/update_permissions.html'
    ]

    # Display the form page
    return TemplateResponse(request, template_name, context)

update_permissions.short_description = ugettext_lazy('Update %(verbose_name)s permissions')
