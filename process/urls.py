from django.urls import path

from . import views

urlpatterns = [
    path('chat', views.chatPage, name='chat'),
    path('generator',views.generator,name='generator'),

    path('chat_jp', views.chatPageJP, name='chat_jp'),
    path('generator_jp',views.generator_jp,name='generator_jp'),
]