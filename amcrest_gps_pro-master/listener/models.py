# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models.signals import post_save as ps
from django.dispatch import receiver
import datetime

class AttachDettach(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=10, blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=4, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'attach_dettach'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class BatteryLow(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    battery_backup_voltage = models.FloatField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'battery_low'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class CrashReport(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'crash_report'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class EngineSummary(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip_mileage = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    journey_fuel_consumption = models.FloatField(blank=True, null=True)
    max_rpm = models.FloatField(blank=True, null=True)
    average_rpm = models.FloatField(blank=True, null=True)
    max_throttle_position = models.FloatField(blank=True, null=True)
    average_throttle_position = models.FloatField(blank=True, null=True)
    max_engine_load = models.FloatField(blank=True, null=True)
    average_engine_load = models.FloatField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    created_date = models.DateTimeField(null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)
    

    def __str__(self):
        return self.imei

    def create_date_object(self, send_date):
        if send_date:
            send_date = str(send_date)
            date_time_fmt = '%Y-%m-%d %H:%M:%S'
            date_time = datetime.datetime.strptime(send_date[:4]+'-'+send_date[4:6]+'-'+send_date[6:8]+' '+send_date[-6:-4]+':'+send_date[-4:-2]+':'+send_date[-2:], date_time_fmt)
            return date_time
        return None

    # def save(self, *args, **kwargs):
    #     # self.created_date = self.create_date_object(self.send_time)
    #     # self.trip_mileage = self.trip_mileage
    #     super(EngineSummary, self).save(*args, **kwargs)

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'engine_summary'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'created_date', 'record_date'])
        ]


class FriMarkers(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    extrnal_power_voltage = models.FloatField(blank=True, null=True)
    report_id = models.CharField(max_length=5, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    hour_meter_count = models.CharField(max_length=15, blank=True, null=True)
    backup_battery_percentage = models.IntegerField(blank=True, null=True)
    device_status = models.CharField(max_length=10, blank=True, null=True)
    engine_rpm = models.FloatField(blank=True, null=True)
    fuel_consumption = models.CharField(max_length=10, blank=True, null=True)
    fuel_level_input = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'fri_markers'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class HarshBehaviour(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    report_type = models.CharField(max_length=3, blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)

    latest_latitude = models.FloatField(blank=True, null=True)
    latest_longitude = models.FloatField(blank=True, null=True)
    latest_altitude = models.FloatField(blank=True, null=True)
    latest_speed = models.FloatField(blank=True, null=True)
    latest_rpm = models.FloatField(blank=True, null=True)
    latest_send_time = models.BigIntegerField(blank=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'harsh_behaviour'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class HarshAcceleration(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    report_type = models.CharField(max_length=3, blank=True, null=True)
    data_status = models.IntegerField(null=True)
    acceleration_x = models.FloatField(null=True)
    acceleration_y = models.FloatField(null=True)
    acceleration_z = models.FloatField(null=True)
    altitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    direction = models.FloatField(blank=True, null=True)
    rpm = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'harsh_acceleration'
        indexes = [
            models.Index(fields=['date', 'imei', 'longitude', 'latitude', 'send_time' ,'protocol', 'record_date'])
        ]


class IgnitionOnoff(models.Model):
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=20, blank=True, null=True)
    duration_of_ignition_off = models.CharField(max_length=20, blank=True, null=True)
    gps_accuracy = models.CharField(max_length=5, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    hour_meter_count = models.CharField(max_length=15, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=5, blank=True, null=True)
    altitude = models.CharField(max_length=50, blank=True, null=True)
    speed = models.CharField(max_length=10, blank=True, null=True)
    fuel_consumption = models.CharField(max_length=50, blank=True, null=True)
    instant_fuel = models.CharField(max_length=50, blank=True, null=True)
    alarm_code = models.IntegerField(null=True)
    external_battery = models.IntegerField(blank=True, null=True)
    engine_coolant_temp = models.IntegerField(blank=True, null=True)
    throttle_position = models.IntegerField(blank=True, null=True)
    remain_fuel = models.IntegerField(blank=True, null=True)
    air_input = models.FloatField(null=True, blank=True)
    air_inflow_temperature = models.FloatField(null=True, blank=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    fuel_level_input = models.FloatField(blank=True, null=True)
    engine_rpm = models.FloatField(blank=True, null=True)
    engine_load = models.FloatField(blank=True, null=True)
    obd_power_voltage = models.FloatField(blank=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'ignition_onoff'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class IdleDevice(models.Model):
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=20, blank=True, null=True)
    duration_of_ignition_off = models.CharField(max_length=20, blank=True, null=True)
    gps_accuracy = models.CharField(max_length=5, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    hour_meter_count = models.CharField(max_length=15, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=5, blank=True, null=True)
    altitude = models.CharField(max_length=50, blank=True, null=True)
    speed = models.CharField(max_length=10, blank=True, null=True)
    fuel_consumption = models.CharField(max_length=50, blank=True, null=True)
    instant_fuel = models.CharField(max_length=50, blank=True, null=True)
    alarm_code = models.IntegerField(null=True)
    external_battery = models.IntegerField(blank=True, null=True)
    engine_coolant_temp = models.IntegerField(blank=True, null=True)
    throttle_position = models.IntegerField(blank=True, null=True)
    remain_fuel = models.IntegerField(blank=True, null=True)
    air_input = models.FloatField(null=True, blank=True)
    air_inflow_temperature = models.FloatField(null=True, blank=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'idle_time'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class ObdMarkers(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=15, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    obd_connection = models.IntegerField(blank=True, null=True)
    obd_power_voltage = models.FloatField(blank=True, null=True)
    supported_pid = models.CharField(max_length=10, blank=True, null=True)
    engine_rpm = models.FloatField(blank=True, null=True)
    vehicle_speed = models.FloatField(blank=True, null=True)
    engine_coolant_temp = models.FloatField(blank=True, null=True)
    fuel_consumption = models.CharField(max_length=10, blank=True, null=True)
    dtc_cleared_distance = models.FloatField(blank=True, null=True)
    mil_activated_distance = models.FloatField(blank=True, null=True)
    mil_status = models.IntegerField(blank=True, null=True)
    number_of_dtc = models.IntegerField(blank=True, null=True)
    dignostic_trouble_codes = models.CharField(max_length=6, blank=True, null=True)
    throttle_position = models.FloatField(blank=True, null=True)
    engine_load = models.FloatField(blank=True, null=True)
    fuel_level_input = models.FloatField(blank=True, null=True)
    obd_protocol = models.CharField(max_length=1, blank=True, null=True)
    obd_mileage = models.FloatField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=6, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)

    instant_fuel_consumption = models.FloatField(blank=True, null=True)
    over_speed = models.FloatField(blank=True, null=True)
    air_pressure = models.FloatField(blank=True, null=True)
    cooling_fluid_temperature = models.FloatField(blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True)
    duration_of_ignition_on = models.FloatField(blank=True, null=True)
    duration_of_ignition_off = models.FloatField(blank=True, null=True)

    air_input = models.FloatField(null=True, blank=True)
    air_inflow_temperature = models.FloatField(null=True, blank=True)

    external_battery = models.IntegerField(blank=True, null=True)
    remain_fuel = models.IntegerField(blank=True, null=True)
    data_status = models.IntegerField(blank=True, null=True)
    device_status = models.CharField(max_length=100 ,blank=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'obd_markers'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'engine_rpm', 'vehicle_speed', 'engine_coolant_temp', 'fuel_consumption', 'throttle_position', 'engine_load', 'record_date'])
        ]


# @receiver(ps, sender=ObdMarkers)
# def update_ObdMarkers(sender, instance=None, created=False, **kwargs):
#     if created:
#         for i in range(100):
#             # print(i)
#             pass


class ObdStatusReport(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    obd_connection = models.IntegerField(blank=True, null=True)
    obd_power_voltage = models.FloatField(blank=True, null=True)
    supported_pid = models.CharField(max_length=10, blank=True, null=True)
    engine_rpm = models.FloatField(blank=True, null=True)
    vehicle_speed = models.FloatField(blank=True, null=True)
    engine_coolant_temp = models.FloatField(blank=True, null=True)
    fuel_consumption = models.CharField(max_length=10, blank=True, null=True)
    dtc_cleared_distance = models.FloatField(blank=True, null=True)
    mil_activated_distance = models.FloatField(blank=True, null=True)
    mil_status = models.IntegerField(blank=True, null=True)
    number_of_dtc = models.IntegerField(blank=True, null=True)
    dignostic_trouble_codes = models.CharField(max_length=6, blank=True, null=True)
    throttle_position = models.FloatField(blank=True, null=True)
    engine_load = models.FloatField(blank=True, null=True)
    fuel_level_input = models.FloatField(blank=True, null=True)
    obd_protocol = models.CharField(max_length=1, blank=True, null=True)
    obd_mileage = models.FloatField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=6, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'obd_status_report'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'obd_protocol', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]





class SttMarkers(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    report_name = models.CharField(max_length=20, null=True, blank=True)
    protocol_version = models.CharField(max_length=8, null=True, blank=True)
    imei = models.CharField(max_length=20, null=True, blank=True)
    device_name = models.CharField(max_length=50, null=True, blank=True)
    state = models.IntegerField(null=True)
    gps_accuracy = models.CharField(max_length=2, null=True, blank=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=4, null=True, blank=True)
    altitude = models.CharField(max_length=8, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time= models.CharField(max_length=20, blank=True, null=True)
    mcc = models.CharField(max_length=4, blank=True, null=True)
    mnc = models.CharField(max_length=4, blank=True, null=True)
    lac = models.CharField(max_length=4, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=10, blank=True, null=True)
    location_status = models.IntegerField(blank=True, null=True, default=0)
    alert_status = models.IntegerField(blank=True, null=True, default=0)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'stt_markers'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'record_date']),
            models.Index(fields=['send_time', 'imei']),
            models.Index(fields=['longitude', 'latitude']),
            models.Index(fields=['send_time', 'imei', 'longitude', 'latitude']),
            models.Index(fields=['record_date', 'imei']),
            models.Index(fields=['report_name', 'imei']),
            models.Index(fields=['imei']),
            models.Index(fields=['send_time']),
        ]




class SttMarkersBackup(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    report_name = models.CharField(max_length=20, null=True, blank=True)
    protocol_version = models.CharField(max_length=8, null=True, blank=True)
    imei = models.CharField(max_length=20, null=True, blank=True)
    device_name = models.CharField(max_length=50, null=True, blank=True)
    state = models.IntegerField(null=True)
    gps_accuracy = models.CharField(max_length=2, null=True, blank=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=4, null=True, blank=True)
    altitude = models.CharField(max_length=8, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time= models.CharField(max_length=20, blank=True, null=True)
    mcc = models.CharField(max_length=4, blank=True, null=True)
    mnc = models.CharField(max_length=4, blank=True, null=True)
    lac = models.CharField(max_length=4, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=10, blank=True, null=True)
    location_status = models.IntegerField(blank=True, null=True, default=0)
    alert_status = models.IntegerField(blank=True, null=True, default=0)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'stt_markers_backup'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'record_date'])
        ]



class BatteryModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    report_name = models.CharField(max_length=20, null=True, blank=True)
    protocol_version = models.CharField(max_length=8, null=True, blank=True)
    imei = models.CharField(max_length=20, null=True, blank=True)
    device_name = models.CharField(max_length=50, null=True, blank=True)
    gps_accuracy = models.CharField(max_length=2, null=True, blank=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=4, null=True, blank=True)
    altitude = models.CharField(max_length=8, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    mcc = models.CharField(max_length=4, blank=True, null=True)
    mnc = models.CharField(max_length=4, blank=True, null=True)
    lac = models.CharField(max_length=4, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    location_status = models.IntegerField(blank=True, null=True)
    alert_status = models.IntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'battery_onoff'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'gps_accuracy', 'speed', 'record_date'])
        ]


class Power(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    report_name = models.CharField(max_length=20, null=True, blank=True) 
    protocol_version = models.CharField(max_length=8, null=True, blank=True)
    imei = models.CharField(max_length=20, null=True, blank=True)
    device_name = models.CharField(max_length=50, null=True, blank=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    alert_status = models.IntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'power_onoff'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'record_date' ])
        ]


class SOS(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    report_name = models.CharField(max_length=20, null=True, blank=True) 
    protocol_version = models.CharField(max_length=8, null=True, blank=True)
    imei = models.CharField(max_length=20, null=True, blank=True)
    device_name  = models.CharField(max_length=50, null=True, blank=True)
    report_type  = models.CharField(max_length=2, null=True, blank=True)
    report_id  = models.CharField(max_length=2, null=True, blank=True)
    number  = models.CharField(max_length=3, null=True, blank=True)
    gps_accuracy  = models.CharField(max_length=3, null=True, blank=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=4, null=True, blank=True)
    altitude = models.CharField(max_length=8, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=20, blank=True, null=True)
    mcc = models.CharField(max_length=4, blank=True, null=True)
    mnc = models.CharField(max_length=4, blank=True, null=True)
    lac = models.CharField(max_length=4, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    battery_percentage = models.CharField(max_length=5, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    alert_status = models.IntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'sos_markers'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'gps_utc_time', 'speed', 'longitude', 'latitude', 'record_date'])
        ]



class GLFriMarkers(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    report_name = models.CharField(max_length=20, blank=True, null=True)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    report_id = models.CharField(max_length=5, blank=True, null=True)
    report_type = models.CharField(max_length=5, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=5, blank=True, null=True)
    altitude = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mcc = models.CharField(max_length=5, blank=True, null=True)
    mnc = models.CharField(max_length=5, blank=True, null=True)
    lac = models.CharField(max_length=5, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    battery_percentage = models.IntegerField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    location_status = models.IntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.imei

    class Meta:
        app_label = 'listener'
        db_table = 'gl_fri_markers'
        indexes = [
            models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time', 'record_date']),
            models.Index(fields=['send_time', 'imei', 'gps_accuracy']),
            models.Index(fields=['longitude', 'latitude']),
            models.Index(fields=['send_time', 'imei', 'longitude', 'latitude', 'gps_accuracy']),
            models.Index(fields=['send_time', 'imei', 'gps_accuracy', 'record_date', 'report_name']),
            models.Index(fields=['imei', 'gps_accuracy', 'record_date', 'report_name']),
            models.Index(fields=['send_time', 'imei']),
            models.Index(fields=['record_date', 'imei']),
        ]



class GLFriMarkersBackup(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    report_name = models.CharField(max_length=20, blank=True, null=True)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    report_id = models.CharField(max_length=5, blank=True, null=True)
    report_type = models.CharField(max_length=5, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    gps_accuracy = models.IntegerField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    azimuth = models.CharField(max_length=5, blank=True, null=True)
    altitude = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mcc = models.CharField(max_length=5, blank=True, null=True)
    mnc = models.CharField(max_length=5, blank=True, null=True)
    lac = models.CharField(max_length=5, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    battery_percentage = models.IntegerField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    location_status = models.IntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.imei

    class Meta:
        app_label = 'listener'
        db_table = 'gl_fri_markers_backup'
        indexes = [
            models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time', 'record_date'])
        ]



class TripProtocolRecord(models.Model):
    imei = models.CharField(max_length=20, null=True, blank=True)
    protocol = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        app_label = 'listener'
        db_table = 'trip_protocol_recorder'
        indexes = [
            models.Index(fields=['imei', 'protocol'])
        ]



class AlertRecords(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    vin = models.CharField(max_length=20, null=True, blank=True)
    device_name = models.CharField(max_length=15, null=True, blank=True)
    gps_accuracy = models.IntegerField(blank=True, null=True) 
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    tail = models.CharField(max_length=5, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    protocol = models.CharField(max_length=20, blank=True, null=True)
    report_id = models.CharField(max_length=5, blank=True, null=True)
    number = models.CharField(max_length=5, blank=True, null=True)
    azimuth = models.CharField(max_length=5, blank=True, null=True)
    altitude = models.CharField(max_length=10, blank=True, null=True)
    mcc = models.CharField(max_length=5, blank=True, null=True)
    mnc = models.CharField(max_length=5, blank=True, null=True)
    lac = models.CharField(max_length=5, blank=True, null=True)
    ceil_id = models.CharField(max_length=20, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    alarm_code = models.IntegerField(null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        app_label = 'listener'
        db_table = 'alert_records'
        indexes = [
            models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time', 'record_date'])
        ]


# {'details': {'date': '05/08/2019', 'time': '21:13:47', 'protocol_version': '360100', 'imei': '135790246811220', 'vin': '1G1JC5444R7252367', 'device_name': None, 'gps_accuracy': '1', 'speed': '4.3', 'longitude': '121.354335', 'latitude': '31.222073', 'gps_utc_time': '20090214013254', 
# 'send_time': '20090214093254', 'count_number': '11F0', 'mileage': '2000.0', 'protocol': '+RESP:GTTOW'}, 'imei': '135790246811220', 'protocol': '+RESP:GTTOW'}


class DTCRecords(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    count_number = models.CharField(max_length=6, blank=True, null=True)
    imei = models.CharField(max_length=20)
    sae_standard = models.CharField(max_length=20, blank=True, null=True)
    error_code = models.CharField(max_length=10, blank=True, null=True)
    error_code_status = models.IntegerField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    vin_number = models.CharField(max_length=50, null=True, blank=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        app_label = 'listener'
        db_table = 'dignosis_trouble_code'
        indexes = [
            models.Index(fields=['date', 'imei', 'send_time', 'record_date'])
        ]


class OBDTCRecords(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol = models.CharField(max_length=40, blank=True, null=True)
    count_number = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=40, blank=True, null=True)
    imei = models.CharField(max_length=20)
    warning_code = models.CharField(max_length=40, blank=True, null=True)
    warning_value = models.CharField(max_length=40, blank=True, null=True)
    warning_details = models.CharField(max_length=240, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.imei

    class Meta:
        app_label = 'listener'
        db_table = 'obd_dignosis_trouble_code'
        indexes = [
            models.Index(fields=['date', 'imei', 'send_time', 'record_date'])
        ]


class SpeedAlertObd(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    report_type = models.CharField(max_length=3, blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'speed_alert_obd'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class GeoFenceObd(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    report_type = models.CharField(max_length=3, blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_utc_time = models.CharField(max_length=14, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)
    source_ip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.imei

    class Meta:
        # managed = False
        app_label = 'listener'
        db_table = 'geofence_obd'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time' ,'protocol', 'record_date'])
        ]


class GeoFenceAck(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    protocol_version = models.CharField(max_length=10, blank=True, null=True)
    imei = models.CharField(max_length=20)
    device_name = models.CharField(max_length=15, blank=True, null=True)
    geo_id = models.CharField(max_length=5, blank=True, null=True)
    send_time = models.BigIntegerField(blank=True, null=True)
    count_number = models.CharField(max_length=10, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    record_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.imei


    class Meta:
        app_label = 'listener'
        db_table = 'geofence_obd_ack'
        indexes = [
            models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'protocol', 'record_date'])
        ]


