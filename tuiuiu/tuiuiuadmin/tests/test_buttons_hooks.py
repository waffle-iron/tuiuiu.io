from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from tuiuiu.tests.utils import TuiuiuTestUtils
from tuiuiu.tuiuiuadmin import widgets as tuiuiuadmin_widgets
from tuiuiu.tuiuiucore import hooks
from tuiuiu.tuiuiucore.models import Page


class TestButtonsHooks(TestCase, TuiuiuTestUtils):
    def setUp(self):
        self.root_page = Page.objects.get(id=2)
        self.login()

    def test_register_page_listing_buttons(self):
        @hooks.register('register_page_listing_buttons')
        def page_listing_buttons(page, page_perms, is_parent=False):
            yield tuiuiuadmin_widgets.PageListingButton(
                'Another useless page listing button',
                '/custom-url',
                priority=10
            )

        response = self.client.get(
            reverse('tuiuiuadmin_explore', args=(self.root_page.id, ))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_button_with_dropdown.html')
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_buttons.html')

        self.assertContains(response, 'Another useless page listing button')

    def test_register_page_listing_more_buttons(self):
        @hooks.register('register_page_listing_more_buttons')
        def page_listing_more_buttons(page, page_perms, is_parent=False):
            yield tuiuiuadmin_widgets.Button(
                'Another useless button in default "More" dropdown',
                '/custom-url',
                priority=10
            )

        response = self.client.get(
            reverse('tuiuiuadmin_explore', args=(self.root_page.id, ))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_button_with_dropdown.html')
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_buttons.html')

        self.assertContains(response, 'Another useless button in default &quot;More&quot; dropdown')

    def test_custom_button_with_dropdown(self):
        @hooks.register('register_page_listing_buttons')
        def page_custom_listing_buttons(page, page_perms, is_parent=False):
            yield tuiuiuadmin_widgets.ButtonWithDropdownFromHook(
                'One more more button',
                hook_name='register_page_listing_one_more_more_buttons',
                page=page,
                page_perms=page_perms,
                is_parent=is_parent,
                attrs={'target': '_blank'},
                priority=50
            )

        @hooks.register('register_page_listing_one_more_more_buttons')
        def page_custom_listing_more_buttons(page, page_perms, is_parent=False):
            yield tuiuiuadmin_widgets.Button(
                'Another useless dropdown button in "One more more button" dropdown',
                '/custom-url',
                priority=10
            )

        response = self.client.get(
            reverse('tuiuiuadmin_explore', args=(self.root_page.id, ))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_button_with_dropdown.html')
        self.assertTemplateUsed(response, 'tuiuiuadmin/pages/listing/_buttons.html')

        self.assertContains(response, 'One more more button')
        self.assertContains(response, 'Another useless dropdown button in &quot;One more more button&quot; dropdown')