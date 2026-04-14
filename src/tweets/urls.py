from django.urls import path
from.api.views import tweets

urlpatterns = [
     path("", tweets),
]

