#!/usr/bin/env python

import time, os, sys, sched, subprocess, re, signal, traceback
import gobject, dbus, dbus.service, dbus.mainloop.glib 

class glb: # gloabl variables
	config_path = '../EpuckConfigFiles'
	robotid = -1
	configfile = ' '
	bd_addr = ' '
	DBUS_PATH = ' '
	DBUS_IFACE = 'uk.ac.newport.ril.EpuckRunManager'
	client_exist = 'False'
	client_pid = 0
	robot_state = ' '

def start_client():
	port = get_config('port')
	cmd = "./go_avoiding_obstacle" + " " + "&"
	subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	#stdout_value = subproc.communicate()
	print '\t at time:', time.time()
	print "\t client started"
	#print '\t got player stdout_value:', stdout_value[0]
	glb.client_pid = subproc.pid + 1 # Strange bug fixed: this is actual PID  
	print "\t client PID: ", glb.client_pid
	glb.client_exist = 'True'

def stop_client():
	print "\t Stopping client >>> PID: ", glb.client_pid
	if(glb.client_pid > 0):
		os.kill(glb.client_pid, signal.SIGKILL)
		glb.client_exist = 'False'

def manage_client():
	if(robot_state == 'Live'):
		if(client_exist = 'False'):
			print "Starting client..."
			start_client()
		if (client_exist = 'True'):
			pass
	if(robot_state == 'Dead'):
		if(client_exist = 'False'):
			pass
		if (client_exist = 'True'):
			print "Stopping client..."
			stop_client()
	


def robot_signal_handler(robot_bdaddr, state):
    print ("Caught signal (in robot signal handler) "
           + robot_bdaddr + ":" + state)
	glb.robot_state = state
	manage_client() 

def get_config(config):
	result = ' '
	f = open(glb.configfile, 'r')
	data = f.read()
	lst = re.split(';', data)
	if(int(lst[0]) != glb.robotid):
		print "Robot ID does not match"
	if (config == 'bdaddr'):
		result = lst[1]
	if(config == 'port'):
		result = lst[2]
	if(config == 'cfgfile'):
		result = lst[3]
	return result
  
def main():
	try:
		loop = gobject.MainLoop()
		loop.run()
	except (KeyboardInterrupt, SystemExit):
		print "User requested exit... shutting down now"
		pass				
	  	sys.exit(0)


if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)	
	bus = dbus.SessionBus()

	numargs = len(sys.argv) - 1
	if numargs > 1 or numargs < 1:
		print "usage:" + sys.argv[0] + "<Robot ID>"
		sys.exit(1)
	else:
		glb.robotid = int(sys.argv[1])
		glb.configfile = glb.config_path + '/robot'+sys.argv[1]+'.txt' # cfg file as "<config_path>/robot<X>.txt"
		glb.bd_addr = get_config('bdaddr')
		glb.DBUS_PATH = '/robot'+sys.argv[1]

	try:
		bus_object  = bus.get_object(glb.DBUS_IFACE, glb.DBUS_PATH)
		bus_object.connect_to_signal("RobotState", robot_signal_handler, dbus_interface=glb.DBUS_IFACE)
		bus.add_signal_receiver(robot_signal_handler, dbus_interface = glb.DBUS_IFACE, signal_name = 'RobotState')
	except dbus.DBusException:
		traceback.print_exc()
		sys.exit(1)
	main()



