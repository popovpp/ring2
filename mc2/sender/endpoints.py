from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sender.views import MessageViewSet


message_router = DefaultRouter()
message_router.register('messages', MessageViewSet, 'messages')

message_endpoint = [
    path('', include([path('', include(message_router.urls)), ]))
]
