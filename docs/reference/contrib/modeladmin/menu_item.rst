======================================
Customising the menu item
======================================

You can use the following attributes and methods on the ``ModelAdmin`` class to
alter the menu item used to represent your model in Tuiuiu's admin area.

.. contents::
    :local:
    :depth: 1

.. _modeladmin_menu_label:

-------------------------
``ModelAdmin.menu_label``
-------------------------

**Expected value**: A string.

Set this attribute to a string value to override the label used for the menu
item that appears in Tuiuiu's sidebar. If not set, the menu item will use
``verbose_name_plural`` from your model's ``Meta`` data.

.. _modeladmin_menu_icon:

-------------------------
``ModelAdmin.menu_icon``
-------------------------

**Expected value**: A string matching one of Tuiuiu's icon class names.

If you want to change the icon used to represent your model, you can set the
``menu_icon`` attribute on your class to use one of the other icons available
in Tuiuiu's CMS. The same icon will be used for the menu item in Tuiuiu's
sidebar, and will also appear in the header on the list page and other views
for your model. If not set, ``'doc-full-inverse'`` will be used for
page-type models, and ``'snippet'`` for others.

If you're using a ``ModelAdminGroup`` class to group together several
``ModelAdmin`` classes in their own sub-menu, and want to change the menu item
used to represent the group, you should override the ``menu_icon`` attribute on
your ``ModelAdminGroup`` class (``'icon-folder-open-inverse'`` is the default).

.. _modeladmin_menu_order:

-------------------------
``ModelAdmin.menu_order``
-------------------------

**Expected value**: An integer between ``1`` and ``999``.

If you want to change the position of the menu item for your model (or group of
models) in Tuiuiu's sidebar, you do that by setting ``menu_order``. The value
should be an integer between ``1`` and ``999``. The lower the value, the higher
up the menu item will appear.

Tuiuiu's 'Explorer' menu item has an order value of ``100``, so supply a value
greater than that if you wish to keep the explorer menu item at the top.

.. _modeladmin_add_to_settings_menu:

-----------------------------------
``ModelAdmin.add_to_settings_menu``
-----------------------------------

**Expected value**: ``True`` or ``False``

If you'd like the menu item for your model to appear in Tuiuiu's 'Settings'
sub-menu instead of at the top level, add ``add_to_setings_menu = True`` to
your ``ModelAdmin`` class.

This will only work for indivdual ``ModelAdmin`` classes registered with their
own ``modeladmin_register`` call. It won't work for members of a
``ModelAdminGroup``.

