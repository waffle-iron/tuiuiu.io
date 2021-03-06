from __future__ import absolute_import, unicode_literals

import posixpath
from collections import defaultdict

from django import VERSION as DJANGO_VERSION
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField, Q
from django.db.models.functions import Length, Substr
from treebeard.mp_tree import MP_NodeQuerySet

from tuiuiu.tuiuiusearch.queryset import SearchableQuerySetMixin


class TreeQuerySet(MP_NodeQuerySet):
    """
    Extends Treebeard's MP_NodeQuerySet with additional useful tree-related operations.
    """
    def descendant_of_q(self, other, inclusive=False):
        q = Q(path__startswith=other.path) & Q(depth__gte=other.depth)

        if not inclusive:
            q &= ~Q(pk=other.pk)

        return q

    def descendant_of(self, other, inclusive=False):
        """
        This filters the QuerySet to only contain pages that descend from the specified page.

        If inclusive is set to True, it will also contain the page itself (instead of just its descendants).
        """
        return self.filter(self.descendant_of_q(other, inclusive))

    def not_descendant_of(self, other, inclusive=False):
        """
        This filters the QuerySet to not contain any pages that descend from the specified page.

        If inclusive is set to True, it will also exclude the specified page.
        """
        return self.exclude(self.descendant_of_q(other, inclusive))

    def child_of_q(self, other):
        return self.descendant_of_q(other) & Q(depth=other.depth + 1)

    def child_of(self, other):
        """
        This filters the QuerySet to only contain pages that are direct children of the specified page.
        """
        return self.filter(self.child_of_q(other))

    def not_child_of(self, other):
        """
        This filters the QuerySet to not contain any pages that are direct children of the specified page.
        """
        return self.exclude(self.child_of_q(other))

    def ancestor_of_q(self, other, inclusive=False):
        paths = [
            other.path[0:pos]
            for pos in range(0, len(other.path) + 1, other.steplen)[1:]
        ]
        q = Q(path__in=paths)

        if not inclusive:
            q &= ~Q(pk=other.pk)

        return q

    def ancestor_of(self, other, inclusive=False):
        """
        This filters the QuerySet to only contain pages that are ancestors of the specified page.

        If inclusive is set to True, it will also include the specified page.
        """
        return self.filter(self.ancestor_of_q(other, inclusive))

    def not_ancestor_of(self, other, inclusive=False):
        """
        This filters the QuerySet to not contain any pages that are ancestors of the specified page.

        If inclusive is set to True, it will also exclude the specified page.
        """
        return self.exclude(self.ancestor_of_q(other, inclusive))

    def parent_of_q(self, other):
        return Q(path=self.model._get_parent_path_from_path(other.path))

    def parent_of(self, other):
        """
        This filters the QuerySet to only contain the parent of the specified page.
        """
        return self.filter(self.parent_of_q(other))

    def not_parent_of(self, other):
        """
        This filters the QuerySet to exclude the parent of the specified page.
        """
        return self.exclude(self.parent_of_q(other))

    def sibling_of_q(self, other, inclusive=True):
        q = Q(path__startswith=self.model._get_parent_path_from_path(other.path)) & Q(depth=other.depth)

        if not inclusive:
            q &= ~Q(pk=other.pk)

        return q

    def sibling_of(self, other, inclusive=True):
        """
        This filters the QuerySet to only contain pages that are siblings of the specified page.

        By default, inclusive is set to True so it will include the specified page in the results.

        If inclusive is set to False, the page will be excluded from the results.
        """
        return self.filter(self.sibling_of_q(other, inclusive))

    def not_sibling_of(self, other, inclusive=True):
        """
        This filters the QuerySet to not contain any pages that are siblings of the specified page.

        By default, inclusive is set to True so it will exclude the specified page from the results.

        If inclusive is set to False, the page will be included in the results.
        """
        return self.exclude(self.sibling_of_q(other, inclusive))


