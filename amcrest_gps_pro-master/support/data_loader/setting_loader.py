import pymysql
import requests
import json


def load_setting(customer_id):
    error = []
    try:
        connection = pymysql.connect(
						host="206.198.230.28",
	                    user="amcrestg_amcgpsu",
	                    password="CH]u{A92pai2",
	                    db="amcrestg_gpsamcr",
	                    cursorclass=pymysql.cursors.DictCursor)
    except(Exception)as e:
        error.append(customer_id)
        return {"status":False, "error":error, "message":"DB Connection Error"}

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `settings` WHERE gps_id={};".format(customer_id)
        cursor.execute(sql)
        result = cursor.fetchall()

        headers = {
        	"Content-Type": "application/json"
        }
        
        for i in result:
        	user_obj = {
        		"customer_id":i.get('gps_id', None),
        		"device_reporting_frequency" : i.get('device_reporting_frequency', '60_sec'),
        		"device_reporting_frequency_desc": i.get('device_reporting_frequency_desc', '60 seconds device frequency'),
        		"imei": i.get('imei', None),
        		"email":i.get("motion_email"),
        		"phone":i.get("motion_phone"),
    			"trip_notification": True,
    			"trip_email": False,
    			"trip_sms": False,
    			"engine_notification": False,
    			"speed_limit": i.get('speed', None),
    			"speed_notification": True,
    			"speed_sms": False,
    			"speed_email": False,
    			"zone_alert_notification": True,
    			"zone_alert_sms": i.get('sms', None),
    			"zone_alert_email": i.get('email', None),
    			"sos_notification": True,
    			"sos_sms": False,
    			"sos_email": False,
    			"charging_notification": True,
    			"charging_sms": False,
    			"charging_email": False,
    			"power_notification": True,
    			"battery_low_limit": i.get('battery_percentage', None),
    			"battery_notification": False,
    			"battery_email": False,
    			"battery_sms": False,
    			"device_name": i.get('device_name', None),
        	}

        	endpoint = "https://api.amcrestgps.net/info/load/settings"
        	r = requests.post(url = endpoint, data = json.dumps(user_obj), headers=headers)
        	if str(r.status_code) == "200":
	        	pass
	        else:
	        	error.append(customer_id)
    connection.close()
    return {"success":True, "error":error, "message":"Settings Migration"}