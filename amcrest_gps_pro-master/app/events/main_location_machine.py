import pymysql
import requests
import json



def get_location(longitude, latitude):
	# connection = pymysql.connect(host="localhost",
	#                              user="root",
	#                              password="r00t",
	#                              db="data_loader",
	#                              cursorclass=pymysql.cursors.DictCursor)

	connection = pymysql.connect(host="206.198.230.28",
	                             user="amcrestg_amcgpsu",
	                             password="CH]u{A92pai2",
	                             db="amcrestg_gpsamcr",
	                             cursorclass=pymysql.cursors.DictCursor)


	with connection.cursor() as cursor:
	    # Read a single record
	    sql = "SELECT * FROM `locations` WHERE latitude={0} AND longitude={1};".format(latitude, longitude)
	    cursor.execute(sql)
	    result = cursor.fetchall()
	    connection.close()
	    if result:
	    	result[0]['location_name'] = result[0]['location']
	    	return result[0]
	    return None

	    
def save_location(location_object):
	# location_object = args[0]
	latitude = location_object['latitude']
	longitude = location_object['longitude']
	location_name = location_object['location_name']
	
	connection = pymysql.connect(host="206.198.230.28",
		                         user="amcrestg_amcgpsu",
		                         password="CH]u{A92pai2",
		                         db="amcrestg_gpsamcr",
		                         cursorclass=pymysql.cursors.DictCursor)
	# connection = pymysql.connect(host="localhost",
	#                              user="root",
	#                              password="r00t",
	#                              db="data_loader",
	#                              cursorclass=pymysql.cursors.DictCursor)

	with connection.cursor() as cursor:
		sql = "INSERT INTO `locations` (latitude, longitude, location) VALUES ({},  {}, '{}');".format(latitude, longitude, location_name)
		print(sql)
		cursor.execute(sql)
		connection.commit()
		print('-----------------saved')
		connection.close()