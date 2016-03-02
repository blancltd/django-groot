Django Groot
============

An alternative admin interface for managing group permissions with
`django-guardian`_. Groot requires django-guardian for maintaining permissions,
however Groot only focuses on groups for object permissions - per user object
level permissions aren't allowed for simplicity.

.. _django-guardian: https://github.com/django-guardian/django-guardian

Installation
------------

Using pip_:

.. _pip: https://pip.pypa.io/

.. code-block:: console

    $ pip install django-groot

Follow the instructions for installing `django-guardian`_ if you haven't
already.

Edit your Django project's settings module, and add ``groot``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'groot',
    ]

Usage
-----

Add `GrootAdminMixin` to the admin class you want Groot to be used on:

.. code-block:: python

    from django.contrib import admin
    from groot.admin import GrootAdminMixin

    from .models import Post


    @admin.register(Post)
    class PostAdmin(GrootAdminMixin, BasePageAdmin):
        pass
