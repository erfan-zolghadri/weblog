from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter

from .permissions import IsPostAuthorOrReadOnly
from .filters import PostFilterSet
from .paginations import DefaultPagination
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    PostSerializer,
    PostCreateUpdateSerializer,
)
from apps.blog.models import Author, Category, Post


class AuthorDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.select_related("user")
    permission_classes = [IsAuthenticated]

    def get_object(self):
        author = get_object_or_404(
            self.get_queryset(), user_id=self.request.user.pk
        )
        return author


class CategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("title")


class PostViewSet(ModelViewSet):
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["title"]
    filterset_class = PostFilterSet
    ordering_fields = ["created_at"]
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsPostAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return PostCreateUpdateSerializer
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        try:
            author = Author.objects.get(user_id=self.request.user.pk)
            context["author"] = author
        except Author.DoesNotExist:
            pass

        return context

    def get_queryset(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return Post.published.select_related(
                "category", "author__user"
            ).order_by("-created_at")
        return Post.objects.select_related(
            "category", "author__user"
        ).order_by("-created_at")
