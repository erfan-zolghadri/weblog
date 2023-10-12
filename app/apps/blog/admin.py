from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


def pluralize_objects(objects_count):
    if objects_count == 1:
        return " was"
    return "s were"


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name"]
    list_per_page = 10
    search_fields = ["user__email__istartswith", "last_name__istartswith"]
    ordering = ["user__email"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def email(self, author):
        return author.user.email


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "posts_count"]
    list_display_links = ["pk", "title"]
    list_per_page = 10
    search_fields = ["title__istartswith"]
    ordering = ["title"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request).annotate(posts_count=Count("posts"))
        )

    @admin.display(description="#posts", ordering="posts_count")
    def posts_count(self, category):
        url = (
            reverse("admin:blog_post_changelist")
            + "?"
            + urlencode({"category_id": category.id})
        )
        return format_html(
            '<a href="{url}">{posts_count}</a>',
            url=url,
            posts_count=category.posts_count,
        )


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "author", "status", "is_active"]
    list_display_links = ["pk", "title"]
    list_editable = ["status", "is_active"]
    list_filter = ["status", "is_active", "created_at"]
    list_per_page = 10
    autocomplete_fields = ["category", "author"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["title"]
    ordering = ["-created_at"]
    actions = ["set_as_draft", "set_as_published"]

    @admin.action(description="Set as draft")
    def set_as_draft(self, request, queryset):
        updated_counts = queryset.update(status=models.Post.STATUS_DRAFT)
        pluralized_posts = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f"{updated_counts} post{pluralized_posts} set as draft.",
        )

    @admin.action(description="Set as published")
    def set_as_published(self, request, queryset):
        updated_counts = queryset.update(status=models.Post.STATUS_PUBLISHED)
        pluralized_posts = pluralize_objects(updated_counts)

        self.message_user(
            request,
            message=f"{updated_counts} post{pluralized_posts} set as published.",
        )
