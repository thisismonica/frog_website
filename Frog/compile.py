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
# compile.py 
# version 1.0: compile 
# usage: python compile.py [file name]
# output: res['msg'] and res['success']
# output: LLVM message in res['llvm_msg']
###########################################################################
res = {}
res['success'] = False
res['msg'] = ""

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	res['msg'] += "Missing argument. Exit.\n"
	print res
	sys.exit()	

testFileName = sys.argv[1]

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
proc = subprocess.Popen(linkCmd, shell=True, stdout=subprocess.PIPE)
llvm_stdout, llvm_stderr = proc.communicate()
res['msg'] += llvm_stdout if llvm_stdout else ""
res['msg'] += llvm_stderr if llvm_stderr else ""
 
if proc.returncode != 0:
	res['msg'] += "Error: Compilation failed, please check syntax based on LLVM message\n"
	print res
	sys.exit() 
else:
	res['msg'] += "Compilation succeed.\n"
	res['success'] =True
	print res
	sys.exit()
