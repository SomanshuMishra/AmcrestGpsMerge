from django.contrib import admin
from app.models import *
# Register your models here.

admin.register(UserObdTrip)
admin.site.register(SettingsModel)
admin.site.register(GoogleMapAPIKey)
admin.site.register(Subscription)