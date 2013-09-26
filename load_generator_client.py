import threading as t
import time
import subprocess
import sys

from flask import Flask, request
from collections import deque

app      = Flask(__name__)		
QUEUE    = deque()

def get_ncpus():
	return str(subprocess.Popen(['nproc'], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0])
	
def is_cpu_value_available():
	return bool(QUEUE)

def get_cpu_value():
   	return QUEUE.popleft()

def put_cpu_value(item):
	QUEUE.append(item)

def run_process(cpu_util, ncpus):
	return subprocess.Popen(['lookbusy', '--ncpus', ncpus, '--cpu-util', cpu_util])


@app.route('/level')
def cpu_level():
	
	cpu_util = str(request.args.get('cpu_util'))
	put_cpu_value(cpu_util)
	return "Ok"

class CPULoaderClient(t.Thread):

	delay    = None
	process  = None

	def __init__(self, delay, ncpus):
		t.Thread.__init__(self)
		self.delay     = delay
		self.ncpus     = ncpus

	def run(self):

		while True: 
			
			while not is_cpu_value_available():

				print "sleep"
				time.sleep(self.delay)
			
			cpu_util    = get_cpu_value()
			tmp_process = run_process(cpu_util, self.ncpus)
			
			if(self.process != None):
				self.process.terminate()
				self.process = tmp_process

			
if __name__ == '__main__':
	
	ncpus	= get_ncpus()
	delay	= int(sys.argv[1])
	
	cpu_loader = CPULoaderClient(delay, ncpus)
	cpu_loader.start()

	app.run(host='0.0.0.0')
