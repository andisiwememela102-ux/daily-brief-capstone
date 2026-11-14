from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from .models import Article, Newsletter, Publisher, ApprovedArticleLog

User = get_user_model()

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NewsApiTests(TestCase):
    def setUp(self):
        request_patcher = patch('news.signals.requests.post')
        request_patcher.start()
        self.addCleanup(request_patcher.stop)
        self.reader = User.objects.create_user(username='reader', password='Pass12345!', role='reader', email='reader@example.com')
        self.journalist = User.objects.create_user(username='writer', password='Pass12345!', role='journalist', email='writer@example.com')
        self.editor = User.objects.create_user(username='editor', password='Pass12345!', role='editor', email='editor@example.com')
        self.publisher = Publisher.objects.create(name='Daily News')
        self.publisher_reader = User.objects.create_user(username='publisherreader', password='Pass12345!', role='reader', email='p@example.com')
        self.publisher_reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)
        self.writer_article = Article.objects.create(title='Writer story', content='Text', author=self.journalist, approved=True)
        self.publisher_article = Article.objects.create(title='Publisher story', content='Text', publisher=self.publisher, approved=True)
        self.other_article = Article.objects.create(title='Other story', content='Text', author=self.journalist, approved=False)
        self.client = APIClient()

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_token_authentication_endpoint(self):
        response = self.client.post('/api/token/', {'username': 'reader', 'password': 'Pass12345!'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_articles_requires_authentication(self):
        self.assertEqual(self.client.get('/api/articles/').status_code, 401)

    def test_reader_sees_only_approved_articles(self):
        self.authenticate(self.reader)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_reader_sees_only_subscribed_content(self):
        self.authenticate(self.reader)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.writer_article.id])

    def test_publisher_subscription_returns_publisher_articles(self):
        self.authenticate(self.publisher_reader)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual([item['id'] for item in response.data], [self.publisher_article.id])

    def test_journalist_can_create_article(self):
        self.authenticate(self.journalist)
        response = self.client.post('/api/articles/', {'title': 'New story', 'content': 'Body'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.get(pk=response.data['id']).author, self.journalist)

    def test_reader_cannot_create_article(self):
        self.authenticate(self.reader)
        response = self.client.post('/api/articles/', {'title': 'No', 'content': 'Body'}, format='json')
        self.assertEqual(response.status_code, 403)

    @patch('news.signals.requests.post')
    def test_editor_can_approve_and_trigger_integration(self, mock_post):
        mock_post.return_value.raise_for_status.return_value = None
        self.authenticate(self.editor)
        response = self.client.post(f'/api/articles/{self.other_article.id}/approve/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Article.objects.get(pk=self.other_article.id).approved)
        mock_post.assert_called_once()

    def test_journalist_can_update_own_article(self):
        self.authenticate(self.journalist)
        response = self.client.patch(f'/api/articles/{self.writer_article.id}/', {'title': 'Updated'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated')

    def test_editor_can_delete_article(self):
        self.authenticate(self.editor)
        response = self.client.delete(f'/api/articles/{self.writer_article.id}/')
        self.assertEqual(response.status_code, 204)

    def test_newsletter_creation_for_journalist(self):
        self.authenticate(self.journalist)
        response = self.client.post('/api/newsletters/', {'title': 'Weekly', 'description': 'Round-up', 'articles': [self.writer_article.id]}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Newsletter.objects.get(pk=response.data['id']).author, self.journalist)

    def test_reader_cannot_create_newsletter(self):
        self.authenticate(self.reader)
        response = self.client.post('/api/newsletters/', {'title': 'No'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_approval_log_endpoint_requires_secret(self):
        response = self.client.post('/api/approved/', {'article_id': self.writer_article.id}, format='json')
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/approved/', {'article_id': self.writer_article.id}, format='json', HTTP_X_APPROVAL_SECRET='local-approval-secret')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ApprovedArticleLog.objects.count(), 1)


class RegistrationTests(TestCase):
    def test_registration_assigns_selected_role_and_group(self):
        for role in (User.Role.READER, User.Role.JOURNALIST, User.Role.EDITOR):
            with self.subTest(role=role):
                username = f'new_{role}'
                response = self.client.post('/register/', {
                    'username': username,
                    'email': f'{username}@example.com',
                    'role': role,
                    'password1': 'A-strong-password-482!',
                    'password2': 'A-strong-password-482!',
                })
                self.assertRedirects(response, '/')
                user = User.objects.get(username=username)
                self.assertEqual(user.role, role)
                self.assertTrue(user.groups.filter(name=role.title()).exists())
                self.assertTrue(response.wsgi_request.user.is_authenticated)
                self.client.logout()

    def test_registration_rejects_invalid_role(self):
        response = self.client.post('/register/', {
            'username': 'badrole',
            'email': 'badrole@example.com',
            'role': 'administrator',
            'password1': 'A-strong-password-482!',
            'password2': 'A-strong-password-482!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='badrole').exists())
