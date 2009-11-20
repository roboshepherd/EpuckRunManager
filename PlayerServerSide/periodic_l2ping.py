#!/usr/bin/env python

import time, os, sys, sched, subprocess, re, signal, traceback
import gobject, dbus, dbus.service, dbus.mainloop.glib 

schedule = sched.scheduler(time.time, time.sleep)

class glb: # gloabl variables
	robotid = -1
	configfile = ' '
	bd_addr = ' '
	DBUS_PATH = ' '
	DBUS_IFACE = 'uk.ac.newport.ril.EpuckRunManager'
	ping_delay = 5 # in sec
	packet_loss = ' '
	server_exist = 'False'
	server_pid = 0
	

class RobotSignal(dbus.service.Object):
	def __init__(self, object_path):
		dbus.service.Object.__init__(self, dbus.SessionBus(), object_path)

	@dbus.service.signal(dbus_interface= glb.DBUS_IFACE, signature='ss')
	def RobotState(self, bdaddr, sig):
		# The signal is emitted when this method exits
		# You can have code here if you wish
		#pass
		print "Now  %s robot signal is: %s" % (bdaddr, sig)
	def Exit(self):
		loop.quit()


#Emit DBus-Signal 
def emit_dbus_signal(sig):
	global dbus_signal
	print "Emitting signal>>> Player server for Epuck " + glb.bd_addr + ": " + sig
	dbus_signal.RobotState(glb.bd_addr, sig)

def stop_player_server():
	emit_dbus_signal('Terminating')
	#time.sleep(1.0)
	print "\t Killling server >>> PID: ", glb.server_pid
	if(glb.server_pid > 0):
		os.kill(glb.server_pid, signal.SIGKILL)
		glb.server_exist = 'False'
		emit_dbus_signal('Killed')	

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
 
def start_player_server():
	port = get_config('port')
	cfgfile = get_config('cfgfile')
	cmd = "/usr/bin/robot-player -q -p " + port + " " + cfgfile + " " + "&"
	subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	#stdout_value = subproc.communicate()
	print '\t at time:', time.time()
	print "\t sever started"
	#print '\t got player stdout_value:', stdout_value[0]
	glb.server_pid = subproc.pid + 1 # Strange bug fixed: this is actual PID  
	print "\t server PID: ", glb.server_pid
	glb.server_exist = 'True'
	emit_dbus_signal('Alive')

def process_ping_output(output):
	#global packet_loss, server_exist
	pct = re.findall(r"\d\%", output)   
	if(pct):   
		print "%loss: ", pct[0]
		glb.packet_loss = pct[0]
	if (glb.packet_loss == '0%'):
		print "Device Alive"
		# start player-server, if not started yet        
		if(glb.server_exist == 'False'):
			start_player_server()
	if (glb.packet_loss == '100%' or glb.packet_loss == ' '):
		print "Device Dead"
		emit_dbus_signal('Dead')	
		# kill player-server, if already exist
		if(glb.server_exist == 'True'):
			stop_player_server()
	glb.packet_loss = ' '

def perform_ping(bdaddr, inc):
    schedule.enter(inc, 0, perform_ping, (bdaddr, inc)) # re-schedule to make it periodic
    cmd = "/usr/bin/l2ping -c " + " 1 " + bdaddr
    #print cmd
    subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdout_value = subproc.communicate()
    print '\t at time:', time.time()
    #print '\t got l2ping stdout_value:', stdout_value[0]
    process_ping_output(stdout_value[0])

def main():
	global dbus_signal
	try:	
		e = schedule.enter(0, 0, perform_ping, (glb.bd_addr, glb.ping_delay))
		schedule.run()
		loop.run()
	except (KeyboardInterrupt, dbus.DBusException, SystemExit):
		print "User requested exit... shutting down now"
		dbus_signal.Exit()
		pass				
	  	sys.exit(0)

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	session_bus = dbus.SessionBus()

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
		name = dbus.service.BusName(glb.DBUS_IFACE, session_bus)
		dbus_signal = RobotSignal(glb.DBUS_PATH)
		loop = gobject.MainLoop()
		print "Running example signal emitter service."	
	except dbus.DBusException:
		traceback.print_exc()
		sys.exit(1)	

	main()

