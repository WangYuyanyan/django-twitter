from django.conf import settings
from django.db import models


class Friendship(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',  # from_user.following.all() → 我关注的人
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',  # to_user.followers.all() → 关注我的人
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('from_user', 'to_user'),)
        index_together = (
            ('from_user', 'created_at'),  # 查"我关注了谁"按时间排序
            ('to_user', 'created_at'),    # 查"谁关注了我"按时间排序
        )

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"