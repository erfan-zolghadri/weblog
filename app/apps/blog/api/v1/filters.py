from django_filters import DateTimeFilter, FilterSet

from apps.blog.models import Post


class PostFilterSet(FilterSet):
    from_date = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    to_date = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Post
        fields = {"category": ["exact", "in"]}
