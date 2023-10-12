from rest_framework import serializers

from apps.blog.models import Author, Category, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["pk", "title", "description"]

    def to_representation(self, instance):
        """
        Changes data representation in category-list and category-detail.
        """
        rep = super().to_representation(instance)
        request = self.context.get("request")

        if not request.parser_context.get("kwargs").get("pk"):
            # Remove description from category-list
            rep.pop("description", None)
        return rep


class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["first_name", "last_name"]


class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = PostAuthorSerializer()

    class Meta:
        model = Post
        fields = [
            "pk",
            "title",
            "body",
            "status",
            "category",
            "author",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        """
        Changes data representation in post-list and post-detail.
        """
        rep = super().to_representation(instance)
        request = self.context.get("request")

        if not request.parser_context.get("kwargs").get("pk"):
            # Remove fields from post-list
            rep.pop("body", None)
            rep.pop("created_at", None)
            rep.pop("updated_at", None)
        return rep


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["category", "title", "body", "status"]

    def create(self, validated_data):
        author = self.context.get("author")
        post = Post.objects.create(author=author, **validated_data)
        self.instance = post
        return post
