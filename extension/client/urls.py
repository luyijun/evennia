"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
   url(r'^$', 'extension.client.views.client', name="index")]
