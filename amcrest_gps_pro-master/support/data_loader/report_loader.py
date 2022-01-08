import pymysql
import requests
import json


def load_report(customer_id):
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
        return {"status":True, "error":error, "message":"DB Connection Error"}

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `reports` WHERE user_id={};".format(customer_id)
        cursor.execute(sql)
        result = cursor.fetchall()

        headers = {
            "Content-Type": "application/json"
        }
        
        for i in result:
            date_time = str(i.get('datetime', None))
            date_time = date_time[:4]+'-'+date_time[4:6]+'-'+date_time[6:8]+' '+date_time[-6:-4]+':'+date_time[-4:-2]+':'+date_time[-2:]
            
            if i.get('notification_sent', None):
                sent_notification = notification_sent_obj.get(str(i.get('notification_sent', None)), None)
            else:
                sent_notification = False
                
            user_obj = {
                "imei" : i.get('imei', None),
                "device_name" : i.get('devicename', None),
                "alert_name" : i.get('alert_name', None),
                "event_type" : i.get('event_type', None),
                "battery_percentage" : i.get('battery_percentage', None),
                "location" : i.get('location', None),
                "longitude" : i.get('longitude', None),
                "latitude" : i.get('latitude', None),
                "speed" : i.get('speed', None),
                "type" : i.get('type', None),
                "notification_sent" : sent_notification,
                "record_date_timezone" : date_time,
            }

            endpoint = "https://api.amcrestgps.net/info/load/report"
            r = requests.post(url = endpoint, data = json.dumps(user_obj), headers=headers)

            if str(r.status_code) == "200":
                pass
            else:
                error.append(customer_id)
    connection.close()
    return {"success":True, "error":error, "message":"Report Migration"}



    