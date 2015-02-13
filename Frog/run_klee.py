mport sys
import subprocess
import re
import glob
import os
import time 
import struct
from support_frog import compute
#####################################################
# run_klee.py
# version 1.0: compile & run klee
# usage: python run_klee.py [file name]
# output: res['msg'] and res['success']
# output: KLEE message in res['klee_msg'], LLVM message in res['llvm_msg']
#####################################################
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
	res['msg'] += "File does not exist. Exit.\n"
	print res
	sys.exit()

#####################################################
# Pre Configuration
#####################################################
# Temp Message File Name
LLVM_COMPILE_MSG = "temp_llvm_compile_msg.txt"
KLEE_MSG = "temp_klee_msg.txt"

# KLEE Related
KLEE_INCLUDE= "tools/KLEE_SOURCE_2015/klee/include/klee"   # Path to include files, for llvm compilation
KLEE_TIMEOUT = 10 
KLEE_OPTIONS = ["--allow-external-sym-calls"] #["--libc=uclibc"]#,"--posix-runtime" ]# KLEE C library Options
KLEE_EXECUTABLE = "./tools/KLEE_SOURCE_2015/klee/Release+Asserts/bin/klee"

# Test Cases 
KTEST = "./tools/KLEE_SOURCE_2015/klee/tools/ktest-tool/ktest-tool "
MAX_TESTS = 10

# Type map for test case result unapck
TYPE_DICT = {'char':'c','signed char':'b','unsigned char':'B','_Bool':'?','short':'h','unsigned short':'H','int':'i','unsigned int':'I','long':'l','unsigned long':'L','long long':'q','unsigned long long':'Q','float':'f','double':'d','char[]':'s','void *':'P'}
CTYPE_DICT = {'int':'%d', 'unsigned int':'%u','double':'%f','float':'%f'}

################################
# 6 - Compile to object file
################################

linkAddr = []
linkAddr.append(KLEE_INCLUDE)

linkCmd = "llvm-gcc --emit-llvm -c -g"
for addr in linkAddr:
	linkCmd += " -I"+addr
linkCmd += " "+testFileName

# Delete old object
if os.path.isfile(testFileObject):
	subprocess.call("rm "+testFileObject,shell=True)

with open(LLVM_COMPILE_MSG, 'w') as f:
	returncode = subprocess.call(linkCmd, stdout=f, shell=True)
with open(LLVM_COMPILE_MSG, 'r') as f:
		res['llvm_msg'] = f.readlines()

if returncode != 0:
	res['msg'] += "Compilation failed, please check syntax based on LLVM message\n"
	print res
	sys.exit() 

################################
# 7 - Klee run
################################

if os.path.isfile(testFileObject):
	
	# Set klee timeout
	with open(KLEE_MSG, 'w') as f:
		proc = subprocess.Popen([KLEE_EXECUTABLE]+KLEE_OPTIONS+[testFileObject], stdout=f)
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

	with open(KLEE_MSG, 'r') as f:
				res['klee_msg'] = f.readlines()
				
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
