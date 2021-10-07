from django.urls import re_path
from .consumers import ChatConsumer

ws_rulpatterns = [ 
    re_path(r'^messages/(?P<username>[\w.@+-]+)/$', ChatConsumer.as_asgi()),
]