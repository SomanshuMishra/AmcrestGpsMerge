import pymysql
import requests
import json


def load_zone(customer_id):
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
	    sql = "SELECT * FROM `zone` WHERE user_id={}".format(customer_id)
	    cursor.execute(sql)
	    result = cursor.fetchall()

	    headers = {
	    	"Content-Type": "application/json"
	    }
	    
	    for i in result:
	    	co = json.loads(i.get('coordinates'))

	    	if i.get('coordinates'):
	    		co = json.loads(i.get('coordinates'))
	    		co = json.dumps(co.get('coordinatesList'))
	    		
		    	user_obj = {
		    		"id":i.get('id', None),
		    		"name" : i.get('name', None),
					"coordinates" : co,
					"type" : i.get('type', None),
					"customer_id" : i.get('user_id', None),
					"status" : i.get('status', None)
		    	}
		    	zone_alert_sql = "SELECT * FROM `zone_alert` WHERE zone_id="+str(i.get('id', None))
		    	cursor.execute(zone_alert_sql)
		    	za_result = cursor.fetchall()
		    	user_obj['zone_alert'] = []
		    	if za_result:
		    		for j in za_result:
		    			za_obj = {
		    				'name': j.get('alert_name', None),
							'type': j.get('type', None),
							'customer_id': j.get('user_id', None),
							'email_one': j.get('email1', None),
							'phone_one': j.get('phone1', None),
							'email_two': j.get('email2', None),
							'phone_two': j.get('phone2', None),
							'imei': j.get('imei_number', None)
		    			}
		    			user_obj['zone_alert'].append(za_obj)
		    			
		    	endpoint = "https://api.amcrestgps.net/info/load/zone"
		    	r = requests.post(url = endpoint, data = json.dumps(user_obj), headers=headers)
		    	if str(r.status_code) == "200":
		    		pass
		    	else:
		    		error.append(customer_id)
	connection.close()
	return {"success":True, "error":error, "message":"Zone Migration"}