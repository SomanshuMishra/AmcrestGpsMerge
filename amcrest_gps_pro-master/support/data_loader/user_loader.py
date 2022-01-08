import pymysql
import requests
import json

def load_user(customer_id):
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

	uom = {
		"1":"kms",
		"2":"miles"
	}
	with connection.cursor() as cursor:
	    sql = "SELECT * FROM `amcrest_gps` WHERE gps_customer_id={};".format(customer_id)
	    cursor.execute(sql)
	    result = cursor.fetchall()

	    headers = {
	    	"Content-Type": "application/json"
	    }
	    
	    for i in result:
	    	try:
	    		_uom = uom.get(i.get("uom", None), 'kms')
	    	except(Exception)as e:
	    		_uom = 'kms'
	    		
	    	user_obj = {
	    		"first_name": i.get("gps_fname", None),
				"last_name": i.get("gps_lname", None),
				"email": i.get("gps_email", None),
				"phone_number": i.get("gps_phone", None),
				"password": 'amcrestgps',
				"order_id": i.get("gps_orderid", None),
				"address": i.get("gps_address", None),
				"city": i.get("gps_city", None),
				"state": i.get("gps_state", None),
				"zip": i.get("gps_zip", None),
				"country": i.get("gps_country", None),
				"status": i.get("gps_status", None),
				"company": i.get("gps_company", None),
				"customer_id": i.get("gps_customer_id", None),
				"subscription_id": i.get("gps_subscription_id", None),
				"transaction_id": i.get("gps_transaction_id", None),
				"assetname": i.get("gps_assetname", None),
				"subscription_status": i.get("subscription_status", None),
				"topic_id": i.get("topic_id", None),
				"time_zone": i.get("time_zone", None),
				"language": i.get("language", None),
				"uom": _uom,
				"hits": i.get("hits", None),
				"rate": i.get("rate", None),
				"later_time": i.get("later_time", None),
				"later_flag": i.get("later_flag", None)
	    	}

	    	endpoint = "https://api.amcrestgps.net/info/load/user"
	    	r = requests.post(url = endpoint, data = json.dumps(user_obj), headers=headers)
	    	if str(r.status_code) == "200":
	    		pass
	    	else:
	    		error.append(i.get("gps_customer_id", None))
	connection.close()

	return {"success":True, "error":error, "message":"User Migration"}