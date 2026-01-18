from django.contrib.auth.models import User
from rest_framework import serializers

class SignupSerializer(serializers.Serializer):
    """
    register: username + email + password
    - 做严格校验（长度、格式、唯一性）
    - username/email 统一 lower, 避免 Alice vs alice 的重复账号 
    """

    username = serializers.CharField(min_length=3, max_length=32)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs["username"].strip().lower()
        email = attrs["email"].strip().lower()
        attrs["username"] = username
        attrs["email"] = email
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})
        return attrs # attrs is a dict of validated data
    
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
    
class LoginSerializer(serializers.Serializer):
    """
    login: username + password
    - username - lower
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs["username"].strip().lower()
        attrs["username"] = username
        return attrs
    
class UserSerializer(serializers.ModelSerializer):
    """
    用户信息（/me)
    - 目前先返回 id/username/email
    - 未来要加 profile: nickname/avatar_url,可在此扩展
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')