from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="author",
    )

    def __str__(self):
        return str(self.user.email)


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_active=True, status=Post.STATUS_PUBLISHED)
        )


class Post(models.Model):
    STATUS_DRAFT = "drf"
    STATUS_PUBLISHED = "pub"
    STATUS_CHOICES = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    # image = models.ImageField(
    #     upload_to=post_media_directory,
    #     null=True,
    #     blank=True,
    #     default='blog/posts/default.png'
    # )
    status = models.CharField(
        max_length=5, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    is_active = models.BooleanField(
        verbose_name="active",
        default=True,
        help_text=_("Unselect this instead of deleting posts."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="posts"
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="posts"
    )

    objects = models.Manager()
    published = PublishedPostManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)

    def delete(self):
        self.is_active = False
        self.save()
