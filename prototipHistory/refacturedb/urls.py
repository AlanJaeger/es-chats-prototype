from django.urls import path, include
from rest_framework import routers

from refacturedb.views import *

router = routers.DefaultRouter()
router.register(r'room', RoomViewSet)

urlpatterns = [
    path('', include(router.urls)),
]