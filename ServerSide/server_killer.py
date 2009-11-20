#!/usr/bin/env python

import os, signal, subprocess, re, sys

cmd = "ps aux | grep manager"
subproc = subprocess.Popen([cmd, ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
output = subproc.communicate()
output=  output[0].split()
if (output[11] != './server_manager.py'):
    sys.exit(1)
print output[1]
pid = int(output[1])
if(pid > 0): 
    os.kill(pid, signal.SIGKILL)
else:
    print "PID not OK"
