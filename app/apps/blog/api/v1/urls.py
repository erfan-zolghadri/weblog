from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "blog_api_1.0"

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("posts", views.PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", views.AuthorDetailAPIView.as_view(), name="author-detail"),
]
