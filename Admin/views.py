import uuid

from django.core.cache import cache
from django.shortcuts import render
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from Admin.models import AdminUser
from Admin.serializers import AdminUserSerializer
from DjangoRest.settings import ADMIN_USER_TIMEOUT


class AdminUsersAPIView(CreateAPIView):

    serializer_class = AdminUserSerializer
    queryset = AdminUser.objects.filter(is_delete=False)


    def post(self, request, *args, **kwargs):

        action = request.query_params.get("action")

        if action == 'register':
            return self.create(request, *args, **kwargs)
        elif action == "login":
            a_username = request.data.get("a_username")
            a_password = request.data.get("a_password")

            user = AdminUser.objects.filter(a_username=a_username)

            if not user.exists():
                raise APIException(detail="用户不存在")
            user = user.first()
            if not user.check_admin_password(a_password):
                raise APIException(detail="密码错误")

            if user.is_delete:
                raise APIException(detail="用户已删除")

            token = uuid.uuid4().hex
            cache.set(token, user.id, timeout=ADMIN_USER_TIMEOUT)
            data = {
                "msg": "ok",
                "status": 200,
                "token": token
            }
            return Response(data)

        else:
            raise APIException(detail="请提供正确的方式")