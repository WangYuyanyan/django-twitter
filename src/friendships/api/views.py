from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipCreateSerializer,
)


def ok(data=None, message="OK", status_code=200):
    return Response(
        {"success": True, "message": message, "data": data}, status=status_code
    )


def fail(message="Bad Request", errors=None, status_code=400):
    payload = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)


@api_view(["GET"])
def followers(request, user_id):
    """
    GET /api/friendships/{user_id}/followers/
    返回关注了 user_id 的所有人（粉丝列表）
    """
    friendships = Friendship.objects.filter(
        to_user_id=user_id
    ).select_related('from_user').order_by('-created_at')
    serializer = FollowerSerializer(friendships, many=True)
    return ok(serializer.data, message="Followers list")


@api_view(["GET"])
def followings(request, user_id):
    """
    GET /api/friendships/{user_id}/followings/
    返回 user_id 关注的所有人（关注列表）
    """
    friendships = Friendship.objects.filter(
        from_user_id=user_id
    ).select_related('to_user').order_by('-created_at')
    serializer = FollowingSerializer(friendships, many=True)
    return ok(serializer.data, message="Followings list")


@api_view(["POST"])
def follow(request):
    """
    POST /api/friendships/follow/
    body: { "to_user_id": 2 }
    当前登录用户关注 to_user_id
    """
    serializer = FriendshipCreateSerializer(
        data=request.data,
        context={'request': request},
    )
    if not serializer.is_valid():
        return fail("Validation error", errors=serializer.errors)

    friendship = serializer.save()
    return ok(
        FollowingSerializer(friendship).data,
        message="Followed successfully",
        status_code=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def unfollow(request):
    """
    POST /api/friendships/unfollow/
    body: { "to_user_id": 2 }
    当前登录用户取消关注 to_user_id
    """
    to_user_id = request.data.get('to_user_id')
    if not to_user_id:
        return fail("to_user_id is required")

    deleted, _ = Friendship.objects.filter(
        from_user=request.user,
        to_user_id=to_user_id,
    ).delete()

    if not deleted:
        return fail("You are not following this user.", status_code=status.HTTP_404_NOT_FOUND)

    return ok(message="Unfollowed successfully")