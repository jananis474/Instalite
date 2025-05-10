from django.contrib import admin
from .models import UserProfile, Post, Comment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'caption')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'text')
