#!/usr/bin/env python

import time, os, sys, sched, subprocess, re, signal, traceback
import gobject, dbus, dbus.service, dbus.mainloop.glib 

class glb: # gloabl variables
	robotid = -1
	configfile = ' '
	bd_addr = ' '
	DBUS_PATH = ' '
	DBUS_IFACE = 'uk.ac.newport.ril.EpuckRunManager'
	client_exist = 'False'
	client_pid = 0
	robot_state = ' '


def manage_client():
	if(robot_state == 'Live'):
		if(client_exist = 'False'):
			print "Starting client..."
		if (client_exist = 'True'):
			pass
	if(robot_state == 'Dead'):
		if(client_exist = 'False'):
			pass
		if (client_exist = 'True'):
			print "Stopping client..."
	


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
		glb.configfile = './robot'+sys.argv[1]+'.txt' # cfg file as "robot<X>.txt"
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



