from django.urls import path, re_path
from django.conf.urls import url

from .views import *
from . import trips
from . import trip_export_pdf
from . import zone_alert as z_alert
from . import settings_module as setting_module
from . import device_frequency
from . import trips_generate_30_min

from app.events import notifications, odometer, trips as trip_event, voltage, harsh_events, gps_events, multiple_events, fuel_economy, driver_score, dtc_event, fuel_emission, fuel_economy_microservice, multiple_events_export, generate_trip_report
from . import individual_track 
from . import telemetry_data
from . import trip_manual_calculation
from . import gpx_file_parser
from . import obd_zone
from .sim_apis import dignostics

from app.battery_calculator.battery_calculator import *

from . import ideal_time_test

# from app.events import trips as trip_event

urlpatterns = [
	url(r'^battery/calculator$', CalculateBatteryApiView.as_view(), name='battery_calculator'),

	url(r'^ideal_time/test', ideal_time_test.GenerateIdealTimeApiView.as_view(), name='ideal_time_test'),

	url(r'^device/settings/(?P<imei>.+)$', setting_module.SettingModuleView.as_view(), name='setting_module'),
	url(r'^setting/devices/(?P<customer_id>.+)$', setting_module.SettingDevicesView.as_view(), name='setting_devices'),

	url(r'^ignitions/(?P<imei>.+)$', VehicleIdleView.as_view(), name='ignition_details'),
	url(r'^engine_summary/(?P<imei>.+)$', EngineSummaryView.as_view(), name='engine_summary'),


	url(r'^subscription$', SubscriptionView.as_view(), name='subscription'),
	url(r'^devices/(?P<customer_id>.+)$', SubscriptionDeviceListView.as_view(), name = 'device_list'),
	url(r'^device/reports/(?P<customer_id>.+)/(?P<imei>.+)$', ReportView.as_view(), name = 'device_resports'),

	url(r'^global/location/(?P<lng>.+)/(?P<lat>.+)$', GlobalLocationView.as_view(), name='global_location'),
	url(r'^location/(?P<lng>.+)/(?P<lat>.+)$', LocationView.as_view(), name='location'),
	url(r'^location/insert$', LocationInsertView.as_view(), name='location_insert'),

	url(r'^zones/zone/(?P<id>.+)$', ZoneIndividualView.as_view(), name='zone'),
	# url(r'^zones/(?P<customer_id>.+)$', ZoneView.as_view(), name='zones'),
	url(r'^zones/(?P<customer_id>.+)$', GpsObdZoneView.as_view(), name='zones'),
	
	url(r'^zone_groups/zone_group/(?P<id>.+)$', ZoneGroupIndividualView.as_view(), name='zone_group'),
	url(r'^zone_groups/(?P<customer_id>.+)$', ZoneGroupView.as_view(), name='zone_groups'),	
	

	url(r'^trips/filter/(?P<customer_id>.+)/(?P<imei>.+)$', trips.TripsRangeView.as_view(), name='trips_filter'),
	url(r'^trips/list/(?P<customer_id>.+)/(?P<imei>.+)/(?P<date>.+)/(?P<month>.+)/(?P<year>.+)', trips.GetTripListView.as_view(), name='trip_list'),
	url(r'^trips/dates/(?P<customer_id>.+)/(?P<imei>.+)$', trips.GetAvailableDates.as_view(), name='available_trips'),
	url(r'^current/trip/(?P<imei>.+)$', trips.CurrentTripView.as_view(), name = 'current_trip'),
	url(r'^trip/measurements/(?P<measure_id>.+)$', trips.TripMesurementView.as_view(), name='trip_measurement'),
	url(r'^last/trip/(?P<imei>.+)/(?P<customer_id>.+)$', trips.LastTripView.as_view(), name='lst_trip'),
	url(r'^last/7/days/trip/(?P<imei>.+)/(?P<customer_id>.+)$', trips.LastSevenDayTripView.as_view(), name='last_7_days_trip'),
	url(r'^last/30/days/trip/(?P<imei>.+)/(?P<customer_id>.+)$', trips.LastThirtyDayTripView.as_view(), name='last_30_days_trip'),

	url(r'^trip/export$', trip_export_pdf.TripExportApiView.as_view(), name='trip_export_pdf'),

	url(r'^generate/trip/report$', generate_trip_report.GenerateTripReport.as_view(), name='generate_trip_report'),
	url(r'^export/trip/report$', generate_trip_report.ExportTripReport.as_view(), name='export_trip_report'),

	url(r'^trip/backup/dates/(?P<customer_id>.+)/(?P<imei>.+)$', trips.TripBackupAvailableDates.as_view(), name='backup_trip_available_dates'),
	url(r'^trips/backup/list/(?P<customer_id>.+)/(?P<imei>.+)/(?P<date>.+)/(?P<month>.+)/(?P<year>.+)', trips.TripBackupApiView.as_view(), name='trip_list_backup'),
	url(r'^trips/backup/filter/(?P<customer_id>.+)/(?P<imei>.+)$', trips.BackupTripsRangeView.as_view(), name='backup_trips_filter'),
	# BackupTripsRangeView

	#------------------OBD Zones
	url(r'^obd/zones/(?P<customer_id>.+)$', obd_zone.ObdZoneApiView.as_view(), name='zone'),
	url(r'^obd_zones/zone/(?P<id>.+)$', obd_zone.ObdZoneIndividualView.as_view(), name='zones'),

	url(r'^obd/zone/alert$', obd_zone.ObdZoneAlertApiView.as_view(), name='obd_zone_alert'),
	url(r'^obd/zone/ack$', obd_zone.ZoneAlertAckApiView.as_view(), name='obd_zone_ack'),	
	
	#-------------------Zone ALert
	url(r'^zone_alert$', z_alert.ZoneAlertView.as_view(), name='zone_alert'),


	#-------------------Notification Sender
	url(r'^notification/token$', NotificationSenderView.as_view(), name='notification_sender'),
	url(r'^notification/remove/token$', NotificationTokenRemovalView.as_view(), name='notification_sender_remove'),

	#-----------------Events
	url(r'^events/odometer/(?P<customer_id>.+)/(?P<imei>.+)$', odometer.OdometerView.as_view(), name='odometer'),
	url(r'^events/trip/(?P<customer_id>.+)/(?P<imei>.+)$', trip_event.TripEventView.as_view(), name='trip_events'),
	url(r'^events/voltage/(?P<customer_id>.+)/(?P<imei>.+)$', voltage.VoltageView.as_view(), name='voltage_events'),
	url(r'^events/fuel_economy/(?P<customer_id>.+)/(?P<imei>.+)$', fuel_economy.FuelEconomyView.as_view(), name='fuel_events'),
	url(r'^events/harsh_behaviour/(?P<customer_id>.+)/(?P<imei>.+)$', harsh_events.HarshEventView.as_view(), name='harsh_events'),
	url(r'^events/driver_score/(?P<customer_id>.+)/(?P<imei>.+)$', driver_score.DriverScoreView.as_view(), name='fuel_events'),
	url(r'^events/dtc_event/(?P<customer_id>.+)/(?P<imei>.+)$', dtc_event.DtcEventView.as_view(), name='dtc_event'),
	url(r'^events/warning/(?P<customer_id>.+)/(?P<imei>.+)$', dtc_event.ObdDtcEventView.as_view(), name='dtc_warning'),
	url(r'^events/emission/(?P<customer_id>.+)/(?P<imei>.+)$', fuel_emission.EmissionView.as_view(), name='emission'),

	url(r'^events/export/emission$', fuel_emission.EmissionExportApiView.as_view(), name='emission_export'),
	url(r'^events/export/odometer$', odometer.OdometerExportApiView.as_view(), name='odometer_export'),
	url(r'^events/export/voltage$', voltage.VoltageExportApiView.as_view(), name='voltage_export'),
	url(r'^events/export/driver_score$', driver_score.DriverScoreExportApiView.as_view(), name='driver_score_export'),
	url(r'^events/export/warning$', dtc_event.WarningExportApiView.as_view(), name='warning_export'),

	url(r'^events/multiple/dates$', multiple_events.MultipleEventsDate.as_view(), name='multiple_events_date'),
	url(r'^events/multiple/list$', multiple_events.MultipleEventListIndivdualDate.as_view(), name='multiple_events_list'),
	url(r'^events/export$', multiple_events_export.ExportMultipleEventListIndivdualDate.as_view(), name='export_multiple_events'),

	url(r'^report/export/obd$', notifications.ReportExportApiView.as_view(), name='report_export_obd'),
	#---------------Notifications
	# url(r'^notifications/zone/(?P<customer_id>.+)/(?P<imei>.+)$', notifications.NotificationView.as_view(), name='zone_notifications'),
	url(r'^notifications/delete/(?P<id>.+)$', notifications.DeleteNotificationView.as_view(), name='delete_notifications'),
	url(r'^notifications/(?P<customer_id>.+)/(?P<imei>.+)$', notifications.NotificationView.as_view(), name='notifications'),


	#---------------Device Frequency
	url(r'^device_frequency$', device_frequency.UpdateDeviceFrequency.as_view(), name='update_device_frequency'),

	#--------------Individual Tracking
	url(r'^individual_tracking/device/details/(?P<token>.+)$', individual_track.IndividualTrackDeviceDetails.as_view(), name='individual_track_device_details'),
	url(r'^individual_tracking/verify/(?P<token>.+)$', individual_track.ValidateTrackingTokenView.as_view(), name='individual_track_verify'),
	url(r'^individual_tracking/location/(?P<lng>.+)/(?P<lat>.+)$', individual_track.IndividualTrackingLocation.as_view(), name='individual_location'),
	url(r'^individual_tracking/(?P<imei>.+)/(?P<customer_id>.+)$', individual_track.IndividualTrackingView.as_view(), name='individual_track'),


	#-------------Telemetry Obd 
	url(r'^telemetry/obd/(?P<imei>.+)$', telemetry_data.TelemetryObdDataView.as_view(), name='telemetry_obd'),
	url(r'^telemetry/gl/(?P<imei>.+)$', telemetry_data.TelemetryGlDataView.as_view(), name='telemetry_gl'),


	#-------------Odometer Update
	url(r'^odometer/update$', UpdateOdometerView.as_view(), name='odometer_update'),

	#------------Speed Update
	url(r'^speed/update$', UpdateSpeedView.as_view(), name='speed_update'),

	#--------------Device Reboot
	url(r'^reboot/device$', DeviceRebootView.as_view(),name='reboot_device'),

	#-------------Live Location Message
	url(r'^live/location/message$', DeviceLiveLocationView.as_view(), name='live_location'),

	#-------------SMS logs and count
	url(r'^sms/log/(?P<imei>.+)$', GetSmsCount.as_view(), name='sms_logs'),

	#-----------Gps Events
	url(r'^gps/dates/events/(?P<imei>.+)/(?P<customer_id>.+)/(?P<event>.+)$', gps_events.GpsEventsDateView.as_view(), name='gps_date_events'),
	url(r'^gps/events/(?P<imei>.+)/(?P<customer_id>.+)/(?P<event>.+)$', gps_events.GpsEventsView.as_view(), name='gps_events'),


	#-----------Trip Calcuation Manual
	url(r'^generate/trip$', trip_manual_calculation.TripManualCalculation.as_view(), name='genrate_trip'),
	url(r'^frequency/generate/trip$', trips_generate_30_min.TripManualCalculation30MinFreq.as_view(), name='30_min_frequency_trip'),
	url(r'^regenerate/trip$', trip_manual_calculation.RegeneratetripApiView.as_view(), name='regenerate_trip'),

	#----------Buffer Trip Cron
	url(r'^buffer/trip$', trips.BufferTripCron.as_view(), name='buffer_trip_cron'),

	#-----Map settings
	url(r'^map/settings$', MapSettingsUpdate.as_view(), name='map_settings'),

	#-------Cancelled Device List
	url(r'^cancelled/device/list/(?P<customer_id>.+)$', CancelledDeviceListView.as_view(), name='cancelled_device_list'),


	#--------GPX File Reader
	url(r'^gpx/file/upload$', gpx_file_parser.GpxFileParserView.as_view(), name='gpx_file_parser'),

	#---------Generate Fuel Economy Manually
	url(r'^generate/manual/fuel_economy$', fuel_economy_microservice.ManualGenerateFuelEconomy.as_view(), name='generate_manual_fuel_economy'),

	#---------Fuel Economy Micro Service
	url(r'^service/fuel_economy$', fuel_economy_microservice.FuelEconomyMicroService.as_view(), name='fuel_economy_microservice'),
	url(r'^service/fuel_consumption$', fuel_economy_microservice.FuelConsumptionMicroService.as_view(), name='fuel_consumption_microservice'),

	url(r'^fuel_economy/export$', fuel_economy_microservice.EconomyExportApiView.as_view(), name='fuel_consumption_export'),
	
	
	#--------Sim Dignostics
	url(r'^sim/dignostics/(?P<imei>.+)$', dignostics.SimDignosticsApiView.as_view(), name='sim_dignostics'),
	url(r'^sim/location/(?P<imei>.+)$', dignostics.SimLocationApiView.as_view(), name='sim_location'),

	#------- Mongo delete
	url(r'mongo/delete$', MongoDataDelete.as_view(), name="mongo"),
	

]

