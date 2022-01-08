from rest_framework import serializers
from listener.models import *
from django.conf import settings
# from rest_framework_mongoengine.serializers import *



class AttachDettachSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = AttachDettach
    	fields = '__all__'




class BatteryLowSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    battery_backup_voltage = serializers.FloatField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = BatteryLow
    	fields = '__all__'


class CrashReportSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = CrashReport
    	fields = '__all__'


class EngineSummarySerializer(serializers.ModelSerializer):
    trip_mileage = serializers.FloatField(required=False, allow_null=False)
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    journey_fuel_consumption = serializers.FloatField(required=False, allow_null=True)
    max_rpm = serializers.FloatField(required=False, allow_null=True)
    average_rpm = serializers.FloatField(required=False, allow_null=True)
    max_throttle_position = serializers.FloatField(required=False, allow_null=True)
    average_throttle_position = serializers.FloatField(required=False, allow_null=True)
    max_engine_load = serializers.FloatField(required=False, allow_null=True)
    average_engine_load = serializers.FloatField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    

    class Meta:
    	model = EngineSummary
    	fields = '__all__'

    def create(self, validated_data):
        return EngineSummary.objects.create(**validated_data)


class FriMarkersSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extrnal_power_voltage = serializers.FloatField(required=False, allow_null=True)
    report_id = serializers.CharField(max_length=2, required=False, allow_blank=True, allow_null=True)
    number = serializers.IntegerField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    hour_meter_count = serializers.CharField(max_length=11, required=False, allow_blank=True, allow_null=True)
    backup_battery_percentage = serializers.IntegerField(required=False, allow_null=True)
    device_status = serializers.CharField(max_length=6, required=False, allow_blank=True, allow_null=True)
    engine_rpm = serializers.FloatField(required=False, allow_null=True)
    fuel_consumption = serializers.CharField(max_length=5, required=False, allow_blank=True, allow_null=True)
    fuel_level_input = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = FriMarkers
    	fields = '__all__'


class HarshBehaviourSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_type = serializers.CharField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    latest_latitude = serializers.FloatField(required=False, allow_null=True)
    latest_longitude = serializers.FloatField(required=False, allow_null=True)
    latest_altitude =serializers.FloatField(required=False, allow_null=True)
    latest_speed = serializers.FloatField(required=False, allow_null=True)
    latest_rpm = serializers.FloatField(required=False, allow_null=True)
    latest_send_time = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = HarshBehaviour
    	fields = '__all__'


class HarshAccelerationSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    data_status = serializers.IntegerField(required=False, allow_null=True)
    acceleration_x = serializers.FloatField(required=False, allow_null=True)
    acceleration_y = serializers.FloatField(required=False, allow_null=True)
    acceleration_z = serializers.FloatField(required=False, allow_null=True)
    altitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    direction = serializers.FloatField(required=False, allow_null=True)
    rpm = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    record_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = HarshAcceleration
        fields = '__all__'


class IgnitionOnoffSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duration_of_ignition_off = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gps_accuracy = serializers.CharField(max_length=2, required=False, allow_blank=True, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    hour_meter_count = serializers.CharField(max_length=11, required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    alarm_code = serializers.IntegerField(required=False, allow_null=True)
    altitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    speed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fuel_consumption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instant_fuel = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    external_battery = serializers.IntegerField(required=False, allow_null=True)
    engine_coolant_temp = serializers.IntegerField(required=False, allow_null=True)
    throttle_position = serializers.IntegerField(required=False, allow_null=True)
    remain_fuel = serializers.IntegerField(required=False, allow_null=True)

    air_input = serializers.FloatField(required=False, allow_null=True)
    air_inflow_temperature = serializers.FloatField(required=False, allow_null=True)
    engine_rpm = serializers.FloatField(required=False, allow_null=True)
    fuel_level_input = serializers.FloatField(required=False, allow_null=True)
    engine_load = serializers.FloatField(required=False, allow_null=True)
    obd_power_voltage = serializers.FloatField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = IgnitionOnoff
    	fields = '__all__'



class IdleDeviceSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duration_of_ignition_off = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gps_accuracy = serializers.CharField(max_length=2, required=False, allow_blank=True, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    hour_meter_count = serializers.CharField(max_length=11, required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    alarm_code = serializers.IntegerField(required=False, allow_null=True)
    altitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    speed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fuel_consumption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instant_fuel = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    external_battery = serializers.IntegerField(required=False, allow_null=True)
    engine_coolant_temp = serializers.IntegerField(required=False, allow_null=True)
    throttle_position = serializers.IntegerField(required=False, allow_null=True)
    remain_fuel = serializers.IntegerField(required=False, allow_null=True)

    air_input = serializers.FloatField(required=False, allow_null=True)
    air_inflow_temperature = serializers.FloatField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = IdleDevice
        fields = '__all__'
    
        

class ObdMarkersSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    obd_connection = serializers.IntegerField(required=False, allow_null=True)
    obd_power_voltage = serializers.FloatField(required=False, allow_null=True)
    supported_pid = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    engine_rpm = serializers.FloatField(required=False, allow_null=True)
    vehicle_speed = serializers.FloatField(required=False, allow_null=True)
    engine_coolant_temp = serializers.FloatField(required=False, allow_null=True)
    fuel_consumption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dtc_cleared_distance = serializers.FloatField(required=False, allow_null=True)
    mil_activated_distance = serializers.FloatField(required=False, allow_null=True)
    mil_status = serializers.IntegerField(required=False, allow_null=True)
    number_of_dtc = serializers.IntegerField(required=False, allow_null=True)
    dignostic_trouble_codes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    throttle_position = serializers.FloatField(required=False, allow_null=True)
    engine_load = serializers.FloatField(required=False, allow_null=True)
    fuel_level_input = serializers.FloatField(required=False, allow_null=True)
    obd_protocol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    obd_mileage = serializers.FloatField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=False)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    instant_fuel_consumption = serializers.FloatField(required=False, allow_null=True)
    over_speed = serializers.FloatField(required=False, allow_null=True)
    air_pressure = serializers.FloatField(required=False, allow_null=True)
    cooling_fluid_temperature = serializers.FloatField(required=False, allow_null=True)
    altitude = serializers.FloatField(required=False, allow_null=True)
    duration_of_ignition_on = serializers.FloatField(required=False, allow_null=True)
    duration_of_ignition_off = serializers.FloatField(required=False, allow_null=True)

    external_battery = serializers.IntegerField(required=False, allow_null=True)
    remain_fuel = serializers.IntegerField(required=False, allow_null=True)
    data_status = serializers.IntegerField(required=False, allow_null=True)
    device_status = serializers.CharField(required=False, allow_null=True)

    air_input = serializers.FloatField(required=False, allow_null=True)
    air_inflow_temperature = serializers.FloatField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = ObdMarkers
    	fields = '__all__'


class ObdStatusReportSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    obd_connection = serializers.IntegerField(required=False, allow_null=True)
    obd_power_voltage = serializers.FloatField(required=False, allow_null=True)
    supported_pid = serializers.CharField(max_length=8, required=False, allow_blank=True, allow_null=True)
    engine_rpm = serializers.FloatField(required=False, allow_null=True)
    vehicle_speed = serializers.FloatField(required=False, allow_null=True)
    engine_coolant_temp = serializers.FloatField(required=False, allow_null=True)
    fuel_consumption = serializers.CharField(max_length=5, required=False, allow_blank=True, allow_null=True)
    dtc_cleared_distance = serializers.FloatField(required=False, allow_null=True)
    mil_activated_distance = serializers.FloatField(required=False, allow_null=True)
    mil_status = serializers.IntegerField(required=False, allow_null=True)
    number_of_dtc = serializers.IntegerField(required=False, allow_null=True)
    dignostic_trouble_codes = serializers.CharField(max_length=6, required=False, allow_blank=True, allow_null=True)
    throttle_position = serializers.FloatField(required=False, allow_null=True)
    engine_load = serializers.FloatField(required=False, allow_null=True)
    fuel_level_input = serializers.FloatField(required=False, allow_null=True)
    obd_protocol = serializers.CharField(max_length=1, required=False, allow_blank=True, allow_null=True)
    obd_mileage = serializers.FloatField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
    	model = ObdStatusReport
    	fields = '__all__'




class SttMarkersSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    state = serializers.IntegerField(required=False, allow_null=True)
    gps_accuracy = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time= serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location_status = serializers.IntegerField(required=False, allow_null=True)
    alert_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SttMarkers
        fields = '__all__'



class SttMarkersBackupSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    state = serializers.IntegerField(required=False, allow_null=True)
    gps_accuracy = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time= serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location_status = serializers.IntegerField(required=False, allow_null=True)
    alert_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SttMarkersBackup
        fields = '__all__'



class BatteryModelSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gps_accuracy = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location_status = serializers.IntegerField(required=False, allow_null=True)
    alert_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = BatteryModel
        fields = '__all__'


class PowerSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True) 
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    alert_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Power
        fields = '__all__'


class SOSSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True) 
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_type  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_id  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    number  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gps_accuracy  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    battery_percentage = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    alert_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SOS
        fields = '__all__'



class GLFriMarkersSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    number = serializers.IntegerField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_null=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    battery_percentage = serializers.IntegerField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = GLFriMarkers
        fields = '__all__'


class GLFriMarkersBackupSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    number = serializers.IntegerField(required=False, allow_null=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_null=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    battery_percentage = serializers.IntegerField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location_status = serializers.IntegerField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = GLFriMarkersBackup
        fields = '__all__'


class AlertRecordsSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    protocol_version = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    imei = serializers.CharField(required=True)
    vin = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gps_accuracy = serializers.IntegerField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    tail = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    protocol = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    report_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    azimuth = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    altitude = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mnc = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lac = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    ceil_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    record_date = serializers.DateTimeField(required=False, allow_null=True)
    source_ip = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = AlertRecords
        fields = '__all__'


class DTCRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DTCRecords
        fields = '__all__'


class OBDTCRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OBDTCRecords
        fields = '__all__'
        

class SpeedAlerObdSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_type = serializers.CharField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SpeedAlertObd
        fields = '__all__'


class GeoFenceObdSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    protocol_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    imei = serializers.CharField(required=True)
    device_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_type = serializers.CharField(required=False, allow_null=True)
    speed = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    gps_utc_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mileage = serializers.FloatField(required=False, allow_null=True)
    send_time = serializers.IntegerField(required=False, allow_null=True)
    count_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = GeoFenceObd
        fields = '__all__'


class GeoFenceAckSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoFenceAck
        fields = '__all__'

#---------------------Telemetry Data
class AttachDettachTelimetry(serializers.ModelSerializer):
    class Meta:
        model = AttachDettach
        fields = ['date', 'time', 'protocol_version','imei','device_name','gps_accuracy','speed','longitude','latitude','gps_utc_time','send_time','protocol', 'record_date']


class BatteryLowTelimetry(serializers.ModelSerializer):
    class Meta:
        model = BatteryLow
        fields = ['date','time','imei','device_name','battery_backup_voltage','gps_accuracy','speed','longitude','latitude','gps_utc_time','send_time','protocol']


class CrashReportTelimetry(serializers.ModelSerializer):
    class Meta:
        model = CrashReport
        fields = ['date','time','imei','device_name','gps_accuracy','speed','longitude','latitude','gps_utc_time','send_time','count_number','protocol']

class EngineSummaryTelimetry(serializers.ModelSerializer):
    class Meta:
        model = EngineSummary
        fields = ['date', 'time','imei' ,'device_name', 'journey_fuel_consumption','max_rpm','average_rpm','max_throttle_position','average_throttle_position','max_engine_load','average_engine_load', 'gps_accuracy','speed','longitude','latitude','gps_utc_time','mileage','send_time','protocol']


class FriMarkersTelimetry(serializers.ModelSerializer):
    class Meta:
        model = FriMarkers
        fields = ['date', 'imei','device_name','extrnal_power_voltage','gps_accuracy','speed','longitude','latitude','gps_utc_time','mileage','backup_battery_percentage','device_status','engine_rpm','fuel_consumption','fuel_level_input','send_time','protocol']

class HarshBehaviourTelimetry(serializers.ModelSerializer):
    class Meta:
        model = HarshBehaviour
        fields = ['date' ,'time', 'imei','device_name','report_type','speed','longitude','latitude','gps_utc_time','mileage','send_time','protocol']

class IgnitionOnoffTelimetry(serializers.ModelSerializer):
    class Meta:
        model = IgnitionOnoff
        fields = ['date','time','protocol','imei','device_name','duration_of_ignition_off','gps_accuracy','longitude','latitude','gps_utc_time','mileage','send_time']

class ObdMarkersTelimetry(serializers.ModelSerializer):
    class Meta:
        model = ObdMarkers
        fields = ['date', 'time', 'imei','device_name','obd_power_voltage','engine_rpm','vehicle_speed','engine_coolant_temp','fuel_consumption','dtc_cleared_distance','mil_activated_distance','mil_status','engine_load','fuel_level_input','obd_mileage','gps_accuracy','speed','longitude','latitude','gps_utc_time','mileage','send_time','protocol']






class SttMarkersTelimetry(serializers.ModelSerializer):
    state = serializers.IntegerField(required=False)
    class Meta:
        model = SttMarkers
        fields = ['date','time','report_name','imei','device_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','send_time', 'state']

class SttMarkersBackupTelimetry(serializers.ModelSerializer):
    state = serializers.IntegerField(required=False)
    class Meta:
        model = SttMarkersBackup
        fields = ['date','time','report_name','imei','device_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','send_time', 'state']


class BatteryModelTelimetry(serializers.ModelSerializer):
    class Meta:
        model = BatteryModel
        fields = ['date','time','report_name','imei','device_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','send_time']

class PowerTelimetry(serializers.ModelSerializer):
    class Meta:
        model = Power
        fields = ['date','time','report_name','imei','device_name','send_time']


class SOSTelimetry(serializers.ModelSerializer):
    class Meta:
        model = SOS
        fields = ['date','time','report_name','imei','device_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','battery_percentage','send_time']


class GLFriMarkersTelimetry(serializers.ModelSerializer):
    class Meta:
        model = GLFriMarkers
        fields = ['date','time','protocol_version','imei','device_name','report_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','battery_percentage','send_time'] 

class GLFriMarkersBackupTelimetry(serializers.ModelSerializer):
    class Meta:
        model = GLFriMarkersBackup
        fields = ['date','time','protocol_version','imei','device_name','report_name','gps_accuracy','speed','azimuth','altitude','longitude','latitude','gps_utc_time','mcc','mnc','lac','mileage','battery_percentage','send_time'] 



class TripProtocolRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripProtocolRecord
        fields = '__all__'