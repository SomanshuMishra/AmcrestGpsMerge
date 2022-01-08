from django.contrib import admin
from services.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here.






admin.site.register(SimMapping)
admin.site.register(ServicePlan)
admin.site.register(Countries)
admin.site.register(States)
admin.site.register(TimeZoneModel)
admin.site.register(Langauges)
admin.site.register(HarshNotificationMessage)
admin.site.register(SimUpdateCredentials)
admin.site.register(AppConfiguration)
admin.site.register(WebhookSubscription)
admin.site.register(DeviceModel)
admin.site.register(PodSimCron)
admin.site.register(SimPlanUpdatedRecord)
admin.site.register(DeviceFrequency)
admin.site.register(NotificationMessage)
admin.site.register(ServicePlanObd)
admin.site.register(DeviceFrequencyObd)
admin.site.register(ReviewModel)
admin.site.register(MobileServiceProvider)
admin.site.register(AppVersion)
admin.site.register(DeviceCommandsList)



class DtcRecordsResource(resources.ModelResource):
    class Meta:
        model = DtcRecords




class DtcRecordsAdmin(ImportExportModelAdmin):
    resource_class = DtcRecordsResource
    # pass

admin.site.register(DtcRecords, DtcRecordsAdmin)