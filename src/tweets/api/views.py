from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework import status
from tweets.models import Tweet
from tweets.api.serializers import TweetCreateSerializer, TweetSerializer

# 成功响应的统一出口
def ok(data=None, message="OK", status_code=200):
    # data=None 允许“只返回成功状态，不带数据”
    # message="OK" 允许自定义成功消息
    # status_code：HTTP 状态码（默认 200）
    return Response(
        {"success": True, "message": message, "data": data}, status=status_code
    )
# 失败响应的统一出口
def fail(message="Bad Request", errors=None, status_code=400):
    # message="Bad Request" 允许自定义失败消息
    # errors=None 允许携带错误详情
    # status_code：HTTP 状态码（默认 400）
    payload = {"success": False, "message": message} # 最小失败响应
    # 保证即使没有 errors，结构也统一
    if errors is not None: # 只有在有详细错误时才返回 errors,避免前端拿到一堆 errors: null
        payload["errors"] = errors # 添加错误详情
    return Response(payload, status=status_code)

@api_view(["GET", "POST"])
def tweets(request): # 输入：request（包含 method、user、data 等）
    # GET：查询推文列表
    # 处理 GET 请求，返回所有 Tweet 列表
    if request.method == "GET":
        qs = Tweet.objects.select_related("user").all()
        # 输入：无（只是 ORM 查询）;输出：qs 是一个 QuerySet（懒加载对象）
        return ok(TweetSerializer(qs, many=True).data, message="Tweets list")
    # POST：创建新推文
    if not request.user or not request.user.is_authenticated:
        return fail("Authentication required", status_code=status.HTTP_401_UNAUTHORIZED)
    
    serializer = TweetCreateSerializer(data=request.data)
    # 输入：request.data（用户提交的数据）;输出：serializer（待验证的序列化器对象）
    if not serializer.is_valid():
        return fail("Validation error", errors=serializer.errors, status_code=400)
    
    tweet = Tweet.objects.create(# 创建新推文对象
        user=request.user,
        content=serializer.validated_data["content"]
        #隐式行为: .create() 会立刻执行 INSERT，并返回对象
        #这里没有调用 serializer.save()，而是手动 create
    )
    return ok(TweetSerializer(tweet).data, message="Tweet created", status_code=status.HTTP_201_CREATED)


