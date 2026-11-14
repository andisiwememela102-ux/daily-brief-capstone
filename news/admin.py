from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Article, ApprovedArticleLog, Newsletter, Publisher, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('News profile', {'fields': ('role', 'subscribed_publishers', 'subscribed_journalists')}),)
    list_display = ('username', 'email', 'role', 'is_staff')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('title', 'content')

admin.site.register(Publisher)
admin.site.register(Newsletter)
admin.site.register(ApprovedArticleLog)
