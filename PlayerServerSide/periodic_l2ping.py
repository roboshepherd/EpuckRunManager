#!/usr/bin/env python

import time, os, sys, sched, subprocess, re, signal


configfile = './player-server-config.txt'
bd_addr = ' '
packet_loss = ' '
server_exist = 'False'
server_pid = 0



schedule = sched.scheduler(time.time, time.sleep)


#Emit DBus-Signal : PlayerServer XXXX (Alive, Killing, Dead)
def emit_dbus_signal(sig):
	print "Emitting signal>>> Player server for Epuck " + bd_addr + ": " + sig


def stop_player_server():
	global server_pid, server_exist
	emit_dbus_signal('Terminating')
	#time.sleep(3.0)
	print "\t Killling server >>> PID: ", server_pid
	
	if(server_pid > 0):
		os.kill(server_pid, signal.SIGKILL)
		server_exist = 'False'
		emit_dbus_signal('Killed')	

def get_config(config):
	global bd_addr, configfile
	result = ' '
	f = open(configfile, 'r')
	data = f.read()
	lst = re.split(';', data)
	if (lst[0] != bd_addr):
		print "BD ADDR does not match"
		return result
	if(config == 'port'):
		result = lst[1]
	if(config == 'cfgfile'):
		result = lst[2]
	return result
 
def start_player_server():
	global server_exist, server_pid
	port = get_config('port')
	cfgfile = get_config('cfgfile')
	cmd = "/usr/bin/robot-player -q -p " + port + " " + cfgfile + " " + "&"
	subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	#stdout_value = subproc.communicate()
	#pscmd = "/bin/ps aux | grep robot-player"
	print '\t at time:', time.time()
	print "\t sever started"
	#print '\t got player stdout_value:', stdout_value[0]
	server_pid = subproc.pid + 1 # Strange Fix! 
	print "\t server PID: ", server_pid
	server_exist = 'True'
	emit_dbus_signal('Alive')

def process_ping_output(output):
	global packet_loss, server_exist
	pct = re.findall(r"\d\%", output)   
	if(pct):   
		print "%loss: ", pct[0]
		packet_loss = pct[0]
	if (packet_loss == '0%'):
		print "Device Alive"
		# start player-server, if not started yet        
		if(server_exist == 'False'):
			start_player_server()
	if (packet_loss == '100%' or packet_loss == ' '):
		print "Device Dead"
		# kill player-server, if already exist
		if(server_exist == 'True'):
			stop_player_server()
	packet_loss = ' '

def perform_ping(bdaddr, inc):
    schedule.enter(inc, 0, perform_ping, (bdaddr, inc)) # re-schedule to make it periodic
    cmd = "/usr/bin/l2ping -c " + " 1 " + bdaddr
    #print cmd
    subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdout_value = subproc.communicate()
    print '\t at time:', time.time()
    #print '\t got l2ping stdout_value:', stdout_value[0]
    process_ping_output(stdout_value[0])

def main(bdaddr, inc=5):
	global bd_addr
	bd_addr = bdaddr
	schedule.enter(0, 0, perform_ping, (bdaddr, inc))
	schedule.run()

if __name__ == '__main__':
	numargs = len(sys.argv) - 1
	if numargs < 1 or numargs > 2:
		print "usage:" + sys.argv[0] + "bdaddr [sec delay]"
		sys.exit(1)
	bdaddr = sys.argv[1]
	if numargs < 3:
		main(bdaddr)
	else:
		inc = int(sys.argv[2])
		main(bdaddr, inc)

