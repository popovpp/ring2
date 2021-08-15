from django.contrib import admin

from sender.models import Message


class MessagesModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_id', 
                    'MC1_timestamp',
                    'MC2_timestamp',
                    'MC3_timestamp',
                    'end_timestamp']
    list_display_links = ['id']

    class Meta:
        model = Message


admin.site.register(Message, MessagesModelAdmin)
