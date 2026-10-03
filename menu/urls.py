from django.urls import path
from .views import cardapio


urlpatterns = [
path('', cardapio, name='cardapio'),
]