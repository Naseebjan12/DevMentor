from django.contrib import admin
from .models import Users
from .models import History

class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_verified')  # Add fields to display in the list view
    search_fields = ('username', 'email')  # Add search functionality
    list_filter = ('is_verified',)  # Add filter for 'is_verified'
    
class MessagesHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_messages', 'bot_messages',)  # Display user and timestamp
    search_fields = ('user__email', 'user_messages', 'bot_messages')  # Add search capability

# Register the model with the updated admin class
admin.site.register(History, MessagesHistoryAdmin)
admin.site.register(Users, UsersAdmin)

