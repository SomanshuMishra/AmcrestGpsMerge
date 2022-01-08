import pymysql
import requests
import json


def load_subscription(customer_id):
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
	    sql = "SELECT * FROM `subscriptions` WHERE customer_id={};".format(customer_id)
	    cursor.execute(sql)
	    result = cursor.fetchall()

	    headers = {
	        "Content-Type": "application/json"
	    }
	    # print(result)
	    for i in result:
	        user_obj = {
	            'customer_id': i.get('customer_id', None),
	            'subscription_id' : i.get('subscription_id', None),
	            'transaction_id' : i.get('transaction_id', None),
	            'subscription_status' : i.get('subscription_status', None),
	            'imei_no' : i.get('imei_no', None),
	            'device_name' : i.get('devicename_formal', None),
	            'device_model' : i.get('imei_device', None),
	            'imei_iccid' : i.get('imei_iccid', None),
	            'sim_status' : i.get('sim_status', None),
	            'ip_address' : i.get('ip_address', None),
	            'start_date' : i.get('start_date', None)[:10],
	            'end_date' : i.get('end_date', None)[:10],
	            'firstBillingDate' : i.get('firstBillingDate', None)[:10],
	            'nextBillingDate' : i.get('nextBillingDate', None)[:10],
	            'order_id' : i.get('order_id', None),
	            'activated_plan_id' : i.get('activated_plan_id', "monthly"),
	            'activated_plan_description' : i.get('activated_plan_description', "$19.99 monthly auto renewal(60 sec reporting) - 10-14 day battery"),
	            'is_active' : i.get('is_active', None),
	            'device_in_use' : i.get('device_in_use', None),
	            'record_date' : str(i.get('record_date', None)),
	            'device_listing' : i.get('device_listing', None),
	            'is_active' : True,
	            'device_in_use':True,
	            'device_listing':True
	        }
	        
	        endpoint = "https://api.amcrestgps.net/info/load/subscription"
	        r = requests.post(url = endpoint, data = json.dumps(user_obj), headers=headers)

	        if str(r.status_code) == "200":
	        	pass
	        else:
	        	error.append(customer_id)
	connection.close()
	return {"success":True, "error":error, "message":"Subscription Migration"}