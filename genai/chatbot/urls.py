from . import views
from django.urls import path
urlpatterns = [
    path('',views.index,name='index'),
    path('usecase',views.usecase,name='usecase'),
    path('contact',views.contact,name='contact'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('bot',views.bot,name='bot'),
    path('new',views.new_chat,name='new_chat'),
    path('verify_email',views.verify_email,name='verify_email'),
    path('logout',views.logout,name='logout'),
    # path('bot', views.chatbot_view, name='chatbot'),
    # path('registration',views.registration,name='registration'),
]
