import sys
import subprocess
import re
import glob
import os
import threading
import time 
import struct
from support_frog import compute
import json

############################################################################
# replay.py 
# version 1.0: replay test cases then run tarantula 
# usage: python replay.py [test file]
# output: res['msg'] and res['success']
# output: res['test'] test case string array
# output file: [test file name]_matrix.txt
###########################################################################

res = {}
res['success'] = False
res['msg'] = ""
res['test_output'] = ""

#####################################################
# Pre Configuration
#####################################################
# Test Cases 
KTEST = "/home/qirong/Frog/frog_test/tools/KLEE_SOURCE_2015/klee/tools/ktest-tool/ktest-tool "
MAX_TESTS = 10

# Type map for test case result unapck
TYPE_DICT = {'char':'c','signed char':'b','unsigned char':'B','_Bool':'?','short':'h','unsigned short':'H','int':'i','unsigned int':'I','long':'l','unsigned long':'L','long long':'q','unsigned long long':'Q','float':'f','double':'d','char[]':'s','void *':'P'}
CTYPE_DICT = {'int':'%d', 'unsigned int':'%u','double':'%f','float':'%f'}

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	res['msg'] += "Missing argument. Exit.\n"
	print json.dumps(res)
	sys.exit()	
targetFile = sys.argv[1]
test_path = os.path.dirname(targetFile)

# Check if file exists
klee_dir = test_path+'/klee-last/';
if not os.path.exists(klee_dir):
	res['msg'] += "KLEE output does not exists. Exit.\n"
	print json.dumps(res)
	sys.exit()

# Get function data from pickle
if not os.path.isfile(targetFile+".pickle"):
	res['msg'] += "Function data of test file does not exists. Exit.\n"
	print json.dumps(res)
	sys.exit()
with open(targetFile+".pickle", "rb") as fb:
	fdata = pickle.load(fb)
	funcType = fdata.funcType
	funcName = fdata.funcName
	argType = fdata.argType
	argName = fdata.argName
	argIsPointer = fdata.argIsPointer
	argSize = fdata.argSize

################################
# 2 - Initialzation
################################

# Gather testcases file for read
temp_tests = "temp_klee_test_cases.txt" # temporary file to store test case values
if os.path.isfile(temp_tests):
	subprocess.call('rm '+temp_tests, shell=True)
tests = glob.glob(klee_dir+'test*.ktest')

# Build Regex 
p = re.compile(r'^object\s*(\d+):\sdata:\s(.*)\n$') #extract argument value
p_gcov = re.compile('^\s+#####') #gcov uncovered line

'''
# Initialize matrix for Fault Localization
F = []
M = []
'''
test_output = [] #Test cases string array to display

