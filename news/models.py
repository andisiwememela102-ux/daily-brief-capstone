"""Database models for newsroom users, publishing, and article approval."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Publisher(models.Model):
    """A newsroom organization with editors, journalists, and subscribers."""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='edited_publishers')
    journalists = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='journalist_publishers')

    def __str__(self):
        """Return the publisher's display name."""
        return self.name


class User(AbstractUser):
    """A Django user with a newsroom role and reader subscriptions."""

    class Role(models.TextChoices):
        """Supported roles for newsroom accounts."""

        READER = 'reader', 'Reader'
        EDITOR = 'editor', 'Editor'
        JOURNALIST = 'journalist', 'Journalist'

    role = models.CharField(max_length=12, choices=Role.choices, default=Role.READER)
    subscribed_publishers = models.ManyToManyField(Publisher, blank=True, related_name='subscribers')
    subscribed_journalists = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='journalist_subscribers',
        limit_choices_to={'role': Role.JOURNALIST},
    )

    def clean(self):
        """Reject subscriptions assigned to non-reader accounts."""
        super().clean()
        if self.role != self.Role.READER and self.pk:
            if self.subscribed_publishers.exists() or self.subscribed_journalists.exists():
                raise ValidationError('Only readers may have subscriptions.')

    def save(self, *args, **kwargs):
        """Persist the user and clear subscriptions when the role is staff."""
        super().save(*args, **kwargs)
        # Django M2M fields cannot be NULL; non-reader users are kept subscription-free.
        if self.role != self.Role.READER:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def __str__(self):
        """Return the account username for admin and relation displays."""
        return self.username


class Article(models.Model):
    """A news article owned by either one journalist or one publisher."""

    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        """Order articles by recency and enforce a single source in the database."""

        ordering = ['-created_at']
        constraints = [models.CheckConstraint(
            condition=(Q(author__isnull=False, publisher__isnull=True) | Q(author__isnull=True, publisher__isnull=False)),
            name='article_has_exactly_one_source',
        )]

    def clean(self):
        """Validate that the article has exactly one valid publishing source."""
        if bool(self.author_id) == bool(self.publisher_id):
            raise ValidationError('An article must belong to either a journalist or a publisher, not both.')
        if self.author_id and self.author.role != User.Role.JOURNALIST:
            raise ValidationError('Independent articles must be authored by a journalist.')

    def __str__(self):
        """Return the article title."""
        return self.title


class Newsletter(models.Model):
    """A journalist-authored collection of articles for distribution."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='newsletters')
    articles = models.ManyToManyField(Article, blank=True, related_name='newsletters')

    def __str__(self):
        """Return the newsletter title."""
        return self.title


class ApprovedArticleLog(models.Model):
    """An audit record created by the internal article approval integration."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='approval_logs')
    title = models.CharField(max_length=250)
    article_url = models.URLField(blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a concise label for the approved article log."""
        return f'Approved: {self.title}'
