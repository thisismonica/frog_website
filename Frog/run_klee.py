import sys
import subprocess
import re
import glob
import os
import threading
import time 
import struct
from support_frog import compute

############################################################################
# run_klee.py
# version 1.0: compile & run klee
# usage: python run_klee.py [file name]
# output: res['msg'] and res['success']
# output: KLEE message in res['klee_msg'], LLVM message in res['llvm_msg']
###########################################################################
res = {}
res['success'] = False
res['msg'] = ""
res['llvm_msg'] = ""
res['klee_msg'] = ""

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	res['msg'] += "Missing argument. Exit.\n"
	print res
	sys.exit()	

testFileName = sys.argv[1]
testFileObject = re.sub('\.c$', '.o', testFileName)

# Check if file exists
if not os.path.isfile(testFileName):
	res['msg'] += testFileName+ "File does not exist. Exit.\n"
	print res
	sys.exit()

#####################################################
# Pre Configuration
#####################################################

# KLEE Related
KLEE_INCLUDE= "/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/include/klee"   # Path to include files, for llvm compilation
KLEE_TIMEOUT = 10 
KLEE_OPTIONS = ["--allow-external-sym-calls"] #["--libc=uclibc"]#,"--posix-runtime" ]# KLEE C library Options
KLEE_EXECUTABLE = "/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/Release+Asserts/bin/klee"

# Test Cases 
KTEST = "/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/tools/ktest-tool/ktest-tool "

################################
# Function definition
###############################
kill_check = threading.Event()
def _kill_process(pid):
	os.kill(pid, signal.SIGTERM)
	kill_check.set()
	return

################################
# 6 - Compile to object file
################################

linkAddr = []
linkAddr.append(KLEE_INCLUDE)

linkCmd = "llvm-gcc --emit-llvm -c -g"
for addr in linkAddr:
	linkCmd += " -I"+addr
linkCmd += " "+testFileName
linkCmd += " -o "+testFileObject

# Delete old object
if os.path.isfile(testFileObject):
	subprocess.call("rm "+testFileObject,shell=True)

# Compile
proc = res['llvm_msg'] = subprocess.Popen(linkCmd, shell=True, stdout=subprocess.PIPE)
llvm_stdout, llvm_stderr = proc.communicate()
res['llvm_msg'] = llvm_stdout if llvm_stdout else ""
res['llvm_msg'] += llvm_stderr if llvm_stderr else ""
 
if proc.returncode != 0:
	res['msg'] += "Compilation failed, please check syntax based on LLVM message\n"
	print res
	sys.exit() 

################################
# 7 - Klee run
################################

if os.path.isfile(testFileObject):
	# Run KLEE	
	proc = subprocess.Popen([KLEE_EXECUTABLE]+KLEE_OPTIONS+[testFileObject], stdout=subprocess.PIPE)

	# Set watchdog timer
	pid = proc.pid
	watchdog = threading.Timer(KLEE_TIMEOUT,_kill_process, args=(pid,))
	watchdog.start()
	(klee_stdout, klee_stderr) = proc.communicate()
	returncode = proc.returncode
	watchdog.cancel()
	isTimeout = kill_check.isSet()
	'''
	start = time.time()
	isTimeout = False
	timeout = KLEE_TIMEOUT 
	while proc.poll() is None:
		time.sleep(0.1)
		now = time.time()
		if (now-start) > timeout:
			res['msg'] += "KLEE timeout..."
			isTimeout = True
			proc.kill()
	returncode = proc.returncode
	if proc.stdout:
		klee_stdout = proc.stdout.read()
		#klee_stdout, klee_stderr= proc.communicate()
	
	with open(KLEE_MSG, 'r') as f:
		res['klee_msg'] = f.readlines()
	'''
	res['klee_msg'] = klee_stdout if klee_stdout else ""
	res['klee_msg'] += klee_stderr if klee_stderr else ""

	if isTimeout:
		res['msg']+="KLEE alreayd run for: ",KLEE_TIMEOUT," secs" 
	else:
		if returncode != 0:
			res['msg'] += "KLEE Failed\n"
			print res
			sys.exit()

	# Sucessfully run klee, Output
	res['msg'] += "KLEE Run Sucessfully.\n"
	res['success'] = True
	print res 

else:
	res['msg'] += "Object file does not exist."
	print res
	sys.exit()
