from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
import requests

from sender.serializers import MessageSerializer


class MessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.data
        instance['MC3_timestamp'] = str(timezone.now())
        serializer1 = MessageSerializer(data=instance)
        serializer1.is_valid(raise_exception=True)
        return Response(serializer1.data, status=status.HTTP_200_OK)
