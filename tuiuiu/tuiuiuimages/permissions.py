from __future__ import absolute_import, unicode_literals

from tuiuiu.tuiuiucore.permission_policies.collections import CollectionOwnershipPermissionPolicy
from tuiuiu.tuiuiuimages import get_image_model
from tuiuiu.tuiuiuimages.models import Image

permission_policy = CollectionOwnershipPermissionPolicy(
    get_image_model(),
    auth_model=Image,
    owner_field_name='uploaded_by_user'
)
