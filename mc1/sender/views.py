from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone

from sender.serializers import MessageSerializer
from sender.models import Message


class MessageViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer
    queryset = Message.objects.all().order_by('id')

    @action(methods=['GET'], detail=False, url_path="start", 
    	    url_name="start",
            permission_classes=[AllowAny])
    def start(self, request, **kwargs):
        print('START', timezone.now())
        return Response('START ' + str(timezone.now()), status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="stop", 
    	    url_name="stop",
            permission_classes=[AllowAny])
    def stop(self, request, **kwargs):
        print('STOP', timezone.now())  
        return Response('STOP ' + str(timezone.now()), status=status.HTTP_200_OK)
