from django.contrib import admin
from app.models import *
# Register your models here.


admin.site.register(MapSettings)
admin.site.register(ZoneGroup)
admin.site.register(Zones)
admin.register(UserTrip)
admin.site.register(SettingsModel)
admin.site.register(ZoneAlert)
admin.site.register(GoogleMapAPIKey)
admin.site.register(Subscription)