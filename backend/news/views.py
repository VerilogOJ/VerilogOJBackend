from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .models import News
from .serializers import NewsSerializer

class NewsViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    """
    公告
    """
    queryset = News.objects.all()
    serializer_class = NewsSerializer
