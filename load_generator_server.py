import threading as t
import cStringIO
import pycurl
import time
import sys
import csv
import logging
import os

from math import ceil
from flask import Flask, request
from collections import deque

app      = Flask(__name__)		
QUEUE    = deque()

log_file_path = str(os.getcwd() + '/log/generator_client.log')

logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_ips_list():
	return QUEUE.popleft()

def update_ips_list(ips_list):
	QUEUE.appendleft(ips_list)

def is_ips_list_available():
	return bool(QUEUE)

def get_put_load_url(ip, cpu_util):
	return 'http://' + ip + ':5555/level?cpu_util=' + cpu_util

def send_load(ip, cpu_util):
	
	url	= get_put_load_url(ip, cpu_util)
	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	buf.close()

def get_metric_value(metric_type, file_name): 

	csvfile  = open(file_name, "rb")
	csv_file = csv.reader(csvfile, delimiter=' ')

	rownum    = 0
	col_index = 0
	col_name  = metric_type
	
	for row in csv_file:

		cpu_util = 0
    		if rownum == 0:
			header = row
			col_index = header.index(col_name)
    		else:
			yield ceil(float(row[col_index])

		rownum += 1

def generate_load(ips_list, metric_util, metric_type):
	
	for ip in ips_list:
		send_load(ip, metric_util)
		logging.info(metric_type + ': ' + metric_util + ' -> ' + ip)

@app.route('/update')
def update_ips():
	
	ips_list = str(request.args.get('ips')).split(';')
	update_ips_list(ips_list)
	
	return "Updated"

class CPULoaderServer(t.Thread):

	delay        = None
	process      = None
	metric_yield = None
	metric_type  = None
	metric_file  = None
	is_active    = None
	ips_list     = []

	def __init__(self, delay, metric_type, metric_file):
		t.Thread.__init__(self)

		self.delay   	  = delay
		self.metric_type  = metric_type
		self.metric_file  = metric_file
		self.metric_yield = get_metric_value(self.metric_type, self.metric_file)
		self.is_active    = True

	def run(self):

		while self.is_active: 
			
			time.sleep(self.delay)

			if is_ips_list_available():
				self.ips_list = list(get_ips_list())
			
			if len(self.ips_list) > 0:
				
				cpu_util = next(self.metric_yield, None)
				
				if cpu_util != None:
					generate_load(self.ips_list, cpu_util, self.metric_type)
				else:
					logging.warning('No more metric values')
					self.is_active = False

if __name__ == '__main__':
	
	delay	    = int(sys.argv[1])
	metric_type = str(sys.argv[2])
	metric_file = str(sys.argv[3])
	
	cpu_loader = CPULoaderServer(delay, metric_type, metric_file)
	cpu_loader.start()

	app.run('0.0.0.0', port=5555)
