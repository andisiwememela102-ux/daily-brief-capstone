API reference
=============

All REST API routes require authentication unless the endpoint is listed as an
internal integration. The API uses Django REST Framework token or session
authentication.

Authentication
--------------

``POST /api/token/`` accepts a username and password and returns a token.

Articles
--------

- ``GET /api/articles/`` lists approved articles.
- ``POST /api/articles/`` lets a journalist create an independent article.
- ``GET /api/articles/subscribed/`` lists approved articles from a reader's
  subscribed journalists and publishers.
- ``GET /api/articles/<id>/`` retrieves an article visible to the current role.
- ``PUT`` or ``PATCH /api/articles/<id>/`` updates an article when role and
  ownership rules permit it.
- ``DELETE /api/articles/<id>/`` deletes an article when role and ownership
  rules permit it.
- ``POST /api/articles/<id>/approve/`` approves an article for editors.

Newsletters and directory
-------------------------

- ``GET /api/newsletters/`` lists newsletters with approved articles or no
  articles. Journalists and editors may create newsletters.
- ``GET /api/newsletters/<id>/`` retrieves a newsletter. Editors and its author
  may update or delete it.
- ``GET /api/publishers/`` lists publishers.
- ``GET /api/users/`` lists user profiles.

Internal approval integration
-----------------------------

``POST /api/approved/`` records an approved article. It is an internal endpoint
and requires an ``X-Approval-Secret`` header. The shared secret must remain
private and should be rotated for any deployment beyond local development.
