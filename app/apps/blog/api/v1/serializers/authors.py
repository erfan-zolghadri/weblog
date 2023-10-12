from rest_framework import serializers

from apps.blog.models import Author


class AuthorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Author
        fields = ["email", "first_name", "last_name"]
