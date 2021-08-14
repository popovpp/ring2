from django.db import models


class Message(models.Model):

    session_id = models.IntegerField(default=0)
    MC1_timestamp = models.DateTimeField(auto_now_add=True)
    MC2_timestamp = models.DateTimeField(blank=True, null=True)
    MC3_timestamp = models.DateTimeField(blank=True, null=True)
    end_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'messages'
