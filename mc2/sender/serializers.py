from rest_framework import serializers
from django.contrib.auth.models import User


class MessageSerializer(serializers.ModelSerializer):
  
    id = serializers.IntegerField(required=False)
#    session_id = serializers.IntegerField()
    MC1_timestamp = serializers.CharField(required=False)
#    MC2_timestamp = serializers.CharField()
#    MC3_timestamp = serializers.CharField()
#    end_timestamp = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'MC1_timestamp']
