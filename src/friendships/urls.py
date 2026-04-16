from django.urls import path
from friendships.api.views import follow, unfollow, followers, followings

urlpatterns = [
    path('follow/', follow),
    path('unfollow/', unfollow),
    path('<int:user_id>/followers/', followers),
    path('<int:user_id>/followings/', followings),
]