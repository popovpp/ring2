from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import requests

from sender.serializers import MessageSerializer


class MessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        instance = serializer.data
        instance['MC2_timestamp'] = str(timezone.now())
        response = requests.post('http://web2:8002/messages/', data=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
