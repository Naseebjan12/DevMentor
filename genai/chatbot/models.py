from django.db import models
# Create your models here.
class Users(models.Model):
    username=models.CharField(max_length=30)
    email=models.EmailField(primary_key=True)
    password=models.CharField(max_length=50)
    verification_code = models.CharField(max_length=6, null=True, blank=True)  # Add verification code field
    is_verified = models.BooleanField(default=False)  # Add field to track verification status
    
    
    def __str__(self):
        return self.email
    
# add a history model to view the history of a user when the user login into the website
class History(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    bot_messages=models.CharField(max_length=3000)
    user_messages=models.CharField(max_length=3000)
    
    def __str__(self):
        return self.bot_messages +" | "+ self.user_messages
    
    
    
    
    
    
    
        
    
    





    
    


