from rest_framework import serializers
from django.contrib.auth.models import User


class MessageSerializer(serializers.ModelSerializer):
  
    id = serializers.IntegerField(required=False)
    session_id = serializers.IntegerField(required=False)
    MC1_timestamp = serializers.CharField(required=False)
    MC2_timestamp = serializers.CharField(required=False)
    MC3_timestamp = serializers.CharField(required=False)
    end_timestamp = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'session_id', 
                  'MC1_timestamp',
                  'MC2_timestamp',
                  'MC3_timestamp',
                  'end_timestamp']
