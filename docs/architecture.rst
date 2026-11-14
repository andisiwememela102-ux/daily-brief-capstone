Architecture
============

Django project
--------------

``news_project`` contains the settings, root URL configuration, and WSGI/ASGI
entry points. ``manage.py`` is the command-line entry point. The ``news`` app
contains the newsroom domain, browser pages, API, role checks, and signals.

Core data
---------

- ``User`` extends Django's user model with Reader, Journalist, and Editor roles.
- ``Publisher`` groups journalists and editors and can have reader subscribers.
- ``Article`` belongs to exactly one journalist or publisher and is hidden from
  general feeds until an editor approves it.
- ``Newsletter`` groups approved articles under a journalist's account.
- ``ApprovedArticleLog`` stores an audit record from the internal integration.

Approval flow
-------------

Editors approve articles from the review page or API. A model signal detects the
transition to approved, emails eligible subscribers, and posts the article ID to
the internal approval endpoint. The endpoint checks a shared secret and creates
an idempotent log entry. Email and API integrations use safe local defaults;
production deployments should use HTTPS and private secrets.
