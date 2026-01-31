from django.urls import path
from.api import tweets

urlpatterns = [
    path("tweets/", tweets),
]

# 这段代码把 /tweets/ 这个 URL 请求，映射到 tweets 这个 API 函数上，
# 是“请求进入后端的第一道门”。