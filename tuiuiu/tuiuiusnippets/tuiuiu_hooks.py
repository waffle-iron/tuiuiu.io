from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import urlresolvers
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from tuiuiu.tuiuiuadmin.menu import MenuItem
from tuiuiu.tuiuiucore import hooks
from tuiuiu.tuiuiusnippets import urls
from tuiuiu.tuiuiusnippets.models import get_snippet_models
from tuiuiu.tuiuiusnippets.permissions import user_can_edit_snippets


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^snippets/', include(urls, app_name='tuiuiusnippets', namespace='tuiuiusnippets')),
    ]


class SnippetsMenuItem(MenuItem):
    def is_shown(self, request):
        return user_can_edit_snippets(request.user)


@hooks.register('register_admin_menu_item')
def register_snippets_menu_item():
    return SnippetsMenuItem(
        _('Snippets'),
        urlresolvers.reverse('tuiuiusnippets:index'),
        classnames='icon icon-snippet',
        order=500
    )


@hooks.register('insert_editor_js')
def editor_js():
    return format_html(
        """
            <script src="{0}"></script>
            <script>window.chooserUrls.snippetChooser = '{1}';</script>
        """,
        static('tuiuiusnippets/js/snippet-chooser.js'),
        urlresolvers.reverse('tuiuiusnippets:choose_generic')
    )


@hooks.register('register_permissions')
def register_permissions():
    content_types = ContentType.objects.get_for_models(*get_snippet_models()).values()
    return Permission.objects.filter(content_type__in=content_types)
