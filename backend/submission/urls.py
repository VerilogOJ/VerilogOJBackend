from django.urls import path, include
from rest_framework import routers
from .views import SubmissionViewSet, SubmitView, SubmissionResultViewSet

router = routers.DefaultRouter()
router.register('submissions', SubmissionViewSet)
router.register('submission-results', SubmissionResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('submit', SubmitView.as_view()),
]