with open(targetFile+"_coverage.txt",'w') as fout:
	testnum = 0
	for test in tests[:MAX_TESTS]:

		# Display test case values, write to temp file klee_tests
		subprocess.call(KTEST+" "+test+' >'+temp_tests, shell=True)					
		testnum += 1
		argcount = 0
		argval = []

		# Find test case value for each argument
		with open(temp_tests,'r') as f:
			testcase_str = ""
			for line in f:
				a = p.findall(line)	
				# If match one parameter value
				if a:
					try:
						index = int( a[0][0])
						raw_val = a[0][1]
					except IndexError, ValueError:
						res['msg'] = "Error: Invalid test case format, Check if ", KTEST, "correct"
						print json.dumps(res)
						sys.exit(1)
					else:
						# Array: Unpack argument string according to size
						if argIsPointer[argcount]:
							arg = raw_val 
							length = len(arg)/argSize[argcount]
							arg_array= []
							unpack_type = TYPE_DICT[ argType[argcount] ]

							try:
								for j in range(size):
									val = struct.unpack(unpack_type, arg[j*length:(j+1)*length] )[0]
									arg_array.append(val)
							except struct.error:
								res['msg'] = "Error: Invalid argument type, unable to unpack from binary format. Check ",KTEST
								print json.dumps(res)
								sys.exit(1)
							
							# Display test cases
							display = argName[ index ] + "="
							
							# Special array: string
							if argType[argcount] == 'char':
								arg_array = "".join(arg_array)
							testcase_str = display + str(arg_array)
							
							# Add test cases for replay
							argval.append( str(arg_array) )
							argcount +=1

						# Single Variable
						else:							
							# Unpack argument according to type
							try:
								unpack_type = TYPE_DICT[ argType[argcount] ] 
								val = struct.unpack(unpack_type, raw_val )[0] 
							except struct.error:
								res['msg'] = "Error: Invalid argument type, unable to unpack from binary format. Check ",KTEST
								print json.dumps(res)
								sys.exit(1)
							
							# Display test cases
							argstr = argName[index]+" = " + str(val)
							testcase_str = argstr
							
							# Add test cases for replay
							argval.append( str(val) )
							argcount += 1
					
		# Judge if argument number valid
		if argcount != len(argName):
			res['msg'] +=  "ERROR: Invalid argument number of only "+str(argcount)
			continue	

		# Build replay test file
		replayFileName = targetFile + '.replay.c'
		if os.path.isfile(replayFileName):
			subprocess.call('rm '+replayFileName, shell=True)
		subprocess.call('cp '+targetFile+' '+replayFileName, shell=True)

		with open(replayFileName, 'ab') as f:
			appendCode = "\n#include <stdio.h>\n"
			appendCode += "int main(){\n"

			# Definition for array type argument
			arg_symbols = {}
			array_cnt = 0
			for i,a in enumerate(argval):
				# Example: int a[5] = {1,2,3,4,5};
				if argIsPointer[i] and argType[i] != 'char':
					s1 = str(argval) 
					s1 = s1.replace('[','{')
					s1 = s1.replace(']','}')
					arg_symbol= "a"+str(array_cnt)
					appendCode = appendCode +'\t'+argType[i]+' '+arg_symbol +'['+str(argSize[i])+'] = '
					appendCode += s1 +";\n"
					array_cnt += 1
					arg_symbols[i] = arg_symbol
					
			if funcType.lower()=='void':
				appendCode+='\t'+funcName+'('
			else:
				appendCode+='\t'+funcType+' returnval='+funcName+'('
			for i,a in enumerate(argval):

				# For string type argument : join list 
				if argIsPointer[i] and argType[i] == 'char':
					a = '"'+a+'"'
				elif argIsPointer[i] and argType[i] != 'char' and i in arg_symbols:
					a = arg_symbols[i]

				appendCode+=a
				if i< len(argval)-1:
					appendCode+=', '
			appendCode+=');\n'
			if funcType.lower() =='void':
				appendCode+='\treturn;\n}'
			else:
				return_type = CTYPE_DICT[funcType.lower()] if funcType.lower() in CTYPE_DICT else '%d'
				appendCode+=r'    printf("Return value is '+return_type + r'\n",returnval);'
				
				appendCode+='\n\treturn;\n}'
			f.write(appendCode)
		
		# Compile test file
		replayOutput = target + '.replay'
		returnval = subprocess.call('gcc -w -fprofile-arcs -ftest-coverage '+replayFileName+' -o '+replayOutput, shell=True)
		if returnval != 0:
			res['msg'] +='ERROR: gcc compile for repalying failed'
			continue
		
		# Run test file
		replay_stdout = subprocess.check_output('./'+replayOutput, shell=True)
		testcase_str += replay_stdout
		
		# Get coverage
		returnval = subprocess.call('gcov '+replayFileName, shell=True)
		if returnval != 0:
			res['msg'] ='ERROR: gcov failed, press ENTER to continue...'
			print json.dumps(res)
			sys.exit(1)

		# RE for not covered lines, marked with"#####" in gcov
		gcovFileName = replayFileName+'.gcov'
		lineCoverage = []
		
		# Read gcov file, write to coverage matrix M
		with open(gcovFileName,'r') as f:
			for i,line in enumerate(f):
				# ignore first 5 lines, not source code
				if i < 5:
					continue
				if p_gcov.match(line) :
					lineCoverage.append(False)
				else:
					lineCoverage.append(True)
		
		test_output.append(testcase_str)			
		fout.write(lineCoverate+"\n")

res['test_output'] = str(test_output)
res['msg'] = "Repaly Suceed."
res['success'] = True
print json.dumps(res)
