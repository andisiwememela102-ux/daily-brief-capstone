Getting started
===============

Requirements
------------

- Python 3.10 or newer
- pip

Install and run locally
-----------------------

Create a virtual environment from the project root and install the packages::

   python -m venv .venv
   .venv/Scripts/activate
   python -m pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver

Open ``http://127.0.0.1:8000/`` for the site and
``http://127.0.0.1:8000/admin/`` for the administration interface. SQLite is
the default database, and Django's console email backend keeps development
messages in the server terminal.

Configuration
-------------

The application reads optional settings from environment variables. Copy
``.env.example`` to ``.env`` only when you need to customize them. The example
values are placeholders; use private values for ``DJANGO_SECRET_KEY`` and
``APPROVED_API_SECRET`` in real deployments. Do not commit ``.env``.

Set ``DB_ENGINE=mysql`` and provide the ``DB_*`` variables to use MariaDB. The
container workflow uses a persistent SQLite volume by default.

Build the Sphinx site
--------------------

With the project environment active, run::

   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser to browse the generated site.
