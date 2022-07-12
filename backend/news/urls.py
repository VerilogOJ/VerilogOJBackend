from django.urls import path, include
from rest_framework import routers
from .views import NewsViewSet

router = routers.DefaultRouter()
router.register('news', NewsViewSet)
# 自动生成list和read两个API
#     list 显示所有newss
#     read 指定pk获取对应的news

urlpatterns = [
    path('', include(router.urls)),
]
