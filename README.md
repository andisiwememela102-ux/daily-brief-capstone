# The Daily Brief — Django News Application

A Django capstone project for independent journalists, publishers, editors and readers. It includes role-based access, subscriptions, editorial approval, email distribution, a REST API with token authentication, and automated API tests.

## 1. Functional requirements implemented

- Readers can browse approved articles and newsletters and subscribe to publishers and journalists.
- Journalists can create and manage their own independent articles and newsletters.
- Publishers can own publisher articles and have multiple editors and journalists assigned in the Django admin.
- Editors can review and approve submitted articles and manage articles/newsletters.
- Approval triggers subscriber email and a `requests` POST to `/api/approved/`, which records the approved article.
- DRF endpoints provide article, subscribed-article, newsletter, publisher and user data.
- Token authentication is available at `/api/token/`.
- Automated tests cover authentication, role access, subscriptions, article CRUD, newsletters and approval integration.

## 2. Roles and permissions

| Role | Read | Create | Update | Delete | Approve |
|---|---|---|---|---|---|
| Reader | Approved articles/newsletters | No | No | No | No |
| Journalist | Articles/newsletters | Yes | Own content | Own content | No |
| Editor | Articles/newsletters | No article creation through API | Yes | Yes | Yes |

Django groups named `Reader`, `Journalist`, and `Editor` are assigned automatically when a user is created. The corresponding model permissions are assigned to each group. API permissions additionally enforce role and object ownership.

## 3. Data model and normalisation

- `User` extends Django's `AbstractUser` and stores one role. Reader subscriptions are many-to-many relations, not duplicated text fields.
- `Publisher` stores publisher details. Its editor and journalist relationships are many-to-many, allowing multiple users in each role and multiple publisher affiliations.
- `Article` stores article-specific data and references either one journalist (`author`) or one publisher (`publisher`). A database check constraint enforces exactly one source.
- `Newsletter` references its author and has a many-to-many relation to articles.
- `ApprovedArticleLog` stores the internal API integration record separately from article content.

This separates users, publishers, articles, newsletters and approval logs into related tables and avoids repeating publisher/user/article data. Many-to-many relationships are represented by Django's join tables.

## 4. User interface plan

The web interface uses a responsive, simple newsroom layout: a shared navigation bar, latest-news cards, an article reading page, a newsletter listing, and a restricted editor review queue. Readers see published content; editors receive a review link; unauthenticated users can log in. Admin is available for managing users, publishers, roles and assignments.

## 5. Setup (Windows PowerShell)

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations news
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the site and `http://127.0.0.1:8000/admin/` for administration. The default email backend prints email messages to the terminal; this makes local development safe without SMTP credentials.

## 6. Create test users and content

Users can create accounts at `/register/` and choose Reader, Journalist, or Editor. The account is signed in immediately and added to the matching Django permission group. Administrators can also create users in Django admin. Add publishers, then assign editors and journalists on the publisher form. Add articles with either an author or publisher (never both). New articles start unapproved. Editors can approve them at `/editor/review/`. Readers can be subscribed to publishers and journalists from their user admin page.

For a journalist to create an independent article through the API, obtain a token and send:

```http
POST /api/articles/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{"title":"A newsroom update","content":"Article text"}
```

## 7. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Obtain DRF token using username/password |
| GET | `/api/articles/` | List approved articles |
| POST | `/api/articles/` | Journalist creates an independent article |
| GET | `/api/articles/subscribed/` | Reader's subscribed publishers/journalists only |
| GET | `/api/articles/<id>/` | Retrieve one article |
| PUT/PATCH | `/api/articles/<id>/` | Editor or owning journalist updates |
| DELETE | `/api/articles/<id>/` | Editor or owning journalist deletes |
| POST | `/api/articles/<id>/approve/` | Editor approves an article |
| GET/POST | `/api/newsletters/` | List/create newsletters |
| GET/PUT/PATCH/DELETE | `/api/newsletters/<id>/` | Retrieve/manage newsletter |
| GET | `/api/publishers/` | List publishers |
| GET | `/api/users/` | List users (authenticated) |
| POST | `/api/approved/` | Internal approval-log endpoint; requires `X-Approval-Secret` |

All API endpoints require authentication except the internal approval endpoint, which uses a shared secret header. Reader subscriptions are enforced by the subscribed endpoint. Only approved articles are returned by the public article list.

## 8. Email and approval integration

The `post_save` signal detects the transition from unapproved to approved. It emails the subscriber list for the article's journalist or publisher and posts the article ID to `APPROVED_API_URL`. The internal endpoint validates `X-Approval-Secret` and writes an `ApprovedArticleLog`. If the local API is temporarily unavailable, the article remains approved and the failed integration is written to the server log.

For production, use HTTPS, a strong secret, a real email backend, and a background task queue for reliable delivery. Do not expose the internal secret in client-side code.

## 9. Automated tests

```powershell
python manage.py test news
```

Tests include successful and failed requests: unauthenticated access, reader restrictions, subscribed publisher/journalist filtering, journalist article creation, editor approval/deletion, newsletter creation restrictions, token authentication and approval-log secret validation. The email backend is mocked by Django's in-memory backend, and the outgoing HTTP request is mocked in the approval test.

## 10. MariaDB configuration

Install and start MariaDB, create a database and user, then copy `.env.example` values into your environment. PowerShell example:

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="news_db"
$env:DB_USER="news_user"
$env:DB_PASSWORD="your-password"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
python manage.py migrate
```

`PyMySQL` is installed as the MySQL-compatible DB-API driver. SQLite remains the default so the project can be run and tested without a local MariaDB server.

## 11. Quality checks

```powershell
python manage.py check
python manage.py test news
```

The code uses modular models, serializers, permissions, views, URL configurations and signals. User-facing article input is validated, permissions are checked at both endpoint and object level, and the external HTTP request has a timeout and exception handling.
