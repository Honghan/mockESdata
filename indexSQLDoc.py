import pyodbc
import httplib
import urllib
import random
import math
import time
import json
import datetime

#db setting
dsn = 'sqlserverdatasource'
user = ''
password = ''
database = ''

# elastic server (using redhat cloud server or local ones)
es_server = ""
indexname = "time2016"

# post data (dictionary) to the elastic server
def postdata(dic):
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(es_server)
    for indexstr in dic:
        params = json.dumps(dic[indexstr]) #urllib.urlencode(dic[indexstr])
        print(params)
        conn.request("POST", indexstr, params, headers)
        response = conn.getresponse()
        data = response.read()
        print (data)
    conn.close()

# delete indice from the elastic server
# arr - the string array containing all indice to be delete
def cleanIndex(arr, conn=None):
    if conn is None:
        conn = httplib.HTTPConnection(es_server)
    for idexstr in arr:
        conn.request('DELETE', idexstr, '')
        resp = conn.getresponse()
        print( resp.read() )


def readDataFromDB():
	data = {}
	con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
	cnxn = pyodbc.connect(con_string)
	cursor = cnxn.cursor()
	cursor.execute("select t.ID, t.src_table, t.src_col, t.doc_id, t.ProcessedText, v.updatetime from test_results t left join vw_COG_all_bin_coordinates v on t.id=v.id and t.doc_id=v.doc_id")
	rows = cursor.fetchall()
	for row in rows:
		indexid = "/" + indexname + "/doc/" + str(row.doc_id)
		d = {}
		d["patientId"] = str(row.ID)
		d["srcTable"] = row.src_table
		d["srcCol"] = row.src_col
		d["docId"] = str(row.doc_id)
		d["html"] =  unicode(row.ProcessedText, errors='ignore')
		d["thumbnail"] = '%s_%s_%s.png' % (row.ID, row.src_table, row.doc_id)
		d["updateTime"] = str(row.updatetime)
		d["timestamp"] = (row.updatetime - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0
		data[indexid] = d
	return data

print('reading data...')
data = readDataFromDB()
print('total %s rows.' % (len(data)) )
print('data read, saving to Elastic Index...')

cleanIndex(['/' + indexname])
postdata(data)
print('all done')






