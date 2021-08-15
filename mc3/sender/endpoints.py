from django.urls import include, path

from sender.views import MessageView


message_endpoint = [
    path('messages/', MessageView.as_view())
]