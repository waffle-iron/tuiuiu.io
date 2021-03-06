.. _pages-theory:

======
Theory
======


Introduction to Trees
~~~~~~~~~~~~~~~~~~~~~

If you're unfamiliar with trees as an abstract data type, you might want to `review the concepts involved. <http://en.wikipedia.org/wiki/Tree_(data_structure)>`_

As a web developer, though, you probably already have a good understanding of trees as filesystem directories or paths. Tuiuiu pages can create the same structure, as each page in the tree has its own URL path, like so::

    /
        people/
            nien-nunb/
            laura-roslin/
        events/
            captain-picard-day/
            winter-wrap-up/

The Tuiuiu admin interface uses the tree to organize content for editing, letting you navigate up and down levels in the tree through its Explorer menu. This method of organization is a good place to start in thinking about your own Tuiuiu models.


Nodes and Leaves
----------------

It might be handy to think of the ``Page``-derived models you want to create as being one of two node types: parents and leaves. Tuiuiu isn't prescriptive in this approach, but it's a good place to start if you're not experienced in structuring your own content types.


Nodes
`````
Parent nodes on the Tuiuiu tree probably want to organize and display a browse-able index of their descendants. A blog, for instance, needs a way to show a list of individual posts.

A Parent node could provide its own function returning its descendant objects.

.. code-block:: python

    class EventPageIndex(Page):
        # ...
        def events(self):
            # Get list of live event pages that are descendants of this page
            events = EventPage.objects.live().descendant_of(self)

            # Filter events list to get ones that are either
            # running now or start in the future
            events = events.filter(date_from__gte=date.today())

            # Order by date
            events = events.order_by('date_from')

            return events

This example makes sure to limit the returned objects to pieces of content which make sense, specifically ones which have been published through Tuiuiu's admin interface (``live()``) and are children of this node (``descendant_of(self)``). By setting a ``subpage_types`` class property in your model, you can specify which models are allowed to be set as children, and by setting a ``parent_page_types`` class property, you can specify which models are allowed to be parents of this page model. Tuiuiu will allow any ``Page``-derived model by default. Regardless, it's smart for a parent model to provide an index filtered to make sense.


Leaves
``````
Leaves are the pieces of content itself, a page which is consumable, and might just consist of a bunch of properties. A blog page leaf might have some body text and an image. A person page leaf might have a photo, a name, and an address.

It might be helpful for a leaf to provide a way to back up along the tree to a parent, such as in the case of breadcrumbs navigation. The tree might also be deep enough that a leaf's parent won't be included in general site navigation.

The model for the leaf could provide a function that traverses the tree in the opposite direction and returns an appropriate ancestor:

.. code-block:: python

    class EventPage(Page):
        # ...
        def event_index(self):
            # Find closest ancestor which is an event index
            return self.get_ancestors().type(EventIndexPage).last()

If defined, ``subpage_types`` and ``parent_page_types`` will also limit the parent models allowed to contain a leaf. If not, Tuiuiu will allow any combination of parents and leafs to be associated in the Tuiuiu tree. Like with index pages, it's a good idea to make sure that the index is actually of the expected model to contain the leaf.


Other Relationships
```````````````````
Your ``Page``-derived models might have other interrelationships which extend the basic Tuiuiu tree or depart from it entirely. You could provide functions to navigate between siblings, such as a "Next Post" link on a blog page (``post->post->post``). It might make sense for subtrees to interrelate, such as in a discussion forum (``forum->post->replies``) Skipping across the hierarchy might make sense, too, as all objects of a certain model class might interrelate regardless of their ancestors (``events = EventPage.objects.all``). It's largely up to the models to define their interrelations, the possibilities are really endless.


.. _anatomy_of_a_tuiuiu_request:

Anatomy of a Tuiuiu Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For going beyond the basics of model definition and interrelation, it might help to know how Tuiuiu handles requests and constructs responses. In short, it goes something like:

    #.  Django gets a request and routes through Tuiuiu's URL dispatcher definitions
    #.  Tuiuiu checks the hostname of the request to determine which ``Site`` record will handle this request.
    #.  Starting from the root page of that site, Tuiuiu traverses the page tree, calling the ``route()`` method and letting each page model decide whether it will handle the request itself or pass it on to a child page.
    #.  The page responsible for handling the request returns a ``RouteResult`` object from ``route()``, which identifies the page along with any additional ``args``/``kwargs`` to be passed to ``serve()``.
    #.  Tuiuiu calls ``serve()``, which constructs a context using ``get_context()``
    #.  ``serve()`` finds a template to pass it to using ``get_template()``
    #.  A response object is returned by ``serve()`` and Django responds to the requester.

You can apply custom behavior to this process by overriding ``Page`` class methods such as ``route()`` and ``serve()`` in your own models. For examples, see :ref:`model_recipes`.
