.. image:: https://cloud.githubusercontent.com/assets/448775/18818105/10d88b0c-8369-11e6-8155-b3c18b617c7c.png
   :alt: Groot
   :align: right
   
Django Groot
============

An alternative admin interface for managing group permissions with
`django-guardian <https://github.com/django-guardian/django-guardian>`__.
Groot requires django-guardian for maintaining permissions, however
Groot only focuses on groups for object permissions - per user object
level permissions aren't allowed for simplicity.

Groot is named after a team discussion about the best 'guardian' in the
galaxy!

Installation
------------

Using `pip <https://pip.pypa.io/>`__:

.. code:: console

    $ pip install django-groot

Follow the instructions for installing
`django-guardian <https://github.com/django-guardian/django-guardian>`__
if you haven't already.

Edit your Django project's settings module, and add ``groot``:

.. code:: python

    INSTALLED_APPS = [
        # ...
        'groot',
    ]

Usage
-----

Add ``GrootAdminMixin`` to the admin class you want Groot to be used on:

.. code:: python

    from django.contrib import admin
    from groot.admin import GrootAdminMixin

    from .models import Post


    @admin.register(Post)
    class PostAdmin(GrootAdminMixin, BasePageAdmin):
        pass

