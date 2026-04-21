from django.contrib.auth.models import User
from rest_framework import serializers
from friendships.models import Friendship


class FollowerSerializer(serializers.ModelSerializer):
    """
    粉丝列表：展示 from_user 的信息（谁关注了我）
    """
    user_id = serializers.IntegerField(source='from_user.id', read_only=True)
    username = serializers.CharField(source='from_user.username', read_only=True)

    class Meta:
        model = Friendship
        fields = ['user_id', 'username', 'created_at']


class FollowingSerializer(serializers.ModelSerializer):
    """
    关注列表：展示 to_user 的信息（我关注了谁）
    """
    user_id = serializers.IntegerField(source='to_user.id', read_only=True)
    username = serializers.CharField(source='to_user.username', read_only=True)

    class Meta:
        model = Friendship
        fields = ['user_id', 'username', 'created_at']


class FriendshipCreateSerializer(serializers.Serializer):
    """
    用于创建关注关系，接收 to_user_id
    """
    to_user_id = serializers.IntegerField()

    def validate_to_user_id(self, value):
        # 目标用户必须存在
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        # 不能关注自己
        if self.context['request'].user.id == value:
            raise serializers.ValidationError("You cannot follow yourself.")
        return value

    def validate(self, attrs):
        from_user = self.context['request'].user
        to_user_id = attrs['to_user_id']
        # 不能重复关注
        if Friendship.objects.filter(from_user=from_user, to_user_id=to_user_id).exists():
            raise serializers.ValidationError("You are already following this user.")
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user=self.context['request'].user,
            to_user_id=validated_data['to_user_id'],
        )