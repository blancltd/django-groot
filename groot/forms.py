import django
from django import forms
from django.conf import settings
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from guardian.shortcuts import get_perms_for_model


class BasePermissionForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Group', is_stacked=False),
        required=True)
    permissions = forms.MultipleChoiceField()

    @property
    def media(self):
        form_media = super(BasePermissionForm, self).media
        jquery_prefix = 'vendor/jquery/' if django.VERSION >= (1, 9) else ''
        jquery_suffix = '' if settings.DEBUG else '.min'
        js = [
            '%sjquery%s.js' % (jquery_prefix, jquery_suffix),
            'jquery.init.js',
            'SelectBox.js',
            'SelectFilter2.js',
        ]
        return forms.Media(js=[static('admin/js/%s' % url) for url in js]) + form_media


def get_permission_form(model):
    class PermissionForm(BasePermissionForm):
        permissions = forms.MultipleChoiceField(
            choices=[(x.codename, x.name) for x in get_perms_for_model(model)], required=True,
            widget=forms.widgets.CheckboxSelectMultiple)

    return PermissionForm


class BaseGroupPermissionForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), required=True, widget=forms.widgets.HiddenInput)

    def clean_group(self):
        # Readonly field to avoid any changes
        if 'group' in self.changed_data:
            raise ValidationError("Can't change group")

        return self.cleaned_data['group']


def get_group_permission_form(model_perms):
    class GroupPermissionForm(BaseGroupPermissionForm):
        def __init__(self, *args, **kwargs):
            super(GroupPermissionForm, self).__init__(*args, **kwargs)

            for perm in model_perms:
                field_name = 'perm_%s' % (perm.codename,)
                self.fields[field_name] = forms.BooleanField(label=perm.name, required=False)

    return GroupPermissionForm
