from __future__ import absolute_import, unicode_literals

import warnings

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import BaseCreateView, BaseDeleteView, BaseUpdateView
from django.views.generic.list import BaseListView

from tuiuiu.utils.deprecation import RemovedInTuiuiu113Warning
from tuiuiu.tuiuiuadmin import messages
from tuiuiu.tuiuiuadmin.utils import permission_denied


class PermissionCheckedMixin(object):
    """
    Mixin for class-based views to enforce permission checks according to
    a permission policy (see tuiuiu.tuiuiucore.permission_policies).

    To take advantage of this, subclasses should set the class property:
    * permission_policy (a policy object)
    and either of:
    * permission_required (an action name such as 'add', 'change' or 'delete')
    * any_permission_required (a list of action names - the user must have
      one or more of those permissions)
    """
    permission_policy = None
    permission_required = None
    any_permission_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.permission_policy is not None:

            if self.permission_required is not None:
                if not self.permission_policy.user_has_permission(
                    request.user, self.permission_required
                ):
                    return permission_denied(request)

            if self.any_permission_required is not None:
                if not self.permission_policy.user_has_any_permission(
                    request.user, self.any_permission_required
                ):
                    return permission_denied(request)

        return super(PermissionCheckedMixin, self).dispatch(request, *args, **kwargs)


class IndexView(PermissionCheckedMixin, TemplateResponseMixin, BaseListView):
    model = None
    header_icon = ''
    index_url_name = None
    add_url_name = None
    edit_url_name = None
    context_object_name = None
    any_permission_required = ['add', 'change', 'delete']
    template_name = None

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['can_add'] = (
            self.permission_policy is None or
            self.permission_policy.user_has_permission(self.request.user, 'add')
        )
        return context


class CreateView(PermissionCheckedMixin, TemplateResponseMixin, BaseCreateView):
    model = None
    form_class = None
    header_icon = ''
    index_url_name = None
    add_url_name = None
    edit_url_name = None
    template_name = 'tuiuiuadmin/generic/create.html'
    permission_required = 'add'
    success_message = None
    error_message = None

    def get_add_url(self):
        return reverse(self.add_url_name)

    def get_success_url(self):
        return reverse(self.index_url_name)

    def get_success_message(self, instance):
        if self.success_message is None:
            return None
        return self.success_message.format(instance)

    def get_error_message(self, instance):
        if self.error_message is None:
            return None
        return self.error_message

    def save_instance(self):
        """
        Called after the form is successfully validated - saves the object to the db
        and returns the new object. Override this to implement custom save logic.
        """
        return self.form.save()

    def form_valid(self, form):
        self.form = form
        self.object = self.save_instance()
        success_message = self.get_success_message(self.object)
        if success_message is not None:
            messages.success(self.request, success_message, buttons=[
                messages.button(reverse(self.edit_url_name, args=(self.object.id,)), _('Edit'))
            ])
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        error_message = self.get_error_message(self.object)
        if error_message is not None:
            messages.error(self.request, error_message)
        return super(CreateView, self).form_invalid(form)


class EditView(PermissionCheckedMixin, TemplateResponseMixin, BaseUpdateView):
    model = None
    form_class = None
    header_icon = ''
    index_url_name = None
    edit_url_name = None
    delete_url_name = None
    page_title = ugettext_lazy("Editing")
    context_object_name = None
    template_name = 'tuiuiuadmin/generic/edit.html'
    permission_required = 'change'
    delete_item_label = ugettext_lazy("Delete")
    success_message = None
    error_message = None

    @property
    def instance(self):
        warnings.warn(
            "instance attribute is deprecated, please use object instead",
            category=RemovedInTuiuiu113Warning
        )
        return self.object

    @instance.setter
    def instance(self, instance):
        warnings.warn(
            "instance attribute is deprecated, please use object instead",
            category=RemovedInTuiuiu113Warning
        )
        self.object = instance

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            self.kwargs['pk'] = self.args[0]
        return super(EditView, self).get_object(queryset)

    def get_queryset(self):
        return self.model.objects.all()

    def get_page_subtitle(self):
        return str(self.instance)

    def get_edit_url(self):
        return reverse(self.edit_url_name, args=(self.instance.id,))

    def get_delete_url(self):
        return reverse(self.delete_url_name, args=(self.instance.id,))

    def get_success_url(self):
        return reverse(self.index_url_name)

    def save_instance(self):
        """
        Called after the form is successfully validated - saves the object to the db.
        Override this to implement custom save logic.
        """
        return self.form.save()

    def get_success_message(self, instance):
        if self.success_message is None:
            return None
        return self.success_message.format(instance)

    def get_error_message(self, instance):
        if self.error_message is None:
            return None
        return self.error_message

    def form_valid(self, form):
        self.form = form
        self.object = self.save_instance()
        success_message = self.get_success_message(self.object)
        if success_message is not None:
            messages.success(self.request, success_message, buttons=[
                messages.button(reverse(self.edit_url_name, args=(self.object.id,)), _('Edit'))
            ])
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        error_message = self.get_error_message(self.object)
        if error_message is not None:
            messages.error(self.request, error_message)
        return super(EditView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['can_delete'] = (
            self.permission_policy is None or
            self.permission_policy.user_has_permission(self.request.user, 'delete')
        ),
        return context


class DeleteView(PermissionCheckedMixin, TemplateResponseMixin, BaseDeleteView):
    model = None
    header_icon = ''
    index_url_name = None
    delete_url_name = None
    template_name = 'tuiuiuadmin/generic/confirm_delete.html'
    context_object_name = None
    permission_required = 'delete'
    success_message = None

    @property
    def instance(self):
        warnings.warn(
            "instance attribute is deprecated, please use object instead",
            category=RemovedInTuiuiu113Warning
        )
        return self.object

    @instance.setter
    def instance(self, instance):
        warnings.warn(
            "instance attribute is deprecated, please use object instead",
            category=RemovedInTuiuiu113Warning
        )
        self.object = instance

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            self.kwargs['pk'] = self.args[0]
        return super(DeleteView, self).get_object(queryset)

    def get_success_url(self):
        return reverse(self.index_url_name)

    def get_queryset(self):
        return self.model.objects.all()

    def get_page_subtitle(self):
        return str(self.instance)

    def get_delete_url(self):
        return reverse(self.delete_url_name, args=(self.instance.id,))

    def get_success_message(self, instance):
        if self.success_message is None:
            return None
        return self.success_message.format(instance)

    def get_context_data(self, **kwargs):
        context = self.get_context()
        if context:
            warnings.warn(
                "get_context() method is deprecated, please use get_context_data() instead",
                category=RemovedInTuiuiu113Warning
            )
        kwargs.update(context)
        return super(DeleteView, self).get_context_data(**kwargs)

    def get_context(self):
        # Deprecated, use get_context_data instead.
        return {}

    def delete(self, request, *args, **kwargs):
        response = super(DeleteView, self).delete(request, *args, **kwargs)
        messages.success(request, self.success_message.format(self.object))
        return response