The Daily Brief
===============

The Daily Brief is a Django newsroom platform for independent journalists,
publishers, editors, and readers. It supports role-based publishing, editorial
approval, subscriptions, newsletters, email distribution, and a REST API.

This documentation covers local setup, the application's structure, API routes,
and the Python modules that implement the project. Build the HTML site from the
project root with::

   .venv/Scripts/sphinx-build -b html docs docs/_build/html

The generated site is stored in ``docs/_build/html`` and is included in the
repository for convenient browsing.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getting_started
   architecture
   api
   modules