class PageQuerySet(SearchableQuerySetMixin, TreeQuerySet):
    def live_q(self):
        return Q(live=True)

    def live(self):
        """
        This filters the QuerySet to only contain published pages.
        """
        return self.filter(self.live_q())

    def not_live(self):
        """
        This filters the QuerySet to only contain unpublished pages.
        """
        return self.exclude(self.live_q())

    def in_menu_q(self):
        return Q(show_in_menus=True)

    def in_menu(self):
        """
        This filters the QuerySet to only contain pages that are in the menus.
        """
        return self.filter(self.in_menu_q())

    def not_in_menu(self):
        """
        This filters the QuerySet to only contain pages that are not in the menus.
        """
        return self.exclude(self.in_menu_q())

    def page_q(self, other):
        return Q(id=other.id)

    def page(self, other):
        """
        This filters the QuerySet so it only contains the specified page.
        """
        return self.filter(self.page_q(other))

    def not_page(self, other):
        """
        This filters the QuerySet so it doesn't contain the specified page.
        """
        return self.exclude(self.page_q(other))

    def type_q(self, klass):
        content_types = ContentType.objects.get_for_models(*[
            model for model in apps.get_models()
            if issubclass(model, klass)
        ]).values()

        return Q(content_type__in=content_types)

    def type(self, model):
        """
        This filters the QuerySet to only contain pages that are an instance
        of the specified model (including subclasses).
        """
        return self.filter(self.type_q(model))

    def not_type(self, model):
        """
        This filters the QuerySet to not contain any pages which are an instance of the specified model.
        """
        return self.exclude(self.type_q(model))

    def exact_type_q(self, klass):
        return Q(content_type=ContentType.objects.get_for_model(klass))

    def exact_type(self, model):
        """
        This filters the QuerySet to only contain pages that are an instance of the specified model
        (matching the model exactly, not subclasses).
        """
        return self.filter(self.exact_type_q(model))

    def not_exact_type(self, model):
        """
        This filters the QuerySet to not contain any pages which are an instance of the specified model
        (matching the model exactly, not subclasses).
        """
        return self.exclude(self.exact_type_q(model))

    def public_q(self):
        from tuiuiu.tuiuiucore.models import PageViewRestriction

        q = Q()
        for restriction in PageViewRestriction.objects.all():
            q &= ~self.descendant_of_q(restriction.page, inclusive=True)
        return q

    def public(self):
        """
        This filters the QuerySet to only contain pages that are not in a private section
        """
        return self.filter(self.public_q())

    def not_public(self):
        """
        This filters the QuerySet to only contain pages that are in a private section
        """
        return self.exclude(self.public_q())

    def first_common_ancestor(self, include_self=False, strict=False):
        """
        Find the first ancestor that all pages in this queryset have in common.
        For example, consider a page heirarchy like::

            - Home/
                - Foo Event Index/
                    - Foo Event Page 1/
                    - Foo Event Page 2/
                - Bar Event Index/
                    - Bar Event Page 1/
                    - Bar Event Page 2/

        The common ancestors for some queries would be:

        .. code-block:: python

            >>> Page.objects\\
            ...     .type(EventPage)\\
            ...     .first_common_ancestor()
            <Page: Home>
            >>> Page.objects\\
            ...     .type(EventPage)\\
            ...     .filter(title__contains='Foo')\\
            ...     .first_common_ancestor()
            <Page: Foo Event Index>

        This method tries to be efficient, but if you have millions of pages
        scattered across your page tree, it will be slow.

        If `include_self` is True, the ancestor can be one of the pages in the
        queryset:

        .. code-block:: python

            >>> Page.objects\\
            ...     .filter(title__contains='Foo')\\
            ...     .first_common_ancestor()
            <Page: Foo Event Index>
            >>> Page.objects\\
            ...     .filter(title__exact='Bar Event Index')\\
            ...     .first_common_ancestor()
            <Page: Bar Event Index>

        A few invalid cases exist: when the queryset is empty, when the root
        Page is in the queryset and ``include_self`` is False, and when there
        are multiple page trees with no common root (a case Tuiuiu does not
        support). If ``strict`` is False (the default), then the first root
        node is returned in these cases. If ``strict`` is True, then a
        ``ObjectDoesNotExist`` is raised.
        """
        # An empty queryset has no ancestors. This is a problem
        if not self.exists():
            if strict:
                raise self.model.DoesNotExist('Can not find ancestor of empty queryset')
            return self.model.get_first_root_node()

        if include_self:
            # Get all the paths of the matched pages.
            paths = self.order_by().values_list('path', flat=True)
        else:
            # Find all the distinct parent paths of all matched pages.
            # The empty `.order_by()` ensures that `Page.path` is not also
            # selected to order the results, which makes `.distinct()` works.
            paths = self.order_by()\
                .annotate(parent_path=Substr(
                    'path', 1, Length('path') - self.model.steplen,
                    output_field=CharField(max_length=255)))\
                .values_list('parent_path', flat=True)\
                .distinct()

        # This method works on anything, not just file system paths.
        common_parent_path = posixpath.commonprefix(paths)

        # That may have returned a path like (0001, 0002, 000), which is
        # missing some chars off the end. Fix this by trimming the path to a
        # multiple of `Page.steplen`
        extra_chars = len(common_parent_path) % self.model.steplen
        if extra_chars != 0:
            common_parent_path = common_parent_path[:-extra_chars]

        if common_parent_path is '':
            # This should only happen when there are multiple trees,
            # a situation that Tuiuiu does not support;
            # or when the root node itself is part of the queryset.
            if strict:
                raise self.model.DoesNotExist('No common ancestor found!')

            # Assuming the situation is the latter, just return the root node.
            # The root node is not its own ancestor, so this is technically
            # incorrect. If you want very correct operation, use `strict=True`
            # and receive an error.
            return self.model.get_first_root_node()

        # Assuming the database is in a consistent state, this page should
        # *always* exist. If your database is not in a consistent state, you've
        # got bigger problems.
        return self.model.objects.get(path=common_parent_path)

    def unpublish(self):
        """
        This unpublishes all live pages in the QuerySet.
        """
        for page in self.live():
            page.unpublish()

    def specific(self):
        """
        This efficiently gets all the specific pages for the queryset, using
        the minimum number of queries.
        """
        if DJANGO_VERSION >= (1, 9):
            clone = self._clone()
            clone._iterable_class = SpecificIterable
            return clone
        else:
            return self._clone(klass=SpecificQuerySet)

    def in_site(self, site):
        """
        This filters the QuerySet to only contain pages within the specified site.
        """
        return self.descendant_of(site.root_page, inclusive=True)


