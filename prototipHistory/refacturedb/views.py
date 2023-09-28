from django.shortcuts import render
from rest_framework import viewsets
from refacturedb.serializers import *
from refacturedb.models import *
# Create your views here.

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
