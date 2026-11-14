import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Article, User

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Article)
def remember_approval_state(sender, instance, **kwargs):
    instance._was_approved = False
    if instance.pk:
        instance._was_approved = sender.objects.filter(pk=instance.pk, approved=True).exists()

@receiver(post_save, sender=Article)
def distribute_approved_article(sender, instance, created, **kwargs):
    if not instance.approved or getattr(instance, '_was_approved', False):
        return
    if instance.publisher_id:
        subscribers = instance.publisher.subscribers.filter(is_active=True)
    elif instance.author_id:
        subscribers = instance.author.journalist_subscribers.filter(is_active=True)
    else:
        subscribers = User.objects.none()
    recipients = list(subscribers.exclude(email='').values_list('email', flat=True).distinct())
    if recipients:
        send_mail(
            subject=f'New approved article: {instance.title}',
            message=f'{instance.title}\n\n{instance.content}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=True,
        )
    try:
        response = requests.post(
            settings.APPROVED_API_URL,
            json={'article_id': instance.pk},
            headers={'X-Approval-Secret': settings.APPROVED_API_SECRET},
            timeout=3,
        )
        response.raise_for_status()
    except requests.RequestException:
        # The article remains approved even if the local integration is temporarily offline.
        logger.exception('Could not log approved article %s to the API.', instance.pk)

@receiver(post_save, sender=User)
def assign_role_group(sender, instance, created, **kwargs):
    # Keep group membership in sync if an administrator changes a user's role.
    instance.groups.remove(*Group.objects.filter(name__in=['Reader', 'Editor', 'Journalist']))
    group, _ = Group.objects.get_or_create(name=instance.role.title())
    content_types = ContentType.objects.filter(app_label='news')
    permissions = Permission.objects.filter(content_type__in=content_types)
    if instance.role == User.Role.READER:
        allowed = {'view_article', 'view_newsletter', 'view_publisher'}
    elif instance.role == User.Role.EDITOR:
        allowed = {'view_article', 'change_article', 'delete_article', 'view_newsletter', 'change_newsletter', 'delete_newsletter', 'view_publisher'}
    else:
        allowed = {'add_article', 'view_article', 'change_article', 'delete_article', 'add_newsletter', 'view_newsletter', 'change_newsletter', 'delete_newsletter', 'view_publisher'}
    group.permissions.set(permissions.filter(codename__in=allowed))
    instance.groups.add(group)
