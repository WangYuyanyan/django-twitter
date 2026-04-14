from rest_framework import serializers
from tweets.models import Tweet


class TweetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ["content"]

    def validate_content(self, value: str):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Content cannot be empty.")
        if len(value) > 280:
            raise serializers.ValidationError("Content must be <= 280 characters.")
        return value


class TweetSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Tweet
        fields = ["id", "user", "content", "created_at"]