def specific_iterator(qs):
    """
    This efficiently iterates all the specific pages in a queryset, using
    the minimum number of queries.

    This should be called from ``PageQuerySet.specific``
    """
    pks_and_types = qs.values_list('pk', 'content_type')
    pks_by_type = defaultdict(list)
    for pk, content_type in pks_and_types:
        pks_by_type[content_type].append(pk)

    # Content types are cached by ID, so this will not run any queries.
    content_types = {pk: ContentType.objects.get_for_id(pk)
                     for _, pk in pks_and_types}

    # Get the specific instances of all pages, one model class at a time.
    pages_by_type = {}
    for content_type, pks in pks_by_type.items():
        model = content_types[content_type].model_class()
        pages = model.objects.filter(pk__in=pks)
        pages_by_type[content_type] = {page.pk: page for page in pages}

    # Yield all of the pages, in the order they occurred in the original query.
    for pk, content_type in pks_and_types:
        yield pages_by_type[content_type][pk]


# Django 1.9 changed how extending QuerySets with different iterators behaved
# considerably, in a way that is not easily compatible between the two versions
if DJANGO_VERSION >= (1, 9):
    from django.db.models.query import BaseIterable

    class SpecificIterable(BaseIterable):
        def __iter__(self):
            return specific_iterator(self.queryset)

else:
    from django.db.models.query import QuerySet

    class SpecificQuerySet(QuerySet):
        iterator = specific_iterator
