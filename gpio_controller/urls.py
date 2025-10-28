from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GPIOConnectionViewSet, JetsonNanoDeviceViewSet

router = DefaultRouter()
router.register(r'connections', GPIOConnectionViewSet, basename='connection')
router.register(r'devices', JetsonNanoDeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
