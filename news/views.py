"""Render newsroom pages and handle registration and editorial actions."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegistrationForm
from .models import Article, Newsletter, User


def home(request):
    """Render the home page with approved articles."""
    articles = Article.objects.filter(approved=True).select_related('author', 'publisher')
    return render(request, 'news/home.html', {'articles': articles})


def register(request):
    """Register a newsroom user, sign them in, and show validation errors."""
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        # The user post_save signal assigns the matching Reader, Editor, or Journalist group.
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('home')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def article_detail(request, pk):
    """Display one approved article to an authenticated reader."""
    article = get_object_or_404(Article, pk=pk, approved=True)
    return render(request, 'news/article_detail.html', {'article': article})


@login_required
def review_articles(request):
    """Display pending articles to editors for moderation."""
    if request.user.role != User.Role.EDITOR:
        raise PermissionDenied('Only editors may review articles.')
    pending = Article.objects.filter(approved=False).select_related('author', 'publisher')
    return render(request, 'news/review.html', {'articles': pending})


@login_required
def approve_article(request, pk):
    """Approve a pending article through an editor-only POST request."""
    if request.method != 'POST' or request.user.role != User.Role.EDITOR:
        raise PermissionDenied('Only editors may approve articles using POST.')
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save(update_fields=['approved'])
    messages.success(request, 'Article approved and distribution triggered.')
    return redirect('review-articles')


@login_required
def newsletter_list(request):
    """Render newsletters and their related articles."""
    newsletters = Newsletter.objects.prefetch_related('articles').all()
    return render(request, 'news/newsletters.html', {'newsletters': newsletters})
