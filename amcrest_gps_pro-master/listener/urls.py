from django.urls import path, re_path
from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^geofence$', GeoFenceApiView.as_view(), name='geofence_api'),
]