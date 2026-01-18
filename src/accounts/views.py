from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, LoginSerializer, UserSerializer


def ok(data=None, message="OK", status_code=200):
    return Response({"success": True, "message": message, "data": data}, status=status_code)


def fail(message="Bad Request", errors=None, status_code=400):
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    POST /api/accounts/signup/
    body: { "username": "...", "email": "...", "password": "..." }

    返回：创建成功的用户信息（不含密码）
    """
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return fail("Validation error", errors=serializer.errors, status_code=400)

    user = serializer.save()
    return ok(UserSerializer(user).data, message="User created", status_code=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/accounts/login/
    body: { "username": "...", "password": "..." }

    返回 access/refresh
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return fail("Validation error", errors=serializer.errors, status_code=400)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return fail("Invalid credentials", status_code=400)

    if not user.check_password(password):
        return fail("Invalid credentials", status_code=400)

    refresh = RefreshToken.for_user(user)
    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}

    return ok(tokens, message="Login success", status_code=200)


@api_view(["POST"])
def logout(request):
    """
    POST /api/accounts/logout/
    headers: Authorization: Bearer <access>
    body: { "refresh": "<refresh_token>" }

    做法：把 refresh token 拉黑(blacklist)
    这样 refresh token 就不能再用来换取新的 access token 了
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return fail("Missing refresh token", status_code=400)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        # refresh token 无效或已过期/已拉黑
        return fail("Invalid refresh token", status_code=400)

    return ok(message="Logged out", status_code=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def me(request):
    """
    GET /api/accounts/me/
    headers: Authorization: Bearer <access>

    返回当前登录用户信息
    """
    return ok(UserSerializer(request.user).data, message="Current user", status_code=200)
