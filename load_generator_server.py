import threading as t
import time
import sys

from flask import Flask, request
from collections import deque

app      = Flask(__name__)		
QUEUE    = deque()

def get_ips_list():
	return QUEUE.popleft()

def update_ips_list(ips_list):
	QUEUE.appendleft(ips_list)

def is_ips_list_available():
	return bool(QUEUE)

''']
import cStringIO
	import pycurl
	import sys
def get_put_load_url(cpu_util):
return 'http://150.165.85.225:5000/level?cpu_util=' + cpu_util

cpu_util = str(sys.argv[1])

url	= get_put_load_url(cpu_util)
	
buf = cStringIO.StringIO()

c = pycurl.Curl()
c.setopt(c.URL, url)
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()

buf.close()
'''
def generate_load(ips_list):
	
	for ip in ips_list:
		print ip

@app.route('/update')
def update_ips():
	
	ips_list = str(request.args.get('ips')).split(';')
	update_ips_list(ips_list)
	
	return "Updated"

class CPULoaderServer(t.Thread):

	delay    = None
	process  = None
	ips_list = []

	def __init__(self, delay):
		t.Thread.__init__(self)
		self.delay     = delay

	def run(self):

		while True: 
			
			time.sleep(self.delay)

			if is_ips_list_available():
				self.ips_list = list(get_ips_list())
			
			generate_load(self.ips_list)

if __name__ == '__main__':
	
	delay	= int(sys.argv[1])
	
	cpu_loader = CPULoaderServer(delay)
	cpu_loader.start()

	app.run('0.0.0.0')
